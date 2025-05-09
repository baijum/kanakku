import pytest
from app.models import User, Book, Account, Transaction, db
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
        book1 = Book(user_id=user_obj.id, name="Book1")

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
    assert any(book["name"] == "Book1" for book in response.json)
    assert any(book["name"] == "Business Expenses" for book in response.json)


def test_get_book(app, client, user, books):
    """Test getting a specific book."""
    _, token = user
    book1, _ = books

    response = client.get(
        f"/api/v1/books/{book1.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["name"] == "Book1"
    assert response.json["id"] == book1.id


def test_update_book(app, client, user, books):
    """Test updating a book's name."""
    _, token = user
    book1, _ = books

    response = client.put(
        f"/api/v1/books/{book1.id}",
        json={"name": "Updated Book1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Book updated successfully"
    assert response.json["book"]["name"] == "Updated Book1"


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
        user_from_db = db.session.get(User, user_obj.id)
        assert user_from_db.active_book_id == book2.id


def test_get_active_book(app, client, user, books):
    """Test getting the active book."""
    user_obj, token = user
    book1, _ = books

    # Explicitly set active book and commit
    with app.app_context():
        # Update directly using the ORM rather than raw SQL
        from app.models import db, User

        user_to_update = db.session.get(User, user_obj.id)
        user_to_update.active_book_id = book1.id
        db.session.commit()

    # Now get the active book
    response = client.get(
        "/api/v1/books/active", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    # Check if response is empty
    assert response.json, "Response is empty"
    # Test for the specific keys
    assert "id" in response.json, f"id not in response: {response.json}"
    assert response.json["id"] == book1.id
    assert response.json["name"] == "Book1"


def test_duplicate_book_name(app, client, user, books):
    """Test creating a book with an existing name (should fail)."""
    _, token = user

    response = client.post(
        "/api/v1/books",
        json={"name": "Book1"},
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
        transaction = db.session.get(Transaction, transaction_id)
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
    """Test that registering a new user creates a default book named 'Book1'."""
    # Register a new user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "defaultbooktest@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert register_response.status_code == 201

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "defaultbooktest@example.com",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json["token"]

    # Fetch the active book
    response = client.get(
        "/api/v1/books/active", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json, "Response is empty"
    assert "id" in response.json, f"id not in response: {response.json}"
    assert response.json["name"] == "Book1"


def test_delete_book(app, client, user, books, accounts):
    """Test deleting a book and verifying cascade deletion of accounts."""
    _, token = user
    book1, _ = books
    account1, account2, _ = accounts

    # Verify book and accounts exist before deletion
    with app.app_context():
        assert db.session.get(Book, book1.id) is not None
        assert db.session.get(Account, account1.id) is not None
        assert db.session.get(Account, account2.id) is not None

    # Delete the book
    response = client.delete(
        f"/api/v1/books/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert (
        response.json["message"]
        == "Book and all associated accounts deleted successfully"
    )

    # Verify book and its accounts are deleted
    with app.app_context():
        assert db.session.get(Book, book1.id) is None
        assert db.session.get(Account, account1.id) is None
        assert db.session.get(Account, account2.id) is None


def test_set_new_active_book_then_delete_previous(app, client, user, books):
    """Test setting a new active book and then deleting the previously active book."""
    user_obj, token = user
    book1, book2 = books

    # First ensure book1 is active
    with app.app_context():
        user_to_update = db.session.get(User, user_obj.id)
        user_to_update.active_book_id = book1.id
        db.session.commit()

    # Set book2 as active
    response = client.post(
        f"/api/v1/books/{book2.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Verify book2 is now active
    with app.app_context():
        user_from_db = db.session.get(User, user_obj.id)
        assert user_from_db.active_book_id == book2.id

    # Now delete the previously active book (book1)
    response = client.delete(
        f"/api/v1/books/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Verify book1 is deleted and book2 is still active
    with app.app_context():
        user_from_db = db.session.get(User, user_obj.id)
        assert db.session.get(Book, book1.id) is None
        assert user_from_db.active_book_id == book2.id


def test_delete_last_book(app, client, user, books):
    """Test deleting the last book and verifying active_book_id is set to None."""
    user_obj, token = user
    book1, book2 = books

    # Delete book2 first
    client.delete(
        f"/api/v1/books/{book2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Delete last book (book1)
    response = client.delete(
        f"/api/v1/books/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify active_book_id is set to None
    with app.app_context():
        user_from_db = db.session.get(User, user_obj.id)
        assert user_from_db.active_book_id is None


def test_delete_nonexistent_book(app, client, user):
    """Test attempting to delete a non-existent book."""
    _, token = user

    response = client.delete(
        "/api/v1/books/99999",  # Non-existent book ID
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404  # Should return 404 Not Found


def test_delete_book_with_transactions(app, client, user, books, accounts):
    """Test deleting a book that has transactions and verifying cascade deletion."""
    user_obj, token = user
    book1, book2 = books
    checking_account, _, _ = accounts

    # Create a transaction in book1
    tx_response = client.post(
        "/api/v1/transactions",
        json={
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payee": "Test Transaction",
            "postings": [{"account": "Checking", "amount": "-100.00"}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert tx_response.status_code == 201
    transaction_id = tx_response.json["transactions"][0]["id"]

    # Verify transaction exists
    with app.app_context():
        assert db.session.get(Transaction, transaction_id) is not None

    # Set book2 as active before deleting book1 to avoid 400 error
    set_active_response = client.post(
        f"/api/v1/books/{book2.id}/set-active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert set_active_response.status_code == 200

    # Delete the book
    response = client.delete(
        f"/api/v1/books/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify book, accounts and transactions are deleted
    with app.app_context():
        assert db.session.get(Book, book1.id) is None
        assert db.session.get(Transaction, transaction_id) is None


def test_delete_unauthorized_book(app, client, user, books):
    """Test attempting to delete another user's book."""
    _, token = user
    book1, _ = books

    # Create another user with their own book
    with app.app_context():
        new_user = User(email="otheruser@example.com")
        new_user.set_password("password123")
        new_user.is_active = True
        db.session.add(new_user)
        db.session.flush()

        other_book = Book(user_id=new_user.id, name="Other User's Book")
        db.session.add(other_book)
        db.session.commit()

        other_book_id = other_book.id

    # Attempt to delete the other user's book
    response = client.delete(
        f"/api/v1/books/{other_book_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 404 not found (as if book doesn't exist for this user)
    assert response.status_code == 404

    # Verify other user's book still exists
    with app.app_context():
        assert db.session.get(Book, other_book_id) is not None


def test_delete_active_book_is_prevented(app, client, user, books):
    """Test that the API prevents deletion of the active book."""
    user_obj, token = user
    book1, book2 = books

    # Ensure book1 is active
    with app.app_context():
        user_to_update = db.session.get(User, user_obj.id)
        user_to_update.active_book_id = book1.id
        db.session.commit()

    # Try to delete the active book
    response = client.delete(
        f"/api/v1/books/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Verify the deletion is prevented with correct error message
    assert response.status_code == 400
    assert "Cannot delete the active book" in response.json["error"]

    # Verify the book still exists
    with app.app_context():
        book = db.session.get(Book, book1.id)
        assert book is not None

        # Verify the active book is still set
        user_from_db = db.session.get(User, user_obj.id)
        assert user_from_db.active_book_id == book1.id
