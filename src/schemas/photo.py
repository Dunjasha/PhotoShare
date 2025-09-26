from typing import Optional
from pydantic import BaseModel, ConfigDict


class PhotoResponse(BaseModel):
    id: int
    url: str
    transformed_url: Optional[str] = None
    description: Optional[str]
    qr_code_path: Optional[str] = None 
    model_config = ConfigDict(from_attributes=True)
