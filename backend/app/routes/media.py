from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/media", tags=["media"])

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_PREFIXES = ("image/", "audio/")
ALLOWED_SUFFIXES = {
    ".apng",
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".mp3",
    ".ogg",
    ".opus",
    ".png",
    ".svg",
    ".wav",
    ".webp",
}


class MediaUploadResponse(BaseModel):
    media_url: str
    filename: str
    content_type: str


def _validate_upload(file: UploadFile) -> str:
    content_type = file.content_type or ""
    if not content_type.startswith(ALLOWED_PREFIXES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image and audio uploads are allowed.",
        )

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type.",
        )

    return suffix


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
):
    suffix = _validate_upload(file)
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file must be 10 MB or smaller.",
        )

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}{suffix}"
    upload_path = UPLOADS_DIR / stored_filename
    upload_path.write_bytes(content)

    return MediaUploadResponse(
        media_url=str(request.url_for("uploads", path=stored_filename)),
        filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
    )
