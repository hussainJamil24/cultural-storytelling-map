from fastapi import APIRouter, Depends, HTTPException, Path, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.comment_model import Comment
from app.models.story_model import Story
from app.models.user_model import User
from app.schemas.comment_schema import CommentCreate, CommentResponse

# registers comment api routes
router = APIRouter()


# returns all comments for a story, oldest first
@router.get("/stories/{story_id}/comments", response_model=list[CommentResponse])
def get_comments(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    # returns 404 when the story does not exist
    if db.query(Story.id).filter(Story.id == story_id).first() is None:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        return (
            db.query(Comment)
            .filter(Comment.story_id == story_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch comments")


# posts a new comment on a story
@router.post(
    "/stories/{story_id}/comments",
    response_model=CommentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_comment(
    comment: CommentCreate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    # rejects comments on a story that does not exist
    if db.query(Story.id).filter(Story.id == story_id).first() is None:
        raise HTTPException(status_code=404, detail="Story not found")

    # rejects comments from an unknown author
    if db.query(User.id).filter(User.id == comment.user_id).first() is None:
        raise HTTPException(status_code=400, detail="Invalid user")

    new_comment = Comment(
        story_id=story_id,
        user_id=comment.user_id,
        content=comment.content,
    )

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save comment")

    return new_comment
