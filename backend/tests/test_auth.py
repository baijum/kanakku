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
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            return existing_user
        
        # Create new user if it doesn't exist
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'token' in data
    assert data['message'] == 'User created successfully'

def test_login(client, user):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'message' in data
    assert data['message'] == 'Login successful'

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_get_current_user(authenticated_client, user):
    response = authenticated_client.get('/api/auth/me')
    assert response.status_code == 200
    assert response.json['username'] == 'testuser' 