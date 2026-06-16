from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_current_user, require_admin
from app.db.session import get_db
from app.models.story_model import Story, StoryCategory, StoryStatus
from app.models.user_model import User, UserRole
from app.schemas.story_schema import (
    StoryCreate,
    StoryPrivateResponse,
    StoryPublicResponse,
    StoryStatusUpdate,
)

router = APIRouter(tags=["stories"])


def _raise_missing_token() -> None:
    raise HTTPException(
        status_code=http_status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/stories", response_model=StoryPrivateResponse, status_code=http_status.HTTP_201_CREATED)
def create_story(
    story: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_story = Story(
        user_id=current_user.id,
        title=story.title,
        content=story.content,
        media_url=story.media_url,
        latitude=story.latitude,
        longitude=story.longitude,
        status=StoryStatus.PENDING.value,
        category=story.category.value,
        is_anonymous=story.is_anonymous,
    )

    try:
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save story")

    return new_story


@router.get("/stories", response_model=list[StoryPublicResponse])
def get_stories(
    status: StoryStatus | None = Query(None),
    category: StoryCategory | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if status is not None and status != StoryStatus.APPROVED:
        if current_user is None:
            _raise_missing_token()
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Admin role required",
            )

    try:
        query = db.query(Story)

        if status is None:
            query = query.filter(Story.status == StoryStatus.APPROVED.value)
        else:
            query = query.filter(Story.status == status.value)

        if category is not None:
            query = query.filter(Story.category == category.value)

        return query.order_by(Story.created_at.desc()).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch stories")


@router.get("/stories/{story_id}", response_model=StoryPublicResponse)
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

    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    return story


@router.patch("/stories/{story_id}/status", response_model=StoryPrivateResponse)
def update_story_status(
    status_update: StoryStatusUpdate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin),
):
    try:
        story = db.query(Story).filter(Story.id == story_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch story")

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
