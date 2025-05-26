from app.extensions import db
from app.models import Book, User


def test_registration_creates_default_book(client, app):
    """Test that registration creates a default book and sets it as active."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "booktest@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 201

    with app.app_context():
        # Verify user was created
        user = User.query.filter_by(email="booktest@example.com").first()
        assert user is not None

        # Verify default book was created
        book = Book.query.filter_by(user_id=user.id).first()
        assert book is not None
        assert book.name == "Book1"  # Updated to match test expectations

        # Verify active book was set
        assert user.active_book_id == book.id


def test_login_returns_user_with_active_book(client, app):
    """Test that login response includes the active book ID."""
    # First create a user with a book
    with app.app_context():
        user = User(email="booklogin@example.com")
        user.set_password("password123")
        user.is_active = True
        db.session.add(user)
        db.session.commit()

        # Create a book
        book = Book(user_id=user.id, name="Test Book")
        db.session.add(book)
        db.session.commit()

        # Set as active book
        user.active_book_id = book.id
        db.session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "booklogin@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.get_json()

    # Verify active book is included
    assert "active_book_id" in data["user"]
    assert data["user"]["active_book_id"] is not None


def test_google_auth_creates_default_book(app, mocker):
    """Test that Google Auth creates a default book for new users."""
    # Mock Google OAuth verification
    mocker.patch(
        "app.auth_bp.services.AuthService.verify_oauth_token",
        return_value={
            "sub": "12345",
            "email": "googleuser@example.com",
            "name": "Google User",
            "picture": "https://example.com/photo.jpg",
        },
    )

    with app.test_client() as client:
        response = client.post(
            "/api/v1/auth/google",
            json={"token": "fake_token"},
        )
        assert response.status_code == 200

        with app.app_context():
            # Verify user was created
            user = User.query.filter_by(email="googleuser@example.com").first()
            assert user is not None

            # Verify default book was created
            book = Book.query.filter_by(user_id=user.id).first()
            assert book is not None
            assert book.name == "Book1"  # Updated to match test expectations

            # Verify active book was set
            assert user.active_book_id == book.id


def test_user_profile_includes_active_book(authenticated_client, app, user):
    """Test that user profile endpoint includes active book info."""
    with app.app_context():
        # Ensure user has an active book
        book = Book.query.filter_by(user_id=user.id).first()
        if not book:
            book = Book(
                user_id=user.id, name="Book1"
            )  # Updated to match test expectations
            db.session.add(book)
            db.session.commit()

        user.active_book_id = book.id
        db.session.commit()

        # Store the book ID separately
        book_id = book.id

    # Get user profile
    response = authenticated_client.get("/api/v1/auth/profile")
    assert response.status_code == 200
    data = response.get_json()

    # Verify active book is included
    assert "data" in data
    assert "active_book_id" in data["data"]
    assert data["data"]["active_book_id"] == book_id
