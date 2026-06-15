from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.like_model import Like
from app.models.story_model import Story
from app.models.user_model import User
from app.schemas.like_schema import LikeRequest, LikeResponse

# registers like api routes
router = APIRouter()


# builds the current like state (count + whether the user likes the story)
def _like_state(db: Session, story_id: int, user_id: int | None) -> LikeResponse:
    like_count = db.query(Like).filter(Like.story_id == story_id).count()
    liked = False
    if user_id is not None:
        liked = (
            db.query(Like.id)
            .filter(Like.story_id == story_id, Like.user_id == user_id)
            .first()
            is not None
        )
    return LikeResponse(story_id=story_id, like_count=like_count, liked=liked)


# ensures the story exists, returning 404 otherwise
def _require_story(db: Session, story_id: int) -> None:
    if db.query(Story.id).filter(Story.id == story_id).first() is None:
        raise HTTPException(status_code=404, detail="Story not found")


# returns the like count and, when user_id is given, whether that user liked it
@router.get("/stories/{story_id}/likes", response_model=LikeResponse)
def get_likes(
    story_id: int = Path(..., gt=0),
    user_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    _require_story(db, story_id)
    try:
        return _like_state(db, story_id, user_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch likes")


# likes a story for a user; idempotent if the like already exists
@router.post("/stories/{story_id}/likes", response_model=LikeResponse)
def like_story(
    payload: LikeRequest,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    _require_story(db, story_id)

    # rejects likes from an unknown user
    if db.query(User.id).filter(User.id == payload.user_id).first() is None:
        raise HTTPException(status_code=400, detail="Invalid user")

    already_liked = (
        db.query(Like.id)
        .filter(Like.story_id == story_id, Like.user_id == payload.user_id)
        .first()
    )
    if already_liked is None:
        try:
            db.add(Like(story_id=story_id, user_id=payload.user_id))
            db.commit()
        except IntegrityError:
            # another request liked it first; treat as already liked
            db.rollback()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Could not like story")

    return _like_state(db, story_id, payload.user_id)


# removes a user's like from a story; idempotent if no like exists
@router.delete("/stories/{story_id}/likes", response_model=LikeResponse)
def unlike_story(
    payload: LikeRequest,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    _require_story(db, story_id)

    try:
        db.query(Like).filter(
            Like.story_id == story_id, Like.user_id == payload.user_id
        ).delete()
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not unlike story")

    return _like_state(db, story_id, payload.user_id)
