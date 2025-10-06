from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    """
    Dependency class to restrict access to routes based on user roles.

    Attributes:
        allowed_roles (list[Role]): List of roles allowed to access the route.
    """
    def __init__(self, allowed_roles: list[Role]):
        """
        Initialize the RoleAccess dependency with allowed roles.

        Args:
            allowed_roles (list[Role]): The roles permitted to access the route.
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Check if the current user's role is in the list of allowed roles.

        Args:
            request (Request): The current HTTP request.
            user (User): The currently authenticated user (injected via dependency).

        Raises:
            HTTPException: If the user's role is not in the allowed_roles list (403 FORBIDDEN).
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )