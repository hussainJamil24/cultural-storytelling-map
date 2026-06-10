from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.session import Base


# allowed status values for story review state
class StoryStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# story table for submitted cultural stories
class Story(Base):
    # stores story records in the stories table
    __tablename__ = "stories"

    # stores the main story fields and map coordinates
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    # links the story to the user who submitted it (nullable so old stories are kept)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # when True the author is hidden from the public api, but user_id is still
    # stored so admins keep accountability for moderation
    is_anonymous = Column(Boolean, nullable=False, default=False)

    # stores moderation status and submission time
    status = Column(String, nullable=False, default=StoryStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
