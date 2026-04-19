from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# shared story fields used in multiple schemas
class StoryBase(BaseModel):
    title: str
    content: str
    media_url: Optional[str] = None
    latitude: float
    longitude: float


# data the client sends when creating a story
class StoryCreate(StoryBase):
    pass


# data the API returns after reading or creating a story
class StoryResponse(StoryBase):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
