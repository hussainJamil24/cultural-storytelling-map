import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core import ai_client
from app.core.dependencies import get_current_user, get_optional_current_user, require_admin
from app.db.session import get_db
from app.models.story_model import Story, StoryCategory, StoryStatus, StoryTranslation
from app.models.user_model import User, UserRole
from app.schemas.story_schema import (
    StoryCreate,
    StoryLocationResponse,
    StoryPrivateResponse,
    StoryPublicResponse,
    StoryStatusUpdate,
    StoryTranslationResponse,
)

router = APIRouter(tags=["stories"])
logger = logging.getLogger(__name__)

SUPPORTED_TRANSLATION_LANGUAGES = {"el", "tr"}

# Human moderation is the default and is required for the demonstration.
AUTO_APPROVE_NEW_STORIES = os.getenv("NARRIFY_AUTO_APPROVE", "false").lower() == "true"


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
        image_url=story.image_url,
        audio_url=story.audio_url,
        latitude=story.latitude,
        longitude=story.longitude,
        status=(
            StoryStatus.APPROVED.value
            if AUTO_APPROVE_NEW_STORIES
            else StoryStatus.PENDING.value
        ),
        category=story.category.value,
        is_anonymous=story.is_anonymous,
    )

    # AI moderation assist: best-effort only. A failure here (no API key, network
    # error, etc.) must never block a story submission -- it just leaves the story
    # unassessed for the human moderator, same as before this feature existed.
    try:
        assessment = ai_client.assess_story_sensitivity(story.title, story.content)
        if assessment is not None:
            new_story.ai_flag = assessment.flagged
            new_story.ai_flag_reason = assessment.reason
    except Exception:
        logger.exception("AI moderation assist raised unexpectedly during story creation")

    try:
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save story")

    return new_story


@router.get("/stories")
def get_stories(
    status: StoryStatus | None = Query(None),
    category: StoryCategory | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    # only an admin querying a non-public status sees moderation-only fields
    # (ai_flag / ai_flag_reason / user_id) -- everyone else gets the public shape
    is_moderation_view = status is not None and status != StoryStatus.APPROVED
    if is_moderation_view:
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

        stories = query.order_by(Story.created_at.desc()).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch stories")

    schema = StoryPrivateResponse if is_moderation_view else StoryPublicResponse
    return [schema.model_validate(story) for story in stories]


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


@router.get(
    "/stories/{story_id}/translate/{language}",
    response_model=StoryTranslationResponse,
)
def translate_story(
    story_id: int = Path(..., gt=0),
    language: str = Path(...),
    db: Session = Depends(get_db),
):
    if language not in SUPPORTED_TRANSLATION_LANGUAGES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language. Choose one of: {sorted(SUPPORTED_TRANSLATION_LANGUAGES)}",
        )

    try:
        story = (
            db.query(Story)
            .filter(Story.id == story_id, Story.status == StoryStatus.APPROVED.value)
            .first()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch story")

    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    # serve the cached translation if we've already paid for one
    try:
        cached = (
            db.query(StoryTranslation)
            .filter(
                StoryTranslation.story_id == story_id,
                StoryTranslation.language == language,
            )
            .first()
        )
    except SQLAlchemyError:
        cached = None

    if cached is not None:
        return StoryTranslationResponse(
            language=language, title=cached.title, content=cached.content, cached=True
        )

    if not ai_client.is_configured():
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI translation is not configured.",
        )

    result = ai_client.translate_story(story.title, story.content, language)
    if result is None:
        raise HTTPException(
            status_code=http_status.HTTP_502_BAD_GATEWAY,
            detail="AI translation failed. Please try again.",
        )

    translation = StoryTranslation(
        story_id=story_id, language=language, title=result.title, content=result.content
    )
    try:
        db.add(translation)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        # translation still succeeded -- serve it even if caching failed
        logger.exception("Failed to cache translation for story %s (%s)", story_id, language)

    return StoryTranslationResponse(
        language=language, title=result.title, content=result.content, cached=False
    )


@router.get("/stories/{story_id}/locate", response_model=StoryLocationResponse)
def locate_story(
    story_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    try:
        story = (
            db.query(Story)
            .filter(Story.id == story_id, Story.status == StoryStatus.APPROVED.value)
            .first()
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch story")

    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    if story.ai_location_label:
        return StoryLocationResponse(label=story.ai_location_label, cached=True)

    if not ai_client.is_configured():
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI location lookup is not configured.",
        )

    result = ai_client.describe_location(story.latitude, story.longitude)
    if result is None:
        raise HTTPException(
            status_code=http_status.HTTP_502_BAD_GATEWAY,
            detail="Could not describe this location. Please try again.",
        )

    try:
        story.ai_location_label = result.label
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        # label still succeeded -- serve it even if caching failed
        logger.exception("Failed to cache location label for story %s", story_id)

    return StoryLocationResponse(label=result.label, cached=False)
