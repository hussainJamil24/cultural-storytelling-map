from fastapi import APIRouter, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user_model import User

router = APIRouter()

# create DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    db = next(get_db())

    # check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"error": "Email already registered"}

    # create new user
    new_user = User(
        name=name,
        email=email,
        password=password  # later we hash this
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}