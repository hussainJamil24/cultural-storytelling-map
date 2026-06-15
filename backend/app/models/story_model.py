from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, false
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

    # links the story to its submitter; nullable for anonymous or logged-out posts.
    # SET NULL keeps the story if the user account is later deleted.
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # when true the submitter is hidden in public responses even if user_id is set
    is_anonymous = Column(Boolean, nullable=False, default=False, server_default=false())

    # links each story to its attached images and audio
    media = relationship(
        "Media",
        back_populates="story",
        cascade="all, delete-orphan",
    )

    # links each story to its comments
    comments = relationship(
        "Comment",
        back_populates="story",
        cascade="all, delete-orphan",
    )

    # links each story to its submitting user
    author = relationship("User", back_populates="stories")

    # returns the submitter name only when the story is not anonymous
    @property
    def author_name(self) -> str | None:
        if self.is_anonymous or self.author is None:
            return None
        return self.author.name
