"""User management endpoints for CRUD operations."""

from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    get_current_user_db,
    get_current_active_superuser,
    get_password_hash,
)
from app.models.user import User
from app.models.company import Company
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    company_id: int | None = None,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """
    List all users with optional filtering by company_id.

    Only superusers can access this endpoint.

    Args:
        skip: Number of records to skip for pagination
        limit: Number of records to return (max 100)
        company_id: Optional company_id filter
        current_user: Current authenticated superuser
        db: Database session

    Returns:
        List of UserResponse objects
    """
    query = select(User).offset(skip).limit(limit)

    if company_id is not None:
        query = query.where(User.company_id == company_id)

    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get a specific user by ID.

    Users can view their own profile, superusers can view any user.

    Args:
        user_id: User ID to retrieve
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: 403 if unauthorized, 404 if user not found
    """
    # Authorization check: superuser or self
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_db),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update a specific user's information.

    Users can update their own profile, superusers can update any user.

    Args:
        user_id: User ID to update
        user_update: Partial user data to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated UserResponse

    Raises:
        HTTPException: 403 if unauthorized, 404 if user not found, 400 if invalid data
    """
    # Authorization check: superuser or self
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)

    # Validate email uniqueness if email is being updated
    if "email" in update_data and update_data["email"]:
        # Check if email is taken by another user
        email_check = await db.execute(
            select(User).where(
                (User.email == update_data["email"]) & (User.id != user_id)
            )
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user",
            )

    # Validate company_id FK if company_id is being updated
    if "company_id" in update_data and update_data["company_id"]:
        company_check = await db.execute(
            select(Company).where(Company.id == update_data["company_id"])
        )
        if not company_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {update_data['company_id']} not found",
            )

    for field, value in update_data.items():
        if field == "password" and value:
            # Hash password if provided
            setattr(user, "hashed_password", get_password_hash(value))
        elif value is not None:
            setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Soft delete a user by setting is_active to False.

    Only superusers can delete users.

    Args:
        user_id: User ID to delete
        current_user: Current authenticated superuser
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Soft delete
    user.is_active = False
    db.add(user)
    await db.commit()

    return {"message": f"User {user_id} has been deactivated"}
