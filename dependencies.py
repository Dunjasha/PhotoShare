from fastapi import Depends, HTTPException, status
from src.entity.models import Role, User
from src.routes.auth import get_current_user  

def require_role(*allowed_roles: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостатньо прав для цієї дії."
            )
        return current_user
    return role_checker
