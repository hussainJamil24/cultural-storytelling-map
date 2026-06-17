from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

router = APIRouter()

class AIRequest(BaseModel):
    title: str
    content: str
    category: str


@router.post("/generate-video")
async def generate_video(data: AIRequest):

    # 🔥 Build prompt
    prompt = f"""
    Create a cinematic storytelling video about:
    Title: {data.title}
    Story: {data.content}
    Category: {data.category}

    Style: emotional, cultural, documentary style
    Include visuals, narration, and background music
    """

    print(prompt)

    # simulate waiting (replace with real API)
    time.sleep(5)

    # fake response (replace later)
    video_url = "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"

    return {
        "video_url": video_url
    }