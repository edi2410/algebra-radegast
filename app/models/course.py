from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.enum.course_status_enum import CourseStatus

class CourseBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: CourseStatus = Field(default=CourseStatus.DRAFT)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: Optional[int] = Field(default=None, foreign_key="user.id")

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int
    teacher_id: Optional[int] = None

class CourseUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CourseStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None