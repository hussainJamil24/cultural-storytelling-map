from fastapi import APIRouter
from pydantic import BaseModel
import replicate
import os

router = APIRouter()

class AIRequest(BaseModel):
    title: str
    content: str
    category: str


@router.post("/generate-video")
async def generate_video(data: AIRequest):

    prompt = f"""
    Create a cinematic storytelling video about:
    Title: {data.title}
    Story: {data.content}
    Category: {data.category}

    Style: emotional, cultural, documentary style
    Include visuals, narration, and background music
    """

    try:
        output = replicate.run(
            "lucataco/text-to-video",
            input={
                "prompt": prompt,
                "num_frames": 24
            }
        )

        video_url = output[0]  # ✅ REAL URL

        return {
            "video_url": video_url
        }

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "video_url": None,
            "error": "AI generation failed"
        }