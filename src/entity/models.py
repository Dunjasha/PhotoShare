from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import DeclarativeBase
from typing import Optional


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_content: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    url: Mapped[str] = mapped_column(String(255))
    public_id: Mapped[str] = mapped_column(String(255), unique=True)
    transformed_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_content: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
