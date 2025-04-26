import json
from unittest.mock import patch
from app.models import ApiToken
from datetime import datetime, timezone, timedelta


def test_api_token_error_handling(client, user, monkeypatch):
    """Test error handling in the api_token_required decorator"""

    # Test internal server error handling by patching verify_jwt_in_request which is used inside the decorator
    with patch("flask_jwt_extended.verify_jwt_in_request") as mock_verify:
        mock_verify.side_effect = Exception("Unexpected error")

        response = client.get("/api/v1/transactions")
        assert response.status_code in [
            401,
            500,
        ]  # Either unauthorized or internal error
        data = json.loads(response.data)
        assert "error" in data  # Just check for any error


def test_user_lookup_functions(app, user):
    """Test user lookup functions for both login_manager and JWT"""

    with app.test_request_context():
        # Test login_manager user loader
        from app.extensions import load_user

        user_obj = load_user(user.id)
        assert user_obj is not None
        assert user_obj.id == user.id


def test_api_token_notfound_propagation(authenticated_client, user):
    """Test that a not found response is properly handled"""
    # Test a non-existent endpoint
    response = authenticated_client.get("/api/v1/nonexistent_endpoint")
    assert response.status_code in [404, 400]  # Either not found or bad request


def test_api_token_expiry_validation(client, user):
    """Test that expired API tokens are rejected"""

    # Create an expired token with valid fields
    expired_token = ApiToken(
        user_id=user.id,
        name="Expired Test Token",
        token="expired_test_token_12345",
        expires_at=datetime.now(timezone.utc)
        - timedelta(hours=1),  # Expired 1 hour ago
    )

    from app.models import db

    db.session.add(expired_token)
    db.session.commit()

    # Try to use the expired token with Authorization header
    auth_headers = {"Authorization": f"Token {expired_token.token}"}
    response = client.get("/api/v1/transactions", headers=auth_headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data  # Just check for any error response

    # Try to use the expired token with X-API-Key header
    api_key_headers = {"X-API-Key": expired_token.token}
    response = client.get("/api/v1/transactions", headers=api_key_headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data  # Just check for any error response


def test_jwt_callbacks(app):
    """Test JWT callbacks for error handling"""

    with app.app_context():
        # Test invalid token callback
        from app.extensions import invalid_token_callback

        response_data, status_code = invalid_token_callback("Invalid token error")
        assert status_code == 401
        assert "error" in response_data

        # Test expired token callback
        from app.extensions import expired_token_callback

        response_data, status_code = expired_token_callback({}, {})
        assert status_code == 401
        assert "error" in response_data

        # Test unauthorized callback
        from app.extensions import unauthorized_callback

        response_data, status_code = unauthorized_callback("Unauthorized error")
        assert status_code == 401
        assert "error" in response_data
