from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# what the client sends to post a comment
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


# what the api returns for each comment
class CommentResponse(BaseModel):
    id: int
    story_id: int
    user_id: int
    content: str
    created_at: datetime

    # include the author's name so the frontend can display it without a second request
    author_name: str

    model_config = ConfigDict(from_attributes=True)
