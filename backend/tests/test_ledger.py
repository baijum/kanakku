import pytest
from app import create_app, db
from app.models import User, Transaction, Account

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            return existing_user
            
        # Create new user if it doesn't exist
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def account(app, db_session):
    with app.app_context():
        # Create a test user first
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db_session.add(user)
            db_session.commit()
        
        # Create an account
        existing_account = Account.query.filter_by(name='Test Account').first()
        if existing_account:
            return existing_account
            
        account = Account(
            user_id=user.id,
            name='Test Account',
            type='asset',
            balance=1000.00,
            currency='USD'
        )
        db_session.add(account)
        db_session.commit()
        return account

def test_get_transactions(authenticated_client, app, db_session):
    """Test getting transactions for a user."""
    with app.app_context():
        # Get or create a user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db_session.add(user)
            db_session.commit()
        
        # Get or create an account
        account = Account.query.filter_by(name='Test Account').first()
        if not account:
            account = Account(
                user_id=user.id,
                name='Test Account',
                type='asset',
                balance=1000.00,
                currency='USD'
            )
            db_session.add(account)
            db_session.commit()
    
    # Create a transaction first
    transaction_data = {
        'date': '2024-01-01',
        'description': 'Test transaction',
        'payee': 'Test Payee',
        'amount': 100.00,
        'account_name': 'Test Account'
    }
    
    # Post the transaction
    response = authenticated_client.post('/api/transactions', json=transaction_data)
    assert response.status_code == 201
    
    # Get transactions
    response = authenticated_client.get('/api/transactions')
    assert response.status_code == 200
    assert len(response.json) >= 1
    
    # At least one transaction should exist with our description
    found = False
    for transaction in response.json:
        if transaction['description'] == 'Test transaction':
            found = True
            break
    assert found

def test_create_account(authenticated_client, user):
    """Test creating a new account."""
    account_data = {
        'name': 'Assets:Savings',
        'type': 'asset',
        'currency': 'USD'
    }
    
    response = authenticated_client.post('/api/accounts', json=account_data)
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'created successfully' in response.json['message'].lower()

def test_get_balance(authenticated_client, user, monkeypatch):
    """Test getting balance report."""
    # Mock the run_ledger_command function directly
    def mock_run_command(*args, **kwargs):
        return 'Assets:Checking    $1000.00\nTotal    $1000.00'
    
    # Apply the mock to the actual function
    monkeypatch.setattr('app.reports.run_ledger_command', mock_run_command)
    
    # Get balance report
    response = authenticated_client.get('/api/reports/balance')
    assert response.status_code == 200
    assert 'balance' in response.json

def test_run_ledger_command(authenticated_client, app, mocker):
    """Test run_ledger_command function"""
    # Mock the subprocess.run function
    mock_subprocess = mocker.patch('subprocess.run')
    mock_subprocess.return_value.stdout = 'Mocked ledger output'
    mock_subprocess.return_value.returncode = 0
    
    # Import the function we're testing
    from app.ledger import run_ledger_command
    
    # Test with app context
    with app.app_context():
        # Explicitly pass ledger_file path
        result = run_ledger_command(['balance'], ledger_file='/tmp/test.ledger')
        
        # Check it was called correctly
        mock_subprocess.assert_called_once()
        assert result == 'Mocked ledger output'

def test_get_balance_report(authenticated_client, monkeypatch):
    """Test getting a balance report from the ledger API"""
    # Mock the run_ledger_command function directly
    def mock_run_command(*args, **kwargs):
        return 'Assets:Checking    $1000.00\nTotal    $1000.00'
    
    # Apply the mock to the actual function
    monkeypatch.setattr('app.reports.run_ledger_command', mock_run_command)
    
    # Make the request
    response = authenticated_client.get('/api/reports/balance_report')
    
    # Check the response
    assert response.status_code == 200
    assert 'balance_report' in response.json
    assert response.json['balance_report'] == 'Assets:Checking    $1000.00\nTotal    $1000.00'

def test_get_register_report(authenticated_client, monkeypatch):
    """Test getting a register report from the ledger API"""
    # Mock the run_ledger_command function directly
    def mock_run_command(*args, **kwargs):
        return '2024-01-01 Opening Balance    Assets:Checking    $1000.00    $1000.00'
    
    # Apply the mock to the actual function
    monkeypatch.setattr('app.reports.run_ledger_command', mock_run_command)
    
    # Make the request
    response = authenticated_client.get('/api/reports/register')
    
    # Check the response
    assert response.status_code == 200
    assert 'register' in response.json 