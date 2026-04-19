from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.story_model import StoryStatus


# shared story fields used across story schemas
class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    media_url: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    # removes blank-only title and content values
    @field_validator("title", "content")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


# data the client sends when creating a story
class StoryCreate(StoryBase):
    pass


# data used to approve or reject a submitted story
class StoryStatusUpdate(BaseModel):
    status: StoryStatus


# data the API returns after reading or creating a story
class StoryResponse(StoryBase):
    id: int
    status: StoryStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
