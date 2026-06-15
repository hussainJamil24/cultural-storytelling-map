from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user_model import User
from app.security import hash_password, verify_password

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

    # create new user with a hashed password
    new_user = User(
        name=name,
        email=email,
        password=hash_password(password)
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

    if not verify_password(password, user.password):
        return {"error": "Incorrect password"}
    
    # only this email is admin
    is_admin = user.email == "admin@gmail.com"

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "is_admin": is_admin
    }