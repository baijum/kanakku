from datetime import date, timedelta

import pytest

from app.models import Account, Book, Transaction, db


def test_get_balance(authenticated_client, setup_test_data):
    """Test the get_balance API endpoint."""
    # Call the endpoint
    response = authenticated_client.get("/api/v1/reports/balance")
    assert response.status_code == 200

    # Check response structure and content
    data = response.get_json()
    assert isinstance(data, dict)
    assert "assets" in data
    assert "expenses" in data
    assert "income" in data

    # Check account balances
    assert any(account["name"] == "Assets:Checking" for account in data["assets"])
    assert any(account["name"] == "Expenses:Groceries" for account in data["expenses"])
    assert any(account["name"] == "Income:Salary" for account in data["income"])

    # Verify specific balances
    assets_checking = next(
        account for account in data["assets"] if account["name"] == "Assets:Checking"
    )
    expenses_groceries = next(
        account
        for account in data["expenses"]
        if account["name"] == "Expenses:Groceries"
    )
    income_salary = next(
        account for account in data["income"] if account["name"] == "Income:Salary"
    )

    assert assets_checking["balance"] == 1350.0  # 1000 - 100 + 500 - 50
    assert expenses_groceries["balance"] == 150.0  # 100 + 50
    assert income_salary["balance"] == 500.0  # 500


def test_get_register(authenticated_client, setup_test_data):
    """Test the get_register API endpoint."""
    # Call the endpoint
    response = authenticated_client.get(
        "/api/v1/reports/register?account=Assets:Checking"
    )
    assert response.status_code == 200

    # Check response structure and content
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3  # Should have 3 transactions for this account

    # Verify transaction details are included
    txs = sorted(data, key=lambda x: x["date"])
    assert txs[0]["description"] == "Groceries"
    assert txs[0]["amount"] == -100.0
    assert txs[1]["description"] == "Salary deposit"
    assert txs[1]["amount"] == 500.0
    assert txs[2]["description"] == "More groceries"
    assert txs[2]["amount"] == -50.0


def test_get_balance_report(authenticated_client, setup_test_data):
    """Test the balance report API endpoint."""
    # Call the endpoint
    response = authenticated_client.get("/api/v1/reports/balance_report")
    assert response.status_code == 200

    # Check response structure and content
    data = response.get_json()
    assert isinstance(data, dict)
    assert "accounts" in data

    # Verify accounts are properly categorized
    account_names = [account["name"] for account in data["accounts"]]
    assert "Assets:Checking" in account_names
    assert "Expenses:Groceries" in account_names
    assert "Income:Salary" in account_names


def test_get_income_statement(authenticated_client, setup_test_data):
    """Test the income statement API endpoint."""
    # Call the endpoint
    response = authenticated_client.get("/api/v1/reports/income_statement")
    assert response.status_code == 200

    # Check response structure and content
    data = response.get_json()
    assert isinstance(data, dict)
    assert "income" in data
    assert "expenses" in data

    # Verify income and expense totals
    assert sum(account["balance"] for account in data["income"]) == 500.0
    assert sum(account["balance"] for account in data["expenses"]) == 150.0


def test_balance_report(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Get or create a Book for the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if book is None:
            book = Book(name="Test Book", user_id=user.id)
            db.session.add(book)
            db.session.flush()

            # Update user's active book
            user.active_book_id = book.id
            db.session.commit()

        # Create accounts
        checking = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Checking",
            balance=1000.0,
            currency="INR",
        )
        savings = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Savings",
            balance=5000.0,
            currency="INR",
        )
        credit = Account(
            user_id=user.id,
            book_id=book.id,
            name="Liabilities:Credit Card",
            balance=-2000.0,
            currency="INR",
        )
        db.session.add_all([checking, savings, credit])
        db.session.commit()

    # Test balance report generation
    response = authenticated_client.get("/api/v1/reports/balance")
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert "balance" in data
    balance_report = data["balance"]

    # Verify account balances are present in the report
    assert "Assets:Bank:Checking" in balance_report
    assert "Assets:Bank:Savings" in balance_report
    assert "Liabilities:Credit Card" in balance_report

    # Verify amounts are present
    assert "1000.00 INR" in balance_report
    assert "5000.00 INR" in balance_report
    assert "-2000.00 INR" in balance_report


