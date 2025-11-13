from fastapi.testclient import TestClient
from sqlmodel import Session


class TestCourseRoutes:
    """Test suite for course routes"""

    def _create_auth_user(self, client: TestClient, role: str = "teacher", email: str = None):
        """Helper method to create a user and return auth headers"""
        if email is None:
            email = f"{role}_course@example.com"

        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": email,
                "password": "testpass123",
                "full_name": f"{role.capitalize()} User",
                "role": role
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_course(self, client: TestClient, headers: dict, course_data: dict = None):
        """Helper method to create a course"""
        if course_data is None:
            course_data = {
                "title": "Test Course",
                "description": "A test course description",
                "status": "draft"
            }

        response = client.post("/api/v1/courses/", json=course_data, headers=headers)
        return response

    # List courses tests
    def test_list_courses_empty(self, client: TestClient, session: Session):
        """Test listing courses when none exist"""
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_courses_success(self, client: TestClient, session: Session):
        """Test successful listing of courses"""
        # Create a teacher user and course
        headers = self._create_auth_user(client, "admin")

        # Create multiple courses
        course1_data = {
            "title": "Python Basics",
            "description": "Learn Python from scratch",
            "status": "draft"
        }
        course2_data = {
            "title": "Advanced Python",
            "description": "Master Python",
            "status": "active"
        }

        self._create_course(client, headers, course1_data)
        self._create_course(client, headers, course2_data)

        # List all courses
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Python Basics"
        assert data[1]["title"] == "Advanced Python"


    def test_create_course_success_admin(self, client: TestClient, session: Session):
        """Test successful course creation by admin"""
        headers = self._create_auth_user(client, "admin", "admin_course@example.com")

        course_data = {
            "title": "Machine Learning",
            "description": "ML fundamentals",
            "status": "active"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == course_data["title"]

    def test_create_course_without_auth(self, client: TestClient):
        """Test course creation without authentication fails"""
        course_data = {
            "title": "Unauthorized Course",
            "description": "Should not be created",
            "status": "draft"
        }

        response = client.post("/api/v1/courses/", json=course_data)
        assert response.status_code == 403

    def test_create_course_guest_role(self, client: TestClient, session: Session):
        """Test course creation with guest role fails"""
        headers = self._create_auth_user(client, "guest", "guest_course@example.com")

        course_data = {
            "title": "Guest Course",
            "description": "Should not be created",
            "status": "draft"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 403

    def test_create_course_minimal_data(self, client: TestClient, session: Session):
        """Test course creation with minimal required data"""
        headers = self._create_auth_user(client, "admin", "minimal@example.com")

        course_data = {
            "title": "Minimal Course"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Course"
        assert data["status"] == "draft"  # Default value
        assert data["description"] is None

    def test_create_course_with_dates(self, client: TestClient, session: Session):
        """Test course creation with start and end dates"""
        headers = self._create_auth_user(client, "admin", "dates@example.com")

        course_data = {
            "title": "Scheduled Course",
            "description": "Course with dates",
            "status": "draft",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-12-31T23:59:59"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Scheduled Course"
        assert data["start_date"] is not None
        assert data["end_date"] is not None

    def test_create_course_invalid_status(self, client: TestClient, session: Session):
        """Test course creation with invalid status"""
        headers = self._create_auth_user(client, "admin", "invalid_status@example.com")

        course_data = {
            "title": "Invalid Status Course",
            "status": "invalid_status"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 422

    # Get course tests
    def test_get_course_success(self, client: TestClient, session: Session):
        """Test successful retrieval of a course"""
        headers = self._create_auth_user(client, "admin", "get_course@example.com")

        # Create a course
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        # Get the course
        response = client.get(f"/api/v1/courses/{course_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert data["title"] == "Test Course"

    def test_get_course_not_found(self, client: TestClient):
        """Test getting a non-existent course"""
        response = client.get("/api/v1/courses/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Course not found"

    # Update course tests
    def test_update_course_success(self, client: TestClient, session: Session):
        """Test successful course update by owner"""
        headers = self._create_auth_user(client, "admin", "update_owner@example.com")

        # Create a course
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        # Update the course
        update_data = {
            "title": "Updated Course Title",
            "description": "Updated description",
            "status": "active"
        }

        response = client.patch(f"/api/v1/courses/{course_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Course Title"
        assert data["description"] == "Updated description"
        assert data["status"] == "active"

    def test_update_course_partial(self, client: TestClient, session: Session):
        """Test partial course update"""
        headers = self._create_auth_user(client, "admin", "partial_update@example.com")

        # Create a course
        course_data = {
            "title": "Original Title",
            "description": "Original description",
            "status": "draft"
        }
        create_response = self._create_course(client, headers, course_data)
        course_id = create_response.json()["id"]

        # Update only the title
        update_data = {
            "title": "New Title Only"
        }

        response = client.patch(f"/api/v1/courses/{course_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        assert data["description"] == "Original description"  # Should remain unchanged
        assert data["status"] == "draft"  # Should remain unchanged

    def test_update_course_without_auth(self, client: TestClient, session: Session):
        """Test updating a course without authentication fails"""
        headers = self._create_auth_user(client, "admin", "create_for_unauth@example.com")
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        update_data = {"title": "Unauthorized Update"}
        response = client.patch(f"/api/v1/courses/{course_id}", json=update_data)
        assert response.status_code == 403

    def test_update_course_not_found(self, client: TestClient, session: Session):
        """Test updating a non-existent course"""
        headers = self._create_auth_user(client, "admin", "update_notfound@example.com")

        update_data = {"title": "Update Non-Existent"}
        response = client.patch("/api/v1/courses/99999", json=update_data, headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Course not found"

    # Delete course tests
    def test_delete_course_success(self, client: TestClient, session: Session):
        """Test successful course deletion by owner"""
        headers = self._create_auth_user(client, "admin", "delete_owner@example.com")

        # Create a course
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        # Delete the course
        response = client.delete(f"/api/v1/courses/{course_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify course is deleted
        get_response = client.get(f"/api/v1/courses/{course_id}")
        assert get_response.status_code == 404

    def test_delete_course_without_auth(self, client: TestClient, session: Session):
        """Test deleting a course without authentication fails"""
        headers = self._create_auth_user(client, "admin", "delete_unauth@example.com")
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/courses/{course_id}")
        assert response.status_code == 403

    def test_delete_course_not_found(self, client: TestClient, session: Session):
        """Test deleting a non-existent course"""
        headers = self._create_auth_user(client, "admin", "delete_notfound@example.com")

        response = client.delete("/api/v1/courses/99999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Course not found"

    # Edge cases and additional tests
    def test_create_course_missing_title(self, client: TestClient, session: Session):
        """Test course creation without title fails"""
        headers = self._create_auth_user(client, "admin", "missing_title@example.com")

        course_data = {
            "description": "Course without title"
        }

        response = self._create_course(client, headers, course_data)
        assert response.status_code == 422

    def test_update_course_all_statuses(self, client: TestClient, session: Session):
        """Test updating course through all status transitions"""
        headers = self._create_auth_user(client, "admin", "all_statuses@example.com")

        # Create a course
        create_response = self._create_course(client, headers)
        course_id = create_response.json()["id"]

        # Update to active
        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"status": "active"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

        # Update to archived
        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"status": "archived"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "archived"

        # Update back to draft
        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"status": "draft"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "draft"
