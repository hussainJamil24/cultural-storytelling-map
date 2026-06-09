from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.like_model import Like
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User
from app.schemas.like_schema import LikeStatusResponse, LikeToggleResponse
from app.security import decode_access_token

router = APIRouter()

# reuse the same token scheme but make it optional (no auto_error)
# so unauthenticated users can still read like counts
optional_oauth2 = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def get_optional_user(
    token: str = Depends(optional_oauth2),
    db: Session = Depends(get_db),
) -> User | None:
    """Return the logged-in user if a valid token is present, otherwise None."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except JWTError:
        return None


def _get_approved_story(story_id: int, db: Session) -> Story:
    """Shared helper — raises 404 if the story doesn't exist or isn't approved."""
    story = db.query(Story).filter(
        Story.id == story_id,
        Story.status == StoryStatus.APPROVED.value,
    ).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


# toggle like on a story — requires login
@router.post("/stories/{story_id}/like", response_model=LikeToggleResponse)
def toggle_like(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_approved_story(story_id, db)

    existing = db.query(Like).filter(
        Like.story_id == story_id,
        Like.user_id == current_user.id,
    ).first()

    try:
        if existing:
            # already liked — remove it (unlike)
            db.delete(existing)
            db.commit()
            liked = False
        else:
            # not yet liked — add it
            db.add(Like(story_id=story_id, user_id=current_user.id))
            db.commit()
            liked = True
    except (SQLAlchemyError, IntegrityError):
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update like")

    like_count = db.query(Like).filter(Like.story_id == story_id).count()
    return LikeToggleResponse(liked=liked, like_count=like_count)


# get like count for a story — public, but also shows if current user liked it
@router.get("/stories/{story_id}/likes", response_model=LikeStatusResponse)
def get_likes(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    _get_approved_story(story_id, db)

    like_count = db.query(Like).filter(Like.story_id == story_id).count()

    liked_by_me = False
    if current_user:
        liked_by_me = db.query(Like).filter(
            Like.story_id == story_id,
            Like.user_id == current_user.id,
        ).first() is not None

    return LikeStatusResponse(like_count=like_count, liked_by_me=liked_by_me)
