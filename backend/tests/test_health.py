import pytest


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok"}
