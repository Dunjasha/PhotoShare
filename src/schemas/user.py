from pydantic import BaseModel, EmailStr, Field, ConfigDict
from src.entity.models import Role

class UserSchema(BaseModel):
    username: str = Field(min_length=4, max_length=16)
    email: EmailStr
    password: str = Field(min_length=4, max_length=16)
    role: Role = Role.USER #default role is USER

class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
