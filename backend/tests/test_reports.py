import pytest
from datetime import date, timedelta
from app.models import Account, Transaction, db

def test_get_balance(authenticated_client, user, app):
    # Create test accounts with hierarchical names
    with app.app_context():
        accounts = [
            Account(user_id=user.id, name='Assets:Bank:Checking', type='asset', currency='INR', balance=1000.0),
            Account(user_id=user.id, name='Assets:Bank:Savings', type='asset', currency='INR', balance=2000.0),
            Account(user_id=user.id, name='Liabilities:Credit Card', type='liability', currency='INR', balance=-500.0)
        ]
        db.session.add_all(accounts)
        db.session.commit()

    # Test without filters
    response = authenticated_client.get('/api/reports/balance')
    assert response.status_code == 200
    data = response.get_json()
    assert 'balance' in data
    balance_lines = data['balance'].split('\n')
    assert len(balance_lines) == 3
    assert 'Assets:Bank:Checking' in balance_lines[0]
    assert '1000.00 INR' in balance_lines[0]

    # Test with account filter
    response = authenticated_client.get('/api/reports/balance?account=Assets:Bank')
    assert response.status_code == 200
    data = response.get_json()
    balance_lines = data['balance'].split('\n')
    assert len(balance_lines) == 2  # Only Bank accounts
    assert 'Liabilities' not in data['balance']

    # Test with depth filter
    response = authenticated_client.get('/api/reports/balance?depth=2')
    assert response.status_code == 200
    data = response.get_json()
    balance_lines = data['balance'].split('\n')
    assert 'Assets:Bank' in data['balance']
    assert 'Checking' not in data['balance']

