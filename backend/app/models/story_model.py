from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.session import Base


# story table for stories shown on the map
class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
