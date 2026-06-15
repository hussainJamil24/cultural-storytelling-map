from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


# allowed media kinds attached to a story
class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"


# media table for images and audio attached to a story
class Media(Base):
    # stores media records in the media table
    __tablename__ = "media"

    # stores the media file reference and its owning story
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(
        Integer,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # links each media item back to its story
    story = relationship("Story", back_populates="media")
