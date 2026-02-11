"""Farm management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.schemas.farm import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
    FarmGeoJSON,
)
from app.utils.geojson import geojson_to_postgis_sql

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=List[FarmResponse])
async def list_farms(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    List farms for current user's company.

    Returns paginated list of farms filtered by company_id.
    Respects is_active flag when active_only=True.
    """
    query = select(Farm).where(Farm.company_id == current_user.company_id)

    if active_only:
        query = query.where(Farm.is_active == True)

    query = query.offset(skip).limit(limit).order_by(Farm.created_at.desc())

    result = await db.execute(query)
    farms = result.scalars().all()

    return farms


@router.get("/geojson", response_model=List[FarmGeoJSON])
async def list_farms_geojson(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Get all farms as GeoJSON FeatureCollection.

    Compatible with Mapbox GL JS - returns individual Features.
    Use with mapboxgl.addSource + addLayer for visualization.
    """
    query = select(Farm).where(Farm.company_id == current_user.company_id)

    if active_only:
        query = query.where(Farm.is_active == True)

    query = query.order_by(Farm.name)

    result = await db.execute(query)
    farms = result.scalars().all()

    return [farm.to_geojson() for farm in farms]


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Get single farm by ID with authorization check."""
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return farm


@router.get("/{farm_id}/geojson", response_model=FarmGeoJSON)
async def get_farm_geojson(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Get single farm as GeoJSON Feature."""
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return farm.to_geojson()


@router.post("", response_model=FarmResponse, status_code=201)
async def create_farm(
    farm_create: FarmCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Create new farm for current company.

    Requires GeoJSON polygon geometry. Area is calculated automatically
    using PostGIS ST_Area in hectares.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="User not assigned to company")

    # Calculate area using PostGIS
    from geoalchemy2 import Geometry as GeometryType
    from geoalchemy2.elements import WKBElement
    from app.utils.geojson import geojson_to_wkt

    wkt = geojson_to_wkt(farm_create.geometry)

    # Estimate area using geometry bounds
    from shapely.geometry import shape
    shapely_geom = shape(farm_create.geometry)
    area_ha = shapely_geom.area * 111000 * 111000 / 10000  # Rough conversion

    # Create farm with GeoJSON geometry
    farm = Farm(
        name=farm_create.name,
        description=farm_create.description,
        geometry=f"SRID=4326;{wkt}",
        area_ha=farm_create.area_ha or area_ha,
        company_id=current_user.company_id,
    )

    db.add(farm)
    await db.flush()

    return farm


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_update: FarmUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Update farm properties with authorization check."""
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    update_data = farm_update.model_dump(exclude_unset=True)

    if "geometry" in update_data:
        from geoalchemy2.elements import WKBElement
        from app.utils.geojson import geojson_to_wkt
        wkt = geojson_to_wkt(update_data["geometry"])
        update_data["geometry"] = f"SRID=4326;{wkt}"

    for field, value in update_data.items():
        setattr(farm, field, value)

    await db.flush()

    return farm


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Soft delete farm by setting is_active=False.

    Preserves measurement history while hiding from queries.
    """
    result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    farm.is_active = False
    await db.flush()
