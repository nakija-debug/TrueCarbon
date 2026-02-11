"""Pydantic schemas for farm operations."""

from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime


class FarmBase(BaseModel):
    """Base farm schema."""

    name: str
    description: Optional[str] = None
    area_ha: Optional[float] = None


class FarmCreate(FarmBase):
    """Schema for farm creation."""

    geometry: dict
    """GeoJSON geometry object - must be type='Polygon'"""

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, v: dict) -> dict:
        """Validate GeoJSON geometry."""
        if not isinstance(v, dict):
            raise ValueError("Geometry must be a dict")

        if v.get("type") != "Polygon":
            raise ValueError(f"Geometry type must be 'Polygon', got '{v.get('type')}'")

        coords = v.get("coordinates")
        if not coords or not coords[0]:
            raise ValueError("Polygon coordinates cannot be empty")

        return v


class FarmUpdate(BaseModel):
    """Schema for partial farm updates."""

    name: Optional[str] = None
    description: Optional[str] = None
    geometry: Optional[dict] = None
    is_active: Optional[bool] = None


class FarmResponse(FarmBase):
    """Farm response schema (excludes geometry by default)."""

    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmGeoJSON(BaseModel):
    """GeoJSON Feature format for Mapbox GL JS compatibility."""

    type: str = "Feature"
    id: int
    geometry: dict
    properties: dict

    model_config = {"from_attributes": False}
