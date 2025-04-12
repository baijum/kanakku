from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone, timedelta
import jwt
from functools import wraps
from app.models import User, db
from app.extensions import login_manager

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_token(user_id):
    """Generate a JWT token for the user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(days=1)),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def jwt_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing!'}), 401
        
        try:
            # Decode the token
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            
            # Get the user from the database
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'error': 'Invalid token payload!'}), 401
                
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found!'}), 401
                
            # Store the current user in g object for use in the route
            g.current_user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            current_app.logger.error(f"JWT auth error: {str(e)}")
            return jsonify({'error': 'Authentication failed!'}), 401
            
        return f(*args, **kwargs)
    return decorated

@auth.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token
    }), 201

@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        token = generate_token(user.id)
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@auth.route('/api/auth/logout', methods=['POST'])
@jwt_required
def logout():
    # With JWT, we don't need to call logout_user() since tokens are stateless
    # The client should simply discard the token
    return jsonify({'message': 'Logout successful'}), 200

@auth.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    user = g.current_user
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200
