from typing import List
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.course_teacher import CourseTeacher, CourseTeacherCreate
from app.models.course import Course
from app.models.user import User
from app.enum.teacher_role_enum import TeacherRole


class CourseTeacherService:

    @staticmethod
    def assign_teacher(
            session: Session,
            course_id: int,
            teacher_data: CourseTeacherCreate,
            current_user: User
    ) -> CourseTeacher:
        """Assign teacher to course"""

        # Check if course exists
        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check if teacher exists
        teacher = session.get(User, teacher_data.teacher_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        existing = session.exec(
            select(CourseTeacher)
            .where(CourseTeacher.course_id == course_id)
            .where(CourseTeacher.teacher_id == teacher_data.teacher_id)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher is already assigned to this course"
            )

        # Create assignment
        course_teacher = CourseTeacher(
            course_id=course_id,
            teacher_id=teacher_data.teacher_id,
            role=teacher_data.role
        )
        session.add(course_teacher)
        session.commit()
        session.refresh(course_teacher)
        return course_teacher

    @staticmethod
    def get_course_teachers(session: Session, course_id: int) -> List[CourseTeacher]:
        """Get all teachers assigned to a course"""
        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        statement = select(CourseTeacher).where(CourseTeacher.course_id == course_id)
        return list(session.exec(statement).all())

    @staticmethod
    def remove_teacher(
            session: Session,
            course_id: int,
            teacher_id: int,
            current_user: User
    ) -> dict:
        # Check if course exists
        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Find assignment
        assignment = session.exec(
            select(CourseTeacher)
            .where(CourseTeacher.course_id == course_id)
            .where(CourseTeacher.teacher_id == teacher_id)
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher assignment not found"
            )

        session.delete(assignment)
        session.commit()
        return {"ok": True, "message": "Teacher removed successfully"}

    @staticmethod
    def update_teacher_role(
            session: Session,
            course_id: int,
            teacher_id: int,
            new_role: TeacherRole,
            current_user: User
    ) -> CourseTeacher:
        """Update the role of a teacher assigned to a course"""

        # find assignment
        assignment = session.exec(
            select(CourseTeacher)
            .where(CourseTeacher.course_id == course_id)
            .where(CourseTeacher.teacher_id == teacher_id)
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher assignment not found"
            )

        assignment.role = new_role
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment