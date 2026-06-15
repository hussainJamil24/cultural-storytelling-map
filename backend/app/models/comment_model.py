from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


# comment table for user comments left on a story
class Comment(Base):
    # stores comment records in the comments table
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    # owning story; comments are removed when the story is deleted
    story_id = Column(
        Integer,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # author; required because comments are always attributed.
    # comments are removed when the user account is deleted.
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # links the comment to its story and author
    story = relationship("Story", back_populates="comments")
    author = relationship("User", back_populates="comments")

    # convenience accessor for the author's display name
    @property
    def author_name(self) -> str | None:
        return self.author.name if self.author is not None else None
