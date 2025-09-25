from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.schemas.user import UserSchema, TokenSchema, UserResponse
from src.repository import users as repositories_users
from src.database.db import get_db
from src.services.auth import auth_service

from src.entity.models import Role, User
from dependencies import require_role

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.patch("/users/{user_id}/role")
def update_role(
    user_id: int,
    new_role: Role,
    db: Session = Depends(get_db),
    current_admin = Depends(require_role(Role.admin))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    user.role = new_role
    db.commit()
    return {"msg": f"Role user {user.email} change to {new_role}"}

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account without email confirmation.

    Args:
        body (UserSchema): User data for registration.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        UserResponse: The newly created user object.

    Raises:
        HTTPException: If an account with the given email already exists.
    """

    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)

    new_user = await repositories_users.create_user(body, db)

    return new_user


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login(body: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.

    Args:
        body (OAuth2PasswordRequestForm): User credentials (email and password).
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        TokenSchema: Dictionary with access token, refresh token, and token type.

    Raises:
        HTTPException: For invalid email, unconfirmed email, or wrong password.
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Generate new JWT tokens using a valid refresh token.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from the request header.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        TokenSchema: Dictionary with new access token, refresh token, and token type.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


