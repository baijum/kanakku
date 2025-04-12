import os
import pytest
from datetime import datetime, date, timedelta, timezone
from flask import Flask
import jwt
from app import create_app
from app.extensions import db
from app.models import User, Transaction, Account

@pytest.fixture(scope='function')
def app():
    """Create a test Flask app using the 'testing' configuration."""
    app = create_app('testing')
    
    # Override some settings to ensure testing environment
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-key'
    })
    
    # Ensure LEDGER_FILE is set for tests
    os.environ['LEDGER_FILE'] = ':memory:'
    
    # Ensure app context is available
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models import User, Transaction, Account
        # Drop any existing tables
        db.drop_all()
        # Create tables
        db.create_all()
        
    yield app
    
    # Cleanup after testing
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    """Create database tables and session."""
    with app.app_context():
        # Create all tables before each test
        db.create_all()
        session = db.session
        yield session
        session.close()
        # Remove all tables after each test
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    with app.app_context():
        # Ensure database tables exist for this test
        db.create_all()
    return app.test_client()

@pytest.fixture(scope='function')
def user(app, db_session):
    """Create a test user."""
    with app.app_context():
        # Check if user already exists
        existing_user = db_session.query(User).filter_by(email='test@example.com').first()
        if existing_user:
            return existing_user
            
        # Create a new user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Get a fresh instance that's attached to the session
        user_id = user.id
        fresh_user = db_session.query(User).get(user_id)
        return fresh_user

@pytest.fixture(scope='function')
def auth_headers(app):
    """Create authentication headers with a manual JWT token."""
    with app.app_context():
        # Create a test user for this token
        import jwt
        from datetime import datetime, timezone, timedelta
        
        # Create the payload
        payload = {
            'user_id': 1,  # Just use ID 1 for testing
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc)
        }
        
        # Generate the token
        token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Return the headers
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture(scope='function')
def authenticated_client(client, app, db_session):
    """Create an authenticated test client that automatically includes auth headers."""
    with app.app_context():
        # Create a test user specifically for this test
        existing_user = db_session.query(User).filter_by(email='test@example.com').first()
        if existing_user:
            user = existing_user
        else:
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('password123')
            db_session.add(user)
            db_session.commit()
        
        # Ensure the user is attached to the current session
        user_id = user.id
        
        # Create a JWT token for this user
        import jwt
        from datetime import datetime, timezone, timedelta
        
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        auth_headers = {'Authorization': f'Bearer {token}'}
        
        class AuthenticatedClient:
            def get(self, path, **kwargs):
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.get(path, **kwargs)
                    
            def post(self, path, **kwargs):
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.post(path, **kwargs)
                    
            def put(self, path, **kwargs):
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.put(path, **kwargs)
                    
            def delete(self, path, **kwargs):
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.delete(path, **kwargs)
        
        return AuthenticatedClient()

@pytest.fixture(scope='function')
def transaction(app, db_session):
    """Create a test transaction."""
    with app.app_context():
        # Get the first user or create one if none exists
        user = db_session.query(User).first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('password123')
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
        transaction = Transaction(
            user_id=user.id,
            date=date(2024, 1, 1),
            description='Test transaction',
            payee='Test payee',
            amount=100.0,
            currency='USD'
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Get fresh instance that's attached to the session
        transaction_id = transaction.id
        return db_session.query(Transaction).get(transaction_id)

@pytest.fixture(scope='function')
def account(app, db_session):
    """Create a test account."""
    with app.app_context():
        # Get the first user or create one if none exists
        user = db_session.query(User).first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('password123')
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
        account = Account(
            user_id=user.id,
            name='Test Account',
            type='asset',
            currency='USD',
            balance=1000.0
        )
        db_session.add(account)
        db_session.commit()
        
        # Get fresh instance that's attached to the session
        account_id = account.id
        return db_session.query(Account).get(account_id)

@pytest.fixture(scope='function')
def mock_ledger_command(mocker):
    """Mock the ledger command execution."""
    # Set a test ledger file path in the environment for testing
    os.environ['LEDGER_FILE'] = '/tmp/test.ledger'
    
    # Mock subprocess.run
    def mock_run(*args, **kwargs):
        # Mock different ledger command responses based on the command
        cmd_args = args[0] if args else []
        
        # Mock different responses based on command
        if 'print' in cmd_args:
            return mocker.Mock(stdout='Mocked transaction data', returncode=0)
        elif 'balance' in cmd_args:
            return mocker.Mock(stdout='Mocked balance data', returncode=0)
        elif 'register' in cmd_args:
            return mocker.Mock(stdout='Mocked register data', returncode=0)
        return mocker.Mock(stdout='', returncode=0)
        
    return mocker.patch('subprocess.run', side_effect=mock_run) 