def test_get_register(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        account = Account(user_id=user.id, name='Assets:Bank:Checking', type='asset', currency='INR', balance=1000.0)
        db.session.add(account)
        db.session.commit()

        transactions = [
            Transaction(
                user_id=user.id,
                account_id=account.id,
                date=date(2024, 1, 1),
                description='Salary',
                payee='Employer',
                amount=5000.0,
                currency='INR'
            ),
            Transaction(
                user_id=user.id,
                account_id=account.id,
                date=date(2024, 1, 2),
                description='Groceries',
                payee='Supermarket',
                amount=-100.0,
                currency='INR'
            )
        ]
        db.session.add_all(transactions)
        db.session.commit()

    # Test without filters
    response = authenticated_client.get('/api/reports/register')
    assert response.status_code == 200
    data = response.get_json()
    assert 'register' in data
    register_lines = data['register'].split('\n')
    assert '2024-01-02' in register_lines[0]
    assert 'Groceries' in register_lines[0]
    assert 'Supermarket' in register_lines[0]
    assert '-100.00 INR' in register_lines[1]

    # Test with account filter
    response = authenticated_client.get('/api/reports/register?account=Assets:Bank')
    assert response.status_code == 200
    data = response.get_json()
    assert 'Assets:Bank:Checking' in data['register']

    # Test with limit
    response = authenticated_client.get('/api/reports/register?limit=1')
    assert response.status_code == 200
    data = response.get_json()
    register_lines = data['register'].split('\n')
    assert len(register_lines) == 2  # One transaction (2 lines per transaction)
    assert '2024-01-02' in register_lines[0]  # Most recent transaction

def test_get_balance_report(authenticated_client, user, app):
    # Create test accounts of different types
    with app.app_context():
        accounts = [
            Account(user_id=user.id, name='Assets:Bank:Checking', type='asset', currency='INR', balance=1000.0),
            Account(user_id=user.id, name='Assets:Bank:Savings', type='asset', currency='INR', balance=2000.0),
            Account(user_id=user.id, name='Liabilities:Credit Card', type='liability', currency='INR', balance=-500.0),
            Account(user_id=user.id, name='Income:Salary', type='income', currency='INR', balance=-5000.0),
            Account(user_id=user.id, name='Expenses:Groceries', type='expense', currency='INR', balance=100.0)
        ]
        db.session.add_all(accounts)
        db.session.commit()

    response = authenticated_client.get('/api/reports/balance_report')
    assert response.status_code == 200
    data = response.get_json()
    assert 'balance_report' in data
    report_lines = data['balance_report'].split('\n')

    # Verify report structure
    assert 'asset' in report_lines[0].lower()
    assert 'Assets:Bank:Checking' in data['balance_report']
    assert 'Assets:Bank:Savings' in data['balance_report']
    assert '₹3000.00' in data['balance_report']  # Total assets
    assert 'liability' in data['balance_report'].lower()
    assert 'Liabilities:Credit Card' in data['balance_report']
    assert '₹-500.00' in data['balance_report']

def test_get_income_statement(authenticated_client, user, app):
    # Create test income and expense accounts
    with app.app_context():
        accounts = [
            Account(user_id=user.id, name='Income:Salary', type='Income', currency='INR', balance=-5000.0),
            Account(user_id=user.id, name='Income:Interest', type='Income', currency='INR', balance=-100.0),
            Account(user_id=user.id, name='Expenses:Groceries', type='Expenses', currency='INR', balance=300.0),
            Account(user_id=user.id, name='Expenses:Rent', type='Expenses', currency='INR', balance=1000.0)
        ]
        db.session.add_all(accounts)
        db.session.commit()

    response = authenticated_client.get('/api/reports/income_statement')
    assert response.status_code == 200
    data = response.get_json()
    assert 'income_statement' in data
    statement_lines = data['income_statement'].split('\n')

    # Verify statement structure
    assert 'Income' in statement_lines[0]
    assert 'Income:Salary' in data['income_statement']
    assert 'Income:Interest' in data['income_statement']
    assert '₹-5100.00' in data['income_statement']  # Total income
    assert 'Expenses' in data['income_statement']
    assert 'Expenses:Groceries' in data['income_statement']
    assert 'Expenses:Rent' in data['income_statement']
    assert '₹1300.00' in data['income_statement']  # Total expenses 

def test_balance_report(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Create accounts
        checking = Account(
            user_id=user.id,
            name='Assets:Bank:Checking',
            type='asset',
            currency='INR',
            balance=1000.0
        )
        savings = Account(
            user_id=user.id,
            name='Assets:Bank:Savings',
            type='asset',
            currency='INR',
            balance=5000.0
        )
        credit = Account(
            user_id=user.id,
            name='Liabilities:Credit Card',
            type='liability',
            currency='INR',
            balance=-2000.0
        )
        db.session.add_all([checking, savings, credit])
        db.session.commit()

    # Test balance report generation
    response = authenticated_client.get('/api/reports/balance')
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert 'balance' in data
    balance_report = data['balance']

    # Verify account balances are present in the report
    assert 'Assets:Bank:Checking' in balance_report
    assert 'Assets:Bank:Savings' in balance_report
    assert 'Liabilities:Credit Card' in balance_report

    # Verify amounts are present
    assert '1000.00 INR' in balance_report
    assert '5000.00 INR' in balance_report
    assert '-2000.00 INR' in balance_report

def test_income_statement(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        # Create accounts
        checking = Account(
            user_id=user.id,
            name='Assets:Bank:Checking',
            type='asset',
            currency='INR',
            balance=0.0  # Start with zero balance
        )
        salary = Account(
            user_id=user.id,
            name='Income:Salary',
            type='Income',
            currency='INR',
            balance=0.0
        )
        groceries = Account(
            user_id=user.id,
            name='Expenses:Groceries',
            type='Expenses',
            currency='INR',
            balance=0.0
        )
        rent = Account(
            user_id=user.id,
            name='Expenses:Rent',
            type='Expenses',
            currency='INR',
            balance=0.0
        )
        db.session.add_all([checking, salary, groceries, rent])
        db.session.commit()

        # Create transactions
        today = date.today()
        last_month = today - timedelta(days=30)

        # Salary transaction - debit checking, credit salary
        salary_tx1 = Transaction(
            user_id=user.id,
            account_id=checking.id,
            date=last_month,
            description='Monthly Salary',
            payee='Employer',
            amount=5000.0,
            currency='INR'
        )
        salary_tx2 = Transaction(
            user_id=user.id,
            account_id=salary.id,
            date=last_month,
            description='Monthly Salary',
            payee='Employer',
            amount=-5000.0,  # Credit to income account
            currency='INR'
        )
        db.session.add_all([salary_tx1, salary_tx2])
        
        # Update account balances
        checking.balance += salary_tx1.amount
        salary.balance += salary_tx2.amount

        # Groceries transaction - credit checking, debit groceries
        groceries_tx1 = Transaction(
            user_id=user.id,
            account_id=checking.id,
            date=last_month,
            description='Groceries',
            payee='Supermarket',
            amount=-500.0,
            currency='INR'
        )
        groceries_tx2 = Transaction(
            user_id=user.id,
            account_id=groceries.id,
            date=last_month,
            description='Groceries',
            payee='Supermarket',
            amount=500.0,  # Debit to expense account
            currency='INR'
        )
        db.session.add_all([groceries_tx1, groceries_tx2])
        
        # Update account balances
        checking.balance += groceries_tx1.amount
        groceries.balance += groceries_tx2.amount

        # Rent transaction - credit checking, debit rent
        rent_tx1 = Transaction(
            user_id=user.id,
            account_id=checking.id,
            date=last_month,
            description='Rent',
            payee='Landlord',
            amount=-2000.0,
            currency='INR'
        )
        rent_tx2 = Transaction(
            user_id=user.id,
            account_id=rent.id,
            date=last_month,
            description='Rent',
            payee='Landlord',
            amount=2000.0,  # Debit to expense account
            currency='INR'
        )
        db.session.add_all([rent_tx1, rent_tx2])
        
        # Update account balances
        checking.balance += rent_tx1.amount
        rent.balance += rent_tx2.amount
        
        db.session.commit()

    # Test income statement generation
    response = authenticated_client.get('/api/reports/income_statement')
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert 'income_statement' in data
    statement = data['income_statement']

    # Verify income and expenses are present in the report
    assert 'Income:Salary' in statement
    assert 'Expenses:Groceries' in statement
    assert 'Expenses:Rent' in statement

    # Verify amounts are present (note: income is negative in the statement)
    assert '5000.00' in statement
    assert '500.00' in statement
    assert '2000.00' in statement

def test_report_date_range(authenticated_client, user, app):
    # Create test accounts and transactions
    with app.app_context():
        checking = Account(
            user_id=user.id,
            name='Assets:Bank:Checking',
            type='asset',
            currency='INR',
            balance=0.0  # Start with zero balance
        )
        salary = Account(
            user_id=user.id,
            name='Income:Salary',
            type='Income',
            currency='INR',
            balance=0.0
        )
        db.session.add_all([checking, salary])
        db.session.commit()

        # Create transactions in different months
        today = date.today()
        last_month = today - timedelta(days=30)
        two_months_ago = today - timedelta(days=60)

        # Recent salary - debit checking, credit salary
        recent_salary1 = Transaction(
            user_id=user.id,
            account_id=checking.id,
            date=last_month,
            description='Recent Salary',
            payee='Employer',
            amount=5000.0,
            currency='INR'
        )
        recent_salary2 = Transaction(
            user_id=user.id,
            account_id=salary.id,
            date=last_month,
            description='Recent Salary',
            payee='Employer',
            amount=-5000.0,  # Credit to income account
            currency='INR'
        )
        db.session.add_all([recent_salary1, recent_salary2])
        
        # Update account balances
        checking.balance += recent_salary1.amount
        salary.balance += recent_salary2.amount

        # Old salary - debit checking, credit salary
        old_salary1 = Transaction(
            user_id=user.id,
            account_id=checking.id,
            date=two_months_ago,
            description='Old Salary',
            payee='Employer',
            amount=4000.0,
            currency='INR'
        )
        old_salary2 = Transaction(
            user_id=user.id,
            account_id=salary.id,
            date=two_months_ago,
            description='Old Salary',
            payee='Employer',
            amount=-4000.0,  # Credit to income account
            currency='INR'
        )
        db.session.add_all([old_salary1, old_salary2])
        
        # Update account balances
        checking.balance += old_salary1.amount
        salary.balance += old_salary2.amount
        
        db.session.commit()

    # Test income statement with date range
    start_date = (last_month - timedelta(days=1)).isoformat()
    end_date = (today + timedelta(days=1)).isoformat()

    response = authenticated_client.get(f'/api/reports/income_statement?start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200
    data = response.get_json()

    # Verify report structure
    assert 'income_statement' in data
    statement = data['income_statement']

    # Verify only recent salary is included
    assert 'Income:Salary' in statement
    assert '9000.00' in statement  # Total income (5000 + 4000)
    assert 'Old Salary' not in statement
    assert '4000.00' not in statement 