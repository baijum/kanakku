from app.models import Account, Transaction, Book, db
from datetime import date


def test_get_accounts(authenticated_client, user, app):
    # Create some test accounts
    with app.app_context():
        # Get the active book from the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()

        account1 = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account 1",
            currency="INR",
            balance=1000.0,
        )
        account2 = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account 2",
            currency="INR",
            balance=2000.0,
        )
        db.session.add_all([account1, account2])
        db.session.commit()

    # Test getting simple account list
    response = authenticated_client.get("/api/v1/accounts")
    assert response.status_code == 200
    data = response.get_json()
    assert "accounts" in data
    assert len(data["accounts"]) == 2
    assert "Test Account 1" in data["accounts"]
    assert "Test Account 2" in data["accounts"]

    # Test getting detailed account list
    response = authenticated_client.get("/api/v1/accounts/details")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Account 1"
    assert data[0]["balance"] == 1000.0
    assert data[1]["name"] == "Test Account 2"
    assert data[1]["balance"] == 2000.0


def test_create_account(authenticated_client, user, app):
    # Get the active book from the user
    book_id = None
    with app.app_context():
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()
            user.active_book_id = book.id
            db.session.commit()
        book_id = book.id

    # Test successful account creation
    response = authenticated_client.post(
        "/api/v1/accounts",
        json={
            "name": "New Account",
            "currency": "USD",
            "balance": 500.0,
            "book_id": book_id,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "account" in data
    assert data["account"]["name"] == "New Account"
    assert data["account"]["currency"] == "USD"
    assert data["account"]["balance"] == 500.0

    # Test creating account with missing fields
    response = authenticated_client.post("/api/v1/accounts", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Test creating duplicate account
    response = authenticated_client.post(
        "/api/v1/accounts", json={"name": "New Account", "book_id": book_id}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_specific_account(authenticated_client, user, app):
    # Create a test account
    with app.app_context():
        # Get the active book from the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()

        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

    # Test getting existing account
    response = authenticated_client.get(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test Account"
    assert data["balance"] == 1000.0

    # Test getting non-existent account
    response = authenticated_client.get("/api/v1/accounts/999999")
    assert response.status_code == 404


def test_update_account(authenticated_client, user, app):
    # Create a test account
    with app.app_context():
        # Get the active book from the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()

        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

    # Test updating all fields
    response = authenticated_client.put(
        f"/api/v1/accounts/{account_id}",
        json={
            "name": "Updated Account",
            "currency": "USD",
            "balance": 2000.0,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["account"]["name"] == "Updated Account"
    assert data["account"]["currency"] == "USD"
    assert data["account"]["balance"] == 2000.0

    # Test partial update
    response = authenticated_client.put(
        f"/api/v1/accounts/{account_id}", json={"name": "Partially Updated Account"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["account"]["name"] == "Partially Updated Account"
    assert data["account"]["currency"] == "USD"  # unchanged

    # Test updating non-existent account
    response = authenticated_client.put(
        "/api/v1/accounts/999999", json={"name": "Non-existent Account"}
    )
    assert response.status_code == 404


def test_delete_account(authenticated_client, user, app):
    # Create a test account
    with app.app_context():
        # Get the active book from the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()

        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

    # Test successful deletion
    response = authenticated_client.delete(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 200
    assert "message" in response.get_json()

    # Verify account was deleted
    response = authenticated_client.get(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 404

    # Test deleting non-existent account
    response = authenticated_client.delete("/api/v1/accounts/999999")
    assert response.status_code == 404


def test_delete_account_with_transactions(authenticated_client, user, app):
    # Create a test account with a transaction
    account_id = None
    with app.app_context():
        # Get the active book from the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if not book:
            book = Book(user_id=user.id, name="Test Book")
            db.session.add(book)
            db.session.commit()

        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

        transaction = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=account.id,
            description="Test Transaction",
            amount=100.0,
            currency="INR",
            date=date(2024, 1, 1),
        )
        db.session.add(transaction)
        db.session.commit()

    # Test deleting account with transactions
    response = authenticated_client.delete(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Cannot delete account with existing transactions" in data["error"]

    # Verify account still exists
    with app.app_context():
        assert db.session.get(Account, account_id) is not None
        assert Transaction.query.filter_by(account_id=account_id).count() == 1
