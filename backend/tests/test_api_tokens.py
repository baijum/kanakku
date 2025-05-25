from datetime import datetime, timedelta, timezone

import pytest

from app.models import ApiToken


@pytest.fixture
def api_token(app, db_session, user):
    """Create a test API token linked to the user fixture."""
    if not user or not user.id:
        pytest.fail("User fixture did not provide a valid user for API token.")

    # Check if a default token exists for this user
    existing_token = (
        db_session.query(ApiToken).filter_by(user_id=user.id, name="Test Token").first()
    )
    if existing_token:
        return existing_token

    # Create a new token
    token = ApiToken(
        user_id=user.id,
        token=ApiToken.generate_token(),
        name="Test Token",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(token)
    db_session.commit()

    return token


def test_create_token(authenticated_client, user, db_session):
    """Test creating a new API token."""
    # Test creating a token without expiry
    response = authenticated_client.post(
        "/api/v1/auth/tokens", json={"name": "Test API Token"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert "name" in data
    assert data["name"] == "Test API Token"
    assert "token" in data  # Token value should be included in the response
    assert data["expires_at"] is None

    # Verify token was created in the database
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=data["id"]).first()
        assert token is not None
        assert token.name == "Test API Token"
        assert token.user_id == user.id
        assert token.is_active is True
        assert token.expires_at is None

    # Test creating a token with expiry
    expiry_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    response = authenticated_client.post(
        "/api/v1/auth/tokens",
        json={"name": "Expiring Token", "expires_at": expiry_date},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Expiring Token"
    assert data["expires_at"] is not None

    # Verify expiry date was set correctly
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=data["id"]).first()
        assert token is not None
        assert token.expires_at is not None
        # Timestamp might not match exactly, but should be within a minute
        expires_at_dt = datetime.fromisoformat(
            data["expires_at"].replace("Z", "+00:00")
        )
        assert abs((token.expires_at - expires_at_dt).total_seconds()) < 60


def test_create_token_validation(authenticated_client):
    """Test validation for token creation."""
    # Test creating a token without a name
    response = authenticated_client.post("/api/v1/auth/tokens", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "no data provided" in data["error"].lower()

    # Test with an empty name
    response = authenticated_client.post("/api/v1/auth/tokens", json={"name": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

    # Test creating a token with invalid expiry format
    response = authenticated_client.post(
        "/api/v1/auth/tokens",
        json={"name": "Invalid Token", "expires_at": "not-a-date"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "invalid" in data["error"].lower()


def test_get_tokens(authenticated_client, api_token, db_session):
    """Test retrieving API tokens."""
    # Test getting all tokens
    response = authenticated_client.get("/api/v1/auth/tokens")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least the token from the fixture

    # Verify the token from fixture is in the response
    fixture_token_found = False
    for token in data:
        if token["id"] == api_token.id:
            fixture_token_found = True
            assert token["name"] == api_token.name
            # In the new format, token value should not be included in the list response
            assert "token" not in token
            break
    assert fixture_token_found, "Token from fixture not found in response"


def test_delete_token(authenticated_client, api_token, db_session):
    """Test deleting an API token."""
    # Test deleting a token
    response = authenticated_client.delete(f"/api/v1/auth/tokens/{api_token.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "revoked" in data["message"].lower()

    # Verify token was deleted from the database
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=api_token.id).first()
        assert token is None


def test_delete_nonexistent_token(authenticated_client):
    """Test trying to delete a token that doesn't exist."""
    response = authenticated_client.delete("/api/v1/auth/tokens/999999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_update_token(authenticated_client, api_token, db_session):
    """Test updating an API token."""
    # Test updating token name
    response = authenticated_client.put(
        f"/api/v1/auth/tokens/{api_token.id}", json={"name": "Updated Token Name"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated Token Name"

    # Verify name was updated in the database
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=api_token.id).first()
        assert token is not None
        assert token.name == "Updated Token Name"

    # Test updating token expiry
    expiry_date = (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()
    response = authenticated_client.put(
        f"/api/v1/auth/tokens/{api_token.id}", json={"expires_at": expiry_date}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["expires_at"] is not None

    # Verify expiry was updated
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=api_token.id).first()
        assert token is not None
        assert token.expires_at is not None

    # Test removing expiry (setting to null)
    response = authenticated_client.put(
        f"/api/v1/auth/tokens/{api_token.id}", json={"expires_at": None}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["expires_at"] is None

    # Verify expiry was removed
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=api_token.id).first()
        assert token is not None
        assert token.expires_at is None

    # Test deactivating a token
    response = authenticated_client.put(
        f"/api/v1/auth/tokens/{api_token.id}", json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_active"] is False

    # Verify token was deactivated
    with db_session.no_autoflush:
        token = db_session.query(ApiToken).filter_by(id=api_token.id).first()
        assert token is not None
        assert token.is_active is False


def test_update_nonexistent_token(authenticated_client):
    """Test trying to update a token that doesn't exist."""
    response = authenticated_client.put(
        "/api/v1/auth/tokens/999999", json={"name": "This should fail"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_token_authentication(app, client, api_token, db_session):
    """Test authenticating with an API token."""
    # Test access with API token via Authorization header
    response = client.get(
        "/api/v1/auth/test", headers={"Authorization": f"Token {api_token.token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "authentication successful" in data["message"].lower()
    assert data["auth_type"] == "API Token"

    # Test access with API token via X-API-Key header
    response = client.get("/api/v1/auth/test", headers={"X-API-Key": api_token.token})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "authentication successful" in data["message"].lower()
    assert data["auth_type"] == "API Token"

    # Test with invalid token in Authorization header
    response = client.get(
        "/api/v1/auth/test", headers={"Authorization": "Token invalid-token"}
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data

    # Test with invalid token in X-API-Key header
    response = client.get("/api/v1/auth/test", headers={"X-API-Key": "invalid-token"})
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data

    # Test with deactivated token
    with app.app_context():
        api_token.is_active = False
        db_session.commit()

    response = client.get(
        "/api/v1/auth/test", headers={"Authorization": f"Token {api_token.token}"}
    )
    assert response.status_code == 401

    # Reactivate the token for subsequent tests
    with app.app_context():
        api_token.is_active = True
        db_session.commit()

    # Test with expired token
    with app.app_context():
        api_token.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()

    response = client.get(
        "/api/v1/auth/test", headers={"Authorization": f"Token {api_token.token}"}
    )
    assert response.status_code == 401


def test_token_model_methods(app, db_session, user):
    """Test ApiToken model methods."""
    with app.app_context():
        # Test token generation
        token_value = ApiToken.generate_token()
        assert isinstance(token_value, str)
        assert len(token_value) == 64  # Should be a 32-byte hex string (64 chars)

        # We need to add tokens to the database before testing their methods
        # Create a token that's not expired
        active_token = ApiToken(
            user_id=user.id,
            token=ApiToken.generate_token(),
            name="Active Token",
            is_active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db_session.add(active_token)

        # Create a token that is expired
        expired_token = ApiToken(
            user_id=user.id,
            token=ApiToken.generate_token(),
            name="Expired Token",
            is_active=True,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(expired_token)

        # Create a token with no expiry
        no_expiry_token = ApiToken(
            user_id=user.id,
            token=ApiToken.generate_token(),
            name="No Expiry Token",
            is_active=True,
            expires_at=None,
        )
        db_session.add(no_expiry_token)

        # Create an inactive token
        inactive_token = ApiToken(
            user_id=user.id,
            token=ApiToken.generate_token(),
            name="Inactive Token",
            is_active=False,
            expires_at=None,
        )
        db_session.add(inactive_token)

        # Commit to database
        db_session.commit()

        # Test is_expired method
        assert active_token.is_expired() is False
        assert expired_token.is_expired() is True
        assert no_expiry_token.is_expired() is False

        # Test is_valid method
        assert active_token.is_valid() is True
        assert expired_token.is_valid() is False
        assert no_expiry_token.is_valid() is True
        assert inactive_token.is_valid() is False

        # Test update_last_used method
        test_token = ApiToken(
            user_id=user.id, token=ApiToken.generate_token(), name="Last Used Token"
        )
        db_session.add(test_token)
        db_session.commit()

        assert test_token.last_used_at is None

        # Save the session ID to ensure we're updating the token
        token_id = test_token.id
        test_token.update_last_used()

        # Reload the token from the database to verify changes
        updated_token = db_session.query(ApiToken).filter_by(id=token_id).first()
        assert updated_token.last_used_at is not None

        # Make sure both are timezone-aware before comparing
        now = datetime.now(timezone.utc)
        if updated_token.last_used_at.tzinfo is None:
            updated_token.last_used_at = updated_token.last_used_at.replace(
                tzinfo=timezone.utc
            )

        assert (
            now - updated_token.last_used_at
        ).total_seconds() < 10  # Should be recent
