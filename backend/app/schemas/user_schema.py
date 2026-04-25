from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# shared user fields used across schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # pydantic validates email format automatically

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("username must not be empty")
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError("username may only contain letters, numbers, - and _")
        return value


# data the client sends when registering
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("password must contain at least one digit")
        return value


# data the client sends when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# data the api returns — never includes the password
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)