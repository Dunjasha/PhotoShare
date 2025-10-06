from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.entity.models import User, Role

from src.schemas.photo import PhotoSchema, PhotoUpdateSchema, PhotoResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(tags=["photos"])


@router.get("/", response_model=list[PhotoResponse], status_code=status.HTTP_200_OK)
async def get_photos(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photos = await repository_photos.get_photos(db, user)
    return photos


@router.get("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo(photo_id, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(file: UploadFile = File(...), description: Optional[str] = Form(None),
                       tags: Optional[str] = Form(None), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else []
    photo = await repository_photos.create_photo(file, description, tags_list, db, user)
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.update_photo_description(photo_id, body, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: int, db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
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


@router.post(
    "/{photo_id}/generate_qr",
    response_model=PhotoResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_qr_code(
        photo_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    return await repository_photos.generate_qr_code(photo_id, db, user)


# --------------- Admin routes -----------------
admin_required = RoleAccess([Role.ADMIN])


@router.get("/admin/all", response_model=list[PhotoResponse], dependencies=[Depends(admin_required)])
async def admin_get_all_photos(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all user photos (admin only).

    This endpoint allows administrators to view all photos uploaded by all users.

    Args:
        db (AsyncSession): The database session (injected).

    Returns:
        list[PhotoResponse]: A list of all photos in the system.
    """
    return await repository_photos.get_all_photos_admin(db)


@router.delete("/admin/{photo_id}", dependencies=[Depends(admin_required)],
               status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Permanently delete any photo by its ID (admin only).

    This operation allows administrators to remove any photo in the system,
    regardless of the owner.

    Args:
        photo_id (int): The unique identifier of the photo to delete.
        db (AsyncSession): The database session (injected).

    Raises:
        HTTPException (404): If the photo with the specified ID does not exist.

    Returns:
        None
    """
    photo = await repository_photos.admin_delete_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.put("/admin/{photo_id}", response_model=PhotoResponse, dependencies=[Depends(admin_required)])
async def admin_update_photo(photo_id: int, body: PhotoUpdateSchema,
                             db: AsyncSession = Depends(get_db)):
    """
    Update a photo's description by its ID (admin only).

    Allows administrators to edit the description of any photo in the database.

    Args:
        photo_id (int): The unique identifier of the photo to update.
        body (PhotoUpdateSchema): The updated photo description.
        db (AsyncSession): The database session (injected).

    Raises:
        HTTPException (404): If the specified photo does not exist.

    Returns:
        PhotoResponse: The updated photo information.
    """
    photo = await repository_photos.admin_update_photo_description(photo_id, body, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo
