from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import SessionDep
from app.models.user import User
from app.models.course_teacher import (
    CourseTeacherCreate,
    CourseTeacherRead,
    CourseTeacherUpdate
)

from app.core.metrics import teacher_assignments, teachers_per_course, track_endpoint_metrics
from app.services.auth_services import AuthService
from app.services.course_teacher_service import CourseTeacherService

router = APIRouter(
    prefix="/courses/{course_id}/teachers",
    tags=["course-teachers"]
)



@router.post("/", response_model=CourseTeacherRead, status_code=status.HTTP_201_CREATED)
@track_endpoint_metrics("course_teacher_assign")
def assign_teacher_to_course(
        course_id: int,
        teacher_data: CourseTeacherCreate,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
) -> CourseTeacherRead:
    try:
        assignment = CourseTeacherService.assign_teacher(
            session, course_id, teacher_data, current_user
        )

        teacher_assignments.labels(operation='assign', status='success').inc()

        # Track teachers per course
        teacher_count = len(CourseTeacherService.get_course_teachers(session, course_id))
        teachers_per_course.observe(teacher_count)

        teacher = session.get(User, assignment.teacher_id)
        result = CourseTeacherRead(
            id=assignment.id,
            course_id=assignment.course_id,
            teacher_id=assignment.teacher_id,
            role=assignment.role,
            assigned_at=assignment.assigned_at,
            teacher_name=teacher.full_name if teacher else None,
            teacher_email=teacher.email if teacher else None
        )
        return result
    except Exception as e:
        teacher_assignments.labels(operation='assign', status='failed').inc()
        raise


@router.delete("/{teacher_id}")
@track_endpoint_metrics("course_teacher_remove")
def remove_teacher_from_course(
        course_id: int,
        teacher_id: int,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
):
    try:
        result = CourseTeacherService.remove_teacher(
            session, course_id, teacher_id, current_user
        )
        teacher_assignments.labels(operation='remove', status='success').inc()
        return result
    except Exception as e:
        teacher_assignments.labels(operation='remove', status='failed').inc()
        raise


@router.patch("/{teacher_id}", response_model=CourseTeacherRead)
@track_endpoint_metrics("course_teacher_update")
def update_teacher_role(
        course_id: int,
        teacher_id: int,
        update_data: CourseTeacherUpdate,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
) -> CourseTeacherRead:
    try:
        if update_data.role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role is required"
            )

        assignment = CourseTeacherService.update_teacher_role(
            session, course_id, teacher_id, update_data.role, current_user
        )

        teacher_assignments.labels(operation='update', status='success').inc()

        teacher = session.get(User, assignment.teacher_id)
        return CourseTeacherRead(
            id=assignment.id,
            course_id=assignment.course_id,
            teacher_id=assignment.teacher_id,
            role=assignment.role,
            assigned_at=assignment.assigned_at,
            teacher_name=teacher.full_name if teacher else None,
            teacher_email=teacher.email if teacher else None
        )
    except Exception as e:
        teacher_assignments.labels(operation='update', status='failed').inc()
        raise