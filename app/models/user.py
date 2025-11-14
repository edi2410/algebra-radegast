from enum import Enum
from typing import Optional, TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.course_teacher import CourseTeacher




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

    courses_teaching: List["CourseTeacher"] = Relationship(back_populates="teacher")


class UserRead(UserBase):
    id: int