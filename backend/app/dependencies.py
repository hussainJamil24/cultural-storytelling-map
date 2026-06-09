from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user_model import User
from app.security import decode_access_token

# tells FastAPI where clients send their token (POST /login returns it).
# routes that declare `Depends(oauth2_scheme)` will require an Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT from the Authorization header and return the matching User.
    Raises 401 if the token is missing, expired, or tampered with.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_error

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Extends get_current_user — additionally requires the user to be an admin.
    Raises 403 Forbidden if they are logged in but not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
