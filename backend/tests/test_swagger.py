from unittest.mock import patch
import json


def test_swagger_ui(client):
    """Test the swagger UI endpoint"""
    response = client.get("/api/docs")
    assert response.status_code == 200

    # Check the response content
    html_content = response.data.decode("utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "Kanakku API Documentation" in html_content
    assert "swagger-ui" in html_content
    assert "/api/swagger.yaml" in html_content

    # Check content type
    assert "text/html" in response.content_type


def test_swagger_yaml(client):
    """Test the swagger.yaml endpoint"""
    response = client.get("/api/swagger.yaml")
    assert response.status_code == 200

    # Check content type is appropriate for YAML
    content_type = response.headers["Content-Type"]
    assert any(
        yaml_type in content_type
        for yaml_type in [
            "text/yaml",
            "application/x-yaml",
            "application/yaml",
            "application/octet-stream",
        ]
    ), f"Invalid content type: {content_type}"

    # Verify it's not empty
    assert len(response.data) > 0


def test_swagger_file_not_found(client):
    """Test handling when swagger file doesn't exist"""

    # Mock the open function to raise FileNotFoundError
    with patch("builtins.open", side_effect=FileNotFoundError):
        response = client.get("/api/swagger.yaml")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
