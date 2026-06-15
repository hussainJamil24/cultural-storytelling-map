from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import stories

# imports user routes (registration, authentication endpoints)
from app.routes import users

# imports category routes (list of story categories)
from app.routes import categories

# imports comment routes (story comments)
from app.routes import comments


# database schema is managed by Alembic migrations (run "alembic upgrade head"),
# so the app no longer creates tables on startup.

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


# returns a basic health check response
@app.get("/")
def root():
    return {"message": "API is working"}

# users registration
app.include_router(users.router)

# registers story routes after middleware setup
app.include_router(stories.router)

# registers category routes
app.include_router(categories.router)

# registers comment routes
app.include_router(comments.router)
