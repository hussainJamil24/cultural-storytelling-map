from passlib.context import CryptContext

# password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# returns a bcrypt hash for a plaintext password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# checks a plaintext password against a stored bcrypt hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
