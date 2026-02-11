"""Authentication Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema for login endpoint."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Schema for token refresh endpoint."""

    refresh_token: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT token claims."""

    sub: str  # user_id
    exp: int  # expiration timestamp
    type: Optional[str] = None  # "access" or "refresh"
