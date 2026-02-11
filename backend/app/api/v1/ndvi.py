"""NDVI time-series endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.models.measurement import Measurement
from app.schemas.ndvi import NDVIRequest, NDVIResponse, NDVIDataPoint
from app.services.ndvi_service import NDVIService
from app.services.earth_engine import EarthEngineManager

router = APIRouter(prefix="/ndvi", tags=["ndvi"])


@router.post("/calculate", response_model=NDVIResponse, status_code=202)
async def calculate_ndvi(
    request: NDVIRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Calculate NDVI time-series for a farm.

    Triggers calculation using Earth Engine Sentinel-2 data.
    Results are stored in the measurements table with measurement_type='ndvi'.

    Returns:
        NDVI data points with statistics (mean, min, max)

    Raises:
        404: Farm not found or unauthorized
        429: Earth Engine quota exceeded
        500: Earth Engine or calculation error
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
        # Get Earth Engine manager and NDVI service
        ee_manager = EarthEngineManager.get_instance()
        ndvi_service = NDVIService(ee_manager)

        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Get GeoJSON geometry from farm
        farm_geojson = farm.to_geojson()

        # Calculate NDVI
        ndvi_data = await ndvi_service.calculate_ndvi_time_series(
            geometry=farm_geojson["geometry"],
            start_date=start_date,
            end_date=end_date,
        )

        if not ndvi_data:
            raise HTTPException(
                status_code=400,
                detail="No NDVI data available for this date range (cloud cover too high?)",
            )

        # Store results in database
        stored_measurements = []
        for data_point in ndvi_data:
            measurement_date = datetime.strptime(data_point["date"], "%Y-%m-%d").date()

            # Check if measurement already exists (avoid duplicates)
            existing = await db.execute(
                select(Measurement).where(
                    and_(
                        Measurement.farm_id == farm.id,
                        Measurement.measurement_type == "ndvi",
                        Measurement.measurement_date == measurement_date,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicates

            measurement = Measurement(
                farm_id=farm.id,
                measurement_type="ndvi",
                measurement_date=measurement_date,
                value=data_point["ndvi"],
                std_dev=data_point.get("std"),
                meta={
                    "source": "Sentinel-2",
                    "band_calculation": "(B8 - B4) / (B8 + B4)",
                },
            )
            db.add(measurement)
            stored_measurements.append(measurement)

        await db.commit()

        # Calculate statistics
        if ndvi_data:
            ndvi_values = [d["ndvi"] for d in ndvi_data]
            mean_ndvi = sum(ndvi_values) / len(ndvi_values)
            min_ndvi = min(ndvi_values)
            max_ndvi = max(ndvi_values)
        else:
            mean_ndvi = min_ndvi = max_ndvi = None

        return NDVIResponse(
            farm_id=farm.id,
            farm_name=farm.name,
            start_date=request.start_date,
            end_date=request.end_date,
            data_points=[
                NDVIDataPoint(**point) for point in ndvi_data
            ],
            total_points=len(ndvi_data),
            mean_ndvi=mean_ndvi,
            min_ndvi=min_ndvi,
            max_ndvi=max_ndvi,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid geometry or date range: {str(e)}",
        )
    except Exception as e:
        # Handle Earth Engine specific errors
        if "quota" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Earth Engine quota exceeded, try again later",
            )
        raise HTTPException(
            status_code=500,
            detail=f"NDVI calculation failed: {str(e)}",
        )


@router.get("/{farm_id}", response_model=NDVIResponse)
async def get_ndvi_time_series(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Retrieve stored NDVI time-series for a farm.

    Returns previously calculated measurements from the database.
    Does not trigger new calculation.
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

    # Retrieve measurements
    measurements_result = await db.execute(
        select(Measurement)
        .where(
            and_(
                Measurement.farm_id == farm.id,
                Measurement.measurement_type == "ndvi",
            )
        )
        .order_by(Measurement.measurement_date)
    )
    measurements = measurements_result.scalars().all()

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No NDVI measurements found for this farm",
        )

    # Convert to response format
    data_points = [
        NDVIDataPoint(
            date=m.measurement_date.isoformat(),
            ndvi=m.value,
            std=m.std_dev or 0.0,
        )
        for m in measurements
    ]

    # Calculate statistics
    ndvi_values = [m.value for m in measurements]
    mean_ndvi = sum(ndvi_values) / len(ndvi_values) if ndvi_values else None

    return NDVIResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        start_date=measurements[0].measurement_date.isoformat(),
        end_date=measurements[-1].measurement_date.isoformat(),
        data_points=data_points,
        total_points=len(data_points),
        mean_ndvi=mean_ndvi,
        min_ndvi=min(ndvi_values) if ndvi_values else None,
        max_ndvi=max(ndvi_values) if ndvi_values else None,
    )
