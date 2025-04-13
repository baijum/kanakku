from flask import Blueprint, request, jsonify, current_app, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, jwt_required as flask_jwt_required, current_user, decode_token
from functools import wraps
from app.models import User, db
from app.extensions import login_manager
import logging

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
    
    # Generate token using Flask-JWT-Extended - convert id to string for sub claim
    token = create_access_token(identity=user.id, additional_claims={"sub": str(user.id)})
    
    return jsonify({
        'message': 'User created successfully',
        'token': token
    }), 201

# Add OPTIONS handler for CORS preflight requests
@auth.route('/api/auth/login', methods=['OPTIONS'])
def login_options():
    response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

@auth.route('/api/auth/login', methods=['POST'])
def login():
    """Simple login endpoint that accepts username/password and returns a token"""
    
    # Log the request for debugging
    current_app.logger.debug(f"LOGIN ENDPOINT CALLED")
    current_app.logger.debug(f"Request method: {request.method}")
    current_app.logger.debug(f"Request headers: {dict(request.headers)}")
    current_app.logger.debug(f"Request data: {request.get_data(as_text=True)}")
    
    # Get the JSON data or form data
    data = None
    try:
        data = request.get_json(silent=True)
        if data is None:
            # Try to get form data instead
            data = request.form.to_dict() or {}
            current_app.logger.debug(f"Got form data: {data}")
        else:
            current_app.logger.debug(f"Got JSON data: {data}")
    except Exception as e:
        current_app.logger.error(f"Error parsing request data: {e}")
        data = {}

    # Handle case with no data
    if not data:
        current_app.logger.error("No data provided in request")
        return jsonify({"error": "No data provided"}), 400

    username = data.get('username')
    password = data.get('password')
    
    # Basic validation
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # Find the user
    user = User.query.filter_by(username=username).first()
    
    # Check password
    if user and user.check_password(password):
        # Generate token
        try:
            token = create_access_token(identity=user.id, additional_claims={"sub": str(user.id)})
            return jsonify({
                "message": "Login successful",
                "token": token
            }), 200
        except Exception as e:
            current_app.logger.error(f"Token generation error: {str(e)}")
            return jsonify({"error": "Error generating token"}), 500
    
    # Invalid credentials
    return jsonify({"error": "Invalid username or password"}), 401

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
