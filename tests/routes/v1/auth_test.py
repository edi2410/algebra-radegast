from fastapi.testclient import TestClient
from sqlmodel import Session


class TestAuthRoutes:
    """Test suite for authentication routes"""

    def test_register_user_success(self, client: TestClient, session: Session):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "newuser@example.com",
                "password": "testpass123",
                "full_name": "New User",
                "role": "guest"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_register_user_duplicate_email(self, client: TestClient, session: Session):
        """Test registration with duplicate email fails"""
        # Create first user
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpass123",
            "full_name": "First User",
            "role": "guest"
        }
        client.post("/api/v1/auth/token/register", json=user_data)

        # Try to create second user with same email
        response = client.post("/api/v1/auth/token/register", json=user_data)
        assert response.status_code == 400

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "notanemail",
                "password": "testpass123",
                "full_name": "Test User",
                "role": "guest"
            }
        )
        assert response.status_code == 422

    def test_register_user_short_password(self, client: TestClient):
        """Test registration with password too short"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "full_name": "Test User",
                "role": "guest"
            }
        )
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, session: Session):
        """Test successful login"""
        # First register a user
        register_data = {
            "email": "loginuser@example.com",
            "password": "testpass123",
            "full_name": "Login User",
            "role": "guest"
        }
        client.post("/api/v1/auth/token/register", json=register_data)

        # Now login - USE PARAMS INSTEAD OF JSON
        response = client.post(
            "/api/v1/auth/token",
            params={  # ← Changed from json= to params=
                "email": "loginuser@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, session: Session):
        """Test login with incorrect password"""
        # First register a user
        register_data = {
            "email": "wrongpass@example.com",
            "password": "correctpass123",
            "full_name": "Test User",
            "role": "guest"
        }
        client.post("/api/v1/auth/token/register", json=register_data)

        # Try to login with wrong password - USE PARAMS
        response = client.post(
            "/api/v1/auth/token",
            params={  # ← Changed from json= to params=
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/token",
            params={  # ← Changed from json= to params=
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        response = client.post(
            "/api/v1/auth/token",
            params={"email": "test@example.com"}  # ← Changed from json= to params=
        )
        assert response.status_code == 422

    def test_register_with_different_roles(self, client: TestClient, session: Session):
        """Test registration with different user roles"""
        roles = ["guest", "teacher", "admin"]

        for idx, role in enumerate(roles):
            response = client.post(
                "/api/v1/auth/token/register",
                json={
                    "email": f"user_{role}_{idx}@example.com",
                    "password": "testpass123",
                    "full_name": f"User {role}",
                    "role": role
                }
            )
            assert response.status_code == 200
            assert "access_token" in response.json()

    def test_auth_headers_teacher(self, client: TestClient):
        """Create a moderator user and return auth headers"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "teacher@example.com",
                "password": "testpass123",
                "full_name": "Teacher User",
                "role": "teacher"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_auth_headers_admin(self, client: TestClient):
        """Create an admin user and return auth headers"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "admin@example.com",
                "password": "testpass123",
                "full_name": "Admin User",
                "role": "admin"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_auth_headers_guest(self, client: TestClient):
        """Create a guest user and return auth headers"""
        response = client.post(
            "/api/v1/auth/token/register",
            json={
                "email": "guest@example.com",
                "password": "testpass123",
                "full_name": "Guest User",
                "role": "guest"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
