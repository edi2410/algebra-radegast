from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field




# Define roles as Enum
class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    GUEST = "guest"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: Role = Field(default=Role.GUEST)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

class UserRead(UserBase):
    id: int