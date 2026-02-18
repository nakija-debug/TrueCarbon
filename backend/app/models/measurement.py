"""Measurement model for storing time-series environmental data."""

from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import String, Date, Float, Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm


class Measurement(BaseModel):
    """
    Measurement model for storing time-series environmental metrics.

    Supports NDVI (Phase 1), LULC (Phase 2), and carbon estimates (Phase 3).
    Designed as an extensible store for any time-series measurement type.
    """

    __tablename__ = "measurements"

    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    """Farm this measurement is for"""

    measurement_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )
    """Type of measurement: 'ndvi', 'lulc', 'carbon', 'temperature', 'humidity', 'lst'"""

    measurement_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )
    """Date of the measurement"""

    value: Mapped[float] = mapped_column(Float, nullable=False)
    """Primary measurement value (e.g., mean NDVI, carbon tonnes)"""

    std_dev: Mapped[float | None] = mapped_column(Float, nullable=True)
    """Standard deviation for uncertainty quantification"""

    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    """Additional metadata (satellite source, cloud cover %, etc.) - renamed from 'metadata' to avoid SQLAlchemy reserved name"""

    # Relationships
    farm: Mapped["Farm"] = relationship(
        "Farm",
        back_populates="measurements",
    )
    """Farm this measurement belongs to"""

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "farm_id",
            "measurement_type",
            "measurement_date",
            name="uq_farm_measurement_date",
        ),
    )
