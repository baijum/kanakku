import os
import pytest
import json
from datetime import datetime, date, timedelta, timezone
from flask import Flask
import jwt
from flask_jwt_extended import create_access_token
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
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': False,  # Make tokens non-expiring for testing
    })
    
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
    """Provide the active SQLAlchemy session."""
    with app.app_context():
        # The scoped session is managed by Flask-SQLAlchemy
        yield db.session
        # Cleanup/close is handled by app context teardown

@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def user(app, db_session):
    """Create a test user and ensure it's returned attached to the session."""
    # Check if user already exists in this session
    existing_user = db_session.query(User).filter_by(email='test@example.com').first()
    if existing_user:
        # Even if existing, ensure it's attached to *this* session scope
        return db_session.merge(existing_user)
        
    # Create a new user
    user = User(
        email='test@example.com'
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    user_id = user.id # Get ID after commit
    
    # Fetch the user using the session to ensure it's attached
    attached_user = db_session.get(User, user_id)
    if not attached_user:
         pytest.fail("Failed to fetch created user from session in user fixture")
    return attached_user

@pytest.fixture(scope='function')
def authenticated_client(client, app, db_session):
    """Ensure test user exists and create an authenticated client for them."""
    
    user_id = None
    # Use app_context to ensure db operations and token creation work
    with app.app_context():
        # Ensure the standard test user exists within this session
        test_user = db_session.query(User).filter_by(email='test@example.com').first()
        if not test_user:
            # Create if doesn't exist (should usually exist due to fixture order)
            test_user = User(email='test@example.com')
            test_user.set_password('password123') # Use consistent password
            db_session.add(test_user)
            db_session.commit()
            user_id = test_user.id
        else:
            # If user exists, make sure it's attached to this session
            test_user = db_session.merge(test_user)
            user_id = test_user.id
            
        if not user_id:
             pytest.fail("Could not get user ID for token creation in authenticated_client")

        # Create a JWT access token for this user using Flask-JWT-Extended
        # Convert user_id to string to avoid "Subject must be a string" error
        token = create_access_token(identity=str(user_id))
        
    auth_headers = {'Authorization': f'Bearer {token}'}
    
    class AuthenticatedClient:
        def get(self, path, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return client.get(path, **kwargs)
                
        def post(self, path, **kwargs):
            # Always set content-type for JSON data
            if 'json' in kwargs:
                headers = kwargs.setdefault('headers', {})
                headers.update(auth_headers)
                headers.update({'Content-Type': 'application/json'})
                # Print request for debugging
                print(f"\nPOST {path} with JSON: {json.dumps(kwargs['json'])}")
                print(f"Headers: {headers}")
                response = client.post(path, **kwargs)
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.data}")
                return response
            else:
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.post(path, **kwargs)
                
        def put(self, path, **kwargs):
            # Always set content-type for JSON data
            if 'json' in kwargs:
                headers = kwargs.setdefault('headers', {})
                headers.update(auth_headers)
                headers.update({'Content-Type': 'application/json'})
                return client.put(path, **kwargs)
            else:
                kwargs.setdefault('headers', {}).update(auth_headers)
                return client.put(path, **kwargs)
                
        def delete(self, path, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return client.delete(path, **kwargs)
    
    return AuthenticatedClient()

@pytest.fixture(scope='function')
def transaction(app, db_session, user):
    """Create a test transaction linked to the user fixture."""
    if not user or not user.id:
        pytest.fail("User fixture did not provide a valid user for transaction.")

    # Check if a default transaction exists for this user, if so return it
    existing_tx = db_session.query(Transaction).filter_by(user_id=user.id, description='Test transaction').first()
    if existing_tx:
        return existing_tx

    transaction = Transaction(
        user_id=user.id,
        date=date(2024, 1, 1),
        description='Test transaction',
        payee='Test payee',
        amount=100.0,
        currency='INR'
        # Ensure account_id is set if needed, maybe link to account fixture?
        # account_id=account.id # Example if account fixture is also used
    )
    db_session.add(transaction)
    db_session.commit()

    return transaction

@pytest.fixture(scope='function')
def account(app, db_session, user):
    """Create a test account linked to the user fixture."""
    if not user or not user.id:
        pytest.fail("User fixture did not provide a valid user for account.")

    # Check if a default account exists for this user, if so return it
    existing_account = db_session.query(Account).filter_by(user_id=user.id, name='Test Account').first()
    if existing_account:
        return existing_account

    account = Account(
        user_id=user.id,
        name='Test Account',
        type='asset',
        currency='INR',
        balance=1000.0
    )
    db_session.add(account)
    db_session.commit()

    return account

@pytest.fixture(scope='function')
def mock_ledger_command(mocker):
    """Mock the ledger command execution."""
    
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