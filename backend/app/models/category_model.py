from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.session import Base


# category table: the managed source of truth for story categories.
# stories reference a category by its slug (e.g. "heritage").
class Category(Base):
    # stores category records in the categories table
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    # stable url/filter key used by stories and the frontend (e.g. "heritage")
    slug = Column(String, unique=True, nullable=False, index=True)
    # human-readable name shown in the UI (e.g. "Oral Histories")
    label = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    # optional icon class used by the frontend (e.g. "bi-mic-fill")
    icon = Column(String, nullable=True)
    # controls display order in category lists
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
