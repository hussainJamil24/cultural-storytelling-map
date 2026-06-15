from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# data the client sends when posting a comment
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    # author id of the logged-in user (comments are always attributed)
    user_id: int

    # rejects blank-only comment text
    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


# data the api returns for a comment
class CommentResponse(BaseModel):
    id: int
    story_id: int
    content: str
    created_at: datetime
    # always-attributed author name
    author_name: Optional[str] = None

    # reads values directly from sqlalchemy model instances
    model_config = ConfigDict(from_attributes=True)
