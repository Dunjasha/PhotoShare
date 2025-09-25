from typing import Optional
from pydantic import BaseModel, ConfigDict


class PhotoResponse(BaseModel):
    id: int
    url: str
    transformed_url: Optional[str] = None
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)
