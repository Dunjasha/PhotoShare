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
    comments = await repository_comment.get_comments_by_post(db, post_id, user)
    return comments

@router.post("/", response_model=CommentaryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentaryCreateSchema,db: AsyncSession = Depends(get_db),user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comment.create_comment(body, db, user)
    return comment

@router.put("/{comment_id}", response_model=CommentaryResponseSchema, status_code=status.HTTP_200_OK)
async def update_comment(comment_id: int, body: CommentaryUpdateSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
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
    comment = await repository_comment.delete_comment(comment_id, db, user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment