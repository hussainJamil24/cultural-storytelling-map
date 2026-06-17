from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.story_model import StoryCategory, StoryStatus


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1, max_length=10000)
    image_url: Optional[str] = Field(default=None, max_length=2048)
    audio_url: Optional[str] = Field(default=None, max_length=2048)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: StoryCategory
    is_anonymous: bool = False

    @field_validator("title", "content", mode="before")
    @classmethod
    def validate_text_fields(cls, value):
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("image_url", "audio_url", mode="before")
    @classmethod
    def normalize_media_url(cls, value):
        if value is None or not isinstance(value, str):
            return value
        value = value.strip()
        return value or None


class StoryCreate(StoryBase):
    pass


class StoryStatusUpdate(BaseModel):
    status: StoryStatus


class StoryPublicResponse(StoryBase):
    id: int
    status: StoryStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoryPrivateResponse(StoryPublicResponse):
    user_id: int
