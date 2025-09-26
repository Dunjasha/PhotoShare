from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PhotoSchema(BaseModel):
    url: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    transformed_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PhotoUpdateSchema(BaseModel):
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    transformed_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PhotoResponse(BaseModel):
    id: int
    owner_id: int
    url: str
    transformed_url: Optional[str] = None
    description: Optional[str]
    tags: list[str]
    public_id: str
    created_at: datetime
    updated_at: datetime
    qr_code_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)