"""LULC (Land Use/Land Cover) classification endpoints."""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.models.measurement import Measurement
from app.schemas.lulc import LULCRequest, LULCResponse, LULCClass, LULCStatistics, AnalysisPeriod
from app.services.lulc_service import LULCService
from app.services.exceptions import (
    InvalidGeometryError,
    InvalidDateRangeError,
    EarthEngineQuotaError,
    EarthEngineError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lulc", tags=["lulc"])


@router.post("/calculate", response_model=LULCResponse, status_code=202)
async def calculate_lulc(
    request: LULCRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Calculate LULC classification for a farm.

    Triggers classification using Google's Dynamic World dataset.
    Results are stored in the measurements table with measurement_type='lulc'.

    Returns:
        LULC classification with class breakdown and statistics

    Raises:
        404: Farm not found or unauthorized
        400: Invalid geometry or date range
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
        # Get LULC service
        lulc_service = LULCService()

        # Get GeoJSON geometry from farm
        farm_geojson = farm.to_geojson()

        # Classify land use
        lulc_result = await lulc_service.classify_land_use(
            farm_geojson=farm_geojson,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        if not lulc_result or not lulc_result.get("classes"):
            raise HTTPException(
                status_code=400,
                detail="No LULC data available for this date range",
            )

        # Parse dates
        measurement_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Get dominant class percentage
        dominant_class = lulc_result.get("dominant_class")
        dominant_percentage = 0.0
        if dominant_class:
            for cls in lulc_result.get("classes", []):
                if cls.get("name") == dominant_class:
                    dominant_percentage = cls.get("percentage", 0.0)
                    break

        # Check if measurement already exists (avoid duplicates)
        existing = await db.execute(
            select(Measurement).where(
                and_(
                    Measurement.farm_id == farm.id,
                    Measurement.measurement_type == "lulc",
                    Measurement.measurement_date == measurement_date,
                )
            )
        )
        if not existing.scalar_one_or_none():
            # Store result in database
            measurement = Measurement(
                farm_id=farm.id,
                measurement_type="lulc",
                measurement_date=measurement_date,
                value=dominant_percentage,
                std_dev=None,
                meta={
                    "total_area_ha": lulc_result.get("total_area_ha", 0.0),
                    "classes": lulc_result.get("classes", []),
                    "dominant_class": dominant_class,
                    "analysis_period": lulc_result.get("analysis_period", {}),
                    "source": "Dynamic World V1",
                    "class_count": len(lulc_result.get("classes", [])),
                },
            )
            db.add(measurement)
            await db.commit()

        # Reconstruct response
        classes_data = lulc_result.get("classes", [])
        total_area_ha = lulc_result.get("total_area_ha", 0.0)
        analysis_period = lulc_result.get("analysis_period", {"start": request.start_date, "end": request.end_date})
        class_count = len(classes_data)

        # Convert class data to LULCClass objects
        lulc_classes = [
            LULCClass(
                id=cls.get("id", 0),
                name=cls.get("name", "Unknown"),
                area_ha=cls.get("area_ha", 0.0),
                percentage=cls.get("percentage", 0.0),
            )
            for cls in classes_data
        ]

        # Build statistics
        statistics = LULCStatistics(
            total_area_ha=total_area_ha,
            dominant_class=dominant_class,
            class_count=class_count,
            analysis_period=AnalysisPeriod(
                start=analysis_period.get("start", request.start_date),
                end=analysis_period.get("end", request.end_date),
            ),
        )

        # Build response
        return LULCResponse(
            farm_id=farm.id,
            farm_name=farm.name,
            classes=lulc_classes,
            statistics=statistics,
            measurement_date=measurement_date.isoformat(),
            total_classes=class_count,
        )

    except InvalidGeometryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid farm geometry: {str(e)}",
        )
    except InvalidDateRangeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date range: {str(e)}",
        )
    except EarthEngineQuotaError as e:
        raise HTTPException(
            status_code=429,
            detail="Earth Engine quota exceeded. Please try again later.",
        )
    except EarthEngineError as e:
        logger.error(f"Earth Engine error during LULC classification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LULC classification failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during LULC calculation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LULC calculation failed: {str(e)}",
        )


@router.get("/{farm_id}", response_model=LULCResponse)
async def get_lulc_classification(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Retrieve stored LULC classification for a farm.

    Returns the most recent LULC classification results from the database.
    Does not trigger new classification.

    Returns:
        LULC classification with detailed class breakdown and statistics

    Raises:
        404: Farm not found, no access, or no LULC data available
        403: User lacks access to farm
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

    # Retrieve LULC measurements (get most recent)
    measurements_result = await db.execute(
        select(Measurement)
        .where(
            and_(
                Measurement.farm_id == farm.id,
                Measurement.measurement_type == "lulc",
            )
        )
        .order_by(Measurement.measurement_date.desc())
    )
    measurements = measurements_result.scalars().all()

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No LULC data found for this farm",
        )

    # Use the most recent measurement
    measurement = measurements[0]

    # Reconstruct response from stored meta field
    meta = measurement.meta or {}
    classes_data = meta.get("classes", [])
    total_area_ha = meta.get("total_area_ha", 0.0)
    dominant_class = meta.get("dominant_class")
    analysis_period = meta.get("analysis_period", {"start": "", "end": ""})
    class_count = meta.get("class_count", len(classes_data))

    # Convert class data to LULCClass objects
    lulc_classes = [
        LULCClass(
            id=cls.get("id", 0),
            name=cls.get("name", "Unknown"),
            area_ha=cls.get("area_ha", 0.0),
            percentage=cls.get("percentage", 0.0),
        )
        for cls in classes_data
    ]

    # Build statistics
    statistics = LULCStatistics(
        total_area_ha=total_area_ha,
        dominant_class=dominant_class,
        class_count=class_count,
        analysis_period=AnalysisPeriod(
            start=analysis_period.get("start", ""),
            end=analysis_period.get("end", ""),
        ),
    )

    # Build response
    return LULCResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        classes=lulc_classes,
        statistics=statistics,
        measurement_date=measurement.measurement_date.isoformat(),
        total_classes=len(lulc_classes),
    )
