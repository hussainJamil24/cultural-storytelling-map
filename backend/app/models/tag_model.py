from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.db.session import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # e.g. "festival", "music", "food"


class StoryTag(Base):
    __tablename__ = "story_tags"

    story_id = Column(Integer, ForeignKey("stories.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    # composite primary key already prevents duplicates, but this makes it explicit
    __table_args__ = (
        UniqueConstraint("story_id", "tag_id", name="uq_story_tag"),
    )
