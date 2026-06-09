from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text

from app.db.session import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    # which story this comment belongs to
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)

    # which user wrote it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
