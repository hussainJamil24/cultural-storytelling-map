from fastapi import APIRouter, Form, Depends
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

# register
@router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # db = next(get_db())

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

# login
@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # db = next(get_db())

    # find user by email
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "User not found"}

    if user.password != password:
        return {"error": "Incorrect password"}

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }