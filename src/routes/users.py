from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.schemas.user import UserResponse
from src.entity.models import User
<<<<<<< HEAD
=======
from src.repository import users as repositories_users
>>>>>>> c7dbed2cd58bf3fa66b3b0fe1c84c137fe57837c
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
