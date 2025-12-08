from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from typing import List, Annotated
from app.core.metrics import course_operations, active_courses, track_endpoint_metrics
from app.core.db import SessionDep
from app.models.course import Course, CourseRead, CourseCreate
from app.models.user import User
from app.services.auth_services import AuthService

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)



@router.get("/", response_model=List[CourseRead])
@track_endpoint_metrics("courses_list")
def list_courses(session: SessionDep) -> List[Course]:
    try:
        courses = session.exec(select(Course)).all()
        course_operations.labels(operation='list', status='success').inc()

        # Update active courses gauge
        count = session.exec(select(func.count(Course.id))).one()
        active_courses.set(count)

        return courses
    except Exception as e:
        course_operations.labels(operation='list', status='failed').inc()
        raise


@router.post("/", response_model=CourseRead)
@track_endpoint_metrics("courses_create")
def create_course(
        course_in: CourseCreate,
        session: SessionDep,
        current_user: Annotated[User, Depends(AuthService.require_admin)]
) -> Course:
    try:
        course = Course(**course_in.model_dump())
        session.add(course)
        session.commit()
        session.refresh(course)

        course_operations.labels(operation='create', status='success').inc()
        active_courses.inc()

        return course
    except Exception as e:
        course_operations.labels(operation='create', status='failed').inc()
        raise


@router.delete("/{course_id}")
@track_endpoint_metrics("courses_delete")
def delete_course(
        course_id: int,
        session: SessionDep,
        current_user: Annotated[User, Depends(AuthService.require_admin)]
):
    try:
        course = session.get(Course, course_id)
        if not course:
            course_operations.labels(operation='delete', status='not_found').inc()
            raise HTTPException(status_code=404, detail="Course not found")

        session.delete(course)
        session.commit()

        course_operations.labels(operation='delete', status='success').inc()
        active_courses.dec()

        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        course_operations.labels(operation='delete', status='failed').inc()
        raise