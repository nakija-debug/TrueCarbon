"""Satellite status model for tracking health metrics."""

from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SatelliteStatus(BaseModel):
    """
    Satellite status model for tracking health and reliability metrics.

    Stores current health status of satellite data sources used for environmental
    and carbon monitoring (Sentinel-2, Landsat-8, ERA5-Land).
    """

    __tablename__ = "satellite_status"

    satellite_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    """Name of satellite (sentinel-2, landsat-8, era5-land)"""

    status: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
        default="unknown",
    )
    """Operational status: 'operational', 'degraded', 'offline', 'unknown'"""

    coverage_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    """Data availability percentage (0-100)"""

    accuracy_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    """Quality accuracy metric percentage (0-100)"""

    data_quality: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="unknown",
    )
    """Data quality level: 'high', 'medium', 'low', 'unknown'"""

    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    """Timestamp of last health check"""

    uptime_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    """Historical uptime percentage (0-100)"""

    health_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    """Additional metrics: cloud cover %, latency ms, last error message, etc."""

    def __repr__(self) -> str:
        return f"<SatelliteStatus({self.satellite_name}, {self.status})>"

    @property
    def is_operational(self) -> bool:
        """Check if satellite is operational."""
        return self.status == "operational"

    @property
    def is_degraded(self) -> bool:
        """Check if satellite is degraded."""
        return self.status == "degraded"

    @property
    def is_offline(self) -> bool:
        """Check if satellite is offline."""
        return self.status == "offline"
