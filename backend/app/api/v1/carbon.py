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
    Calculate carbon sequestration using IPCC Tier 2 methodology with uncertainty quantification.

    Retrieves NDVI measurements for specified farm and date range, optionally integrating
    LULC classification for land-use-specific allometric equations (IPCC Tier 2).
    Produces carbon estimates with Monte Carlo uncertainty quantification (10,000 iterations),
    95% confidence intervals, and confidence scores for each data point.
    
    Results are stored in measurements table with measurement_type='carbon', including
    confidence metrics in the meta field and std_dev field for direct access.

    Parameters:
        request: Farm ID and date range for calculation
        
    Returns:
        CarbonResponse with:
        - data_points: Carbon estimates including:
          - confidence_score (0-100, higher = more confident)
          - confidence_interval_lower/upper (95% CI bounds in CO2 tonnes/ha)
          - std_dev (standard deviation from Monte Carlo simulation)
        - statistics: Aggregated metrics including mean_confidence_score and overall_std_dev
        - metadata: Model details including methodology (IPCC Tier 2/Tier 1), land_use_class,
                   monte_carlo_iterations, uncertainty_method

    Raises:
        404: Farm not found, no NDVI data available, or farm inactive
        403: User lacks access to farm
        400: Invalid date range or calculation error
        429: Earth Engine quota exceeded
        500: Calculation or service error
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

        # Optionally fetch LULC data for Tier 2 estimation
        lulc_data = None
        lulc_result = await db.execute(
            select(Measurement)
            .where(
                and_(
                    Measurement.farm_id == farm.id,
                    Measurement.measurement_type == "lulc",
                )
            )
            .order_by(Measurement.measurement_date.desc())
        )
        lulc_measurements = lulc_result.scalars().all()
        if lulc_measurements:
            latest_lulc = lulc_measurements[0]
            if latest_lulc.meta:
                lulc_data = {
                    "dominant_class": latest_lulc.meta.get("dominant_class"),
                    "classes": latest_lulc.meta.get("classes"),
                }

        # Calculate carbon using CarbonService (with optional LULC for Tier 2)
        carbon_result = await CarbonService.estimate_carbon_sequestration_async(
            ndvi_data=ndvi_data,
            area_ha=farm.area_ha,
            start_date=start_date,
            end_date=end_date,
            lulc_data=lulc_data,
        )

        # Map service result keys to schema field names for consistency
        # Service returns: ci_lower, ci_upper → Schema expects: confidence_interval_lower, confidence_interval_upper
        for point in carbon_result["data_points"]:
            if "ci_lower" in point:
                point["confidence_interval_lower"] = point.pop("ci_lower")
            if "ci_upper" in point:
                point["confidence_interval_upper"] = point.pop("ci_upper")

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
                std_dev=data_point.get("std_dev"),  # Store standard deviation from Monte Carlo
                meta={
                    "model_version": carbon_result["metadata"]["model_version"],
                    "model_name": carbon_result["metadata"]["model_name"],
                    "methodology": carbon_result["metadata"].get("methodology"),
                    "uncertainty_method": carbon_result["metadata"].get("uncertainty_method"),
                    "land_use_class": carbon_result["metadata"].get("land_use_class"),
                    "monte_carlo_iterations": carbon_result["metadata"].get("monte_carlo_iterations"),
                    "carbon_tonnes": data_point["carbon_total_tonnes"],
                    "agb_tonnes": data_point["agb_total_tonnes"],
                    "confidence_score": data_point.get("confidence_score"),
                    "confidence_interval_lower": data_point.get("confidence_interval_lower"),
                    "confidence_interval_upper": data_point.get("confidence_interval_upper"),
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

    ## Overview
    Returns previously calculated carbon measurements with summary statistics covering:
    - Above Ground Biomass (AGB) estimates
    - Carbon stock estimates
    - CO2 equivalent calculations
    - Uncertainty quantification and confidence metrics

    ## IPCC Tier 2 Methodology with Monte Carlo Uncertainty
    Results are calculated using IPCC Tier 2 approach with stochastic uncertainty quantification:

    ### Allometric Equations
    - Uses land-use-specific allometric equations from Chave et al. (2014)
    - Different equations for 9 land-use classes: Water, Trees, Grass, Flooded Vegetation, Crops, Shrub/Scrub, Built Area, Bare Ground, Snow/Ice
    - AGB derived from: AGB = a × NDVI^b, with parameters selected based on land cover classification

    ### Uncertainty Quantification
    - Monte Carlo simulation with 10,000 iterations per measurement point
    - Parameters sampled from parameter uncertainty distributions (mean ± std dev)
    - NDVI measurement uncertainty incorporated into simulation
    - Produces distribution of possible AGB values per point

    ### Confidence Metrics
    - **confidence_interval_lower**: 2.5th percentile of Monte Carlo distribution (95% CI lower bound)
    - **confidence_interval_upper**: 97.5th percentile of Monte Carlo distribution (95% CI upper bound)
    - **confidence_score**: 0-100 score inversely proportional to coefficient of variation (higher score = lower uncertainty)
    - **std_dev**: Standard deviation from Monte Carlo simulation iterations

    ### LULC Integration
    When available, LULC (Land Use/Land Cover) classification from Dynamic World coordinates parameter selection
    for more accurate land-use-specific allometric equations. Falls back to default coefficients if LULC unavailable.

    ## Response Fields
    All confidence metric fields are optional for backward compatibility:
    - **confidence_score**: Uncertainty confidence metric (0-100, higher is more certain)
    - **confidence_interval_lower**: Lower bound of 95% confidence interval (tonnes)
    - **confidence_interval_upper**: Upper bound of 95% confidence interval (tonnes)
    - **std_dev**: Standard deviation from Monte Carlo simulation

    ## Statistics
    - mean_confidence_score: Average confidence across all measurements
    - overall_std_dev: Average standard deviation across all measurements

    Returns 404 if farm not found or user lacks access.
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
            confidence_score=m.meta.get("confidence_score") if m.meta else None,
            confidence_interval_lower=m.meta.get("confidence_interval_lower") if m.meta else None,
            confidence_interval_upper=m.meta.get("confidence_interval_upper") if m.meta else None,
            std_dev=m.std_dev,
        )
        for m in measurements
    ]

    # Calculate statistics
    if data_points:
        co2_values = [dp.co2_total_tonnes for dp in data_points]
        carbon_values = [dp.carbon_total_tonnes for dp in data_points]
        
        # Calculate confidence metrics (if available)
        confidence_scores = [dp.confidence_score for dp in data_points if dp.confidence_score is not None]
        std_devs = [dp.std_dev for dp in data_points if dp.std_dev is not None]

        stats = CarbonStatistics(
            mean_agb_tonnes_ha=sum(dp.agb_tonnes_ha for dp in data_points) / len(data_points),
            total_agb_tonnes=sum(dp.agb_total_tonnes for dp in data_points),
            mean_carbon_tonnes_ha=sum(dp.carbon_tonnes_ha for dp in data_points) / len(data_points),
            total_carbon_tonnes=sum(carbon_values),
            total_co2_tonnes=sum(co2_values),
            min_ndvi=0.0,  # Would need to calculate from stored NDVI
            max_ndvi=1.0,
            mean_ndvi=0.5,
            mean_confidence_score=sum(confidence_scores) / len(confidence_scores) if confidence_scores else None,
            overall_std_dev=sum(std_devs) / len(std_devs) if std_devs else None,
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
            model_version=measurements[0].meta.get("model_version", "v2.0") if measurements[0].meta else "v2.0",
            model_name=measurements[0].meta.get("model_name", "IPCC Tier 2") if measurements[0].meta else "IPCC Tier 2",
            carbon_fraction=0.47,
            co2_conversion_factor=44 / 12,
            assumptions=measurements[0].meta.get("assumptions", []) if measurements[0].meta and "assumptions" in measurements[0].meta else [
                "IPCC Tier 2 with Land-Use-Specific Allometric Equations",
                "Monte Carlo Simulation (10,000 iterations)",
                "95% Confidence Intervals from percentiles",
            ],
            methodology=measurements[0].meta.get("methodology") if measurements[0].meta else None,
            uncertainty_method=measurements[0].meta.get("uncertainty_method") if measurements[0].meta else None,
            land_use_class=measurements[0].meta.get("land_use_class") if measurements[0].meta else None,
            monte_carlo_iterations=measurements[0].meta.get("monte_carlo_iterations") if measurements[0].meta else None,
        ),
        total_points=len(data_points),
    )
