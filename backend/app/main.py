from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine
# imports story model so sqlalchemy registers the table before creation
from app.models import story_model
from app.routes import stories

# imports user routes (registration, authentication endpoints)
from app.routes import users
# imports user model so SQLAlchemy registers the users table
from app.models import user_model


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

# users registration
app.include_router(users.router)

# registers story routes after middleware setup
app.include_router(stories.router)
