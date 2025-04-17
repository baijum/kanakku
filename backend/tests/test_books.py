import pytest
from app.models import User, Book, Account, Transaction
from app.extensions import db
from datetime import datetime


@pytest.fixture
def user(app, client):
    """Create a test user and log in."""
    with app.app_context():
        # Create a test user
        user = User(email="testuser@example.com")
        user.set_password("password123")
        user.is_active = True
        db.session.add(user)
        db.session.commit()

        # Log in the user and get JWT token
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "password123"},
        )
        token = response.json["token"]

        # Return the user and token
        yield user, token


@pytest.fixture
def books(app, user):
    """Create test books for a user."""
    with app.app_context():
        user_obj, _ = user

        # Create test books
        book1 = Book(user_id=user_obj.id, name="Personal Finances")

        book2 = Book(user_id=user_obj.id, name="Business Expenses")

        db.session.add_all([book1, book2])
        db.session.commit()

        # Set the first book as active
        user_obj.active_book_id = book1.id
        db.session.commit()

        yield book1, book2


@pytest.fixture
def accounts(app, user, books):
    """Create test accounts in different books."""
    with app.app_context():
        user_obj, _ = user
        book1, book2 = books

        # Create accounts in first book
        account1 = Account(
            user_id=user_obj.id,
            book_id=book1.id,
            name="Checking",
            description="Primary checking account",
            balance=1000.0,
        )

        account2 = Account(
            user_id=user_obj.id,
            book_id=book1.id,
            name="Savings",
            description="Savings account",
            balance=5000.0,
        )

        # Create account in second book with same name as in first book
        account3 = Account(
            user_id=user_obj.id,
            book_id=book2.id,
            name="Checking",
            description="Business checking account",
            balance=2000.0,
        )

        db.session.add_all([account1, account2, account3])
        db.session.commit()

        yield account1, account2, account3


def test_create_book(app, client, user):
    """Test creating a new book."""
    _, token = user

    response = client.post(
        "/api/v1/books",
        json={"name": "Investment Portfolio"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json["message"] == "Book created successfully"
    assert response.json["book"]["name"] == "Investment Portfolio"


def test_get_books(app, client, user, books):
    """Test getting all books for a user."""
    _, token = user

    response = client.get("/api/v1/books", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert len(response.json) == 2
    assert any(book["name"] == "Personal Finances" for book in response.json)
    assert any(book["name"] == "Business Expenses" for book in response.json)


def test_get_book(app, client, user, books):
    """Test getting a specific book."""
    _, token = user
    book1, _ = books

    response = client.get(
        f"/api/v1/books/{book1.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["name"] == "Personal Finances"
    assert response.json["id"] == book1.id


def test_update_book(app, client, user, books):
    """Test updating a book's name."""
    _, token = user
    book1, _ = books

    response = client.put(
        f"/api/v1/books/{book1.id}",
        json={"name": "Updated Personal Finances"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Book updated successfully"
    assert response.json["book"]["name"] == "Updated Personal Finances"


def test_set_active_book(app, client, user, books):
    """Test setting a book as active."""
    _, token = user
    _, book2 = books

    response = client.post(
        f"/api/v1/books/{book2.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["message"] == f"Book '{book2.name}' set as active"
    assert response.json["active_book"]["id"] == book2.id

    # Verify the user's active_book_id was updated
    user_obj, _ = user
    with app.app_context():
        user_from_db = User.query.get(user_obj.id)
        assert user_from_db.active_book_id == book2.id


def test_get_active_book(app, client, user, books):
    """Test getting the active book."""
    _, token = user
    book1, _ = books

    response = client.get(
        "/api/v1/books/active", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["id"] == book1.id
    assert response.json["name"] == "Personal Finances"


def test_duplicate_book_name(app, client, user, books):
    """Test creating a book with an existing name (should fail)."""
    _, token = user

    response = client.post(
        "/api/v1/books",
        json={"name": "Personal Finances"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "Book with this name already exists" in response.json["error"]


def test_get_accounts_in_active_book(app, client, user, books, accounts):
    """Test getting accounts from the active book only."""
    _, token = user
    book1, _ = books

    response = client.get(
        "/api/v1/accounts/details", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Should only have accounts from the active book (book1)
    assert len(response.json) == 2

    # All accounts should be from book1
    for account in response.json:
        assert account["book_id"] == book1.id


def test_create_account_in_active_book(app, client, user, books):
    """Test creating an account in the active book."""
    _, token = user
    book1, _ = books

    response = client.post(
        "/api/v1/accounts",
        json={"name": "Credit Card", "description": "Credit card account"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json["account"]["name"] == "Credit Card"
    assert response.json["account"]["book_id"] == book1.id


def test_same_account_names_in_different_books(app, client, user, books, accounts):
    """Test that accounts with the same name can exist in different books."""
    _, token = user
    book1, book2 = books

    # First, change active book to book2
    client.post(
        f"/api/v1/books/{book2.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get accounts from book2
    response = client.get(
        "/api/v1/accounts/details", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Should have 1 account from book2
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Checking"
    assert response.json[0]["book_id"] == book2.id

    # Change back to book1
    client.post(
        f"/api/v1/books/{book1.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get accounts from book1
    response = client.get(
        "/api/v1/accounts/details", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Should have 2 accounts from book1
    assert len(response.json) == 2
    account_names = [account["name"] for account in response.json]
    assert "Checking" in account_names
    assert "Savings" in account_names


def test_create_transaction_in_active_book(app, client, user, books, accounts):
    """Test creating a transaction in the active book."""
    _, token = user
    book1, _ = books
    checking_account, _, _ = accounts

    response = client.post(
        "/api/v1/transactions",
        json={
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payee": "Test Payee",
            "postings": [{"account": "Checking", "amount": "-50.00"}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json["message"] == "Transaction created successfully"

    # Verify transaction is in the active book
    transaction_id = response.json["transactions"][0]["id"]
    with app.app_context():
        transaction = Transaction.query.get(transaction_id)
        assert transaction.book_id == book1.id


def test_get_transactions_in_active_book(app, client, user, books, accounts):
    """Test getting transactions from the active book only."""
    _, token = user
    book1, book2 = books
    checking_account, _, _ = accounts

    # Create a transaction in book1
    client.post(
        "/api/v1/transactions",
        json={
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payee": "Book 1 Transaction",
            "postings": [{"account": "Checking", "amount": "-100.00"}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Set book2 as active
    client.post(
        f"/api/v1/books/{book2.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Create a transaction in book2
    client.post(
        "/api/v1/transactions",
        json={
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payee": "Book 2 Transaction",
            "postings": [{"account": "Checking", "amount": "-200.00"}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get transactions from book2
    response = client.get(
        "/api/v1/transactions", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Should only have transactions from book2
    assert len(response.json["transactions"]) == 1
    assert response.json["transactions"][0]["payee"] == "Book 2 Transaction"

    # Change back to book1
    client.post(
        f"/api/v1/books/{book1.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get transactions from book1
    response = client.get(
        "/api/v1/transactions", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Should only have transactions from book1
    assert len(response.json["transactions"]) == 1
    assert response.json["transactions"][0]["payee"] == "Book 1 Transaction"


def test_default_book_creation(app, client):
    """Test that a default book is created during user registration."""
    with app.app_context():
        # Register a new user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )

        assert response.status_code == 201

        # Get the user
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None

        # Check if a default book was created
        default_book = Book.query.filter_by(user_id=user.id).first()
        assert default_book is not None
        assert default_book.name == "Personal Finances"  # Default name

        # Check if it's set as active
        assert user.active_book_id == default_book.id
