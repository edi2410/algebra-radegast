from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import SessionDep
from app.models.user import User
from app.models.course_teacher import (
    CourseTeacher,
    CourseTeacherCreate,
    CourseTeacherRead,
    CourseTeacherUpdate
)
from app.services.auth_services import AuthService
from app.services.course_teacher_service import CourseTeacherService

router = APIRouter(
    prefix="/courses/{course_id}/teachers",
    tags=["course-teachers"]
)


@router.post("/", response_model=CourseTeacherRead, status_code=status.HTTP_201_CREATED)
def assign_teacher_to_course(
        course_id: int,
        teacher_data: CourseTeacherCreate,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
) -> CourseTeacherRead:
    """
    Assign teacher to course (only ADMIN)
    """
    assignment = CourseTeacherService.assign_teacher(
        session, course_id, teacher_data, current_user
    )

    # Fill response with teacher data
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


@router.get("/", response_model=List[CourseTeacherRead])
def get_course_teachers(
        course_id: int,
        session: SessionDep
) -> List[CourseTeacherRead]:
    """
    Fetch all teachers assigned to a course
    """
    assignments = CourseTeacherService.get_course_teachers(session, course_id)


    results = []
    for assignment in assignments:
        teacher = session.get(User, assignment.teacher_id)
        results.append(CourseTeacherRead(
            id=assignment.id,
            course_id=assignment.course_id,
            teacher_id=assignment.teacher_id,
            role=assignment.role,
            assigned_at=assignment.assigned_at,
            teacher_name=teacher.full_name if teacher else None,
            teacher_email=teacher.email if teacher else None
        ))

    return results


@router.delete("/{teacher_id}")
def remove_teacher_from_course(
        course_id: int,
        teacher_id: int,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
):
    """
    Remove teacher from course (only ADMIN)
    """
    return CourseTeacherService.remove_teacher(
        session, course_id, teacher_id, current_user
    )


@router.patch("/{teacher_id}", response_model=CourseTeacherRead)
def update_teacher_role(
        course_id: int,
        teacher_id: int,
        update_data: CourseTeacherUpdate,
        session: SessionDep,
        current_user: User = Depends(AuthService.require_admin)
) -> CourseTeacherRead:
    """
    Update teacher role in a course (only ADMIN)
    """
    if update_data.role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role is required"
        )

    assignment = CourseTeacherService.update_teacher_role(
        session, course_id, teacher_id, update_data.role, current_user
    )
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
