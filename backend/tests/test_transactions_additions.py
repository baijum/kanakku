import json
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Account, Book, Transaction


def test_get_recent_transactions(authenticated_client, user):
    """Test the recent transactions endpoint"""
    # Get the book or create one if it doesn't exist
    book = Book.query.filter_by(user_id=user.id).first()
    if not book:
        book = Book(user_id=user.id, name="Test Book")
        db.session.add(book)
        db.session.flush()

        # Set active book
        user.active_book_id = book.id
        db.session.commit()

    # Get the account or create one if it doesn't exist
    account = Account.query.filter_by(user_id=user.id, book_id=book.id).first()
    if not account:
        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            description="Test account for transactions",
            currency="INR",
        )
        db.session.add(account)
        db.session.commit()

    # Create transactions with different dates
    today = datetime.now().date()
    for i in range(5):
        tx_date = today - timedelta(days=i)
        tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=account.id,
            date=tx_date,
            description=f"Test transaction {i}",
            payee=f"Test payee {i}",
            amount=100.0 * (i + 1),
            currency="INR",
        )
        db.session.add(tx)

    db.session.commit()

    # Test the endpoint
    response = authenticated_client.get("/api/v1/transactions/recent")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "transactions" in data
    assert len(data["transactions"]) > 0

    # Verify transactions are ordered by date (newest first)
    dates = [
        datetime.strptime(tx["date"], "%Y-%m-%d").date() for tx in data["transactions"]
    ]
    assert all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1))


def test_transaction_create_validation_errors(client, authenticated_client, user):
    """Test various validation errors in transaction creation"""

    # Test missing JSON data
    response = client.post(
        "/api/v1/transactions", data="not a json", content_type="application/json"
    )
    assert response.status_code == 401  # Unauthorized without token

    # Create invalid requests with authenticated client
    # Test empty JSON
    response = authenticated_client.post("/api/v1/transactions", json={})
    assert response.status_code == 400
    assert "Missing required fields" in response.get_data(as_text=True)

    # Get or create book and account for testing
    book = Book.query.filter_by(user_id=user.id).first()
    if not book:
        book = Book(user_id=user.id, name="Test Book")
        db.session.add(book)
        db.session.flush()
        user.active_book_id = book.id
        db.session.commit()

    account = Account.query.filter_by(user_id=user.id, book_id=book.id).first()
    if not account:
        account = Account(
            user_id=user.id,
            book_id=book.id,
            name="Test Account",
            description="Test account for transactions",
            currency="INR",
        )
        db.session.add(account)
        db.session.commit()

    # Test invalid account
    invalid_account_tx = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payee": "Test Payee",
        "postings": [{"account": "NonExistentAccount", "amount": "100.00"}],
    }
    response = authenticated_client.post(
        "/api/v1/transactions", json=invalid_account_tx
    )
    assert response.status_code == 404
    assert "Account not found" in response.get_data(as_text=True)

    # Test invalid amount format
    invalid_amount_tx = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payee": "Test Payee",
        "postings": [{"account": account.name, "amount": "not-a-number"}],
    }
    response = authenticated_client.post("/api/v1/transactions", json=invalid_amount_tx)
    assert response.status_code == 400
    assert "Invalid amount format" in response.get_data(as_text=True)


def test_handle_errors_decorator(client, authenticated_client, monkeypatch):
    """Test the handle_errors decorator with database errors"""
    from app.transactions_bp.routes import handle_errors

    # Create a mock function that will be decorated
    @handle_errors
    def mock_function_db_error(*args, **kwargs):
        raise SQLAlchemyError("Test database error")

    # Just call the function to see logs
    mock_function_db_error()

    # Monkeypatch the get_transactions function to raise an SQLAlchemyError
    def mock_db_query(*args, **kwargs):
        raise SQLAlchemyError("Mock database error")

    monkeypatch.setattr("app.models.Transaction.query", mock_db_query)

    # Test that the endpoint properly handles the database error
    response = authenticated_client.get("/api/v1/transactions")
    assert response.status_code == 500
    data = json.loads(response.data)
    # Check for any error message, we're just testing that the decorator is handling the error
    assert "error" in data
    assert len(data["error"]) > 0
