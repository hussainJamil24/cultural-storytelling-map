from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.story_model import Story, StoryStatus
from app.schemas.story_schema import StoryCreate, StoryResponse, StoryStatusUpdate

# story api routes
router = APIRouter()

# temporary local setting so ui-only testing works without admin approval
# switch this back to False when a real moderation flow is being used
AUTO_APPROVE_NEW_STORIES = True


# creates a new story submission
@router.post("/stories", response_model=StoryResponse, status_code=http_status.HTTP_201_CREATED)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    # creates a new story record in the database
    new_story = Story(
        title=story.title,
        content=story.content,
        media_url=story.media_url,
        latitude=story.latitude,
        longitude=story.longitude,
        status=StoryStatus.APPROVED.value if AUTO_APPROVE_NEW_STORIES else StoryStatus.PENDING.value,
    )

    try:
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save story")

    return new_story


@router.get("/stories", response_model=list[StoryResponse])
def get_stories(
    status: StoryStatus | None = Query(None),
    db: Session = Depends(get_db),
):
    # returns approved stories by default and can filter by a specific status
    try:
        query = db.query(Story)

        # public api shows only approved stories by default
        # passing ?status=... is useful for internal testing and moderation checks
        if status is None:
            query = query.filter(Story.status == StoryStatus.APPROVED.value)
        else:
            query = query.filter(Story.status == status.value)

        return query.order_by(Story.created_at.desc()).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch stories")


@router.get("/stories/{story_id}", response_model=StoryResponse)
def get_story(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    # returns one approved story by its database id
    try:
        story = (
            db.query(Story)
            .filter(
                Story.id == story_id,
                Story.status == StoryStatus.APPROVED.value,
            )
            .first()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch story")

    # returns 404 when the story id does not exist
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    return story


@router.patch("/stories/{story_id}/status", response_model=StoryResponse)
def update_story_status(
    status_update: StoryStatusUpdate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    # updates a story status for the moderation workflow
    # this currently acts like a simple internal moderation endpoint
    try:
        story = db.query(Story).filter(Story.id == story_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch story")

    # returns 404 when the story id does not exist
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        story.status = status_update.status.value
        db.commit()
        db.refresh(story)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update story status")

    return story
