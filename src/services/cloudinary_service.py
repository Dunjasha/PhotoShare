import cloudinary
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from src.conf.config import config

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
            secure=True,
        )
        self.max_file_size = 5 * 1024 * 1024  # 5 МБ

    async def upload_image(self, file: UploadFile, folder: str = "photoshare") -> str:
        contents = await file.read()
        if len(contents) > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Max file size {self.max_file_size // (1024*1024)} МБ"
            )
        await file.seek(0)

        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="image"
        )
        return result.get("secure_url")

    async def delete_image(self, public_id: str):
        cloudinary.uploader.destroy(public_id, resource_type="image")

    async def transform_image(self, public_id: str, transformation: str) -> str:
        transformations = {
            "resize": {"width": 300, "height": 300, "crop": "scale"},
            "crop": {"width": 200, "height": 200, "crop": "crop"},
            "grayscale": {"effect": "grayscale"},
            "quality": {"quality": "auto"},
        }

        if transformation not in transformations:
            raise ValueError("Unsupported transformation")

        result = cloudinary.uploader.explicit(
            public_id,
            type="upload",
            eager=[transformations[transformation]],
        )

        return result["eager"][0]["secure_url"]