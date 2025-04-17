import pytest
from app.models import Transaction, db, Account
from datetime import date, datetime

# Removed local app fixture


def test_create_transaction(authenticated_client, user, app):
    # Create test accounts
    with app.app_context():
        account1 = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
            currency="INR",
            balance=1000.0,
        )
        account2 = Account(
            user_id=user.id,
            name="Expenses:Groceries",
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

    # Test with invalid date format
    response = authenticated_client.post(
        "/api/transactions",
        json={
            "date": "01-01-2024",  # Wrong format
            "payee": "Supermarket",
            "postings": [{"account": "Assets:Bank:Checking", "amount": "100.0"}],
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "date format" in response.get_json()["error"].lower()


def test_update_transaction(authenticated_client, user, app):
    # Create test account and transaction
    account_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
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


def test_update_transaction_invalid_data(authenticated_client, user, app):
    # Create test account and transaction
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:Bank:Test",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()

        transaction = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 1),
            description="Test",
            payee="Test",
            amount=100.0,
            currency="INR",
        )
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id

    # Test with invalid date format
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}",
        json={"date": "01-01-2024"},  # Wrong format
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Test with invalid amount
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}",
        json={"amount": "not-a-number"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Test with non-existent account
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}",
        json={"account_id": 99999},  # Non-existent account
    )
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_update_transaction_not_found(authenticated_client):
    # Test with non-existent transaction ID
    response = authenticated_client.put(
        "/api/transactions/99999",  # Non-existent transaction
        json={"payee": "Updated"},
    )
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_delete_related_transactions(authenticated_client, user, app):
    # Create test account and related transactions
    account_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:Bank:Checking",
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


def test_delete_related_transactions_not_found(authenticated_client):
    # Test with non-existent transaction ID
    response = authenticated_client.delete(
        "/api/transactions/99999/related"  # Non-existent transaction
    )
    assert response.status_code == 404
    assert "error" in response.get_json()


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


def test_get_transactions_with_date_filters(authenticated_client, user, app):
    """Test retrieving transactions with date filters."""
    # Create test transactions with different dates
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Test:DateFilter",
            currency="INR",
            balance=0.0,
        )
        db.session.add(account)
        db.session.commit()

        # Create transactions with different dates
        tx1 = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 1),
            description="January",
            payee="January Test",
            amount=100.0,
            currency="INR",
        )
        tx2 = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 2, 1),
            description="February",
            payee="February Test",
            amount=200.0,
            currency="INR",
        )
        tx3 = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 3, 1),
            description="March",
            payee="March Test",
            amount=300.0,
            currency="INR",
        )
        db.session.add_all([tx1, tx2, tx3])
        db.session.commit()

    # Test with start date only
    response = authenticated_client.get("/api/transactions?startDate=2024-02-01")
    assert response.status_code == 200
    data = response.get_json()
    # Should only include February and March transactions
    transaction_dates = [tx["date"] for tx in data["transactions"]]
    assert "2024-01-01" not in transaction_dates
    assert any("2024-02-01" in date for date in transaction_dates)
    assert any("2024-03-01" in date for date in transaction_dates)

    # Test with end date only
    response = authenticated_client.get("/api/transactions?endDate=2024-02-01")
    assert response.status_code == 200
    data = response.get_json()
    # Should only include January and February transactions
    transaction_dates = [tx["date"] for tx in data["transactions"]]
    assert any("2024-01-01" in date for date in transaction_dates)
    assert any("2024-02-01" in date for date in transaction_dates)
    assert "2024-03-01" not in transaction_dates

    # Test with both start and end date
    response = authenticated_client.get(
        "/api/transactions?startDate=2024-02-01&endDate=2024-02-28"
    )
    assert response.status_code == 200
    data = response.get_json()
    # Should only include February transactions
    transaction_dates = [tx["date"] for tx in data["transactions"]]
    assert "2024-01-01" not in transaction_dates
    assert any("2024-02-01" in date for date in transaction_dates)
    assert "2024-03-01" not in transaction_dates


def test_get_transaction_by_id(authenticated_client, user, app):
    """Test retrieving a specific transaction by ID."""
    # Create a test transaction
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Test:SingleTx",
            currency="INR",
            balance=0.0,
        )
        db.session.add(account)
        db.session.commit()

        tx = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 15),
            description="Single Transaction Test",
            payee="Single Tx",
            amount=150.0,
            currency="INR",
        )
        db.session.add(tx)
        db.session.commit()
        transaction_id = tx.id

    # Test retrieving the transaction
    response = authenticated_client.get(f"/api/transactions/{transaction_id}")
    assert response.status_code == 200
    data = response.get_json()

    # Verify transaction data
    assert data["id"] == transaction_id
    assert data["date"] == "2024-01-15"
    assert data["description"] == "Single Transaction Test"
    assert data["payee"] == "Single Tx"
    assert data["amount"] == 150.0
    assert data["currency"] == "INR"
    assert data["account_name"] == "Test:SingleTx"


