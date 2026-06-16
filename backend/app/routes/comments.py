from fastapi import APIRouter, Depends, HTTPException, Path, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.comment_model import Comment
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User, UserRole
from app.schemas.comment_schema import CommentCreate, CommentResponse

router = APIRouter()


def _get_approved_story(db: Session, story_id: int) -> Story:
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


def _serialize_comment(comment: Comment, author_name: str) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        story_id=comment.story_id,
        user_id=comment.user_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
        author_name=author_name,
    )


@router.post(
    "/stories/{story_id}/comments",
    response_model=CommentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_comment(
    comment: CommentCreate,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_approved_story(db, story_id)

    if comment.parent_id is not None:
        parent = (
            db.query(Comment)
            .filter(
                Comment.id == comment.parent_id,
                Comment.story_id == story_id,
            )
            .first()
        )
        if parent is None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Parent comment not found on this story",
            )

    new_comment = Comment(
        story_id=story_id,
        user_id=current_user.id,
        parent_id=comment.parent_id,
        content=comment.content,
    )

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save comment")

    return _serialize_comment(new_comment, current_user.name)


@router.get("/stories/{story_id}/comments", response_model=list[CommentResponse])
def list_comments(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    _get_approved_story(db, story_id)

    try:
        rows = (
            db.query(Comment, User.name)
            .join(User, Comment.user_id == User.id)
            .filter(Comment.story_id == story_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch comments")

    return [_serialize_comment(comment, author_name) for comment, author_name in rows]


@router.delete("/comments/{comment_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch comment")

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    is_owner = comment.user_id == current_user.id
    is_moderator = current_user.role in (UserRole.ADMIN.value, UserRole.MODERATOR.value)
    if not is_owner and not is_moderator:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this comment",
        )

    try:
        # reattach any replies to the deleted comment's parent so they aren't orphaned
        db.query(Comment).filter(Comment.parent_id == comment.id).update(
            {Comment.parent_id: comment.parent_id}, synchronize_session=False
        )
        db.delete(comment)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete comment")

    return None
