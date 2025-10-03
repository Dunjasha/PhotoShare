from fastapi import Depends, HTTPException, status
from src.entity.models import User
from src.services.auth import auth_service


def is_owner_or_admin(user_id: int, current_user: User = Depends(auth_service.get_current_user)):
    if current_user.role == "ADMIN":
        return current_user
    if current_user.id == user_id:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="not enough permissions"
    )
