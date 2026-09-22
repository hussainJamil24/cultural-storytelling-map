import json
import logging
import os
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Gemini has a genuinely free tier (no credit card required) via a key generated
# at https://aistudio.google.com/apikey -- see backend/.env.example.
# Using the "lite" tier deliberately: the full "flash" model returned persistent
# 503 "high demand" errors on this free-tier key during testing, while "flash-lite"
# was reliable -- likely better free-tier capacity/priority.
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

_client = None
_client_checked = False


def _get_client():
    """Lazily builds the Gemini client. Returns None if no API key is configured
    so every caller can fall back gracefully instead of crashing the request."""
    global _client, _client_checked
    if _client_checked:
        return _client

    _client_checked = True
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai

        _client = genai.Client(api_key=api_key)
    except Exception:
        logger.exception("Failed to initialize Gemini client")
        _client = None

    return _client


def is_configured() -> bool:
    return _get_client() is not None


T = TypeVar("T", bound=BaseModel)


def _generate_json(
    system_instruction: str, prompt: str, schema_model: Type[T], max_output_tokens: int
) -> Optional[T]:
    """Shared helper: calls Gemini with a JSON schema constraint and validates the
    result against schema_model. Returns None on any failure -- missing key,
    network error, malformed output -- so callers always have a clean fallback path."""
    client = _get_client()
    if client is None:
        return None

    try:
        from google.genai import types

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_json_schema=schema_model.model_json_schema(),
                max_output_tokens=max_output_tokens,
            ),
        )
        data = json.loads(response.text)
        return schema_model.model_validate(data)
    except Exception:
        logger.exception("Gemini call failed")
        return None


class CompanionCardFields(BaseModel):
    short_summary: str
    themes: list[str]
    timeline: list[str]
    cultural_value: str


def generate_companion_card_ai(
    title: str, content: str, category: str
) -> Optional[CompanionCardFields]:
    """Real LLM-generated companion card. Returns None on any failure so the
    caller can fall back to the deterministic heuristic version."""
    return _generate_json(
        system_instruction=(
            "You write short, respectful 'companion cards' for cultural heritage "
            "stories submitted to a community storytelling map. Read the story and "
            "produce a factual, warm summary grounded only in what the story actually "
            "says -- never invent details that aren't there. "
            "themes: 3-5 short lowercase theme words. "
            "timeline: 2-4 short present-tense steps describing the story's narrative arc. "
            "cultural_value: one sentence on why this story matters for cultural "
            "visibility and inclusion."
        ),
        prompt=f"Category: {category}\nTitle: {title}\n\nStory:\n{content}",
        schema_model=CompanionCardFields,
        max_output_tokens=1500,
    )


class SensitivityAssessment(BaseModel):
    flagged: bool
    severity: str  # none | low | medium | high
    reason: str


def assess_story_sensitivity(title: str, content: str) -> Optional[SensitivityAssessment]:
    """Lightweight moderation assist: surfaces a flag + reason for the human moderator.
    Never blocks story creation -- returns None on any failure so callers treat it as
    'not assessed' rather than an error."""
    return _generate_json(
        system_instruction=(
            "You assist human moderators on a cultural storytelling platform for "
            "minority and underrepresented communities. Read the submitted story and "
            "flag it ONLY if it contains hate speech, harassment, explicit content, "
            "personal attacks, or content that demeans a cultural, ethnic, or religious "
            "group. Do NOT flag a story merely for describing difficult history, "
            "discrimination the author experienced, war, migration, or loss -- those are "
            "exactly the stories this platform exists to preserve. When in doubt, do not "
            "flag. A human moderator makes the final call either way; your job is only to "
            "surface something a busy moderator might miss. Keep 'reason' to one short "
            "sentence, and set it to 'No concerns detected.' when flagged is false."
        ),
        prompt=f"Title: {title}\n\nStory:\n{content}",
        schema_model=SensitivityAssessment,
        max_output_tokens=800,
    )


class TranslationFields(BaseModel):
    title: str
    content: str


LANGUAGE_NAMES = {"el": "Greek", "tr": "Turkish", "en": "English"}


def translate_story(title: str, content: str, target_lang: str) -> Optional[TranslationFields]:
    """Translates a story's title and content into the target language. Returns None
    if AI translation isn't configured or the call fails -- there's no sane heuristic
    fallback for translation, so callers should surface a clear error instead."""
    language_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    return _generate_json(
        system_instruction=(
            f"Translate the given story title and content into natural, fluent "
            f"{language_name}. Preserve the tone, meaning, and cultural nuance of the "
            "original as closely as possible. Do not summarize, shorten, or add "
            "commentary -- translate faithfully in full."
        ),
        prompt=f"Title: {title}\n\nContent:\n{content}",
        schema_model=TranslationFields,
        max_output_tokens=8192,
    )


class LocationLabelFields(BaseModel):
    label: str


def describe_location(latitude: float, longitude: float) -> Optional[LocationLabelFields]:
    """Turns raw GPS coordinates into a short, human-readable place description
    (e.g. 'Old Town, Nicosia') using Gemini's general geographic knowledge --
    not a geocoding lookup, so treat it as an approximate, friendly label rather
    than an authoritative address. Returns None on any failure."""
    return _generate_json(
        system_instruction=(
            "Given GPS coordinates, write a short, natural, human-friendly "
            "description of the nearest notable town, neighbourhood, or area -- "
            "like a caption under a photo, not a technical address. Maximum 6 "
            "words. If you are not confident, give your best general-area guess "
            "rather than refusing."
        ),
        prompt=f"Latitude: {latitude}\nLongitude: {longitude}",
        schema_model=LocationLabelFields,
        max_output_tokens=200,
    )
