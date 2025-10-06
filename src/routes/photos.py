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
    """
    Retrieve all photos for the currently authenticated user.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user.

    Returns:
        list[PhotoResponse]: A list of photo posts belonging to the user.

    Raises:
        HTTPException: If the user has no access to any photos (403), handled internally by repository if needed.
    """
    photos = await repository_photos.get_photos(db, user)
    return photos


@router.get("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a specific photo by its ID for the currently authenticated user.

    Args:
        photo_id (int): The ID of the photo to retrieve.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user.

    Returns:
        PhotoResponse: The requested photo as a validated response model.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If the user is not authorized to access this photo (403), handled internally by repository if needed.
    """
    photo = await repository_photos.get_photo(photo_id, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(file: UploadFile = File(...), description: Optional[str] = Form(None),
                       tags: Optional[str] = Form(None), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    Upload a new photo with optional description and tags.

    Args:
        file (UploadFile): The photo file to upload.
        description (Optional[str]): Optional description for the photo.
        tags (Optional[str]): Optional comma-separated tags for the photo.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user uploading the photo.

    Returns:
        PhotoResponse: The newly created photo as a validated response model.

    Raises:
        HTTPException: If the file upload fails or database operation fails (handled internally by repository).
    """
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else []
    photo = await repository_photos.create_photo(file, description, tags_list, db, user)
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def update_photo_description(photo_id: int, body: PhotoUpdateSchema, db: AsyncSession = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):
    """
    Update the description, transformed URL, or tags of an existing photo.

    Args:
        photo_id (int): The ID of the photo to update.
        body (PhotoUpdateSchema): The schema containing the updated description, transformed URL, or tags.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user attempting to update the photo.

    Returns:
        PhotoResponse: The updated photo as a validated response model.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If the user is not authorized to update this photo (403).
        HTTPException: If more than 5 tags are provided (400), handled internally by repository.
    """
    photo = await repository_photos.update_photo_description(photo_id, body, db, user)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: int, db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    Delete a photo by its ID.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user attempting to delete the photo.

    Returns:
        dict: A confirmation message that the photo was successfully deleted.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If the user is not authorized to delete this photo (403).
    """
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
    """
    Apply a visual transformation to a photo and update its transformed URL.

    Args:
        photo_id (int): The ID of the photo to transform.
        transformation (str): The transformation type or parameters to apply.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user requesting the transformation.

    Returns:
        PhotoResponse: The updated photo with the transformed image URL.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If the transformation type is invalid or unsupported (400), handled internally by repository.
        HTTPException: If the user is not authorized to transform this photo (403), handled internally by repository.
    """
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
    """
    Generate a QR code for the transformed image of a photo and update its QR code path.

    Args:
        photo_id (int): The ID of the photo for which to generate a QR code.
        db (AsyncSession): SQLAlchemy asynchronous database session.
        user (User): The currently authenticated user requesting the QR code.

    Returns:
        PhotoResponse: The updated photo containing the path to the generated QR code.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If the photo does not have a transformed image (400), handled internally by repository.
        HTTPException: If the user is not authorized to generate a QR code for this photo (403), handled internally by repository.
    """
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
