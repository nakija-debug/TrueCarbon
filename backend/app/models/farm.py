"""Farm model for storing boundary geometries."""

from typing import TYPE_CHECKING
import sqlalchemy
from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.measurement import Measurement
    from app.models.report import Report


class Farm(BaseModel):
    """
    Farm model representing a piece of land for carbon measurement.

    Stores boundary geometry as GeoJSON and supports multi-tenancy
    through company_id. Measurements (NDVI, LULC, carbon) are stored separately.
    
    Note: In development (SQLite), geometry is stored as JSON.
    In production (PostgreSQL), use GeoAlchemy2 Geometry type.
    """

    __tablename__ = "farms"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    """Farm identifier - user-provided name"""

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    """Optional farm description or notes"""

    geometry: Mapped[dict] = mapped_column(JSON, nullable=False)
    """Farm boundary polygon as GeoJSON (Polygon geometry object)"""

    area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    """Calculated area in hectares"""

    company_id: Mapped[int] = mapped_column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    """Company that owns this farm - enables multi-tenancy"""

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    """Soft delete flag - inactive farms are hidden from queries"""

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="farms",
    )
    """Company that owns this farm"""

    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement",
        back_populates="farm",
        cascade="all, delete-orphan",
    )
    """Time-series measurements (NDVI, LULC, etc.)"""

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="farm",
        cascade="all, delete-orphan",
    )
    """Generated reports"""

    def to_geojson(self) -> dict:
        """
        Convert farm to GeoJSON Feature format compatible with Mapbox GL JS.

        Returns:
            GeoJSON Feature dict with geometry and properties
        """
        return {
            "type": "Feature",
            "id": self.id,
            "geometry": self.geometry,  # Already in GeoJSON format
            "properties": {
                "name": self.name,
                "description": self.description,
                "area_ha": self.area_ha,
                "company_id": self.company_id,
                "is_active": self.is_active,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            },
        }
