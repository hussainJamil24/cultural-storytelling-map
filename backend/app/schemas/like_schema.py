from pydantic import BaseModel


# data the client sends when liking or unliking a story
class LikeRequest(BaseModel):
    # id of the logged-in user performing the like
    user_id: int


# like state the api returns for a story
class LikeResponse(BaseModel):
    story_id: int
    # total number of likes on the story
    like_count: int
    # whether the requesting user currently likes the story
    liked: bool
