from fastapi import APIRouter, Depends

from src.services.auth import auth_service
from src.schemas.user import UserResponse
from src.entity.models import User

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
