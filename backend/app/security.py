from passlib.context import CryptContext

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
