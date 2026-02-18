"""FastAPI application factory and configuration."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, init_db, AsyncSessionLocal
from app.api.v1 import api_router
from app.services.satellite_health_service import SatelliteHealthService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the background task
_satellite_health_task: asyncio.Task | None = None


async def _satellite_health_check_task():
    """Background task that periodically checks satellite health."""
    interval_seconds = settings.SATELLITE_HEALTH_CHECK_INTERVAL_HOURS * 3600
    service = SatelliteHealthService()
    
    try:
        while True:
            try:
                logger.debug("Starting satellite health check task")
                db = AsyncSessionLocal()
                try:
                    await service.update_all_satellite_status(db)
                    logger.info("Satellite health check completed successfully")
                except Exception as e:
                    logger.error(f"Satellite health check failed: {e}")
                finally:
                    await db.close()
            except Exception as e:
                logger.error(f"Error in satellite health check task: {e}")
            
            # Wait for the configured interval
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Satellite health check task cancelled")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global _satellite_health_task
    
    # Startup
    try:
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'SQLite'}")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Start satellite health check background task
        if settings.SATELLITE_HEALTH_CHECK_ENABLED:
            logger.info(
                f"Starting satellite health check task "
                f"(interval: {settings.SATELLITE_HEALTH_CHECK_INTERVAL_HOURS} hours)"
            )
            _satellite_health_task = asyncio.create_task(_satellite_health_check_task())
        else:
            logger.info("Satellite health check is disabled")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # Shutdown
    try:
        logger.info("Shutting down...")
        
        # Cancel satellite health check task
        if _satellite_health_task and not _satellite_health_task.done():
            logger.info("Cancelling satellite health check task")
            _satellite_health_task.cancel()
            try:
                await _satellite_health_task
            except asyncio.CancelledError:
                logger.info("Satellite health check task cancelled successfully")
        
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint returning service status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity verification."""
    try:
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "service": settings.PROJECT_NAME,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )
