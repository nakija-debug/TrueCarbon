"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import auth, users, farms, ndvi, carbon, lulc, reports

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(farms.router)
api_router.include_router(ndvi.router)
api_router.include_router(carbon.router)
api_router.include_router(lulc.router)
api_router.include_router(reports.router, tags=["Reports"])


@api_router.get("/status")
async def api_status():
    """API v1 status endpoint."""
    return {
        "status": "API v1 ready",
        "endpoints": "Authentication, user management, farms, NDVI, carbon, and LULC implemented",
        "available_modules": [
            "/auth - Authentication (login, register, refresh, me)",
            "/users - User management (list, get, update, delete)",
            "/farms - Farm management and GeoJSON queries",
            "/ndvi - NDVI index calculations and time-series retrieval",
            "/carbon - Carbon estimation and tracking",
            "/lulc - Land use land cover classification",
        ],
        "planned_modules": [
            "/reports - PDF and CSV report generation",
        ],
    }


# Placeholder for future routers to be added in subsequent phases:
# from app.api.v1 import lulc, carbon, reports
# api_router.include_router(lulc.router, prefix="/lulc", tags=["LULC"])
# api_router.include_router(carbon.router, prefix="/carbon", tags=["Carbon"])
# api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