def test_income_statement(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Get or create a Book for the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if book is None:
            book = Book(name="Test Book", user_id=user.id)
            db.session.add(book)
            db.session.flush()

            # Update user's active book
            user.active_book_id = book.id
            db.session.commit()

        # Create accounts
        checking = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Checking",
            balance=0.0,  # Start with zero balance
            currency="INR",
        )
        salary = Account(
            user_id=user.id,
            book_id=book.id,
            name="Income:Salary",
            balance=0.0,
            currency="INR",
        )
        groceries = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Groceries",
            balance=0.0,
            currency="INR",
        )
        rent = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Rent",
            balance=0.0,
            currency="INR",
        )
        db.session.add_all([checking, salary, groceries, rent])
        db.session.commit()

        # Create transactions
        today = date.today()
        last_month = today - timedelta(days=30)

        # Salary transaction - debit checking, credit salary
        salary_tx1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=last_month,
            description="Monthly Salary",
            payee="Employer",
            amount=5000.0,
            currency="INR",
        )
        salary_tx2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=salary.id,
            date=last_month,
            description="Monthly Salary",
            payee="Employer",
            amount=-5000.0,  # Credit to income account
            currency="INR",
        )
        db.session.add_all([salary_tx1, salary_tx2])

        # Update account balances
        checking.balance += salary_tx1.amount
        salary.balance += salary_tx2.amount

        # Groceries transaction - credit checking, debit groceries
        groceries_tx1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=last_month,
            description="Groceries",
            payee="Supermarket",
            amount=-500.0,
            currency="INR",
        )
        groceries_tx2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=groceries.id,
            date=last_month,
            description="Groceries",
            payee="Supermarket",
            amount=500.0,  # Debit to expense account
            currency="INR",
        )
        db.session.add_all([groceries_tx1, groceries_tx2])

        # Update account balances
        checking.balance += groceries_tx1.amount
        groceries.balance += groceries_tx2.amount

        # Rent transaction - credit checking, debit rent
        rent_tx1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=last_month,
            description="Rent",
            payee="Landlord",
            amount=-2000.0,
            currency="INR",
        )
        rent_tx2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=rent.id,
            date=last_month,
            description="Rent",
            payee="Landlord",
            amount=2000.0,  # Debit to expense account
            currency="INR",
        )
        db.session.add_all([rent_tx1, rent_tx2])

        # Update account balances
        checking.balance += rent_tx1.amount
        rent.balance += rent_tx2.amount

        db.session.commit()

    # Test income statement generation
    response = authenticated_client.get("/api/v1/reports/income_statement")
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert "income_statement" in data
    statement = data["income_statement"]

    # Verify income and expenses are present in the report
    assert "Income:Salary" in statement
    assert "Expenses:Groceries" in statement
    assert "Expenses:Rent" in statement

    # Verify amounts are present (note: income is negative in the statement)
    assert "5000.00" in statement
    assert "500.00" in statement
    assert "2000.00" in statement


