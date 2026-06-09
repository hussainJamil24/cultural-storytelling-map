from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.comment_model import Comment
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User
from app.schemas.comment_schema import CommentCreate, CommentResponse

router = APIRouter()


# post a comment on a story — requires login
@router.post(
    "/stories/{story_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    body: CommentCreate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # only allow comments on approved stories
    story = db.query(Story).filter(
        Story.id == story_id,
        Story.status == StoryStatus.APPROVED.value,
    ).first()

    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        comment = Comment(
            story_id=story_id,
            user_id=current_user.id,
            content=body.content.strip(),
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save comment")

    # attach author name for the response
    comment.author_name = current_user.name
    return comment


# get all comments for a story — public
@router.get("/stories/{story_id}/comments", response_model=list[CommentResponse])
def get_comments(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    story = db.query(Story).filter(
        Story.id == story_id,
        Story.status == StoryStatus.APPROVED.value,
    ).first()

    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        # join with users so we can return the author name in one query
        results = (
            db.query(Comment, User.name)
            .join(User, Comment.user_id == User.id)
            .filter(Comment.story_id == story_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch comments")

    # stitch author_name onto each comment object before returning
    comments = []
    for comment, author_name in results:
        comment.author_name = author_name
        comments.append(comment)

    return comments


# delete a comment — only the author can delete their own comment
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    # prevent users from deleting other people's comments
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    try:
        db.delete(comment)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete comment")
