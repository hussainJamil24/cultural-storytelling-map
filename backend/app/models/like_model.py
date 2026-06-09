from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from app.db.session import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)

    # which story was liked
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)

    # which user liked it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # prevents a user from liking the same story more than once
    __table_args__ = (
        UniqueConstraint("story_id", "user_id", name="uq_like_story_user"),
    )
