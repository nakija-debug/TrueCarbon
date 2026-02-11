"""User Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str  # Will be validated: min 8 chars in endpoint
    company_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for partial user updates."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database (includes all fields)."""

    id: int
    is_active: bool
    is_superuser: bool
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    """Public-facing user schema (excludes sensitive fields)."""

    id: int
    is_active: bool
    is_superuser: bool
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
