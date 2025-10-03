from fastapi import HTTPException



from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema, UserUpdateSchema
from src.services.auth import auth_service

async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new user in the database.

    Args:
        body (UserSchema): The user data for creation.
        db (AsyncSession): The database session (injected).

    Returns:
        User: The newly created user.
    """

    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    Get public information about a user by username.

    Args:
        username (str): User's username.
        db (AsyncSession): DB session.

    Returns:
        UserResponse: Public user data.
    """
    stmt = select(User).where(User.username == username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user from the database by email.

    Args:
        email (str): The email of the user to search for.
        db (AsyncSession): The database session (injected).

    Returns:
        User | None: The user object if found, otherwise None.
    """
    stmt = select(User).where(User.email == email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Mark a user's email as confirmed.

    Args:
        email (str): The email of the user to confirm.
        db (AsyncSession): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update the user's refresh token.

    Args:
        user (User): The user to update.
        token (str | None): The new refresh token.
        db (AsyncSession): The database session.
    """
    user.refresh_token = token
    await db.commit()

async def update_user(user_id: int, body: UserUpdateSchema, db: AsyncSession):
    """
    Update user information.

    Args:
        user_id (int): The ID of the user to update.
        body (UserSchema): The new user data.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user object.
    """
    user = await db.get(User, user_id)
    if not user:
        return None

    update_data = body.model_dump(exclude_unset=True)

    # Перевірка унікальності username
    if "username" in update_data and update_data["username"]:
        existing_user = await get_user_by_username(update_data["username"], db)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Username already in use")

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
