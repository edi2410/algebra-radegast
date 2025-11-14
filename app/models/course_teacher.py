from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship

from app.enum.teacher_role_enum import TeacherRole

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class CourseTeacherBase(SQLModel):
    course_id: int = Field(foreign_key="course.id")
    teacher_id: int = Field(foreign_key="user.id")
    role: TeacherRole = Field(default=TeacherRole.ASSISTANT)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class CourseTeacher(CourseTeacherBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    course: Optional["Course"] = Relationship(back_populates="teachers")
    teacher: Optional["User"] = Relationship(back_populates="courses_teaching")


class CourseTeacherCreate(SQLModel):
    teacher_id: int
    role: TeacherRole = Field(default=TeacherRole.ASSISTANT)


class CourseTeacherRead(CourseTeacherBase):
    id: int
    teacher_name: Optional[str] = None
    teacher_email: Optional[str] = None


class CourseTeacherUpdate(SQLModel):
    role: Optional[TeacherRole] = None