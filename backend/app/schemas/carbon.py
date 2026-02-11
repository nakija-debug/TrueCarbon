"""Pydantic schemas for carbon estimation operations."""

from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime


class CarbonDataPoint(BaseModel):
    """Single carbon measurement from NDVI data point."""

    date: str  # YYYY-MM-DD
    ndvi: float
    agb_tonnes_ha: float  # Above-ground biomass per hectare
    agb_total_tonnes: float  # Total AGB for farm
    carbon_tonnes_ha: float  # Carbon per hectare
    carbon_total_tonnes: float  # Total carbon for farm
    co2_tonnes_ha: float  # CO2 equivalent per hectare
    co2_total_tonnes: float  # Total CO2 equivalent for farm
    confidence_score: Optional[float] = None  # Confidence score (0-100, higher = more confident)
    confidence_interval_lower: Optional[float] = None  # 95% CI lower bound (CO2 tonnes/ha)
    confidence_interval_upper: Optional[float] = None  # 95% CI upper bound (CO2 tonnes/ha)
    std_dev: Optional[float] = None  # Standard deviation from Monte Carlo simulation


class CarbonStatistics(BaseModel):
    """Statistics summary for carbon calculation."""

    mean_agb_tonnes_ha: float
    total_agb_tonnes: float
    mean_carbon_tonnes_ha: float
    total_carbon_tonnes: float
    total_co2_tonnes: float
    min_ndvi: float
    max_ndvi: float
    mean_ndvi: float
    mean_confidence_score: Optional[float] = None  # Average confidence score across all data points
    overall_std_dev: Optional[float] = None  # Average standard deviation across data points


class CarbonRequest(BaseModel):
    """Request schema for carbon estimation."""

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


class CarbonMetadata(BaseModel):
    """Metadata about carbon calculation model."""

    model_version: str
    model_name: str
    agb_coefficient_a: Optional[float] = None
    agb_exponent_b: Optional[float] = None
    carbon_fraction: float
    co2_conversion_factor: float
    assumptions: List[str]
    methodology: Optional[str] = None  # e.g., "Monte Carlo Simulation (10,000 iterations)"
    uncertainty_method: Optional[str] = None  # e.g., "95% Confidence Intervals"
    land_use_class: Optional[str] = None  # Dominant LULC class if Tier 2 used
    monte_carlo_iterations: Optional[int] = None  # Number of MC iterations


class CarbonResponse(BaseModel):
    """Response schema for carbon calculation."""

    farm_id: int
    farm_name: str
    start_date: str
    end_date: str
    area_ha: float
    data_points: List[CarbonDataPoint]
    statistics: CarbonStatistics
    metadata: CarbonMetadata
    total_points: int

    @property
    def summary(self) -> str:
        """Generate human-readable summary."""
        stats = self.statistics
        return (
            f"Farm: {self.farm_name} ({self.area_ha} ha)\n"
            f"Period: {self.start_date} to {self.end_date}\n"
            f"Mean Carbon: {stats.mean_carbon_tonnes_ha:.2f} t/ha\n"
            f"Total Carbon: {stats.total_carbon_tonnes:.2f} tonnes\n"
            f"CO2 Equivalent: {stats.total_co2_tonnes:.2f} tonnes"
        )
