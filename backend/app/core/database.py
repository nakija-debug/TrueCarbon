from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize database extensions (PostGIS if using PostgreSQL)."""
    # Only initialize PostGIS for PostgreSQL databases
    if "postgresql" not in settings.DATABASE_URL:
        return

    async with engine.begin() as conn:
        # Enable PostGIS extension
        await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis;")
        # Enable PostGIS topology extension
        await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
