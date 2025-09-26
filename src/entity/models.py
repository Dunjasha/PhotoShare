from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean, Table, Integer, Column
from sqlalchemy.orm import DeclarativeBase
from typing import Optional


class Base(DeclarativeBase):
    pass

photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

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
    description: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    url: Mapped[str] = mapped_column(String(255))

    public_id: Mapped[str] = mapped_column(String(255), unique=True)
    transformed_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    qr_code_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=photo_tags, back_populates="photos", lazy="selectin"
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    photos: Mapped[list["Post"]] = relationship("Post", secondary=photo_tags, back_populates="tags", lazy="selectin")

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
