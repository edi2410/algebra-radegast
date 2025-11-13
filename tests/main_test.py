from fastapi.testclient import TestClient


def test_app_startup(client: TestClient):
    """Test that the app starts successfully"""
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_app_includes_routers(client: TestClient):
    """Test that all routers are included"""
    response = client.get("api/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})


    # Check that auth endpoints exist
    assert "/api/v1/auth/token" in paths
    assert "/api/v1/auth/token/register" in paths

    # Check that course endpoints exist
    assert "/api/v1/courses/" in paths
    assert "/api/v1/courses/{course_id}" in paths
