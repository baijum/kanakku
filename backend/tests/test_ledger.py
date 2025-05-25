from datetime import date, timedelta

import pytest

from app import db
from app.models import Account, Book, Preamble, Transaction, User


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


@pytest.fixture
def preamble(app, db_session, user):
    """Create a test preamble for the user."""
    with app.app_context():
        existing_preamble = Preamble.query.filter_by(
            user_id=user.id, is_default=True
        ).first()
        if existing_preamble:
            return existing_preamble

        preamble = Preamble(
            user_id=user.id,
            name="Default Preamble",
            content="account Assets:Cash INR\naccount Expenses:Food INR",
            is_default=True,
        )
        db_session.add(preamble)
        db_session.commit()
        return preamble


@pytest.fixture
def non_default_preamble(app, db_session, user):
    """Create a non-default test preamble for the user."""
    with app.app_context():
        existing_preamble = Preamble.query.filter_by(
            user_id=user.id, name="Non-Default Preamble"
        ).first()
        if existing_preamble:
            return existing_preamble

        preamble = Preamble(
            user_id=user.id,
            name="Non-Default Preamble",
            content="account Assets:Bank INR\naccount Expenses:Entertainment INR",
            is_default=False,
        )
        db_session.add(preamble)
        db_session.commit()
        return preamble


@pytest.fixture
def book(app, db_session, user):
    """Create a test book for the user"""
    with app.app_context():
        book = Book.query.filter_by(user_id=user.id).first()
        if book:
            return book

        book = Book(user_id=user.id, name="Test Book")
        db_session.add(book)
        db_session.commit()
        return book


@pytest.fixture
def sample_transactions(app, db_session, user, book):
    """Create sample transactions for testing date filtering."""
    with app.app_context():
        # Use the book from the fixture
        book = Book.query.filter_by(user_id=user.id).first()

        # Set as active book if not already
        if not user.active_book_id:
            user.active_book_id = book.id
            db.session.commit()

        # Check for account
        test_account = Account.query.filter_by(
            user_id=user.id, name="Test Account"
        ).first()
        if not test_account:
            test_account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Test Account",
                balance=1000.0,
                currency="INR",
            )
            db_session.add(test_account)
            db_session.commit()
            # Refresh
            test_account = Account.query.filter_by(
                user_id=user.id, name="Test Account"
            ).first()

        # Create transactions with different dates
        transactions = []

        # Check if transactions already exist for this test
        existing_tx = Transaction.query.filter_by(
            user_id=user.id, description="Past Transaction"
        ).first()
        if existing_tx:
            # If transactions for this test already exist, return them
            return Transaction.query.filter(
                Transaction.user_id == user.id,
                Transaction.description.in_(
                    [
                        "Past Transaction",
                        "Recent Transaction",
                        "Today Transaction",
                        "USD Transaction",
                        "Pending Transaction",
                    ]
                ),
            ).all()

        # Past transaction
        past_tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=test_account.id,
            date=date.today() - timedelta(days=30),
            description="Past Transaction",
            payee="Past Vendor",
            amount=-50.00,
            currency="INR",
        )
        db_session.add(past_tx)
        transactions.append(past_tx)

        # Recent transaction
        recent_tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=test_account.id,
            date=date.today() - timedelta(days=5),
            description="Recent Transaction",
            payee="Recent Vendor",
            amount=-25.00,
            currency="INR",
        )
        db_session.add(recent_tx)
        transactions.append(recent_tx)

        # Today's transaction
        today_tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=test_account.id,
            date=date.today(),
            description="Today Transaction",
            payee="Today Vendor",
            amount=-10.00,
            currency="INR",
        )
        db_session.add(today_tx)
        transactions.append(today_tx)

        # Transaction with USD currency
        usd_tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=test_account.id,
            date=date.today() - timedelta(days=2),
            description="USD Transaction",
            payee="USD Vendor",
            amount=-15.00,
            currency="USD",
        )
        db_session.add(usd_tx)
        transactions.append(usd_tx)

        # Transaction with pending status
        pending_tx = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=test_account.id,
            date=date.today() - timedelta(days=1),
            description="Pending Transaction",
            payee="Pending Vendor",
            amount=-30.00,
            currency="INR",
            status="pending",
        )
        db_session.add(pending_tx)
        transactions.append(pending_tx)

        db_session.commit()
        return transactions


def test_get_transactions(authenticated_client, app, db_session, user):
    """Test getting transactions for a user."""
    with db_session.no_autoflush:
        # First, ensure user has an active book
        book = Book.query.filter_by(user_id=user.id).first()
        if not book:
            # Create a book if it doesn't exist
            book = Book(user_id=user.id, name="Test Book")
            db_session.add(book)
            db_session.commit()

        # Set as active book if not already
        if not user.active_book_id:
            user.active_book_id = book.id
            db_session.commit()

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
                book_id=book.id,  # Set the book_id here
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
        "description": "A savings account",
    }

    # WHEN I submit a POST request with valid account data
    response = authenticated_client.post("/api/v1/accounts", json=account_data)

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


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_get_transactions_ledger_format(authenticated_client, app, db_session, user):
    """Test getting transactions in ledger format."""
    with app.app_context():
        # Fetch user and the specific test account within this session context
        attached_user = db_session.get(User, user.id)

        # First, ensure user has an active book
        book = Book.query.filter_by(user_id=user.id).first()
        if not book:
            # Create a book if it doesn't exist
            book = Book(user_id=user.id, name="Test Book")
            db_session.add(book)
            db_session.commit()

        # Set as active book if not already
        if not user.active_book_id:
            user.active_book_id = book.id
            db_session.commit()

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
                book_id=book.id,  # Set the book_id here
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
            book_id=book.id,  # Set the book_id here for the transaction
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
        assert "2024-07-27 Grocery Shopping" in text
        assert "Test Account" in text
        assert "-75.50" in text


