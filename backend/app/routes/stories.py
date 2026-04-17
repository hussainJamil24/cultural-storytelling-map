from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter()

# Temporary storage (in memory)
stories = []

@router.post("/stories")
async def create_story(
    title: str = Form(...),
    narrative: str = Form(None),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    story = {
        "id": len(stories) + 1,
        "title": title,
        "narrative": narrative,
        "location": {
            "lat": lat,
            "lng": lng
        },
        "image": image.filename if image else None,
        "audio": audio.filename if audio else None
    }

    stories.append(story)

    return {"message": "Story created", "story": story}


@router.get("/stories")
def get_stories():
    return stories