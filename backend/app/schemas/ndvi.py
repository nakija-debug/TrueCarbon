"""Pydantic schemas for NDVI operations."""

from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime


class NDVIDataPoint(BaseModel):
    """Single NDVI measurement."""

    date: str  # YYYY-MM-DD
    ndvi: float
    std: float


class NDVIRequest(BaseModel):
    """Request schema for NDVI calculation."""

    farm_id: int
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Date must be YYYY-MM-DD format: {e}")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """Validate end_date is after start_date."""
        if "start_date" in info.data:
            start = datetime.strptime(info.data["start_date"], "%Y-%m-%d")
            end = datetime.strptime(v, "%Y-%m-%d")

            if start >= end:
                raise ValueError("start_date must be before end_date")

            # Check max 5 years
            days_diff = (end - start).days
            if days_diff > 365 * 5:
                raise ValueError(f"Date range too large: {days_diff} days (max 5 years)")

        return v


class NDVIResponse(BaseModel):
    """Response schema for NDVI calculation."""

    farm_id: int
    farm_name: str
    start_date: str
    end_date: str
    data_points: List[NDVIDataPoint]
    total_points: int
    mean_ndvi: Optional[float] = None
    min_ndvi: Optional[float] = None
    max_ndvi: Optional[float] = None
