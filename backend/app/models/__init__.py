# imports all models so SQLAlchemy registers every table and resolves
# relationships (e.g. Story.media -> Media) whenever app.models is loaded
from app.models.user_model import User  # noqa: F401
from app.models.story_model import Story, StoryStatus  # noqa: F401
from app.models.media_model import Media, MediaType  # noqa: F401
from app.models.category_model import Category  # noqa: F401
from app.models.comment_model import Comment  # noqa: F401
