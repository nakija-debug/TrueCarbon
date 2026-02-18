"""NDVI time-series endpoints."""

import logging
from datetime import datetime
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.models.measurement import Measurement
from app.schemas.ndvi import NDVIRequest, NDVIResponse, NDVIDataPoint
from app.schemas.environmental import EnvironmentalRequest, EnvironmentalResponse, EnvironmentalDataPoint
from app.services.ndvi_service import NDVIService
from app.services.carbon_service import CarbonService, CarbonCalculationError
from app.services.earth_engine import EarthEngineManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ndvi", tags=["ndvi"])


@router.post("/calculate", response_model=NDVIResponse, status_code=202)
async def calculate_ndvi(
    request: NDVIRequest,
    calculate_carbon: bool = Query(False, description="Also calculate carbon sequestration"),
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

        # Optionally calculate carbon sequestration if requested
        if calculate_carbon and ndvi_data:
            try:
                # Call carbon service to estimate sequestration from NDVI data
                carbon_result = await CarbonService.estimate_carbon_sequestration_async(
                    ndvi_data=ndvi_data,
                    area_ha=farm.area_ha,
                    start_date=request.start_date,
                    end_date=request.end_date,
                )

                # Store carbon measurements in database
                for data_point in carbon_result.get("data_points", []):
                    measurement_date = data_point["date"]
                    
                    # Check if carbon measurement already exists
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
                        continue

                    carbon_measurement = Measurement(
                        farm_id=farm.id,
                        measurement_type="carbon",
                        measurement_date=measurement_date,
                        value=data_point["carbon_tonnes_ha"],
                        std_dev=None,
                        meta={
                            "model": "Pan-tropical allometric equation",
                            "model_version": carbon_result["metadata"]["version"],
                            "agb_tonnes_ha": data_point["agb_tonnes_ha"],
                            "co2_tonnes_ha": data_point["co2_tonnes_ha"],
                            "ndvi_input": data_point["ndvi"],
                            "coefficient_a": carbon_result["metadata"]["coefficient_a"],
                            "coefficient_b": carbon_result["metadata"]["coefficient_b"],
                        },
                    )
                    db.add(carbon_measurement)

                await db.commit()
            except CarbonCalculationError as e:
                logger.warning(f"Carbon calculation failed for farm {farm.id}: {str(e)}")
                # Don't fail the NDVI response, just log the carbon error

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


@router.post("/environmental/calculate", response_model=EnvironmentalResponse, status_code=202)
async def calculate_environmental_data(
    request: EnvironmentalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Calculate environmental metrics (temperature, humidity, LST).

    Triggers calculation using Earth Engine satellite data and stores results.

    Query Parameters:
        measurement_type: Type of environmental data ('temperature', 'humidity', 'lst')

    Returns:
        Environmental data points with statistics

    Raises:
        404: Farm not found or unauthorized
        400: Invalid measurement type or date range
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
        # Get NDVI service
        ndvi_service = NDVIService()

        # Get GeoJSON geometry from farm
        farm_geojson = farm.to_geojson()

        # Route to appropriate calculation method
        if request.measurement_type == "temperature":
            env_data = await ndvi_service.calculate_temperature_time_series(
                farm_geojson=farm_geojson,
                start_date=request.start_date,
                end_date=request.end_date,
            )
            measurement_key = "temperature_celsius"
            meta = {
                "source": "ERA5-Land",
                "dataset": "ECMWF/ERA5_LAND/HOURLY",
                "band": "temperature_2m",
                "unit": "celsius",
                "resolution_km": 9,
                "temporal_resolution": "hourly_aggregated_daily",
                "accuracy_celsius": 0.5,
                "data_quality": "high",
                "processing_date": datetime.utcnow().isoformat(),
            }

        elif request.measurement_type == "humidity":
            env_data = await ndvi_service.calculate_humidity_time_series(
                farm_geojson=farm_geojson,
                start_date=request.start_date,
                end_date=request.end_date,
            )
            measurement_key = "humidity_percent"
            meta = {
                "source": "ERA5-Land",
                "dataset": "ECMWF/ERA5_LAND/HOURLY",
                "bands": ["temperature_2m", "dewpoint_temperature_2m"],
                "unit": "percent",
                "calculation_method": "Magnus formula",
                "resolution_km": 9,
                "accuracy_percent": 5,
                "data_quality": "high",
                "processing_date": datetime.utcnow().isoformat(),
            }

        elif request.measurement_type == "lst":
            env_data = await ndvi_service.calculate_land_surface_temperature(
                farm_geojson=farm_geojson,
                start_date=request.start_date,
                end_date=request.end_date,
            )
            measurement_key = "lst_day_celsius"
            meta = {
                "source": "MODIS Terra",
                "dataset": "MODIS/061/MOD11A1",
                "bands": ["LST_Day_1km", "LST_Night_1km"],
                "unit": "celsius",
                "resolution_m": 1000,
                "quality_filtered": True,
                "emissivity_corrected": True,
                "accuracy_celsius": 1.0,
                "processing_date": datetime.utcnow().isoformat(),
            }

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid measurement type: {request.measurement_type}",
            )

        if not env_data:
            raise HTTPException(
                status_code=400,
                detail=f"No {request.measurement_type} data available for this date range",
            )

        # Store results in database
        for data_point in env_data:
            measurement_date = datetime.strptime(data_point["date"], "%Y-%m-%d").date()

            # Check if measurement already exists
            existing = await db.execute(
                select(Measurement).where(
                    and_(
                        Measurement.farm_id == farm.id,
                        Measurement.measurement_type == request.measurement_type,
                        Measurement.measurement_date == measurement_date,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Extract value based on measurement type
            if request.measurement_type == "temperature":
                value = data_point["temperature_celsius"]
            elif request.measurement_type == "humidity":
                value = data_point["humidity_percent"]
            else:  # lst
                value = (data_point["lst_day_celsius"] + data_point["lst_night_celsius"]) / 2

            measurement = Measurement(
                farm_id=farm.id,
                measurement_type=request.measurement_type,
                measurement_date=measurement_date,
                value=value,
                std_dev=data_point.get("std"),
                meta=meta,
            )
            db.add(measurement)

        await db.commit()

        # Calculate statistics
        values = []
        for dp in env_data:
            if request.measurement_type == "temperature":
                values.append(dp["temperature_celsius"])
            elif request.measurement_type == "humidity":
                values.append(dp["humidity_percent"])
            else:  # lst
                values.append((dp["lst_day_celsius"] + dp["lst_night_celsius"]) / 2)

        mean_value = sum(values) / len(values) if values else None
        min_value = min(values) if values else None
        max_value = max(values) if values else None

        # Format response data points
        response_data_points = []
        for dp in env_data:
            if request.measurement_type == "temperature":
                response_data_points.append(
                    EnvironmentalDataPoint(
                        date=dp["date"],
                        value=dp["temperature_celsius"],
                        std=dp.get("std", 0),
                        min_value=dp.get("min_temp"),
                        max_value=dp.get("max_temp"),
                    )
                )
            elif request.measurement_type == "humidity":
                response_data_points.append(
                    EnvironmentalDataPoint(
                        date=dp["date"],
                        value=dp["humidity_percent"],
                        std=dp.get("std", 0),
                    )
                )
            else:  # lst
                response_data_points.append(
                    EnvironmentalDataPoint(
                        date=dp["date"],
                        value=(dp["lst_day_celsius"] + dp["lst_night_celsius"]) / 2,
                        std=dp.get("std", 0),
                        min_value=dp.get("lst_night_celsius"),
                        max_value=dp.get("lst_day_celsius"),
                    )
                )

        return EnvironmentalResponse(
            farm_id=farm.id,
            farm_name=farm.name,
            measurement_type=request.measurement_type,
            start_date=request.start_date,
            end_date=request.end_date,
            data_points=response_data_points,
            total_points=len(response_data_points),
            mean_value=mean_value,
            min_value=min_value,
            max_value=max_value,
            metadata=meta,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        if "quota" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Earth Engine quota exceeded, try again later",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Environmental data calculation failed: {str(e)}",
        )


@router.get("/environmental/{farm_id}", response_model=EnvironmentalResponse)
async def get_environmental_data(
    farm_id: int,
    measurement_type: Literal["temperature", "humidity", "lst"] = Query(..., description="Type of environmental measurement"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Retrieve stored environmental measurements for a farm.

    Returns previously calculated measurements from the database.
    Does not trigger new calculation.

    Query Parameters:
        measurement_type: Required - Type of data ('temperature', 'humidity', 'lst')
        start_date: Optional - Filter by date range (YYYY-MM-DD)
        end_date: Optional - Filter by date range (YYYY-MM-DD)
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

    # Build query
    query = select(Measurement).where(
        and_(
            Measurement.farm_id == farm.id,
            Measurement.measurement_type == measurement_type,
        )
    )

    # Add date filtering if provided
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.where(Measurement.measurement_date >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.where(Measurement.measurement_date <= end)

    query = query.order_by(Measurement.measurement_date)

    # Execute query
    measurements_result = await db.execute(query)
    measurements = measurements_result.scalars().all()

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail=f"No {measurement_type} measurements found for this farm",
        )

    # Convert to response format
    response_data_points = [
        EnvironmentalDataPoint(
            date=m.measurement_date.isoformat(),
            value=m.value,
            std=m.std_dev or 0.0,
        )
        for m in measurements
    ]

    # Calculate statistics
    values = [m.value for m in measurements]
    mean_value = sum(values) / len(values) if values else None

    return EnvironmentalResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        measurement_type=measurement_type,
        start_date=measurements[0].measurement_date.isoformat() if measurements else start_date,
        end_date=measurements[-1].measurement_date.isoformat() if measurements else end_date,
        data_points=response_data_points,
        total_points=len(response_data_points),
        mean_value=mean_value,
        min_value=min(values) if values else None,
        max_value=max(values) if values else None,
        metadata=measurements[0].meta or {},
    )


@router.get("/environmental/{farm_id}/latest", response_model=EnvironmentalResponse)
async def get_latest_environmental_data(
    farm_id: int,
    measurement_type: Optional[Literal["temperature", "humidity", "lst"]] = Query(None, description="Type of environmental measurement (optional)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Get the latest environmental measurements for a farm.

    Returns the most recent measurement for each requested type.
    Useful for dashboard KPI display.

    Query Parameters:
        measurement_type: Optional - Get latest for specific type, or all types if omitted
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

    # Build query for latest measurements
    if measurement_type:
        query = select(Measurement).where(
            and_(
                Measurement.farm_id == farm.id,
                Measurement.measurement_type == measurement_type,
            )
        )
    else:
        # Get all environmental types
        query = select(Measurement).where(
            and_(
                Measurement.farm_id == farm.id,
                Measurement.measurement_type.in_(["temperature", "humidity", "lst"]),
            )
        )

    query = query.order_by(desc(Measurement.measurement_date))

    measurements_result = await db.execute(query)
    all_measurements = measurements_result.scalars().all()

    if not all_measurements:
        raise HTTPException(
            status_code=404,
            detail=f"No environmental measurements found for this farm",
        )

    # Get the latest measurement for each type
    latest_by_type = {}
    for m in all_measurements:
        if m.measurement_type not in latest_by_type:
            latest_by_type[m.measurement_type] = m

    # Filter to requested type if specified
    if measurement_type:
        measurements = [latest_by_type.get(measurement_type)]
        if not measurements[0]:
            raise HTTPException(
                status_code=404,
                detail=f"No {measurement_type} measurements found for this farm",
            )
    else:
        measurements = list(latest_by_type.values())

    # Convert to response format
    response_data_points = [
        EnvironmentalDataPoint(
            date=m.measurement_date.isoformat(),
            value=m.value,
            std=m.std_dev or 0.0,
        )
        for m in measurements
    ]

    # Calculate statistics
    values = [m.value for m in measurements]
    mean_value = sum(values) / len(values) if values else None

    # Determine the measurement type for response
    response_type = measurement_type or "mixed"
    if not measurement_type and len(latest_by_type) == 1:
        response_type = list(latest_by_type.keys())[0]

    return EnvironmentalResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        measurement_type=response_type,
        start_date=min(m.measurement_date for m in measurements).isoformat(),
        end_date=max(m.measurement_date for m in measurements).isoformat(),
        data_points=response_data_points,
        total_points=len(response_data_points),
        mean_value=mean_value,
        min_value=min(values) if values else None,
        max_value=max(values) if values else None,
        metadata=measurements[0].meta or {},
    )
