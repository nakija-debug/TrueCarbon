"""Report model for storing generated reports."""

from typing import TYPE_CHECKING
from enum import Enum
import sqlalchemy
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm


class ReportType(str, Enum):
    """Supported report file formats."""
    PDF = "pdf"
    CSV = "csv"
    GEOJSON = "geojson"


class ReportStatus(str, Enum):
    """Status of report generation."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class Report(BaseModel):
    """
    Report model for storing generated reports.

    Stores metadata about generated reports including file paths,
    URLs, date ranges, and generation status. Supports multiple
    report formats (PDF, CSV, GeoJSON).
    """

    __tablename__ = "reports"

    farm_id: Mapped[int] = mapped_column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("farms.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    """Farm that the report covers"""

    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    """Report format: 'pdf', 'csv', or 'geojson'"""

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    """Local file system path where report is stored"""

    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    """URL for downloading the report"""

    start_date: Mapped[sqlalchemy.date] = mapped_column(Date, nullable=False)
    """Start date of data included in report"""

    end_date: Mapped[sqlalchemy.date] = mapped_column(Date, nullable=False)
    """End date of data included in report"""

    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    """JSON metadata for report parameters and generation details"""

    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    """Size of generated file in bytes"""

    status: Mapped[str] = mapped_column(
        String(50),
        default=ReportStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    """Report generation status: pending, completed, failed, or deleted"""

    # Relationships
    farm: Mapped["Farm"] = relationship(
        "Farm",
        back_populates="reports",
    )
    """Farm that this report covers"""
