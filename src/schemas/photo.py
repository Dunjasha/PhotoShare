from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TagSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class PhotoSchema(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    transformed_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PhotoUpdateSchema(BaseModel):
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    transformed_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PhotoResponse(BaseModel):
    id: int
    user_id: int
    url: str
    transformed_url: Optional[str] = None
    description: Optional[str]
    tags: list[TagSchema]
    public_id: str
    created_at: datetime
    updated_at: datetime
    qr_code_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

