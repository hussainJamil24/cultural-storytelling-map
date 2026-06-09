from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User
from app.schemas.story_schema import StoryCreate, StoryResponse, StoryStatusUpdate

# registers story api routes
router = APIRouter()


# creates a new story submission — requires a logged-in user
@router.post("/stories", response_model=StoryResponse, status_code=http_status.HTTP_201_CREATED)
def create_story(
    story: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 401 if not logged in
):
    # creates a new story record, stamping it with the submitting user's id
    new_story = Story(
        title=story.title,
        content=story.content,
        media_url=story.media_url,
        latitude=story.latitude,
        longitude=story.longitude,
        status=StoryStatus.PENDING.value,
        category=story.category,
        user_id=current_user.id,
    )

    try:
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save story")

    return new_story


# returns approved stories or filters by review status
@router.get("/stories", response_model=list[StoryResponse])
def get_stories(
    status: StoryStatus | None = Query(None),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    # returns approved stories by default and can filter by a specific status
    try:
        query = db.query(Story)

        # public api shows only approved stories by default
        if status is None:
            query = query.filter(Story.status == StoryStatus.APPROVED.value)
        else:
            query = query.filter(Story.status == status.value)

        # category filter
        if category is not None:
            query = query.filter(Story.category == category)

        return query.order_by(Story.created_at.desc()).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch stories")


# returns one approved story by its database id
@router.get("/stories/{story_id}", response_model=StoryResponse)
def get_story(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
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


# updates a story status — requires admin
@router.patch("/stories/{story_id}/status", response_model=StoryResponse)
def update_story_status(
    status_update: StoryStatusUpdate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),  # 401 if not logged in, 403 if not admin
):
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
