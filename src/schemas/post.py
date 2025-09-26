from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class PostCreate(BaseModel):
    description: str = Field(max_length=255)
    url: str
    tags: Optional[List[str]] = None  # до 5 тегов


class PostResponse(BaseModel):
    id: int
    description: str
    url: str
    transformed_url: Optional[str]
    public_id: str
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content: str = Field(max_length=255)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)
