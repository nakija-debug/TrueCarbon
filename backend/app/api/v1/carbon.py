"""Carbon estimation endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.models.measurement import Measurement
from app.schemas.carbon import CarbonRequest, CarbonResponse, CarbonDataPoint, CarbonStatistics, CarbonMetadata
from app.services.carbon_service import CarbonService, CarbonCalculationError

router = APIRouter(prefix="/carbon", tags=["carbon"])


@router.post("/calculate", response_model=CarbonResponse, status_code=202)
async def calculate_carbon(
    request: CarbonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Calculate carbon sequestration from NDVI time-series.

    Retrieves NDVI measurements for specified farm and date range,
    then estimates carbon using allometric equations.
    Results are stored in measurements table with measurement_type='carbon'.

    Returns:
        Carbon estimation with data points and statistics

    Raises:
        404: Farm not found or no NDVI data available
        403: User lacks access to farm
        400: Invalid date range or calculation error
    """
    # Verify farm exists and user has access
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == request.farm_id,
                Farm.company_id == current_user.company_id,
                Farm.is_active == True,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail=f"Farm {request.farm_id} not found or inactive",
        )

    try:
        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Retrieve NDVI measurements for date range
        ndvi_result = await db.execute(
            select(Measurement)
            .where(
                and_(
                    Measurement.farm_id == farm.id,
                    Measurement.measurement_type == "ndvi",
                    Measurement.measurement_date >= start_date,
                    Measurement.measurement_date <= end_date,
                )
            )
            .order_by(Measurement.measurement_date)
        )
        ndvi_measurements = ndvi_result.scalars().all()

        if not ndvi_measurements:
            raise HTTPException(
                status_code=404,
                detail="No NDVI data available for this date range",
            )

        # Convert to CarbonService format
        ndvi_data = [
            {
                "date": m.measurement_date.isoformat(),
                "ndvi": m.value,
            }
            for m in ndvi_measurements
        ]

        # Calculate carbon using CarbonService
        carbon_result = await CarbonService.estimate_carbon_sequestration_async(
            ndvi_data=ndvi_data,
            area_ha=farm.area_ha,
            start_date=start_date,
            end_date=end_date,
        )

        # Store carbon measurements in database
        stored_measurements = []
        for data_point in carbon_result["data_points"]:
            measurement_date = datetime.strptime(data_point["date"], "%Y-%m-%d").date()

            # Check if measurement already exists (avoid duplicates)
            existing = await db.execute(
                select(Measurement).where(
                    and_(
                        Measurement.farm_id == farm.id,
                        Measurement.measurement_type == "carbon",
                        Measurement.measurement_date == measurement_date,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicates

            measurement = Measurement(
                farm_id=farm.id,
                measurement_type="carbon",
                measurement_date=measurement_date,
                value=data_point["co2_total_tonnes"],  # Store CO2 equivalent
                std_dev=None,  # No uncertainty for now
                meta={
                    "model_version": carbon_result["metadata"]["model_version"],
                    "model_name": carbon_result["metadata"]["model_name"],
                    "carbon_tonnes": data_point["carbon_total_tonnes"],
                    "agb_tonnes": data_point["agb_total_tonnes"],
                },
            )
            db.add(measurement)
            stored_measurements.append(measurement)

        await db.commit()

        # Build response
        return CarbonResponse(
            farm_id=farm.id,
            farm_name=farm.name,
            start_date=request.start_date,
            end_date=request.end_date,
            area_ha=farm.area_ha,
            data_points=[CarbonDataPoint(**point) for point in carbon_result["data_points"]],
            statistics=CarbonStatistics(**carbon_result["statistics"]),
            metadata=CarbonMetadata(**carbon_result["metadata"]),
            total_points=len(carbon_result["data_points"]),
        )

    except CarbonCalculationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Carbon calculation failed: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date range or calculation parameters: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during carbon calculation: {str(e)}",
        )


@router.get("/{farm_id}", response_model=CarbonResponse)
async def get_carbon_estimates(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Retrieve stored carbon estimates for a farm.

    Returns previously calculated carbon measurements with summary statistics.
    Does not trigger new calculations.
    """
    # Verify farm exists and user has access
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
                Farm.is_active == True,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Retrieve carbon measurements
    measurements_result = await db.execute(
        select(Measurement)
        .where(
            and_(
                Measurement.farm_id == farm.id,
                Measurement.measurement_type == "carbon",
            )
        )
        .order_by(Measurement.measurement_date)
    )
    measurements = measurements_result.scalars().all()

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No carbon estimates found for this farm",
        )

    # Convert to response format
    # Note: We need to reconstruct data points - in real scenario, would store full breakdown
    data_points = [
        CarbonDataPoint(
            date=m.measurement_date.isoformat(),
            ndvi=0.0,  # Would need to look up from NDVI measurement
            agb_tonnes_ha=m.meta.get("agb_tonnes", 0) / farm.area_ha if m.meta else 0,
            agb_total_tonnes=m.meta.get("agb_tonnes", 0) if m.meta else 0,
            carbon_tonnes_ha=m.meta.get("carbon_tonnes", 0) / farm.area_ha if m.meta else 0,
            carbon_total_tonnes=m.meta.get("carbon_tonnes", 0) if m.meta else 0,
            co2_tonnes_ha=m.value / farm.area_ha,
            co2_total_tonnes=m.value,
        )
        for m in measurements
    ]

    # Calculate statistics
    if data_points:
        co2_values = [dp.co2_total_tonnes for dp in data_points]
        carbon_values = [dp.carbon_total_tonnes for dp in data_points]

        stats = CarbonStatistics(
            mean_agb_tonnes_ha=sum(dp.agb_tonnes_ha for dp in data_points) / len(data_points),
            total_agb_tonnes=sum(dp.agb_total_tonnes for dp in data_points),
            mean_carbon_tonnes_ha=sum(dp.carbon_tonnes_ha for dp in data_points) / len(data_points),
            total_carbon_tonnes=sum(carbon_values),
            total_co2_tonnes=sum(co2_values),
            min_ndvi=0.0,  # Would need to calculate from stored NDVI
            max_ndvi=1.0,
            mean_ndvi=0.5,
        )
    else:
        stats = CarbonStatistics(
            mean_agb_tonnes_ha=0,
            total_agb_tonnes=0,
            mean_carbon_tonnes_ha=0,
            total_carbon_tonnes=0,
            total_co2_tonnes=0,
            min_ndvi=0,
            max_ndvi=0,
            mean_ndvi=0,
        )

    return CarbonResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        start_date=measurements[0].measurement_date.isoformat(),
        end_date=measurements[-1].measurement_date.isoformat(),
        area_ha=farm.area_ha,
        data_points=data_points,
        statistics=stats,
        metadata=CarbonMetadata(
            model_version="v1.0",
            model_name="Pan-tropical Allometric Equation (Chave et al. 2014)",
            agb_coefficient_a=142.9,
            agb_exponent_b=1.60,
            carbon_fraction=0.47,
            co2_conversion_factor=44 / 12,
            assumptions=[
                "AGB = 142.9 * NDVI^1.60",
                "Carbon = AGB * 0.47 (IPCC Tier 1)",
                "CO2 equivalent = Carbon * 44/12",
                "Valid for tropical/subtropical regions",
            ],
        ),
        total_points=len(data_points),
    )
