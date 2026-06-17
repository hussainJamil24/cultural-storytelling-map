from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.db.session import init_db
# imports story model so sqlalchemy registers the table before creation
from app.models import story_model
from app.routes import stories
from app.routes import comments
from app.routes import likes
from app.routes import media

from fastapi.staticfiles import StaticFiles


# imports user routes (registration, authentication endpoints)
from app.routes import users
# imports user model so SQLAlchemy registers the users table
from app.models import user_model
# imports comment model so SQLAlchemy registers the comments table
from app.models import comment_model
# imports like model so SQLAlchemy registers the likes table
from app.models import like_model


# creates database tables from the registered models
init_db()

# creates the main fastapi application
app = FastAPI()
UPLOADS_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# adds cors middleware before routes are registered
app.add_middleware(
    CORSMiddleware,
    # allows the local frontend during development, including CRA fallback ports
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


# mount uploads AFTER app exists
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# returns a basic health check response
@app.get("/")
def root():
    return {"message": "API is working"}

# users registration
app.include_router(users.router)

# registers story routes after middleware setup
app.include_router(stories.router)

# registers comment routes
app.include_router(comments.router)

# registers like routes
app.include_router(likes.router)

# registers media upload routes
app.include_router(media.router)

from app.routes import ai

app.include_router(ai.router, prefix="/ai", tags=["AI"])

