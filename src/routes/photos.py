from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.entity.models import User

from src.schemas.post import PhotoSchema, PhotoUpdateSchema
from src.schemas import PhotoSchema, PhotoUpdateSchema, PhotoResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])

@router.get("/", response_model=list[TodoResponse], status_code=status.HTTP_200_OK)
async def get_photos(db: AsyncSession = Depends(get_db), current_user: int = Depends(auth_service.get_current_user)):
    photos = await repository_photos.get_photos(db)
    return photos

@router.get("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo(photo_id, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(body: PhotoSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.create_photo(body, db, user)
    return photo

@router.put("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.update_photo_description(photo_id, body, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.delete("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.delete_photo(photo_id, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.post("/transform", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def transform_photo(
    photo_id: int,
    transformation: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
 
    return await repository_photos.transform_photo(photo_id, transformation, db, user)
