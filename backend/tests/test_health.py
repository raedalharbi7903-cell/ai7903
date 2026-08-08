from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_healthy_status() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_versioned_health_check_returns_healthy_status() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_unknown_route_uses_consistent_error_response() -> None:
    with TestClient(app) as client:
        response = client.get("/unknown")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "http_error", "message": "Not Found"}}
