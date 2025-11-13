from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List, Annotated

from app.core.db import SessionDep
from app.models.course import Course, CourseRead, CourseCreate, CourseUpdate
from app.models.user import User
from app.services.auth_services import AuthService

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)


@router.get("/", response_model=List[CourseRead])
def list_courses(session: SessionDep) -> List[Course]:
    return session.exec(select(Course)).all()


@router.post("/", response_model=CourseRead)
def create_course(
        course_in: CourseCreate,
        session: SessionDep,
        current_user: Annotated[User, Depends(AuthService.require_creator_or_admin)]
) -> Course:
    course = Course(**course_in.model_dump(), teacher_id=current_user.id)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, session: SessionDep) -> Course:
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
        course_id: int,
        course_in: CourseUpdate,
        session: SessionDep,
        current_user: Annotated[User, Depends(AuthService.require_creator_or_admin)]
) -> Course:
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own courses.")
    for field, value in course_in.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}")
def delete_course(course_id: int, session: SessionDep,
                  current_user: Annotated[User, Depends(AuthService.require_creator_or_admin)]):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own courses.")
    session.delete(course)
    session.commit()
    return {"ok": True}
