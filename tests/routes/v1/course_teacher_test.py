from typing import Type

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.user import User
from app.models.course import Course


class TestCourseTeacherRoutes:

    @pytest.fixture
    def admin_user(self, client: TestClient, session: Session) -> User:
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "admin@example.com",
                "password": "adminpass",
                "full_name": "Admin User",
                "role": "admin"
            }
        )
        assert response.status_code == 200
        statement = select(User).where(User.email == "admin@example.com")
        user = session.exec(statement).first()
        return user

    @pytest.fixture
    def teacher_user(self, client: TestClient, session: Session) -> User:
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "teacher@example.com",
                "password": "teacherpass",
                "full_name": "Teacher User",
                "role": "teacher"
            }
        )
        assert response.status_code == 200
        statement = select(User).where(User.email == "teacher@example.com")
        user = session.exec(statement).first()
        return user

    @pytest.fixture
    def guest_user(self, client: TestClient, session: Session) -> User:
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "guest@example.com",
                "password": "guestpass",
                "full_name": "Guest User",
                "role": "guest"
            }
        )
        assert response.status_code == 200
        statement = select(User).where(User.email == "guest@example.com")
        user = session.exec(statement).first()
        return user

    @pytest.fixture
    def test_course(self, session: Session) -> Course:
        course = Course(
            title="Test Course",
            description="Test Description"
        )
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

    @pytest.fixture
    def admin_token(self, client: TestClient, admin_user: User) -> str:
        response = client.post(
            "/api/v1/auth/token",
            params={
                "email": "admin@example.com",
                "password": "adminpass"
            }
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    @pytest.fixture
    def teacher_token(self, client: TestClient, teacher_user: User) -> str:
        response = client.post(
            "/api/v1/auth/token",
            params={
                "email": "teacher@example.com",
                "password": "teacherpass"
            }
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    def test_assign_teacher_success(
            self,
            client: TestClient,
            session: Session,
            test_course: Course,
            teacher_user: User,
            admin_token: str
    ):
        response = client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={
                "teacher_id": teacher_user.id,
                "role": "PRIMARY"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["teacher_id"] == teacher_user.id
        assert data["course_id"] == test_course.id
        assert data["role"] == "PRIMARY"
        assert data["teacher_name"] == "Teacher User"
        assert data["teacher_email"] == "teacher@example.com"

    def test_assign_teacher_duplicate(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            admin_token: str
    ):
        response1 = client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response1.status_code == 201

        response2 = client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response2.status_code == 400
        assert "already assigned" in response2.json()["detail"].lower()

    def test_assign_to_nonexistent_course(
            self,
            client: TestClient,
            teacher_user: User,
            admin_token: str
    ):
        response = client.post(
            f"/api/v1/courses/99999/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
        assert "course not found" in response.json()["detail"].lower()

    def test_get_course_teachers(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            admin_token: str
    ):
        client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "PRIMARY"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        response = client.get(f"/api/v1/courses/{test_course.id}/teachers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["teacher_id"] == teacher_user.id
        assert data[0]["role"] == "PRIMARY"
        assert data[0]["teacher_name"] == "Teacher User"
        assert data[0]["teacher_email"] == "teacher@example.com"

    def test_get_course_teachers_empty(
            self,
            client: TestClient,
            test_course: Course
    ):
        response = client.get(f"/api/v1/courses/{test_course.id}/teachers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_teachers_nonexistent_course(self, client: TestClient):
        response = client.get(f"/api/v1/courses/99999/teachers/")
        assert response.status_code == 404

    def test_remove_teacher(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            admin_token: str
    ):
        client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        response = client.delete(
            f"/api/v1/courses/{test_course.id}/teachers/{teacher_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

        get_response = client.get(f"/api/v1/courses/{test_course.id}/teachers/")
        assert len(get_response.json()) == 0

    def test_remove_nonexistent_teacher(
            self,
            client: TestClient,
            test_course: Course,
            admin_token: str
    ):
        response = client.delete(
            f"/api/v1/courses/{test_course.id}/teachers/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    def test_update_teacher_role(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            admin_token: str
    ):
        client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        response = client.patch(
            f"/api/v1/courses/{test_course.id}/teachers/{teacher_user.id}",
            json={"role": "PRIMARY"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "PRIMARY"

    def test_unauthorized_assign_teacher(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            teacher_token: str
    ):
        response = client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 403

    def test_unauthorized_remove_teacher(
            self,
            client: TestClient,
            test_course: Course,
            teacher_user: User,
            teacher_token: str,
            admin_token: str
    ):
        client.post(
            f"/api/v1/courses/{test_course.id}/teachers/",
            json={"teacher_id": teacher_user.id, "role": "ASSISTANT"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        response = client.delete(
            f"/api/v1/courses/{test_course.id}/teachers/{teacher_user.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 403