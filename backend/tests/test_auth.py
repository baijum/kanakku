import pytest
from app import db
from app.models import User


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email="test@example.com").first()
        if existing_user:
            return existing_user

        # Create new user if it doesn't exist
        user = User(email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        return user


def test_register(client):
    response = client.post(
        "/api/auth/register", json={"email": "new@example.com", "password": "password"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "user_id" in data
    assert "pending activation" in data["message"]


def test_login(client, user, app):
    # First activate the user
    with app.app_context():
        # Fetch the user again within the app context
        user = User.query.filter_by(email="test@example.com").first()
        user.set_password("password123")
        user.activate()
        db.session.commit()

    response = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert "message" in data
    assert data["message"] == "Login successful"


def test_invalid_login(client):
    response = client.post(
        "/api/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_get_current_user(authenticated_client, user, db_session):
    # Using db_session ensures the user object from the fixture
    # can be used for comparison if needed, although accessing response data is preferred.
    with db_session.no_autoflush:
        response = authenticated_client.get("/api/auth/me")
        # Primary assertion should be on status code and response content
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data is not None
        # Compare response data against the known ID from the fixture user
        assert response_data.get("id") == user.id
        assert response_data.get("email") == user.email


def test_forgot_password(client, user, app):
    # Test with existing user
    response = client.post(
        "/api/auth/forgot-password", json={"email": "test@example.com"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Test with non-existent user (should still return 200 for security)
    response = client.post(
        "/api/auth/forgot-password", json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


def test_reset_password(client, user, app, db_session):
    # First generate a reset token
    with app.app_context():
        # Get a fresh user instance attached to the current session
        user = db_session.query(User).filter_by(email="test@example.com").first()
        token = user.generate_reset_token()
        db_session.commit()

    # Test successful password reset
    response = client.post(
        "/api/auth/reset-password",
        json={
            "email": "test@example.com",
            "token": token,
            "new_password": "newpassword123",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Activate the user
    with app.app_context():
        user = db_session.query(User).filter_by(email="test@example.com").first()
        user.activate()
        db_session.commit()

    # Verify new password works
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "newpassword123"},
    )
    assert response.status_code == 200

    # Test with invalid token
    response = client.post(
        "/api/auth/reset-password",
        json={
            "email": "test@example.com",
            "token": "invalidtoken",
            "new_password": "newpassword123",
        },
    )
    assert response.status_code == 400


def test_update_password(authenticated_client, user, app, db_session):
    # First activate the user
    with app.app_context():
        user = db_session.query(User).filter_by(email="test@example.com").first()
        user.activate()
        db_session.commit()

    # Test successful password update
    response = authenticated_client.put(
        "/api/auth/password",
        json={"current_password": "password123", "new_password": "newpassword123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Verify new password works
    response = authenticated_client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "newpassword123"},
    )
    assert response.status_code == 200

    # Test with incorrect current password
    response = authenticated_client.put(
        "/api/auth/password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
    )
    assert response.status_code == 401


def test_activate_user(authenticated_client, user, app):
    # First deactivate the user
    with app.app_context():
        user.deactivate()
        db.session.commit()

    # Test activating the user
    response = authenticated_client.post(
        f"/api/auth/users/{user.id}/activate", json={"is_active": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "activated" in data["message"]

    # Test deactivating the user
    response = authenticated_client.post(
        f"/api/auth/users/{user.id}/activate", json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "deactivated" in data["message"]

    # Test with non-existent user
    response = authenticated_client.post(
        "/api/auth/users/999999/activate", json={"is_active": True}
    )
    assert response.status_code == 404


def test_google_login(client, app):
    # Configure Google OAuth in the app
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"

    # Test the Google login endpoint
    response = client.get("/api/auth/google")
    assert response.status_code == 200
    data = response.get_json()
    assert "auth_url" in data
    assert "accounts.google.com/o/oauth2/v2/auth" in data["auth_url"]
    assert "client_id=test-client-id" in data["auth_url"]
    assert "state=" in data["auth_url"]

    # Verify state was stored in session
    with client.session_transaction() as session:
        assert "oauth_state" in session


def test_google_callback_success(client, app, mocker):
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"
    app.config["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
    app.config["FRONTEND_URL"] = "http://localhost:3000"

    # Mock requests library
    mock_requests = mocker.patch("app.auth.requests")

    # Mock token response
    mock_token_response = mocker.Mock()
    mock_token_response.raise_for_status.return_value = None
    mock_token_response.json.return_value = {"access_token": "mock_token"}
    mock_requests.post.return_value = mock_token_response

    # Mock userinfo response
    mock_userinfo_response = mocker.Mock()
    mock_userinfo_response.raise_for_status.return_value = None
    mock_userinfo_response.json.return_value = {
        "sub": "google-user-id",
        "email": "google@example.com",
        "picture": "https://example.com/photo.jpg",
    }
    mock_requests.get.return_value = mock_userinfo_response

    # Set state in session
    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    # Test callback
    response = client.get("/api/auth/google/callback?state=test-state&code=test-code")
    assert response.status_code == 302  # Redirect
    assert "/google-auth-callback?token=" in response.location

    # Verify user was created
    with app.app_context():
        user = User.query.filter_by(email="google@example.com").first()
        assert user is not None
        assert user.is_active
        assert user.google_id == "google-user-id"
        assert user.picture == "https://example.com/photo.jpg"


def test_google_callback_invalid_state(client, app):
    # Test with invalid state
    response = client.get(
        "/api/auth/google/callback?state=invalid_state&code=test-code"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_google_callback_existing_user(client, app, mocker):
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"
    app.config["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
    app.config["FRONTEND_URL"] = "http://localhost:3000"

    # Create an existing user
    with app.app_context():
        existing_user = User(email="google@example.com", is_active=True)
        existing_user.set_password("password")
        db.session.add(existing_user)
        db.session.commit()
        existing_user_id = existing_user.id

    # Mock requests library
    mock_requests = mocker.patch("app.auth.requests")

    # Mock token response
    mock_token_response = mocker.Mock()
    mock_token_response.raise_for_status.return_value = None
    mock_token_response.json.return_value = {"access_token": "mock_token"}
    mock_requests.post.return_value = mock_token_response

    # Mock userinfo response
    mock_userinfo_response = mocker.Mock()
    mock_userinfo_response.raise_for_status.return_value = None
    mock_userinfo_response.json.return_value = {
        "sub": "google-user-id",
        "email": "google@example.com",
        "picture": "https://example.com/photo.jpg",
    }
    mock_requests.get.return_value = mock_userinfo_response

    # Set state in session
    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    # Test callback
    response = client.get("/api/auth/google/callback?state=test-state&code=test-code")
    assert response.status_code == 302  # Redirect
    assert "/google-auth-callback?token=" in response.location

    # Verify existing user was updated
    with app.app_context():
        user = User.query.filter_by(email="google@example.com").first()
        assert user is not None
        assert user.id == existing_user_id
        assert user.google_id == "google-user-id"
        assert user.picture == "https://example.com/photo.jpg"
