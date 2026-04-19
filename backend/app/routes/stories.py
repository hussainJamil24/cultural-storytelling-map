from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.story_model import Story
from app.schemas.story_schema import StoryCreate, StoryResponse

router = APIRouter()


@router.post("/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    # creates a new story record in the database
    new_story = Story(
        title=story.title,
        content=story.content,
        media_url=story.media_url,
        latitude=story.latitude,
        longitude=story.longitude,
    )

    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    return new_story


@router.get("/stories", response_model=list[StoryResponse])
def get_stories(db: Session = Depends(get_db)):
    # returns all saved stories from the database
    return db.query(Story).order_by(Story.created_at.desc()).all()
