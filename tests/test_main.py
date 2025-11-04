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
    assert "/auth/token" in paths
    assert "/auth/token/register" in paths