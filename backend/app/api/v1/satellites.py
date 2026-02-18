"""Satellite health monitoring endpoints."""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.schemas.satellite import (
    SatelliteHealthResponse,
    SatelliteHealthListResponse,
)
from app.services.satellite_health_service import SatelliteHealthService
from app.services.exceptions import SatelliteHealthCheckError, EarthEngineQuotaError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/satellites", tags=["Satellites"])


@router.get("/health", response_model=SatelliteHealthListResponse)
async def get_satellite_health(
    refresh: bool = Query(False, description="Trigger live health check"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Get satellite health and availability metrics.

    Returns current operational status, coverage percentages, and data quality
    for Sentinel-2, Landsat-8, and ERA5-Land satellites.

    Query Parameters:
        refresh: If True, trigger live health check from Earth Engine

    Returns:
        SatelliteHealthListResponse with list of satellite metrics and aggregates

    Raises:
        401: Unauthorized
        429: Earth Engine quota exceeded
        500: Health check failed
    """
    try:
        service = SatelliteHealthService()

        # Trigger live check if requested
        if refresh:
            logger.info("Refreshing satellite health status (user-triggered)")
            try:
                await service.update_all_satellite_status(db)
            except EarthEngineQuotaError:
                logger.warning("Earth Engine quota exceeded during health check")
                raise HTTPException(
                    status_code=429,
                    detail="Earth Engine quota exceeded, try again later",
                )
            except SatelliteHealthCheckError as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Health check failed: {str(e)}",
                )

        # Retrieve current health summary from database
        summary = await service.get_satellite_health_summary(db)

        # Convert satellite models to response schemas
        satellite_responses = [
            SatelliteHealthResponse(
                satellite_name=sat.satellite_name,
                status=sat.status,
                coverage_percent=sat.coverage_percent,
                accuracy_percent=sat.accuracy_percent,
                data_quality=sat.data_quality,
                last_update=sat.last_update,
                uptime_percent=sat.uptime_percent,
                metadata=sat.health_metadata,
            )
            for sat in summary["satellites"]
        ]

        return SatelliteHealthListResponse(
            satellites=satellite_responses,
            total_satellites=summary["total_satellites"],
            operational_count=summary["operational_count"],
            degraded_count=summary["degraded_count"],
            offline_count=summary["offline_count"],
            average_uptime=summary["average_uptime"],
            last_check=summary["last_check"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in satellite health endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve satellite health: {str(e)}",
        )


@router.get("/health/{satellite_name}", response_model=SatelliteHealthResponse)
async def get_satellite_health_by_name(
    satellite_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Get health metrics for a specific satellite.

    Returns current operational status, coverage, and data quality for named satellite.

    Path Parameters:
        satellite_name: Name of satellite (sentinel-2, landsat-8, or era5-land)

    Returns:
        SatelliteHealthResponse with metrics for requested satellite

    Raises:
        401: Unauthorized
        404: Satellite not found
        500: Database error
    """
    try:
        service = SatelliteHealthService()
        summary = await service.get_satellite_health_summary(db)

        # Find requested satellite
        satellite = next(
            (s for s in summary["satellites"] if s.satellite_name == satellite_name),
            None,
        )

        if not satellite:
            raise HTTPException(
                status_code=404,
                detail=f"Satellite '{satellite_name}' not found. Valid options: sentinel-2, landsat-8, era5-land",
            )

        return SatelliteHealthResponse(
            satellite_name=satellite.satellite_name,
            status=satellite.status,
            coverage_percent=satellite.coverage_percent,
            accuracy_percent=satellite.accuracy_percent,
            data_quality=satellite.data_quality,
            last_update=satellite.last_update,
            uptime_percent=satellite.uptime_percent,
            metadata=satellite.health_metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving satellite health for {satellite_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve satellite health: {str(e)}",
        )


@router.post("/health/refresh", status_code=202)
async def refresh_satellite_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Trigger manual refresh of all satellite health checks.

    Performs live health checks via Earth Engine API and updates database.
    Requires admin or elevated privileges.

    Returns:
        202 Accepted with task status

    Raises:
        401: Unauthorized
        403: Insufficient permissions
        429: Earth Engine quota exceeded
        500: Health check failed
    """
    try:
        # In production, should check user role/permissions
        # For now, allow authenticated users to trigger refresh
        logger.info(f"Satellite health refresh triggered by user {current_user.email}")

        service = SatelliteHealthService()

        try:
            await service.update_all_satellite_status(db)
            logger.info("Satellite health refresh completed successfully")

            return {
                "status": "accepted",
                "message": "Satellite health check in progress",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except EarthEngineQuotaError:
            logger.error("Earth Engine quota exceeded during manual refresh")
            raise HTTPException(
                status_code=429,
                detail="Earth Engine quota exceeded, try again later",
            )
        except SatelliteHealthCheckError as e:
            logger.error(f"Health check failed during refresh: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during health refresh: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh satellite health: {str(e)}",
        )
