from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Account, Book, Transaction, User, db


@pytest.fixture
def setup_books_and_accounts(app):
    """Set up users with books and accounts for integration testing."""
    with app.app_context():
        # Create a test user
        user = User(email="integration@example.com")
        user.set_password("password123")
        user.is_active = True
        db.session.add(user)
        db.session.commit()

        # Create two books for the user
        personal_book = Book(user_id=user.id, name="Personal")
        business_book = Book(user_id=user.id, name="Business")
        db.session.add_all([personal_book, business_book])
        db.session.commit()

        # Set the personal book as active
        user.active_book_id = personal_book.id
        db.session.commit()

        # Create accounts in personal book
        checking = Account(
            user_id=user.id, book_id=personal_book.id, name="Checking", balance=1000.0
        )

        savings = Account(
            user_id=user.id, book_id=personal_book.id, name="Savings", balance=5000.0
        )

        # Create accounts in business book
        business_checking = Account(
            user_id=user.id,
            book_id=business_book.id,
            name="Business Checking",
            balance=2000.0,
        )

        business_expense = Account(
            user_id=user.id,
            book_id=business_book.id,
            name="Business Expense",
            balance=0.0,
        )

        db.session.add_all([checking, savings, business_checking, business_expense])
        db.session.commit()

        # Store IDs to retrieve fresh instances in the tests
        data = {
            "user_id": user.id,
            "personal_book_id": personal_book.id,
            "business_book_id": business_book.id,
            "account_ids": {
                "checking": checking.id,
                "savings": savings.id,
                "business_checking": business_checking.id,
                "business_expense": business_expense.id,
            },
        }

    return data


def test_book_account_relationships(app, setup_books_and_accounts):
    """Test that accounts properly belong to their books."""
    data = setup_books_and_accounts

    with app.app_context():
        # Get personal book accounts
        personal_accounts = Account.query.filter_by(
            book_id=data["personal_book_id"]
        ).all()

        # Get business book accounts
        business_accounts = Account.query.filter_by(
            book_id=data["business_book_id"]
        ).all()

        # Check personal book accounts
        assert len(personal_accounts) == 2
        account_names = [account.name for account in personal_accounts]
        assert "Checking" in account_names
        assert "Savings" in account_names

        # Check business book accounts
        assert len(business_accounts) == 2
        account_names = [account.name for account in business_accounts]
        assert "Business Checking" in account_names
        assert "Business Expense" in account_names


def test_create_transaction_in_correct_book(app, setup_books_and_accounts):
    """Test creating transactions in different books."""
    data = setup_books_and_accounts

    with app.app_context():
        user = db.session.get(User, data["user_id"])
        personal_book = db.session.get(Book, data["personal_book_id"])
        business_book = db.session.get(Book, data["business_book_id"])

        # Create a transaction in the personal book
        personal_checking = Account.query.filter_by(
            book_id=personal_book.id, name="Checking"
        ).first()

        personal_savings = Account.query.filter_by(
            book_id=personal_book.id, name="Savings"
        ).first()

        personal_transaction = Transaction(
            user_id=user.id,
            book_id=personal_book.id,
            account_id=personal_checking.id,
            date=date.today(),
            description="Transfer to savings",
            payee="Self",
            amount=-500.0,
        )

        savings_transaction = Transaction(
            user_id=user.id,
            book_id=personal_book.id,
            account_id=personal_savings.id,
            date=date.today(),
            description="Transfer from checking",
            payee="Self",
            amount=500.0,
        )

        # Update account balances
        personal_checking.balance -= 500.0
        personal_savings.balance += 500.0

        db.session.add_all([personal_transaction, savings_transaction])
        db.session.commit()

        # Create a transaction in the business book
        business_checking = Account.query.filter_by(
            book_id=business_book.id, name="Business Checking"
        ).first()

        business_expense = Account.query.filter_by(
            book_id=business_book.id, name="Business Expense"
        ).first()

        business_transaction = Transaction(
            user_id=user.id,
            book_id=business_book.id,
            account_id=business_checking.id,
            date=date.today(),
            description="Business expense",
            payee="Vendor",
            amount=-200.0,
        )

        expense_transaction = Transaction(
            user_id=user.id,
            book_id=business_book.id,
            account_id=business_expense.id,
            date=date.today(),
            description="Business expense",
            payee="Vendor",
            amount=200.0,
        )

        # Update account balances
        business_checking.balance -= 200.0
        business_expense.balance += 200.0

        db.session.add_all([business_transaction, expense_transaction])
        db.session.commit()

        # Verify transactions are in correct books
        personal_transactions = Transaction.query.filter_by(
            book_id=personal_book.id
        ).all()

        business_transactions = Transaction.query.filter_by(
            book_id=business_book.id
        ).all()

        assert len(personal_transactions) == 2
        assert len(business_transactions) == 2

        # Verify account balances
        assert db.session.get(Account, personal_checking.id).balance == 500.0
        assert db.session.get(Account, personal_savings.id).balance == 5500.0
        assert db.session.get(Account, business_checking.id).balance == 1800.0
        assert db.session.get(Account, business_expense.id).balance == 200.0