def test_report_date_range(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Get or create a Book for the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if book is None:
            book = Book(name="Test Book", user_id=user.id)
            db.session.add(book)
            db.session.flush()

            # Update user's active book
            user.active_book_id = book.id
            db.session.commit()

        # Create accounts
        checking = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Checking",
            balance=0.0,  # Start with zero balance
            currency="INR",
        )
        salary = Account(
            user_id=user.id,
            book_id=book.id,
            name="Income:Salary",
            balance=0.0,
            currency="INR",
        )
        groceries = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Groceries",
            balance=0.0,
            currency="INR",
        )
        rent = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Rent",
            balance=0.0,
            currency="INR",
        )
        db.session.add_all([checking, salary, groceries, rent])
        db.session.commit()

        # Create transactions in different months
        today = date.today()
        last_month = today - timedelta(days=30)
        two_months_ago = today - timedelta(days=60)

        # Recent salary - debit checking, credit salary
        recent_salary1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=last_month,
            description="Recent Salary",
            payee="Employer",
            amount=5000.0,
            currency="INR",
        )
        recent_salary2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=salary.id,
            date=last_month,
            description="Recent Salary",
            payee="Employer",
            amount=-5000.0,  # Credit to income account
            currency="INR",
        )
        db.session.add_all([recent_salary1, recent_salary2])

        # Update account balances
        checking.balance += recent_salary1.amount
        salary.balance += recent_salary2.amount

        # Old salary - debit checking, credit salary
        old_salary1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=two_months_ago,
            description="Old Salary",
            payee="Employer",
            amount=4000.0,
            currency="INR",
        )
        old_salary2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=salary.id,
            date=two_months_ago,
            description="Old Salary",
            payee="Employer",
            amount=-4000.0,  # Credit to income account
            currency="INR",
        )
        db.session.add_all([old_salary1, old_salary2])

        # Update account balances
        checking.balance += old_salary1.amount
        salary.balance += old_salary2.amount

        db.session.commit()

    # Test income statement with date range
    start_date = (last_month - timedelta(days=1)).isoformat()
    end_date = (today + timedelta(days=1)).isoformat()

    response = authenticated_client.get(
        f"/api/v1/reports/income_statement?start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert "income_statement" in data
    statement = data["income_statement"]

    # Verify only recent salary is included
    assert "Income:Salary" in statement
    assert "9000.00" in statement  # Total income (5000 + 4000)
    assert "Old Salary" not in statement
    assert "4000.00" not in statement


def test_get_balance_with_all_top_level_accounts(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Get or create a Book for the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if book is None:
            book = Book(name="Test Book", user_id=user.id)
            db.session.add(book)
            db.session.flush()

            # Update user's active book
            user.active_book_id = book.id
            db.session.commit()

        # Create accounts with hierarchical structure
        checking = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Checking",
            balance=1000.0,
            currency="INR",
        )
        savings = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Bank:Savings",
            balance=5000.0,
            currency="INR",
        )
        cash = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Cash",
            balance=500.0,
            currency="INR",
        )
        groceries = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Groceries",
            balance=200.0,
            currency="INR",
        )
        rent = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Rent",
            balance=1500.0,
            currency="INR",
        )
        salary = Account(
            user_id=user.id,
            book_id=book.id,
            name="Income:Salary",
            balance=-8000.0,  # Credit balance for income
            currency="INR",
        )
        interest = Account(
            user_id=user.id,
            book_id=book.id,
            name="Income:Interest",
            balance=-200.0,  # Credit balance for income
            currency="INR",
        )
        # Create a Liabilities account to ensure the account type is present
        credit_card = Account(
            user_id=user.id,
            book_id=book.id,
            name="Liabilities:Credit Card",
            balance=-1500.0,  # Credit balance for liability
            currency="INR",
        )
        db.session.add_all(
            [checking, savings, cash, groceries, rent, salary, interest, credit_card]
        )
        db.session.commit()

        # Test with depth=1 to get top-level accounts
        response = authenticated_client.get("/api/v1/reports/balance?depth=1")
        assert response.status_code == 200
        data = response.get_json()
        assert "balance" in data

        # The report should contain all top-level account types that have accounts
        balance_lines = data["balance"].split("\n")

        # Get account names from the report
        account_names = [
            line.split()[0].strip() for line in balance_lines if line.strip()
        ]

        # Verify all top-level account types with accounts are included
        assert "Assets" in account_names
        assert "Liabilities" in account_names
        assert "Income" in account_names
        assert "Expenses" in account_names

        # Check balances are properly aggregated at the top level
        assets_line = next(
            (line for line in balance_lines if line.startswith("Assets")), None
        )
        assert assets_line is not None
        assert "6500.00 INR" in assets_line

        expenses_line = next(
            (line for line in balance_lines if line.startswith("Expenses")), None
        )
        assert expenses_line is not None
        assert "1700.00 INR" in expenses_line


@pytest.fixture
def setup_test_data(app, user):
    """Set up test data for reports testing."""
    with app.app_context():
        # Get or create a Book for the user
        book = db.session.query(Book).filter_by(user_id=user.id).first()
        if book is None:
            book = Book(name="Test Book", user_id=user.id)
            db.session.add(book)
            db.session.flush()

            # Update user's active book
            user.active_book_id = book.id
            db.session.commit()

        # Create accounts
        checking = Account(
            user_id=user.id,
            book_id=book.id,
            name="Assets:Checking",
            balance=1000.0,
            currency="INR",
        )
        groceries = Account(
            user_id=user.id,
            book_id=book.id,
            name="Expenses:Groceries",
            balance=0.0,
            currency="INR",
        )
        salary = Account(
            user_id=user.id,
            book_id=book.id,
            name="Income:Salary",
            balance=0.0,
            currency="INR",
        )
        db.session.add_all([checking, groceries, salary])
        db.session.commit()

        # Create transactions
        tx1 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=date.today() - timedelta(days=10),
            description="Groceries",
            amount=-100.0,
            currency="INR",
        )
        tx2 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=groceries.id,
            date=date.today() - timedelta(days=10),
            description="Groceries",
            amount=100.0,
            currency="INR",
        )
        tx3 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=date.today() - timedelta(days=5),
            description="Salary deposit",
            amount=500.0,
            currency="INR",
        )
        tx4 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=salary.id,
            date=date.today() - timedelta(days=5),
            description="Salary deposit",
            amount=-500.0,
            currency="INR",
        )
        tx5 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=checking.id,
            date=date.today() - timedelta(days=2),
            description="More groceries",
            amount=-50.0,
            currency="INR",
        )
        tx6 = Transaction(
            user_id=user.id,
            book_id=book.id,
            account_id=groceries.id,
            date=date.today() - timedelta(days=2),
            description="More groceries",
            amount=50.0,
            currency="INR",
        )
        db.session.add_all([tx1, tx2, tx3, tx4, tx5, tx6])

        # Update account balances
        checking.balance = 1350.0  # 1000 - 100 + 500 - 50
        groceries.balance = 150.0  # 100 + 50
        salary.balance = -500.0  # -500 (income is negative)

        db.session.commit()

        yield

        # Clean up
        db.session.query(Transaction).delete()
        db.session.query(Account).delete()
        db.session.commit()
