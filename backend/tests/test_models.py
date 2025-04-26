import pytest
from app.models import User, Transaction, Account, Book
from datetime import date


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(db_session):
    """Create a test user."""
    user = User(email="test@example.com")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def book(db_session, user):
    """Create a test book."""
    book = Book(user_id=user.id, name="Test Book")
    db_session.add(book)
    db_session.commit()

    # Set as active book
    user.active_book_id = book.id
    db_session.commit()

    return book


def test_user_creation(db_session, user):
    """Test creating a user."""
    assert user.email == "test@example.com"
    assert user.check_password("password123")


def test_transaction_creation(db_session, user, book):
    """Test creating a transaction."""
    transaction = Transaction(
        user_id=user.id,
        book_id=book.id,
        date=date(2024, 1, 1),
        description="Test transaction",
        payee="Test payee",
        amount=100.0,
        currency="INR",
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None
    assert transaction.user_id == user.id
    assert transaction.description == "Test transaction"
    assert transaction.amount == 100.0


def test_account_creation(db_session, user, book):
    """Test creating an account."""
    account = Account(
        user_id=user.id,
        book_id=book.id,
        name="Test Account",
        currency="INR",
        balance=1000.0,
    )
    db_session.add(account)
    db_session.commit()

    assert account.id is not None
    assert account.user_id == user.id
    assert account.name == "Test Account"
    assert account.balance == 1000.0


def test_user_transactions_relationship(db_session, user, book):
    """Test the relationship between a user and their transactions."""
    transaction = Transaction(
        user_id=user.id,
        book_id=book.id,
        date=date(2024, 1, 1),
        description="Test transaction",
        payee="Test payee",
        amount=100.0,
        currency="INR",
    )
    db_session.add(transaction)
    db_session.commit()

    # Refresh user to get updated relationships
    db_session.refresh(user)

    assert user.transactions[0].description == "Test transaction"
    assert transaction.user.email == "test@example.com"


def test_user_accounts_relationship(db_session, user, book):
    """Test the relationship between a user and their accounts."""
    account = Account(
        user_id=user.id,
        book_id=book.id,
        name="Test Account",
        currency="INR",
        balance=1000.0,
    )
    db_session.add(account)
    db_session.commit()

    # Refresh user to get updated relationships
    db_session.refresh(user)

    assert user.accounts[0].name == "Test Account"
    assert account.user.email == "test@example.com"
