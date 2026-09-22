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
    image_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    is_anonymous = Column(Boolean, nullable=False, default=False)

    status = Column(String, nullable=False, default=StoryStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # AI moderation assist: null means "not assessed" (e.g. no API key configured),
    # distinct from False which means "assessed, nothing found". A human moderator
    # always makes the final approve/reject call -- this only surfaces a hint.
    ai_flag = Column(Boolean, nullable=True)
    ai_flag_reason = Column(String, nullable=True)

    # AI-written human-readable place description (e.g. "Old Town, Nicosia"),
    # computed lazily on first request and cached here so it's a one-time cost.
    ai_location_label = Column(String, nullable=True)


class StoryTranslation(Base):
    """Caches AI-generated translations so a story is translated once per
    language, not re-translated on every page view."""

    __tablename__ = "story_translations"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    language = Column(String, nullable=False)  # "el" or "tr"
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
