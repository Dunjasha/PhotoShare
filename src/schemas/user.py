from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSchema(BaseModel):
    username: str = Field(min_length=4, max_length=16)
    email: EmailStr
    password: str = Field(min_length=4, max_length=16)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)  # noqa


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
