from fastapi import APIRouter, Depends, HTTPException, Path, status as http_status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.like_model import Like
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User
from app.schemas.like_schema import LikeStatusResponse

router = APIRouter(tags=["likes"])


def _ensure_approved_story(db: Session, story_id: int) -> Story:
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


def _like_status(db: Session, story_id: int, user_id: int | None) -> LikeStatusResponse:
    try:
        count = db.query(Like).filter(Like.story_id == story_id).count()
        liked = False
        if user_id is not None:
            liked = (
                db.query(Like)
                .filter(Like.story_id == story_id, Like.user_id == user_id)
                .first()
                is not None
            )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch likes")

    return LikeStatusResponse(story_id=story_id, count=count, liked=liked)


@router.post(
    "/stories/{story_id}/likes",
    response_model=LikeStatusResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def like_story(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_approved_story(db, story_id)

    existing = (
        db.query(Like)
        .filter(Like.story_id == story_id, Like.user_id == current_user.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Story already liked",
        )

    new_like = Like(story_id=story_id, user_id=current_user.id)
    try:
        db.add(new_like)
        db.commit()
    except IntegrityError:
        # unique constraint hit by a concurrent like; treat as already liked
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Story already liked",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not like story")

    return _like_status(db, story_id, current_user.id)


@router.delete("/stories/{story_id}/likes", response_model=LikeStatusResponse)
def unlike_story(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_approved_story(db, story_id)

    like = (
        db.query(Like)
        .filter(Like.story_id == story_id, Like.user_id == current_user.id)
        .first()
    )
    if like is None:
        raise HTTPException(status_code=404, detail="Like not found")

    try:
        db.delete(like)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not unlike story")

    return _like_status(db, story_id, current_user.id)


@router.get("/stories/{story_id}/likes", response_model=LikeStatusResponse)
def get_likes(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    _ensure_approved_story(db, story_id)
    user_id = current_user.id if current_user is not None else None
    return _like_status(db, story_id, user_id)
