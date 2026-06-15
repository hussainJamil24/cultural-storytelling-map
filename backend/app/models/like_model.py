from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


# like table: one row per (story, user); the unique constraint prevents
# a user from liking the same story more than once.
class Like(Base):
    # stores like records in the likes table
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("story_id", "user_id", name="uq_likes_story_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # liked story; likes are removed when the story is deleted
    story_id = Column(
        Integer,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # the user who liked; likes are removed when the user is deleted
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # links the like to its story and user
    story = relationship("Story", back_populates="likes")
    user = relationship("User", back_populates="likes")
