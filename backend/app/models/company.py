"""Company model for multi-tenancy support."""

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Company(BaseModel):
    """Company model for organizing users and carbon credits."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    # Relationship to users
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    # Relationship to farms
    farms: Mapped[list["Farm"]] = relationship(
        "Farm",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name})>"
