"""Pydantic schemas for satellite health monitoring."""

from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SatelliteStatusEnum(str, Enum):
    """Operational status enum."""

    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class DataQualityEnum(str, Enum):
    """Data quality level enum."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SatelliteHealthResponse(BaseModel):
    """Response schema for individual satellite health status."""

    satellite_name: str = Field(..., description="Satellite name (sentinel-2, landsat-8, era5-land)")
    status: SatelliteStatusEnum = Field(..., description="Current operational status")
    coverage_percent: float = Field(..., description="Data availability percentage", ge=0, le=100)
    accuracy_percent: float = Field(..., description="Quality accuracy percentage", ge=0, le=100)
    data_quality: DataQualityEnum = Field(..., description="Quality level assessment")
    last_update: datetime = Field(..., description="Last health check timestamp")
    uptime_percent: float = Field(..., description="Historical uptime percentage", ge=0, le=100)
    metadata: Optional[dict] = Field(default=None, description="Additional metrics (cloud cover, latency, etc.)")

    @field_validator("coverage_percent", "accuracy_percent", "uptime_percent")
    @classmethod
    def validate_percentages(cls, v: float) -> float:
        """Validate percentage fields are in 0-100 range."""
        if not (0 <= v <= 100):
            raise ValueError(f"Percentage must be between 0 and 100, got {v}")
        return round(v, 2)


class SatelliteHealthListResponse(BaseModel):
    """Response schema for list of satellite health statuses."""

    satellites: List[SatelliteHealthResponse] = Field(..., description="List of satellite health metrics")
    total_satellites: int = Field(..., description="Total number of satellites tracked")
    operational_count: int = Field(..., description="Number of operational satellites")
    degraded_count: int = Field(..., description="Number of degraded satellites")
    offline_count: int = Field(..., description="Number of offline satellites")
    average_uptime: float = Field(..., description="Average uptime across all satellites", ge=0, le=100)
    last_check: datetime = Field(..., description="Latest health check timestamp")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "satellites": [
                    {
                        "satellite_name": "sentinel-2",
                        "status": "operational",
                        "coverage_percent": 95.5,
                        "accuracy_percent": 92.3,
                        "data_quality": "high",
                        "last_update": "2024-01-15T10:30:00Z",
                        "uptime_percent": 98.7,
                        "metadata": {"cloud_cover_percent": 15, "latency_ms": 45},
                    }
                ],
                "total_satellites": 3,
                "operational_count": 3,
                "degraded_count": 0,
                "offline_count": 0,
                "average_uptime": 97.5,
                "last_check": "2024-01-15T10:30:00Z",
            }
        }
