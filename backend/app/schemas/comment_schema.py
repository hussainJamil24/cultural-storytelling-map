from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    # null/omitted means a top-level comment; otherwise it's a reply
    parent_id: Optional[int] = Field(default=None, gt=0)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value):
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class CommentResponse(BaseModel):
    id: int
    story_id: int
    user_id: int
    parent_id: Optional[int]
    content: str
    created_at: datetime
    author_name: str

    model_config = ConfigDict(from_attributes=True)
