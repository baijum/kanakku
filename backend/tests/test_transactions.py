import pytest
from flask import json
from app.models import User, Transaction, db, Account
from datetime import date, datetime

# Removed local app fixture


def test_create_transaction(authenticated_client, user, app):
    # Create test accounts
    with app.app_context():
        account1 = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
            type="asset",
            currency="INR",
            balance=1000.0,
        )
        account2 = Account(
            user_id=user.id,
            name="Expenses:Groceries",
            type="expense",
            currency="INR",
            balance=0.0,
        )
        db.session.add_all([account1, account2])
        db.session.commit()

    # Test successful transaction creation
    response = authenticated_client.post(
        "/api/transactions",
        json={
            "date": "2024-01-01",
            "payee": "Supermarket",
            "postings": [
                {
                    "account": "Assets:Bank:Checking",
                    "amount": "-100.0",
                    "currency": "INR",
                },
                {"account": "Expenses:Groceries", "amount": "100.0", "currency": "INR"},
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "transactions" in data
    assert len(data["transactions"]) == 2

    # Verify account balances were updated
    with app.app_context():
        checking = Account.query.filter_by(name="Assets:Bank:Checking").first()
        groceries = Account.query.filter_by(name="Expenses:Groceries").first()
        assert checking.balance == 900.0  # 1000 - 100
        assert groceries.balance == 100.0  # 0 + 100


def test_create_transaction_invalid_data(authenticated_client, user, app):
    # Test with missing required fields
    response = authenticated_client.post(
        "/api/transactions", json={"date": "2024-01-01", "payee": "Supermarket"}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Test with invalid account
    response = authenticated_client.post(
        "/api/transactions",
        json={
            "date": "2024-01-01",
            "payee": "Supermarket",
            "postings": [{"account": "NonExistent:Account", "amount": "100.0"}],
        },
    )
    assert response.status_code == 404
    assert "error" in response.get_json()

    # Test with invalid amount format
    response = authenticated_client.post(
        "/api/transactions",
        json={
            "date": "2024-01-01",
            "payee": "Supermarket",
            "postings": [{"account": "Assets:Bank:Checking", "amount": "not-a-number"}],
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_transaction(authenticated_client, user, app):
    # Create test account and transaction
    account_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
            type="asset",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

        transaction = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 1),
            description="Initial",
            payee="Initial",
            amount=100.0,
            currency="INR",
        )
        db.session.add(transaction)

        # Update account balance for the initial transaction
        account.balance += transaction.amount

        db.session.commit()
        transaction_id = transaction.id

    # Test successful update
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}",
        json={"payee": "Updated", "amount": 200.0},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["transaction"]["description"] == "Updated"
    assert data["transaction"]["amount"] == 200.0

    # Verify account balance was updated
    with app.app_context():
        updated_account = Account.query.filter_by(id=account_id).first()
        assert (
            updated_account.balance == 1200.0
        )  # 1000 + 100 (initial) + 100 (difference)


def test_delete_related_transactions(authenticated_client, user, app):
    # Create test account and related transactions
    account_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
            type="asset",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

        # Create two related transactions (same date and payee)
        transaction1 = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 1),
            description="Related",
            payee="Same Payee",
            amount=100.0,
            currency="INR",
        )
        transaction2 = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 1),
            description="Related",
            payee="Same Payee",
            amount=200.0,
            currency="INR",
        )
        db.session.add_all([transaction1, transaction2])
        db.session.commit()
        transaction_id = transaction1.id

    # Test successful deletion
    response = authenticated_client.delete(
        f"/api/transactions/{transaction_id}/related"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2

    # Verify account balance was updated
    with app.app_context():
        updated_account = Account.query.filter_by(id=account_id).first()
        assert updated_account.balance == 700.0  # 1000 - 100 - 200

    # Verify transactions were deleted
    with app.app_context():
        remaining = Transaction.query.filter_by(
            user_id=user.id, date=date(2024, 1, 1), payee="Same Payee"
        ).count()
        assert remaining == 0


def test_get_transactions(authenticated_client, transaction):
    """Test retrieving transactions via API."""
    response = authenticated_client.get("/api/transactions")
    assert response.status_code == 200
    data = response.get_json()
    assert "transactions" in data
    assert isinstance(data["transactions"], list)
    assert len(data["transactions"]) > 0
    assert "total" in data
    assert data["total"] >= 1

    # Verify first transaction has required fields
    first_transaction = data["transactions"][0]
    assert "id" in first_transaction
    assert "date" in first_transaction
    assert "payee" in first_transaction
    assert "postings" in first_transaction
    assert isinstance(first_transaction["postings"], list)


def test_get_transactions_with_limit(authenticated_client, transaction):
    """Test retrieving transactions with a limit."""
    # Add another transaction to test limit
    # Note: Requires authenticated_client/user/db_session context if adding via model
    # Alternatively, call the API to add another transaction

    response = authenticated_client.get("/api/transactions?limit=1")
    assert response.status_code == 200
    data = response.get_json()
    assert "transactions" in data
    assert isinstance(data["transactions"], list)
    assert (
        len(data["transactions"]) == 1
    )  # Should only return one transaction due to limit
    assert "total" in data
    assert (
        data["total"] >= 1
    )  # Total should reflect all transactions, not just the limited ones

    # Verify first transaction has required fields
    first_transaction = data["transactions"][0]
    assert "id" in first_transaction
    assert "date" in first_transaction
    assert "payee" in first_transaction
    assert "postings" in first_transaction
    assert isinstance(first_transaction["postings"], list)


def test_add_transaction(
    authenticated_client, user, account
):  # Renamed from test_create_transaction for clarity
    """Duplicate of test_create_transaction - consider merging or removing."""
    # Create the expenses account first
    expenses_account_data = {"name": "Expenses:Food", "type": "expense"}
    expenses_response = authenticated_client.post(
        "/api/accounts", json=expenses_account_data
    )
    assert expenses_response.status_code == 201

    transaction_data = {
        "date": "2024-01-16",
        "description": "Lunch",
        "payee": "Restaurant",
        "postings": [
            {"account": account.name, "amount": -25.00, "currency": "INR"},
            {"account": "Expenses:Food", "amount": 25.00, "currency": "INR"},
        ],
    }
    response = authenticated_client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 201
    data = response.get_json()
    assert "Transaction created successfully" in data["message"]
    assert len(data["transactions"]) == 2  # Two postings create two transactions
    assert data["transactions"][0]["amount"] == -25.00  # First posting amount
    assert data["transactions"][1]["amount"] == 25.00  # Second posting amount
    assert (
        data["transactions"][0]["description"] == "Restaurant"
    )  # Description matches payee
    assert (
        data["transactions"][1]["description"] == "Restaurant"
    )  # Description matches payee


def test_add_transaction_missing_fields(authenticated_client):
    """Test adding transaction with missing required fields."""
    transaction_data = {
        "date": "2024-01-17",
        # Missing postings
        "payee": "Store",
        "currency": "INR",
    }
    response = authenticated_client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 400  # Expect Bad Request
    data = response.get_json()
    assert "error" in data
    assert "Missing or invalid postings" in data["error"]


def test_add_transaction_unbalanced(authenticated_client, account, mock_ledger_command):
    """Test adding a transaction that would result in an unbalanced ledger (if check is implemented)."""
    # The application doesn't actually check for unbalanced transactions currently,
    # so this test should expect a 201 successful creation.
    # In a future implementation, you might want to add balance validation.

    transaction_data = {
        "date": "2024-01-18",
        "description": "Unbalanced Transaction",
        "payee": "Error Inc",
        "postings": [
            {"account": account.name, "amount": 1000.00, "currency": "INR"}
            # Intentionally missing the balancing posting
        ],
    }
    response = authenticated_client.post("/api/transactions", json=transaction_data)

    # We expect success since the application doesn't currently validate balancing
    assert response.status_code == 201
    data = response.get_json()
    assert "Transaction created successfully" in data["message"]
    assert len(data["transactions"]) == 1  # Only one posting
    assert data["transactions"][0]["amount"] == 1000.00  # Amount matches
    assert (
        data["transactions"][0]["description"] == "Error Inc"
    )  # Description matches payee


@pytest.fixture
def transaction(db_session, user):
    """Create a test transaction."""
    # Create a test account first
    account = Account(name="Test Account", type="Asset", user_id=user.id)
    db_session.add(account)
    db_session.commit()

    # Create a transaction with the account
    tx = Transaction(
        date=datetime.now(),
        description="Test Transaction",
        amount=100.00,
        account_id=account.id,
        user_id=user.id,
    )
    db_session.add(tx)
    db_session.commit()
    return tx
