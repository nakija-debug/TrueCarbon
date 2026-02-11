"""Authentication endpoints for login, register, refresh, and user profile."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_db,
)
from app.models.user import User
from app.models.company import Company
from app.schemas.auth import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        login_request: Email and password for authentication
        db: Database session

    Returns:
        Token with access_token, refresh_token, and token_type

    Raises:
        HTTPException: 401 if credentials are invalid or user is inactive
    """
    # Query for user by email
    result = await db.execute(select(User).where(User.email == login_request.email))
    user = result.scalar_one_or_none()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Create a new user account.

    Args:
        user_create: User data including email, password, full_name, optional company_id
        db: Database session

    Returns:
        Created UserResponse

    Raises:
        HTTPException: 400 if email already exists, 404 if company not found
    """
    # Validate password length
    if len(user_create.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_create.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # If company_id provided, verify company exists
    if user_create.company_id:
        result = await db.execute(
            select(Company).where(Company.id == user_create.company_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

    # Create new user
    hashed_password = get_password_hash(user_create.password)
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        company_id=user_create.company_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_request: Refresh token
        db: Database session

    Returns:
        Token with new access_token, refresh_token, and token_type

    Raises:
        HTTPException: 401 if refresh token is invalid, expired, or user not found/inactive
    """
    # Decode refresh token
    try:
        payload = decode_token(refresh_request.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type is refresh
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type, expected refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id and verify user exists and is active
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_db),
) -> User:
    """
    Get the current authenticated user's profile.

    Args:
        current_user: Current user from JWT token

    Returns:
        UserResponse with user details
    """
    return current_user
