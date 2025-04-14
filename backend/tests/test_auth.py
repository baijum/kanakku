import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        if existing_user:
            return existing_user
        
        # Create new user if it doesn't exist
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

def test_register(client):
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'password'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'user_id' in data
    assert 'pending activation' in data['message']

def test_login(client, user, app):
    # First activate the user
    with app.app_context():
        # Fetch the user again within the app context
        user = User.query.filter_by(email='test@example.com').first()
        user.set_password('password123')
        user.activate()
        db.session.commit()
    
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'message' in data
    assert data['message'] == 'Login successful'

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_get_current_user(authenticated_client, user, db_session):
    # Using db_session ensures the user object from the fixture 
    # can be used for comparison if needed, although accessing response data is preferred.
    with db_session.no_autoflush:
        response = authenticated_client.get('/api/auth/me')
        # Primary assertion should be on status code and response content
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data is not None
        # Compare response data against the known ID from the fixture user
        assert response_data.get('id') == user.id
        assert response_data.get('email') == user.email 