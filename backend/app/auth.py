from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, jwt_required as flask_jwt_required, current_user
from functools import wraps
from app.models import User, db
from app.extensions import login_manager

auth = Blueprint('auth', __name__)

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
    
    # Generate token using Flask-JWT-Extended
    token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token
    }), 201

@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        # Generate token using Flask-JWT-Extended
        token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@auth.route('/api/auth/logout', methods=['POST'])
@flask_jwt_required()
def logout():
    # JWT logout is typically handled client-side by discarding the token.
    # Flask-JWT-Extended offers blocklisting for server-side revocation if needed.
    return jsonify({'message': 'Logout successful (token invalidated client-side)'}), 200

@auth.route('/api/auth/me', methods=['GET'])
@flask_jwt_required()
def get_current_user():
    # Access the user loaded by @jwt.user_lookup_loader via current_user proxy
    user = current_user
    if not user:
         # This case should ideally not happen if @flask_jwt_required() and user_lookup_loader work
         return jsonify({'error': 'User not found despite valid token'}), 404
    # Explicitly convert user object to dict before jsonify
    return jsonify(user.to_dict()), 200
