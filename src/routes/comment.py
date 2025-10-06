from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import comment as repository_comment
from src.entity.models import User, Post, Comment, Role

from src.schemas.comment import CommentaryCreateSchema, CommentaryUpdateSchema, CommentaryResponseSchema
from src.services.auth import auth_service
from src.services.auth_service import is_owner_or_admin
from src.services.roles import RoleAccess


router = APIRouter(tags=["comment"])

access_to_route_all = RoleAccess([Role.ADMIN, Role.MODERATOR])

@router.get("/post/{post_id}", response_model=list[CommentaryResponseSchema], status_code=status.HTTP_200_OK)
async def get_comments_by_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieve all comments for a specific post.

    Args:
        post_id (int): The ID of the post to get comments for.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user.

    Returns:
        list[CommentaryResponseSchema]: A list of comments for the specified post.

    Raises:
        HTTPException: If the post is not found (404).
        HTTPException: If the user is not authorized to view comments for this post (403).
    """
    comments = await repository_comment.get_comments_by_post(db, post_id, user)
    return comments

@router.post("/", response_model=CommentaryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentaryCreateSchema,db: AsyncSession = Depends(get_db),user: User = Depends(auth_service.get_current_user)):
    """
    Create a new comment for a specific post.

    Args:
        body (CommentaryCreateSchema): The schema containing the comment content and associated post ID.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user creating the comment.

    Returns:
        CommentaryResponseSchema: The newly created comment as a validated response model.

    Raises:
        HTTPException: If the specified post is not found (404).
    """
    comment = await repository_comment.create_comment(body, db, user)
    return comment

@router.put("/{comment_id}", response_model=CommentaryResponseSchema, status_code=status.HTTP_200_OK)
async def update_comment(comment_id: int, body: CommentaryUpdateSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Update an existing comment by its ID.

    Args:
        comment_id (int): The ID of the comment to update.
        body (CommentaryUpdateSchema): The schema containing the updated comment content.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user.

    Returns:
        CommentaryResponseSchema: The updated comment as a validated response model.

    Raises:
        HTTPException: If the comment is not found (404).
        HTTPException: If the user is not authorized to update this comment (403).
    """
    comment = await repository_comment.update_comment(comment_id, body, db, user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}",  dependencies=[Depends(access_to_route_all)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(is_owner_or_admin)
):
    """
    Delete a comment by its ID.

    Args:
        comment_id (int): The ID of the comment to delete.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user, must be owner or admin.

    Returns:
        dict: A confirmation message that the comment was successfully deleted.

    Raises:
        HTTPException: If the comment is not found (404).
        HTTPException: If the user is not authorized to delete the comment (403).
    """
    comment = await repository_comment.delete_comment(comment_id, db, user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment