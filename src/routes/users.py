from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.schemas.user import UserResponse, UserPublicResponse, UserUpdateSchema
from src.services.roles import RoleAccess
from src.entity.models import User, Role

from src.repository import users as repositories_users
from src.database.db import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve the currently authenticated user's information.

    Args:
        user (User): Current authenticated user (auto-injected via dependency).

    Returns:
        UserResponse: Detailed information about the authenticated user.
    """
    return user


@router.get("/public/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    Get public information about a user by username.

    Args:
        username (str): User's username.
        db (AsyncSession): DB session.

    Returns:
        UserResponse: Public user data.
    """
    user = await repositories_users.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_public_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.get("/me", response_model=UserResponse)
async def get_private_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=UserUpdateSchema)
async def update_me(
    body: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Update the currently authenticated user's information.

    Args:
        body (UserUpdateSchema): The user data to update.
        db (AsyncSession): The database session (injected).
        user (User): Current authenticated user (auto-injected via dependency).

    Returns:
        UserUpdateSchema: The updated user data.
    """
    updated_user = await repositories_users.update_user(user.id, body, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.patch("/{user_id}/deactivate", response_model=UserResponse,
              dependencies=[Depends(RoleAccess([Role.ADMIN]))])
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deactivate a user (admin only).
    """
    user = await repositories_users.set_user_active_status(user_id, False, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}/activate", response_model=UserResponse,
              dependencies=[Depends(RoleAccess([Role.ADMIN]))])
async def activate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Reactivate a user (admin only).
    """
    user = await repositories_users.set_user_active_status(user_id, True, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
