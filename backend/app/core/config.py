from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable configuration."""

    # Project info
    PROJECT_NAME: str = "True Carbon API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    """
    Database URL for SQLAlchemy.
    Examples:
    - PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/truecarbon
    - SQLite: sqlite+aiosqlite:///./truecarbon.db
    """

    # Security
    SECRET_KEY: str
    """Secret key for JWT signing. Generate with: openssl rand -hex 32"""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google Earth Engine
    GEE_PROJECT: str
    """Google Earth Engine project ID (e.g., 'student-research-carbon')"""
    GEE_SERVICE_ACCOUNT: Optional[str] = None
    """Optional: JSON string for GEE service account authentication"""
    GEE_MAX_RETRIES: int = 3
    """Maximum number of retries for GEE quota errors"""
    GEE_RETRY_DELAY: int = 1
    """Initial retry delay in seconds (exponential backoff applied)"""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"
    """development, staging, or production"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def database_url_async(self) -> str:
        """Convert database URL to async driver if needed."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


# Singleton instance
settings = Settings()
