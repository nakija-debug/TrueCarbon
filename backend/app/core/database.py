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

    try:
        async with engine.begin() as conn:
            # Enable PostGIS extension (requires SUPERUSER privileges)
            # On Render free tier, this might fail - that's okay
            await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis;")
            # Enable PostGIS topology extension
            await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            print("PostGIS extensions created successfully")
    except Exception as e:
        # Log the error but don't fail startup
        # PostGIS extensions might already exist or user might not have permissions
        print(f"Note: Could not create PostGIS extensions (this is okay if they already exist): {e}")
        pass