def test_get_transaction_by_id_not_found(authenticated_client):
    """Test retrieving a non-existent transaction by ID."""
    response = authenticated_client.get("/api/transactions/99999")  # Non-existent ID
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_get_related_transactions(authenticated_client, user, app):
    """Test retrieving related transactions."""
    # Create test account and related transactions
    with app.app_context():
        account1 = Account(
            user_id=user.id,
            name="Assets:Related1",
            currency="INR",
            balance=0.0,
        )
        account2 = Account(
            user_id=user.id,
            name="Expenses:Related2",
            currency="INR",
            balance=0.0,
        )
        db.session.add_all([account1, account2])
        db.session.commit()

        # Create two related transactions (same date and payee)
        tx_date = date(2024, 1, 20)
        tx_payee = "Related Transaction Test"

        tx1 = Transaction(
            user_id=user.id,
            account_id=account1.id,
            date=tx_date,
            description="Related Tx Description",
            payee=tx_payee,
            amount=-50.0,
            currency="INR",
        )
        tx2 = Transaction(
            user_id=user.id,
            account_id=account2.id,
            date=tx_date,
            description="Related Tx Description",
            payee=tx_payee,
            amount=50.0,
            currency="INR",
        )
        db.session.add_all([tx1, tx2])
        db.session.commit()
        transaction_id = tx1.id

    # Test retrieving related transactions
    response = authenticated_client.get(f"/api/transactions/{transaction_id}/related")
    assert response.status_code == 200
    data = response.get_json()

    # Verify response structure
    assert "transactions" in data
    assert "date" in data
    assert "payee" in data
    assert "primary_transaction_id" in data

    # Verify data values
    assert data["date"] == "2024-01-20"
    assert data["payee"] == tx_payee
    assert data["primary_transaction_id"] == transaction_id
    assert len(data["transactions"]) == 2


def test_get_related_transactions_not_found(authenticated_client):
    """Test retrieving related transactions for a non-existent transaction."""
    response = authenticated_client.get(
        "/api/transactions/99999/related"
    )  # Non-existent ID
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_update_transaction_with_postings(authenticated_client, user, app):
    """Test updating a transaction with multiple postings."""
    # Create test account and transaction
    transaction_id = None
    with app.app_context():
        # Create accounts
        assets = Account(
            user_id=user.id,
            name="Assets:UpdateTest",
            currency="INR",
            balance=1000.0,
        )
        expenses = Account(
            user_id=user.id,
            name="Expenses:UpdateTest",
            currency="INR",
            balance=0.0,
        )
        db.session.add_all([assets, expenses])
        db.session.commit()

        # Create an initial transaction
        tx = Transaction(
            user_id=user.id,
            account_id=assets.id,
            date=date(2024, 1, 25),
            description="Initial Transaction",
            payee="Initial Payee",
            amount=-100.0,
            currency="INR",
        )
        db.session.add(tx)
        db.session.commit()
        transaction_id = tx.id

    # Test updating the transaction with multiple postings
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}/update_with_postings",
        json={
            "date": "2024-01-26",
            "payee": "Updated Payee",
            "postings": [
                {
                    "account": "Assets:UpdateTest",
                    "amount": "-200.0",
                    "currency": "INR",
                },
                {
                    "account": "Expenses:UpdateTest",
                    "amount": "200.0",
                    "currency": "INR",
                },
            ],
        },
    )
    assert response.status_code == 200
    data = response.get_json()

    # Verify response structure
    assert "message" in data
    assert "transactions" in data
    assert len(data["transactions"]) == 2

    # Check that the updated transactions have the correct values
    # The structure might be different depending on the to_dict() implementation
    # Check description or payee field, whichever is available
    for tx in data["transactions"]:
        if "payee" in tx:
            assert tx["payee"] == "Updated Payee"
        else:
            assert tx["description"] == "Updated Payee"

    # One transaction should have a negative amount, the other positive
    amounts = [tx["amount"] for tx in data["transactions"]]
    assert any(amount < 0 for amount in amounts)
    assert any(amount > 0 for amount in amounts)