def test_get_transactions_ledger_format_with_date_filters(
    authenticated_client, app, db_session, user, sample_transactions
):
    """Test getting transactions in ledger format with date filters."""
    # Set the start date to 7 days ago and end date to today
    start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    response = authenticated_client.get(
        f"/api/v1/ledgertransactions?startDate={start_date}&endDate={end_date}"
    )

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    # The response should include only transactions from the last 7 days
    text = response.text
    assert "Recent Transaction" in text
    assert "Today Transaction" in text
    assert "USD Transaction" in text
    assert "Pending Transaction" in text

    # Should not include the past transaction (30 days ago)
    assert "Past Transaction" not in text


def test_get_transactions_ledger_format_with_default_preamble(
    authenticated_client, app, db_session, user, sample_transactions, preamble
):
    """Test getting transactions with default preamble."""
    response = authenticated_client.get("/api/v1/ledgertransactions")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    # Check that the default preamble content is included
    text = response.text
    assert "account Assets:Cash INR" in text
    assert "account Expenses:Food INR" in text

    # Also verify transactions are included
    assert "Today Transaction" in text


def test_get_transactions_ledger_format_with_specific_preamble(
    authenticated_client,
    app,
    db_session,
    user,
    sample_transactions,
    preamble,
    non_default_preamble,
):
    """Test getting transactions with a specific preamble."""
    with app.app_context():
        # Get the preamble ID within the app context
        specific_preamble = Preamble.query.filter_by(
            user_id=user.id, name="Non-Default Preamble"
        ).first()

        if not specific_preamble:
            pytest.fail("Non-default preamble not found")

        preamble_id = specific_preamble.id

        response = authenticated_client.get(
            f"/api/v1/ledgertransactions?preamble_id={preamble_id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "text/plain"

        # Check that the specific preamble content is included
        text = response.text
        assert "account Assets:Bank INR" in text
        assert "account Expenses:Entertainment INR" in text

        # The default preamble content should not be present
        assert "account Assets:Cash INR" not in text

        # Verify transactions are included
        assert "Today Transaction" in text


def test_get_transactions_ledger_format_status(
    authenticated_client, app, db_session, user, sample_transactions
):
    """Test getting transactions in ledger format with a status."""
    response = authenticated_client.get("/api/v1/ledgertransactions")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    # Check that the transaction status is included in the output
    text = response.text
    assert "pending Pending Transaction" in text


def test_get_transactions_ledger_format_empty(
    authenticated_client, app, db_session, user
):
    """Test getting transactions when there are no transactions."""
    # Delete any existing transactions for the user
    with app.app_context():
        Transaction.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    response = authenticated_client.get("/api/v1/ledgertransactions")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert response.text == ""


def test_get_transactions_ledger_format_currency_formatting(
    authenticated_client, app, db_session, user, sample_transactions
):
    """Test that different currencies are formatted correctly in the ledger output."""
    response = authenticated_client.get("/api/v1/ledgertransactions")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    text = response.text

    # Check INR formatting - should use ₹ symbol
    assert "₹-10.00" in text

    # Check USD formatting - should not use ₹ symbol
    assert "-15.00 USD" in text


def test_get_transactions_ledger_format_unauthorized(client):
    """Test that unauthorized users cannot access ledger transactions."""
    response = client.get("/api/v1/ledgertransactions")

    assert response.status_code == 401
    assert "error" in response.json
    assert "Authentication required" in response.json["error"]


def test_get_transactions_ledger_format_invalid_date_formats(
    authenticated_client, app, db_session, user, sample_transactions
):
    """Test ledger transactions endpoint with invalid date formats."""
    # Test with invalid start date format
    response = authenticated_client.get(
        "/api/v1/ledgertransactions?startDate=01-01-2024"  # MM-DD-YYYY instead of YYYY-MM-DD
    )

    assert response.status_code == 200  # Should still return 200
    assert response.mimetype == "text/plain"

    # All transactions should be included since the invalid date was ignored
    text = response.text
    assert "Past Transaction" in text
    assert "Recent Transaction" in text

    # Test with invalid end date format
    response = authenticated_client.get(
        "/api/v1/ledgertransactions?endDate=12/31/2024"  # MM/DD/YYYY instead of YYYY-MM-DD
    )

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    # All transactions should be included since the invalid date was ignored
    text = response.text
    assert "Past Transaction" in text
    assert "Recent Transaction" in text


@pytest.mark.parametrize("exception_type", [ValueError, TypeError, Exception])
def test_get_transactions_ledger_format_with_exceptions(
    authenticated_client, app, db_session, user, mocker, exception_type
):
    """Test ledger transactions endpoint with various exceptions."""
    # Mock the db.session.query to raise the specified exception
    mocker.patch(
        "app.ledger.db.session.query", side_effect=exception_type("Test exception")
    )

    response = authenticated_client.get("/api/v1/ledgertransactions")

    # Should return a 500 error with a specific error message
    assert response.status_code == 500
    assert response.json["error"] == "Failed to generate ledger format"


def test_user_not_found_after_decorator(client):  # Use regular client without auth
    """Test scenario where user is not found after decorator execution."""
    # API endpoint should return 401 for unauthorized requests
    response = client.get("/api/v1/ledgertransactions")

    assert response.status_code == 401
    assert response.json["error"] == "Authentication required"