def test_switching_active_book(app, setup_books_and_accounts):
    """Test switching the active book for a user."""
    data = setup_books_and_accounts

    with app.app_context():
        user = db.session.get(User, data["user_id"])
        personal_book = db.session.get(Book, data["personal_book_id"])
        business_book = db.session.get(Book, data["business_book_id"])

        # Verify initial state (personal book is active)
        assert user.active_book_id == personal_book.id

        # Switch to business book
        user.active_book_id = business_book.id
        db.session.commit()

        # Verify active book changed
        user_refreshed = db.session.get(User, user.id)
        assert user_refreshed.active_book_id == business_book.id

        # Check that accounts from active book are returned
        # Here we're simulating what the API would do
        active_accounts = Account.query.filter_by(
            user_id=user.id, book_id=user.active_book_id
        ).all()

        # Should get business accounts only
        assert len(active_accounts) == 2
        account_names = [account.name for account in active_accounts]
        assert "Business Checking" in account_names
        assert "Business Expense" in account_names


def test_account_uniqueness_per_book(app, setup_books_and_accounts):
    """Test that accounts with the same name can exist in different books."""
    data = setup_books_and_accounts

    with app.app_context():
        user = db.session.get(User, data["user_id"])
        personal_book = db.session.get(Book, data["personal_book_id"])
        business_book = db.session.get(Book, data["business_book_id"])

        # Create an account with the same name in both books
        personal_account = Account(
            user_id=user.id,
            book_id=personal_book.id,
            name="Shared Account Name",
            balance=100.0,
        )

        business_account = Account(
            user_id=user.id,
            book_id=business_book.id,
            name="Shared Account Name",
            balance=200.0,
        )

        db.session.add_all([personal_account, business_account])
        db.session.commit()

        # Verify both accounts exist
        personal_accounts = Account.query.filter_by(
            book_id=personal_book.id, name="Shared Account Name"
        ).all()

        business_accounts = Account.query.filter_by(
            book_id=business_book.id, name="Shared Account Name"
        ).all()

        assert len(personal_accounts) == 1
        assert len(business_accounts) == 1
        assert personal_accounts[0].id != business_accounts[0].id
        assert personal_accounts[0].balance == 100.0
        assert business_accounts[0].balance == 200.0

        # Try to create a duplicate account in the same book (should fail)
        duplicate_account = Account(
            user_id=user.id,
            book_id=personal_book.id,
            name="Shared Account Name",
            balance=300.0,
        )

        db.session.add(duplicate_account)

        # This should raise an IntegrityError due to the unique constraint
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_deleting_book_cascades_to_accounts_and_transactions(
    app, setup_books_and_accounts
):
    """Test that deleting a book also deletes all its accounts and transactions."""
    data = setup_books_and_accounts

    with app.app_context():
        user = db.session.get(User, data["user_id"])
        personal_book = db.session.get(Book, data["personal_book_id"])
        business_book = db.session.get(Book, data["business_book_id"])

        # First create some transactions in the business book
        business_checking = Account.query.filter_by(
            book_id=business_book.id, name="Business Checking"
        ).first()

        business_expense = Account.query.filter_by(
            book_id=business_book.id, name="Business Expense"
        ).first()

        transaction1 = Transaction(
            user_id=user.id,
            book_id=business_book.id,
            account_id=business_checking.id,
            date=date.today(),
            description="Transaction 1",
            amount=-100.0,
        )

        transaction2 = Transaction(
            user_id=user.id,
            book_id=business_book.id,
            account_id=business_expense.id,
            date=date.today(),
            description="Transaction 2",
            amount=100.0,
        )

        db.session.add_all([transaction1, transaction2])
        db.session.commit()

        # Verify transactions exist
        transactions = Transaction.query.filter_by(book_id=business_book.id).all()
        assert len(transactions) == 2

        # Now delete the business book
        db.session.delete(business_book)
        db.session.commit()

        # Verify book is deleted
        deleted_book = db.session.get(Book, business_book.id)
        assert deleted_book is None

        # Verify accounts are deleted
        accounts = Account.query.filter_by(book_id=business_book.id).all()
        assert len(accounts) == 0

        # Verify transactions are deleted
        transactions = Transaction.query.filter_by(book_id=business_book.id).all()
        assert len(transactions) == 0

        # Verify personal book still exists
        personal_book_check = db.session.get(Book, personal_book.id)
        assert personal_book_check is not None
