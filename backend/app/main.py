from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stories

app = FastAPI()

# CORS MUST come BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # better than "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is working"}

# include routes AFTER middleware
app.include_router(stories.router)