from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional


class CreateShortUrlRequest(BaseModel):
    original_url: HttpUrl


class CreateShortUrlResponse(BaseModel):
    short_url: str


class DeactivateLinkResponse(BaseModel):
    message: str

    model_config = ConfigDict()


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_url: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
