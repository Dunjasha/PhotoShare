import cloudinary.uploader
from src.conf.config import config


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
            secure=True,
        )

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
