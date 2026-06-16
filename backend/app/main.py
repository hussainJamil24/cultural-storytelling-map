from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.session import init_db
# imports story model so sqlalchemy registers the table before creation
from app.models import story_model
from app.routes import stories
from app.routes import comments

# imports user routes (registration, authentication endpoints)
from app.routes import users
# imports user model so SQLAlchemy registers the users table
from app.models import user_model
# imports comment model so SQLAlchemy registers the comments table
from app.models import comment_model


# creates database tables from the registered models
init_db()

# creates the main fastapi application
app = FastAPI()

# adds cors middleware before routes are registered
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allows the local frontend during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


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
