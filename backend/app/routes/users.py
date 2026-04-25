from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse

router = APIRouter()


# registers a new user account
@router.post("/users/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # checks that email and username are not already taken
    existing = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if existing:
        if existing.email == user.email:
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=409, detail="Username already taken")

    # hashes the password before storing it
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create user")

    return new_user


# logs in an existing user by verifying their credentials
@router.post("/users/login", response_model=UserResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):

    # looks up the user by email
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch user")

    # returns the same vague error whether email or password is wrong (security best practice)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # prevents disabled accounts from logging in
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return user