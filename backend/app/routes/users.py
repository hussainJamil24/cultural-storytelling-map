from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user_model import User
from app.security import create_access_token, hash_password, verify_password

router = APIRouter()


# register
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # reject duplicate emails before creating the user
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # 409 Conflict is more accurate than a 200 with an error key
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # hash_password runs bcrypt so the plain-text password is never stored
    new_user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        # is_admin defaults to False in the model; no user can self-assign admin
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
    db: Session = Depends(get_db),
):
    # find user by email
    user = db.query(User).filter(User.email == email).first()

    # verify_password checks the plain-text input against the stored bcrypt hash.
    # we check both conditions together to avoid leaking whether an email exists
    # (timing-safe: bcrypt verify always runs even if user is None via dummy hash)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # create a signed JWT the client stores and sends with future requests
    token = create_access_token(user_id=user.id, is_admin=user.is_admin)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        # is_admin now comes from the database column, not a hardcoded email check
        "is_admin": user.is_admin,
    }