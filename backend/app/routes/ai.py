import logging
import os
import re
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
import replicate

router = APIRouter()
logger = logging.getLogger(__name__)


class AIRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1, max_length=10000)
    category: str = Field(..., min_length=1, max_length=80)

    @field_validator("title", "content", "category", mode="before")
    @classmethod
    def strip_whitespace(cls, value):
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value).strip()
        return value


class CompanionCardRequest(AIRequest):
    pass


class CompanionCardResponse(BaseModel):
    short_summary: str
    themes: list[str]
    timeline: list[str]
    cultural_value: str
    respect_note: str
    safety_notice: str


class VideoGenerationResponse(BaseModel):
    video_url: str


def _clean_text(text: str, max_length: int = 10000) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned


def _extract_themes(category: str, content: str) -> list[str]:
    category_key = category.lower().strip()
    safe_theme_map = {
        "heritage": "heritage",
        "memory": "memory",
        "tradition": "tradition",
        "identity": "identity",
        "community": "community",
        "place": "place identity",
        "family": "family",
        "story": "storytelling",
        "culture": "culture",
        "art": "art",
        "language": "language",
        "nature": "nature",
        "music": "music",
        "food": "food",
        "migration": "migration",
        "religion": "religion",
        "landmarks": "landmarks",
        "oral_history": "oral history",
        "customs": "customs",
        "craft": "craft",
        "celebration": "celebration",
    }

    themes = []
    if category_key in safe_theme_map:
        themes.append(safe_theme_map[category_key])
    elif category_key:
        themes.append(category_key)

    words = re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
    added = set(themes)
    for word in words:
        if len(themes) >= 5:
            break
        if word in safe_theme_map:
            theme = safe_theme_map[word]
            if theme not in added:
                themes.append(theme)
                added.add(theme)

    if "memory" not in added and len(themes) < 5:
        if any(word in content.lower() for word in ["memory", "remember", "remembrance"]):
            themes.append("memory")
            added.add("memory")

    while len(themes) < 3:
        for fallback_theme in ["culture", "memory", "community"]:
            if fallback_theme not in added:
                themes.append(fallback_theme)
                added.add(fallback_theme)
                if len(themes) >= 3:
                    break

    return themes[:5]


def _generate_short_summary(content: str) -> str:
    content = content.strip()
    sentences = re.split(r"(?<=[.!?])\s+", content)
    if sentences and sentences[0]:
        summary = sentences[0]
    else:
        summary = content

    if len(summary) > 140:
        summary = summary[:137].rstrip() + "..."

    summary = re.sub(r"\s+", " ", summary).strip()
    return (
        summary
        or "A meaningful story that highlights cultural heritage and lived experience."
    )


def _generate_timeline() -> list[str]:
    return [
        "A memory or tradition is preserved from the past.",
        "The storyteller connects the memory to present identity.",
        "Sharing the story helps strengthen cultural visibility.",
    ]


def _generate_cultural_value(themes: list[str]) -> str:
    if "heritage" in themes or "memory" in themes:
        return "This story supports cultural inclusion by making personal and community memory more visible."
    return "This story supports cultural inclusion by highlighting shared meaning and cultural connection."


def _build_video_prompt(data: AIRequest) -> str:
    return (
        "Create a cinematic storytelling video about:\n"
        f"Title: {data.title}\n"
        f"Story: {data.content}\n"
        f"Category: {data.category}\n\n"
        "Style: emotional, cultural, documentary style.\n"
        "Include respectful visuals, narration, and background music."
    )


def _extract_video_url(output: Any) -> str | None:
    if isinstance(output, str):
        return output

    if isinstance(output, (list, tuple)):
        if not output:
            return None
        output = output[0]

    url = getattr(output, "url", None)
    if url:
        return str(url)

    if output:
        return str(output)

    return None


def generate_companion_card(title: str, content: str, category: str) -> CompanionCardResponse:
    clean_content = _clean_text(content, max_length=10000)
    clean_category = _clean_text(category, max_length=80)

    summary = _generate_short_summary(clean_content)
    themes = _extract_themes(clean_category, clean_content)
    timeline = _generate_timeline()
    cultural_value = _generate_cultural_value(themes)

    return CompanionCardResponse(
        short_summary=summary,
        themes=themes,
        timeline=timeline,
        cultural_value=cultural_value,
        respect_note=(
            "This AI companion card summarizes only the submitted story. "
            "The human story remains the source of truth."
        ),
        safety_notice="Generated card requires moderation before publication.",
    )


@router.post("/generate-companion-card", response_model=CompanionCardResponse)
async def generate_companion_card_endpoint(data: CompanionCardRequest):
    return generate_companion_card(data.title, data.content, data.category)


@router.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_video(data: AIRequest):
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI video generation is not configured.",
        )

    try:
        output = replicate.run(
            "lucataco/text-to-video",
            input={
                "prompt": _build_video_prompt(data),
                "num_frames": 24,
            },
        )
    except Exception as e:
        logger.exception("AI video generation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI video generation failed.",
        ) from e

    video_url = _extract_video_url(output)
    if not video_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI video generation did not return a video URL.",
        )

    return VideoGenerationResponse(video_url=video_url)
