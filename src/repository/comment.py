from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from src.entity.models import User, Post, Comment
from src.schemas.comment import CommentaryResponseSchema, CommentaryCreateSchema, CommentaryUpdateSchema


async def get_comments_by_post(db: AsyncSession, post_id: int, user: User):
    """
    Retrieves all comments associated with a specific post, ensuring the user has permission to view them.

    Args:
        db (AsyncSession): The asynchronous database session.
        post_id (int): The ID of the post for which to retrieve comments.
        user (User): The user requesting to view the comments.

    Raises:
        HTTPException: If the post is not found (404).
        HTTPException: If the user does not have permission to view comments for this post (403).

    Returns:
        list[CommentaryResponseSchema]: A list of validated comment response objects associated with the specified post.
    """
    post = await db.get(Post, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view comments for this post")
    stmt = (
        select(Comment)
        .filter_by(post_id=post.id)
        .options(selectinload(Comment.user))
    )
    comments = await db.execute(stmt)
    result = comments.scalars().all()
    return [CommentaryResponseSchema.model_validate(comment) for comment in result]

async def create_comment(body: CommentaryCreateSchema, db: AsyncSession, user: User):
    """
    Creates a new comment associated with a specific post.

    Args:
        body (CommentaryCreateSchema): The schema containing the content of the comment and the related post ID.
        db (AsyncSession): The asynchronous database session.
        user (User): The user creating the comment.

    Raises:
        HTTPException: If the specified post is not found (404).

    Returns:
        CommentaryResponseSchema: The created comment represented as a validated response model.
    """
    post = await db.get(Post, body.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment = Comment(
        comment_content=body.comment_content,
        post_id=body.post_id,
        user_id=user.id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return CommentaryResponseSchema.model_validate(new_comment)

async def update_comment(comment_id: int, body: CommentaryUpdateSchema, db: AsyncSession, user: User):
    """
    Updates the content of an existing comment.

    Args:
        comment_id (int): The ID of the comment to update.
        body (CommentaryUpdateSchema): The schema containing updated comment data.
        db (AsyncSession): The asynchronous database session.
        user (User): The user attempting to update the comment.

    Raises:
        HTTPException: If the comment is not found (404).
        HTTPException: If the user does not have permission to update the comment (403).

    Returns:
        CommentaryResponseSchema: The updated comment represented as a validated response model.
    """
    stmt = select(Comment).filter_by(id=comment_id).options(selectinload(Comment.user))
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    if body.comment_content is not None:
        comment.comment_content = body.comment_content
        comment.updated_at = datetime.now()

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentaryResponseSchema.model_validate(comment)