from pydantic import BaseModel


class LikeStatusResponse(BaseModel):
    story_id: int
    count: int
    liked: bool
