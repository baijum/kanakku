import pytest
from datetime import date
from app import db
from app.models import User, Transaction, Account


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


@pytest.fixture
def account(app, db_session):
    with app.app_context():
        # Create a test user first
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(email="test@example.com")
            user.set_password("password")
            db_session.add(user)
            db_session.commit()

        # Create an account
        existing_account = Account.query.filter_by(name="Test Account").first()
        if existing_account:
            return existing_account

        account = Account(
            user_id=user.id,
            name="Test Account",
            balance=1000.00,
            currency="INR",
        )
        db_session.add(account)
        db_session.commit()
        return account


def test_get_transactions(authenticated_client, app, db_session, user):
    """Test getting transactions for a user."""
    with db_session.no_autoflush:
        # Fetch the known test account within this session using the user
        test_account = (
            db_session.query(Account)
            .filter_by(user_id=user.id, name="Test Account")
            .first()
        )
        if not test_account:
            # If it doesn't exist for some reason (e.g., fixture failed), create it
            test_account = Account(
                user_id=user.id,
                name="Test Account",
                balance=1000.0,
                currency="INR",
            )
            db_session.add(test_account)
            db_session.commit()
            # Need to re-fetch after commit if created here
            test_account = (
                db_session.query(Account)
                .filter_by(user_id=user.id, name="Test Account")
                .first()
            )
            if not test_account:
                pytest.fail("Failed to create or find Test Account in session")

        transaction_data = {
            "date": "2024-01-01",
            "description": "Test transaction for ledger test",
            "payee": "Test Payee",
            "postings": [
                {"account": test_account.name, "amount": 100.00, "currency": "INR"}
            ],
        }

        post_response = authenticated_client.post(
            "/api/v1/transactions", json=transaction_data
        )
        assert post_response.status_code == 201

        get_response = authenticated_client.get("/api/v1/transactions")
        assert get_response.status_code == 200
        response_data = get_response.get_json()
        assert isinstance(response_data, dict)
        assert "transactions" in response_data
        assert "total" in response_data
        assert isinstance(response_data["transactions"], list)
        assert len(response_data["transactions"]) >= 1

        found = False
        for tx in response_data["transactions"]:
            if tx.get("payee") == "Test Payee":
                found = True
                break
        assert found, "Test transaction not found in GET response"


def test_create_account(authenticated_client, user, db_session):
    """Test creating an account via the API."""
    # GIVEN a user and form data for a new account
    account_data = {
        "name": "Assets:Savings",
        "currency": "INR",
        "description": "A savings account"
    }

    # WHEN I submit a POST request with valid account data
    response = authenticated_client.post("/api/accounts", json=account_data)

    # THEN the response should indicate success
    assert response.status_code == 201, f"Failed to create account: {response.data}"
    data = response.get_json()
    assert "account" in data
    assert data["account"]["name"] == "Assets:Savings"

    # AND the account should exist in the database
    with db_session.no_autoflush:
        # Fetch user within this session context
        attached_user = db_session.get(User, user.id)
        if not attached_user:
            pytest.fail("User fixture could not be re-fetched in session")
        new_account = (
            db_session.query(Account)
            .filter_by(user_id=attached_user.id, name="Assets:Savings")
            .first()
        )
        assert new_account is not None


def test_get_transactions_ledger_format(authenticated_client, app, db_session, user):
    """Test getting transactions in ledger format."""
    with db_session.no_autoflush:
        # Fetch user and the specific test account within this session context
        attached_user = db_session.get(User, user.id)
        # Fetch account by name and user ID
        test_account = (
            db_session.query(Account)
            .filter_by(user_id=user.id, name="Test Account")
            .first()
        )

        if not attached_user:
            pytest.fail("User fixture could not be re-fetched in session")
        if not test_account:
            # If the account doesn't exist (e.g., fixture setup issue), create it here
            test_account = Account(
                user_id=user.id,
                name="Test Account",
                balance=1000.0,
                currency="INR",
            )
            db_session.add(test_account)
            db_session.commit()
            # Re-fetch after commit
            test_account = (
                db_session.query(Account)
                .filter_by(user_id=user.id, name="Test Account")
                .first()
            )
            if not test_account:
                pytest.fail("Failed to create or find Test Account within test")

        transaction = Transaction(
            user_id=attached_user.id,
            account_id=test_account.id,  # Use ID from fetched account
            date=date(2024, 7, 27),
            description="Grocery Shopping",
            payee="Local Mart",
            amount=-75.50,
            currency="INR",
        )
        db_session.add(transaction)
        db_session.commit()

        response = authenticated_client.get("/api/v1/ledgertransactions")

        assert response.status_code == 200
        assert response.mimetype == "text/plain"

        # Check the key parts of the response instead of the exact format
        text = response.text
        assert "2024-07-27 * Grocery Shopping" in text
        assert "Test Account" in text
        assert "-75.50" in text
