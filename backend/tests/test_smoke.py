"""
Smoke tests verifying basic application startup and core functionality.
"""

from fastapi.testclient import TestClient
from main import app


def test_smoke():
    """Verify app starts and basic health endpoint works."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_app_has_required_routes():
    """Verify essential routes are registered."""
    client = TestClient(app)

    # Check that key endpoints exist (may require auth, so 401/422 is acceptable)
    routes_to_check = [
        ("GET", "/"),
        ("GET", "/health"),
        ("POST", "/auth/register"),
        ("POST", "/auth/login"),
        ("POST", "/chat"),
        ("POST", "/products/search"),
    ]

    for method, path in routes_to_check:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json={})

        # Route exists if we don't get 404
        assert response.status_code != 404, f"Route {method} {path} not found"
