from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.story_model import StoryStatus


# shared story fields used across story schemas
class StoryBase(BaseModel):
    # validates story title, content, and map coordinates
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    media_url: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: str = Field(..., min_length=1)

    # removes blank-only title and content values
    @field_validator("title", "content")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value
    
    # Validate allowed categories
    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        allowed = {"heritage", "landmarks", "oral", "customs"}
        if value not in allowed:
            raise ValueError("Invalid category")
        return value


# data the client sends when creating a story
class StoryCreate(StoryBase):
    # when True, the author will be hidden from public responses
    is_anonymous: bool = False


# data used to approve or reject a submitted story
class StoryStatusUpdate(BaseModel):
    status: StoryStatus


# data the api returns after reading or creating a story
class StoryResponse(StoryBase):
    id: int
    status: StoryStatus
    created_at: datetime
    user_id: Optional[int] = None  # None for stories submitted before auth was added
    is_anonymous: bool = False

    # reads values directly from sqlalchemy model instances
    model_config = ConfigDict(from_attributes=True)

    # hide the author id from the public response when the story is anonymous.
    # the real user_id stays in the database for moderation/accountability.
    @model_validator(mode="after")
    def hide_anonymous_author(self):
        if self.is_anonymous:
            self.user_id = None
        return self
