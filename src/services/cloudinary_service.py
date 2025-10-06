
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from src.conf.config import config

class CloudinaryService:
    """
    Service class for interacting with Cloudinary for image upload, deletion, and transformations.

    Attributes:
        max_file_size (int): Maximum allowed file size for uploads in bytes (default 5 MB).
    """
    def __init__(self):
        """
        Initialize the CloudinaryService by configuring Cloudinary credentials and maximum file size.
        """
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
            secure=True,
        )
        self.max_file_size = 5 * 1024 * 1024  # 5 МБ

    async def upload_image(self, file: UploadFile, folder: str = "photoshare") -> tuple[str, str]:
        """
    Upload an image file to Cloudinary and return its URL and public ID.

    Args:
        file (UploadFile): The image file to upload.
        folder (str, optional): The Cloudinary folder to store the image. Defaults to "photoshare".

    Returns:
        tuple[str, str]: A tuple containing the secure URL of the uploaded image and its public ID.

    Raises:
        HTTPException: If the file size exceeds the maximum allowed limit (413 Request Entity Too Large).
        HTTPException: If the upload fails (handled internally by Cloudinary, may raise exceptions from the Cloudinary SDK).
    """
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
        url = result["secure_url"]
        public_id = result["public_id"]
        return url, public_id

    async def delete_image(self, public_id: str):
        """
    Delete an image from Cloudinary by its public ID.

    Args:
        public_id (str): The public ID of the image to delete.

    Raises:
        HTTPException: If the deletion fails (handled internally by Cloudinary, may raise exceptions from the Cloudinary SDK).
    """
        cloudinary.uploader.destroy(public_id, resource_type="image")

    async def transform_image(self, public_id: str, transformation: str) -> str:
        """
    Apply a predefined transformation to an image in Cloudinary and return the transformed image URL.

    Args:
        public_id (str): The public ID of the image to transform.
        transformation (str): The type of transformation to apply. Supported transformations: 
                              "resize", "crop", "grayscale", "quality".

    Returns:
        str: The secure URL of the transformed image.

    Raises:
        ValueError: If an unsupported transformation type is provided.
        HTTPException: If the transformation fails (handled internally by Cloudinary, may raise exceptions from the Cloudinary SDK).
    """
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