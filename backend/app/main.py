from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine
from app.models import comment_model, story_model, user_model
from app.routes import comments, stories, users


# creates database tables from the registered models
Base.metadata.create_all(bind=engine)

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

app.include_router(users.router)
app.include_router(stories.router)
app.include_router(comments.router)
