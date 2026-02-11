"""Pydantic schemas for report generation operations."""

from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime, date


class ReportRequest(BaseModel):
    """Request schema for report generation."""

    farm_id: int
    """Farm ID to generate report for"""

    start_date: str  # YYYY-MM-DD
    """Start date for report data range"""

    end_date: str  # YYYY-MM-DD
    """End date for report data range"""

    report_types: List[str]  # 'pdf', 'csv', 'geojson'
    """List of report formats to generate"""

    include_charts: bool = True
    """Include charts in PDF report"""

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

    @field_validator("report_types")
    @classmethod
    def validate_report_types(cls, v: List[str]) -> List[str]:
        """Validate report types are supported."""
        valid_types = {"pdf", "csv", "geojson"}
        for report_type in v:
            if report_type.lower() not in valid_types:
                raise ValueError(f"Unsupported report type: {report_type}. Valid: {valid_types}")
        return [t.lower() for t in v]


class ReportMetadata(BaseModel):
    """Metadata about a generated report."""

    methodology: Optional[str] = None
    """Carbon calculation methodology used"""

    confidence_summary: Optional[dict] = None
    """Summary of confidence metrics"""

    data_sources: Optional[List[str]] = None
    """Data sources used in report (Sentinel-2, Dynamic World, etc.)"""

    generation_timestamp: Optional[str] = None
    """ISO timestamp when report was generated"""

    parameters: Optional[dict] = None
    """Report generation parameters"""


class ReportResponse(BaseModel):
    """Response schema for individual report."""

    report_id: int
    """Unique report identifier"""

    farm_id: int
    """Farm ID"""

    farm_name: Optional[str] = None
    """Farm name"""

    report_type: str
    """Report format: 'pdf', 'csv', or 'geojson'"""

    file_url: str
    """URL for downloading the report"""

    download_url: str
    """Full download URL including base path"""

    status: str
    """Report generation status: pending, completed, failed"""

    file_size: Optional[int] = None
    """Size of generated file in bytes"""

    start_date: str
    """Start date of report data range"""

    end_date: str
    """End date of report data range"""

    metadata: Optional[ReportMetadata] = None
    """Report metadata"""

    created_at: str
    """ISO timestamp when report was created"""

    class Config:
        """Pydantic config."""
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response schema for list of reports."""

    reports: List[ReportResponse]
    """List of reports"""

    total: int
    """Total number of reports"""

    skip: int
    """Number of records skipped"""

    limit: int
    """Limit of records returned"""
