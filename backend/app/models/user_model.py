from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.session import Base


# role values to distinguish regular users from moderators/admins
class UserRole(str):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


# user table for registered accounts
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # core identity fields
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)

    # stores a bcrypt hash, never the raw password
    hashed_password = Column(String, nullable=False)

    # role controls what the user is allowed to do
    role = Column(String, nullable=False, default=UserRole.USER)

    # soft disable without deleting the account
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)