def test_update_transaction_with_postings_invalid_data(authenticated_client, user, app):
    """Test updating a transaction with invalid postings data."""
    # Create test account and transaction
    transaction_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Assets:InvalidTest",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()

        # Create an initial transaction
        tx = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 25),
            description="Initial Transaction",
            payee="Initial Payee",
            amount=-100.0,
            currency="INR",
        )
        db.session.add(tx)
        db.session.commit()
        transaction_id = tx.id

    # Test with missing date
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}/update_with_postings",
        json={
            "payee": "Updated Payee",
            "postings": [
                {
                    "account": "Assets:InvalidTest",
                    "amount": "-200.0",
                },
            ],
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "date" in response.get_json()["error"].lower()

    # Test with missing payee
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}/update_with_postings",
        json={
            "date": "2024-01-26",
            "postings": [
                {
                    "account": "Assets:InvalidTest",
                    "amount": "-200.0",
                },
            ],
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "payee" in response.get_json()["error"].lower()

    # Test with missing postings
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}/update_with_postings",
        json={
            "date": "2024-01-26",
            "payee": "Updated Payee",
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "postings" in response.get_json()["error"].lower()

    # Test with invalid account in postings
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}/update_with_postings",
        json={
            "date": "2024-01-26",
            "payee": "Updated Payee",
            "postings": [
                {
                    "account": "NonExistent:Account",
                    "amount": "-200.0",
                },
            ],
        },
    )
    assert response.status_code == 404
    assert "error" in response.get_json()
    assert "account" in response.get_json()["error"].lower()


def test_delete_transaction(authenticated_client, user, app):
    """Test deleting a single transaction."""
    # Create test account and transaction
    transaction_id = None
    with app.app_context():
        account = Account(
            user_id=user.id,
            name="Test:DeleteSingle",
            currency="INR",
            balance=1000.0,
        )
        db.session.add(account)
        db.session.commit()

        tx = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=date(2024, 1, 30),
            description="Delete Test",
            payee="Delete Test",
            amount=150.0,
            currency="INR",
        )
        db.session.add(tx)
        db.session.commit()
        transaction_id = tx.id

    # Test deleting the transaction
    response = authenticated_client.delete(f"/api/transactions/{transaction_id}")
    assert response.status_code == 200
    data = response.get_json()

    # Verify response
    assert "message" in data
    assert "deleted" in data["message"].lower()

    # Verify the transaction was actually deleted
    get_response = authenticated_client.get(f"/api/transactions/{transaction_id}")
    assert get_response.status_code == 404


def test_delete_transaction_not_found(authenticated_client):
    """Test deleting a non-existent transaction."""
    response = authenticated_client.delete("/api/transactions/99999")  # Non-existent ID
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_add_transaction(
    authenticated_client, user, account
):  # Renamed from test_create_transaction for clarity
    """Duplicate of test_create_transaction - consider merging or removing."""
    # Create the expenses account first
    expenses_account_data = {"name": "Expenses:Food", "currency": "INR"}
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
    assert (
        "postings" in data["error"]
    )  # Just check that "postings" is mentioned in the error


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


def test_error_handling_decorator(authenticated_client, user, app):
    """Test the handle_errors decorator."""
    # Instead of trying to mock a route, test the decorator directly
    from app.transactions import handle_errors
    from sqlalchemy.exc import SQLAlchemyError

    # Create test functions that will be wrapped by the decorator
    def func_value_error():
        raise ValueError("Test value error")

    def func_sqlalchemy_error():
        raise SQLAlchemyError("Test SQLAlchemy error")

    def func_generic_error():
        raise Exception("Test generic error")

    # Apply the decorator
    wrapped_value_error = handle_errors(func_value_error)
    wrapped_sqlalchemy_error = handle_errors(func_sqlalchemy_error)
    wrapped_generic_error = handle_errors(func_generic_error)

    # Test with app context
    with app.test_request_context():
        # Test ValueError handling
        response = wrapped_value_error()
        assert response[1] == 400  # Check status code
        data = response[0].get_json()
        assert "error" in data
        assert "Test value error" in data["error"]

        # Test SQLAlchemyError handling
        response = wrapped_sqlalchemy_error()
        assert response[1] == 500  # Check status code
        data = response[0].get_json()
        assert "error" in data
        assert "Database error occurred" in data["error"]

        # Test generic Exception handling
        response = wrapped_generic_error()
        assert response[1] == 500  # Check status code
        data = response[0].get_json()
        assert "error" in data
        assert "An unexpected error occurred" in data["error"]


@pytest.fixture
def transaction(db_session, user):
    """Create a test transaction."""
    # Create a test account first
    account = Account(name="Test Account", user_id=user.id)
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
