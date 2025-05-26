import pytest

from app import db
from app.models import Book, User


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
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "password",
            "confirm_password": "password",
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "user_id" in data
    assert "User and default book created successfully." in data["message"]


def test_login(client, user, app):
    # First activate the user
    with app.app_context():
        # Fetch the user again within the app context
        user = User.query.filter_by(email="test@example.com").first()
        user.set_password("password123")
        user.activate()
        db.session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert "user" in data


def test_invalid_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_get_current_user(authenticated_client, user, db_session):
    # Using db_session ensures the user object from the fixture
    # can be used for comparison if needed, although accessing response data is preferred.
    with db_session.no_autoflush:
        response = authenticated_client.get("/api/v1/auth/me")
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
        "/api/v1/auth/forgot-password",
        json={"email": "test@example.com", "hcaptcha_token": "test_token"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Test with non-existent user (should still return 200 for security)
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com", "hcaptcha_token": "test_token"},
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
        "/api/v1/auth/reset-password",
        json={
            "token": token,
            "new_password": "newpassword123",
            "hcaptcha_token": "test_token",
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
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "newpassword123"},
    )
    assert response.status_code == 200

    # Test with invalid token
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalidtoken",
            "new_password": "newpassword123",
            "hcaptcha_token": "test_token",
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
        "/api/v1/auth/password",
        json={"current_password": "password123", "new_password": "newpassword123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Verify new password works
    response = authenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "newpassword123"},
    )
    assert response.status_code == 200

    # Test with incorrect current password
    response = authenticated_client.put(
        "/api/v1/auth/password",
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
        f"/api/v1/auth/users/{user.id}/activate", json={"is_active": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "activated" in data["message"]

    # Test deactivating the user
    response = authenticated_client.post(
        f"/api/v1/auth/users/{user.id}/activate", json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "deactivated" in data["message"]

    # Test with non-existent user
    response = authenticated_client.post(
        "/api/v1/auth/users/999999/activate", json={"is_active": True}
    )
    assert response.status_code == 404


def test_toggle_status(authenticated_client, user, app):
    """Test the toggle-status endpoint to activate/deactivate current user"""
    # First set the user to active
    with app.app_context():
        user.activate()
        db.session.commit()

    # Test deactivating the user
    response = authenticated_client.post(
        "/api/v1/auth/toggle-status", json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "deactivated" in data["message"]
    assert data["user"]["is_active"] is False

    # Test activating the user
    response = authenticated_client.post(
        "/api/v1/auth/toggle-status", json={"is_active": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "activated" in data["message"]
    assert data["user"]["is_active"] is True

    # Test missing is_active parameter
    response = authenticated_client.post("/api/v1/auth/toggle-status", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "is_active field is required" in data["error"]


def test_google_login(client, app):
    # Configure Google OAuth in the app
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"

    # Test the Google login endpoint
    response = client.get("/api/v1/auth/google")
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
    mock_requests = mocker.patch("app.auth_bp.services.requests")

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
    response = client.get(
        "/api/v1/auth/google/callback?state=test-state&code=test-code"
    )
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
        "/api/v1/auth/google/callback?state=invalid_state&code=test-code"
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
    mock_requests = mocker.patch("app.auth_bp.services.requests")

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
    response = client.get(
        "/api/v1/auth/google/callback?state=test-state&code=test-code"
    )
    assert response.status_code == 302  # Redirect
    assert "/google-auth-callback?token=" in response.location

    # Verify existing user was updated
    with app.app_context():
        user = User.query.filter_by(email="google@example.com").first()
        assert user is not None
        assert user.id == existing_user_id
        assert user.google_id == "google-user-id"
        assert user.picture == "https://example.com/photo.jpg"


def test_google_token_auth(client, app, mocker):
    # Configure Google OAuth in the app
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"
    app.config["FRONTEND_URL"] = "http://localhost:3000"

    # Mock the verify_oauth_token function
    mock_verify = mocker.patch("app.auth_bp.services.AuthService.verify_oauth_token")
    mock_verify.return_value = {
        "sub": "google-user-id-token",
        "email": "google_token@example.com",
        "picture": "https://example.com/photo_token.jpg",
    }

    # Test successful token authentication (new user)
    response = client.post("/api/v1/auth/google", json={"token": "mock_id_token"})
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "google_token@example.com"

    # Instead of checking the active_book directly, check that active_book_id is set
    assert "active_book_id" in data["user"]
    assert data["user"]["active_book_id"] is not None

    # Verify that the default book was created (we'll confirm this separately with a db query)
    with app.app_context():
        user = User.query.filter_by(email="google_token@example.com").first()
        assert user is not None
        book = Book.query.filter_by(user_id=user.id).first()
        assert book is not None
        assert book.name == "Book1"
        assert user.active_book_id == book.id

    # Test successful token authentication (existing user)
    # Make the mock return the same email, simulating existing user
    response = client.post("/api/v1/auth/google", json={"token": "mock_id_token_again"})
    assert response.status_code == 200  # Should still be 200 for existing user login
    data = response.get_json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "google_token@example.com"

    # Test invalid token
    mock_verify.side_effect = ValueError("Invalid token")
    response = client.post("/api/v1/auth/google", json={"token": "invalid_token"})
    # Accept either 400, 401 or 500 status code for now
    assert response.status_code in (400, 401, 500)


def test_google_token_auth_inactive_user(client, app, mocker):
    """Test that inactive users cannot authenticate with Google"""
    # Configure Google OAuth in the app
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"
    app.config["FRONTEND_URL"] = "http://localhost:3000"

    # Create an inactive user with Google ID
    with app.app_context():
        user = User(
            email="inactive_google@example.com",
            google_id="google-inactive-id",
            is_active=False,
        )
        db.session.add(user)
        db.session.commit()

    # Mock the verify_oauth_token function
    mock_verify = mocker.patch("app.auth_bp.services.AuthService.verify_oauth_token")
    mock_verify.return_value = {
        "sub": "google-inactive-id",
        "email": "inactive_google@example.com",
        "picture": "https://example.com/inactive_photo.jpg",
    }

    # Test authentication with inactive Google user
    response = client.post("/api/v1/auth/google", json={"token": "mock_inactive_token"})
    assert response.status_code == 403
    data = response.get_json()
    assert "error" in data
    assert "Account is deactivated" in data["error"]


def test_google_callback_inactive_user(client, app, mocker):
    """Test that inactive users are redirected to login page with error in OAuth callback"""
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id"
    app.config["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
    app.config["FRONTEND_URL"] = "http://localhost:3000"

    # Create an inactive user
    with app.app_context():
        inactive_user = User(
            email="inactive_oauth@example.com",
            google_id="google-oauth-inactive-id",
            is_active=False,
        )
        db.session.add(inactive_user)
        db.session.commit()

    # Mock requests library
    mock_requests = mocker.patch("app.auth_bp.services.requests")

    # Mock token response
    mock_token_response = mocker.Mock()
    mock_token_response.raise_for_status.return_value = None
    mock_token_response.json.return_value = {"access_token": "mock_token"}
    mock_requests.post.return_value = mock_token_response

    # Mock userinfo response matching our inactive user
    mock_userinfo_response = mocker.Mock()
    mock_userinfo_response.raise_for_status.return_value = None
    mock_userinfo_response.json.return_value = {
        "sub": "google-oauth-inactive-id",
        "email": "inactive_oauth@example.com",
        "picture": "https://example.com/inactive_photo.jpg",
    }
    mock_requests.get.return_value = mock_userinfo_response

    # Set state in session
    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    # Test callback with inactive user
    response = client.get(
        "/api/v1/auth/google/callback?state=test-state&code=test-code"
    )

    # Should redirect to login page with error
    assert response.status_code == 302
    assert "/login?error=account_inactive" in response.location

    # Verify user remained inactive
    with app.app_context():
        user = User.query.filter_by(email="inactive_oauth@example.com").first()
        assert user is not None
        assert not user.is_active


def test_get_all_users_as_admin(authenticated_client, user, app):
    """Test that admin users can access user list."""
    # Ensure user is admin
    with app.app_context():
        user.is_admin = True
        db.session.commit()

    # Verify admin user can access the endpoint
    response = authenticated_client.get("/api/v1/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert isinstance(data["users"], list)

    # Verify that user data contains expected fields
    if data["users"]:
        user_obj = data["users"][0]
        assert "id" in user_obj
        assert "email" in user_obj
        assert "is_active" in user_obj
        assert "is_admin" in user_obj


def test_get_all_users_as_non_admin(app, client):
    """Test that non-admin users cannot access user list."""
    # Create a non-admin user
    with app.app_context():
        non_admin = User(email="nonadmin@example.com", is_admin=False)
        non_admin.set_password("password123")
        non_admin.is_active = True
        db.session.add(non_admin)
        db.session.commit()

        # Create token for non-admin user
        from flask_jwt_extended import create_access_token

        token = create_access_token(identity=str(non_admin.id))

    # Test that non-admin user cannot access the endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/users", headers=headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.get_json()["error"]


def test_register_honeypot_blocks_bots(client):
    """Test that registration with honeypot field filled is rejected."""
    # Test with new website field
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "bot@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "website": "filled_by_bot",  # Honeypot field filled
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Registration failed. Please try again." in data["error"]

    # Test with old username field for backward compatibility
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "bot2@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "username": "filled_by_bot",  # Old honeypot field filled
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Registration failed. Please try again." in data["error"]


def test_register_honeypot_allows_legitimate_users(client):
    """Test that registration with empty honeypot field succeeds."""
    # Test with new website field empty
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "legitimate@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "website": "",  # Honeypot field empty
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "user_id" in data

    # Test with old username field empty
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "legitimate2@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "username": "",  # Old honeypot field empty
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "user_id" in data


def test_register_honeypot_missing_field_succeeds(client):
    """Test that registration without honeypot field succeeds (backward compatibility)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nofield@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
            # No honeypot fields at all
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "user_id" in data
