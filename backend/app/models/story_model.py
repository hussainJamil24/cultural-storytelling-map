from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.session import Base


class StoryStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class StoryCategory(str, Enum):
    HERITAGE = "heritage"
    LANDMARKS = "landmarks"
    ORAL_HISTORY = "oral_history"
    CUSTOMS = "customs"
    FOOD = "food"
    MUSIC = "music"
    RELIGION = "religion"
    MIGRATION = "migration"


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    is_anonymous = Column(Boolean, nullable=False, default=False)

    status = Column(String, nullable=False, default=StoryStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
