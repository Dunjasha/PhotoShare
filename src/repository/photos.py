from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import selectinload

from src.entity.models import User, Post, Tag
from src.schemas.photo import PhotoSchema, PhotoUpdateSchema, PhotoResponse
from src.services.cloudinary_service import CloudinaryService
import qrcode
from sqlalchemy import func
import os
from pathlib import Path

cloudinary_service = CloudinaryService()

QR_CODES_DIR = Path("qrcodes")
QR_CODES_DIR.mkdir(exist_ok=True)

async def get_photos(db: AsyncSession, user: User):
    stmt = select(Post).options(selectinload(Post.tags))
    photos = await db.execute(stmt)
    result = photos.scalars().all()
    return [PhotoResponse.model_validate(photo) for photo in result]

async def get_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Post).filter_by(id=photo_id).options(selectinload(Post.tags))
    todo = await db.execute(stmt)
    photo = todo.scalar_one_or_none()
    return PhotoResponse.model_validate(photo) if photo else None


async def create_photo(file: UploadFile, description: Optional[str], tags: Optional[list[str]], db: AsyncSession, user: User):
    url, public_id = await cloudinary_service.upload_image(file)

    tag_objects = []
    if tags:
        for tag_name in tags:
            result = await db.execute(select(Tag).filter_by(name=tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()  # получить id
            tag_objects.append(tag)

    new_photo = Post(
        description=description,
        tags=tag_objects,
        url=url,
        public_id=public_id,
        user_id=user.id
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    return PhotoResponse.model_validate(new_photo)


async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Post).filter_by(id=photo_id).options(selectinload(Post.tags))
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Photo not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to update this photo")

    changed = False

    if body.description is not None:
        post.description = body.description
        changed = True

    if body.transformed_url is not None:
        post.transformed_url = body.transformed_url
        changed = True

    if body.tags is not None:
        raw = ",".join(body.tags)
        parts = [t.strip() for t in raw.split(",") if t.strip()]

        seen = set()
        normalized_tags = []
        for t in parts:
            key = t.casefold()
            if key not in seen:
                seen.add(key)
                normalized_tags.append(t)

        tag_objects: list[Tag] = []
        for tag_name in normalized_tags:
            q = await db.execute(select(Tag).where(func.lower(Tag.name) == tag_name.casefold()))
            tag = q.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()
            tag_objects.append(tag)

        post.tags[:] = []
        post.tags.extend(tag_objects)
        db.add(post)
        changed = True

    if not changed:
        return PhotoResponse.model_validate(post)

    await db.commit()
    await db.refresh(post)

    return PhotoResponse.model_validate(post)




async def delete_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Post).filter_by(id=photo_id).options(selectinload(Post.tags))
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Photo not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this photo")

    await db.delete(post)
    await db.commit()

    return {"detail": "Photo deleted successfully"}



async def transform_photo(photo_id: int, transformation: str, db: AsyncSession, user):
    stmt = select(Post).filter_by(id=photo_id, user_id=user.id).options(selectinload(Post.tags))
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        transformed_url = await cloudinary_service.transform_image(photo.public_id, transformation)
        photo.transformed_url = transformed_url
        await db.commit()
        await db.refresh(photo)
        return PhotoResponse.model_validate(photo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def generate_qr_code(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Post).filter_by(id=photo_id, user_id=user.id).options(selectinload(Post.tags))
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if not photo.transformed_url:
        raise HTTPException(status_code=400, detail="No transformed image found")

    img = qrcode.make(photo.transformed_url)

    qr_path = QR_CODES_DIR / f"photo_{photo.id}_qr.png"
    img.save(qr_path)

    photo.qr_code_path = str(qr_path)
    await db.commit()
    await db.refresh(photo)

    return PhotoResponse.model_validate(photo)
