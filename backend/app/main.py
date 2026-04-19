from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine
# imports story model before table creation
from app.models import story_model
from app.routes import stories


# creates database tables from models
Base.metadata.create_all(bind=engine)

# main fastapi application
app = FastAPI()

# CORS MUST come BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # better than "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# basic health check route
@app.get("/")
def root():
    return {"message": "API is working"}


# include routes AFTER middleware
app.include_router(stories.router)
