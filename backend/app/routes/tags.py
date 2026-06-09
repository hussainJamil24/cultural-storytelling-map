from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_admin
from app.models.story_model import Story, StoryStatus
from app.models.tag_model import StoryTag, Tag
from app.models.user_model import User
from app.schemas.tag_schema import StoryTagAdd, TagCreate, TagResponse

router = APIRouter()


# ── Tag management (admin only) ───────────────────────────────────────────────

# create a new tag
@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    # normalise to lowercase so "Food" and "food" don't become two different tags
    name = body.name.strip().lower()

    if db.query(Tag).filter(Tag.name == name).first():
        raise HTTPException(status_code=409, detail="Tag already exists")

    try:
        tag = Tag(name=name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create tag")

    return tag


# list all available tags — public
@router.get("/tags", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).order_by(Tag.name).all()


# ── Story ↔ Tag assignment (admin only) ──────────────────────────────────────

# assign a tag to a story
@router.post("/stories/{story_id}/tags", response_model=list[TagResponse], status_code=status.HTTP_201_CREATED)
def add_tag_to_story(
    body: StoryTagAdd,
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    # story must exist (any status — admin can tag pending stories too)
    if not db.query(Story).filter(Story.id == story_id).first():
        raise HTTPException(status_code=404, detail="Story not found")

    if not db.query(Tag).filter(Tag.id == body.tag_id).first():
        raise HTTPException(status_code=404, detail="Tag not found")

    # silently ignore if already tagged
    already = db.query(StoryTag).filter(
        StoryTag.story_id == story_id,
        StoryTag.tag_id == body.tag_id,
    ).first()

    if not already:
        try:
            db.add(StoryTag(story_id=story_id, tag_id=body.tag_id))
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Could not add tag")

    return _get_story_tags(story_id, db)


# remove a tag from a story
@router.delete("/stories/{story_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_story(
    story_id: int = Path(..., gt=0),
    tag_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    story_tag = db.query(StoryTag).filter(
        StoryTag.story_id == story_id,
        StoryTag.tag_id == tag_id,
    ).first()

    if not story_tag:
        raise HTTPException(status_code=404, detail="Tag not assigned to this story")

    try:
        db.delete(story_tag)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not remove tag")


# ── Public read ───────────────────────────────────────────────────────────────

# get all tags for a story — public
@router.get("/stories/{story_id}/tags", response_model=list[TagResponse])
def get_story_tags(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    if not db.query(Story).filter(
        Story.id == story_id,
        Story.status == StoryStatus.APPROVED.value,
    ).first():
        raise HTTPException(status_code=404, detail="Story not found")

    return _get_story_tags(story_id, db)


# get all stories that have a specific tag — public
@router.get("/tags/{tag_id}/stories")
def get_stories_by_tag(
    tag_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    if not db.query(Tag).filter(Tag.id == tag_id).first():
        raise HTTPException(status_code=404, detail="Tag not found")

    story_ids = [
        row.story_id for row in
        db.query(StoryTag).filter(StoryTag.tag_id == tag_id).all()
    ]

    return db.query(Story).filter(
        Story.id.in_(story_ids),
        Story.status == StoryStatus.APPROVED.value,
    ).all()


# ── Internal helper ───────────────────────────────────────────────────────────

def _get_story_tags(story_id: int, db: Session) -> list[Tag]:
    tag_ids = [
        row.tag_id for row in
        db.query(StoryTag).filter(StoryTag.story_id == story_id).all()
    ]
    return db.query(Tag).filter(Tag.id.in_(tag_ids)).order_by(Tag.name).all()
