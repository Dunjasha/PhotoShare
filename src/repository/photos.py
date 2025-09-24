from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Photo
from src.schemas.photo import PhotoSchema, PhotoUpdateSchema

async def get_photos(db: AsyncSession):
    stmt = select(Photo)
    photos = await db.execute(stmt)
    return photos.scalars().all()

async def get_todo(photo_id: int, db: AsyncSession):
    stmt = select(Photo).filter_by(id=photo_id)
    todo = await db.execute(stmt)
    return todo.scalar_one_or_none()


async def create_todo(body: PhotoSchema, db: AsyncSession):
    photo = Photo(**body.model_dump(exclude_unset=True))
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession):
    stmt = select(Photo).filter_by(id=photo_id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo:
        photo.description = body.description
        await db.commit()
        await db.refresh(photo)
    return photo


async def delete_todo(photo_id: int, db: AsyncSession):
    stmt = select(Photo).filter_by(id=photo_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        await db.delete(photo)
        await db.commit()
    return photo