import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# loads variables from the .env file into the environment
load_dotenv()

# ── Password hashing ──────────────────────────────────────────────────────────

# tells passlib to use bcrypt as the hashing algorithm.
# bcrypt is slow by design — it makes brute-force attacks expensive.
# "deprecated='auto'" means older hash schemes are auto-upgraded on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Turn a plain-text password into a bcrypt hash for safe storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain-text password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT tokens ────────────────────────────────────────────────────────────────

# Secret key used to sign tokens — loaded from the .env file, never committed.
# Fail loudly at startup if it is missing, rather than silently using a weak default.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Copy backend/.env.example to backend/.env "
        "and set a SECRET_KEY value."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def create_access_token(user_id: int, is_admin: bool) -> str:
    """
    Build a signed JWT containing the user's id and admin flag.
    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),   # 'sub' (subject) is the standard JWT claim for user identity
        "is_admin": is_admin,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Verify the token signature and expiry, then return its payload.
    Raises JWTError if the token is invalid or expired.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
