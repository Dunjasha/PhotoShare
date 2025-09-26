from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile

from src.entity.models import Photo, User
from src.schemas.photo import PhotoSchema, PhotoUpdateSchema
from src.services.cloudinary_service import CloudinaryService
import qrcode
import os
from pathlib import Path

cloudinary_service = CloudinaryService()

QR_CODES_DIR = Path("qrcodes")
QR_CODES_DIR.mkdir(exist_ok=True)

async def get_photos(db: AsyncSession, user: User):
    stmt = select(Photo)
    photos = await db.execute(stmt)
    return photos.scalars().all()

async def get_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id)
    todo = await db.execute(stmt)
    return todo.scalar_one_or_none()


async def create_photo(file: UploadFile, body: PhotoSchema, db: AsyncSession, user: User):
    url = await cloudinary_service.upload_image(file)
    new_photo = Photo(**body.dict(), url=url, owner_id=user.id)
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    return new_photo


async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo:
        photo.description = body.description
        await db.commit()
        await db.refresh(photo)
    return photo


async def delete_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.public_id:
            await cloudinary_service.delete_image(public_id=photo.public_id)
        await db.delete(photo)
        await db.commit()
    return photo

async def transform_photo(photo_id: int, transformation: str, db: AsyncSession, user):
    stmt = select(Photo).filter_by(id=photo_id, owner_id=user.id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        transformed_url = await cloudinary_service.transform_image(photo.public_id, transformation)
        photo.transformed_url = transformed_url
        await db.commit()
        await db.refresh(photo)

        return photo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def generate_qr_code(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, owner_id=user.id)
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

    return photo
