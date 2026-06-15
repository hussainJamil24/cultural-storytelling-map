from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    # stores moderation status and submission time
    status = Column(String, nullable=False, default=StoryStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # links each story to its attached images and audio
    media = relationship(
        "Media",
        back_populates="story",
        cascade="all, delete-orphan",
    )
