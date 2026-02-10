"""
Authentication helpers (skeleton).
This file documents where to add your user manager and auth routes using fastapi-users.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def auth_status():
    return {"status": "auth router placeholder"}

# In a full implementation, import and mount fastapi-users routers here,
# e.g. from fastapi_users import FastAPIUsers
