from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary.uploader
from src.database.db import get_db
from src.services.auth import auth_service
router = APIRouter(
    prefix="/api/photos",
    tags=["Photos"]
)

