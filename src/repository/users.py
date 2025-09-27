from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


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


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    Get public information about a user by username.

    Args:
        username (str): User's username.
        db (AsyncSession): DB session.

    Returns:
        UserResponse: Public user data.
    """
    stmt = select(User).where(User.email == username)
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
