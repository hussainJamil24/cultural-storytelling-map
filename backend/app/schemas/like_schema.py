from pydantic import BaseModel


# returned after a like or unlike action
class LikeToggleResponse(BaseModel):
    liked: bool        # True = just liked, False = just unliked
    like_count: int    # updated total for the story


# returned when fetching like status for a story
class LikeStatusResponse(BaseModel):
    like_count: int
    liked_by_me: bool  # False if the request comes from a non-logged-in user
