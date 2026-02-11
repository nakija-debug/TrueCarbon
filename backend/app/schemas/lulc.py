"""Pydantic schemas for LULC (Land Use/Land Cover) operations."""

from typing import List, Optional, Dict
from pydantic import BaseModel, field_validator
from datetime import datetime


class LULCRequest(BaseModel):
    """Request schema for LULC classification."""

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


class LULCClass(BaseModel):
    """Represents a single land cover class detected in LULC analysis."""

    id: int
    """Dynamic World class ID (0-8)"""

    name: str
    """Class name from LULC_CLASS_NAMES"""

    area_ha: float
    """Area of this class in hectares"""

    percentage: float
    """Percentage of total farm area"""


class AnalysisPeriod(BaseModel):
    """Analysis period for LULC classification."""

    start: str
    """Start date in YYYY-MM-DD format"""

    end: str
    """End date in YYYY-MM-DD format"""


class LULCStatistics(BaseModel):
    """Statistics summary for LULC classification."""

    total_area_ha: float
    """Total farm area in hectares"""

    dominant_class: Optional[str] = None
    """Most common land cover type"""

    class_count: int
    """Number of distinct classes found"""

    analysis_period: AnalysisPeriod
    """Start and end dates of analysis"""


class LULCResponse(BaseModel):
    """Response schema for LULC classification data."""

    farm_id: int
    """Farm ID"""

    farm_name: str
    """Farm name"""

    classes: List[LULCClass]
    """All detected land cover classes"""

    statistics: LULCStatistics
    """Statistics and summary"""

    measurement_date: str
    """Date of classification in YYYY-MM-DD format"""

    total_classes: int
    """Number of distinct classes detected"""
