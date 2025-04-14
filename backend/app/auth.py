from flask import Blueprint, request, jsonify, current_app, Response, url_for, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, jwt_required as flask_jwt_required, current_user, decode_token
from functools import wraps
from app.models import User, db
from app.extensions import login_manager
import logging
import requests
import json
import os

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
        email=data['email'],
        is_active=False  # Default is False, users need to be activated by an admin
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Don't generate token since user is inactive by default
    return jsonify({
        'message': 'User created successfully. Your account is pending activation by an administrator.',
        'user_id': user.id
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
        # Check if user is active
        if not user.is_active:
            return jsonify({"error": "Account is inactive. Please contact an administrator."}), 403
            
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

@auth.route('/api/auth/users/<int:user_id>/activate', methods=['POST'])
@flask_jwt_required()
def activate_user(user_id):
    # Only admins should be able to activate/deactivate users
    # TODO: Add proper admin role checking once roles are implemented
    
    # Get the target user
    user_to_update = User.query.get(user_id)
    if not user_to_update:
        return jsonify({'error': 'User not found'}), 404
    
    # Get request data
    data = request.get_json()
    is_active = data.get('is_active', True)
    
    # Update user active status
    if is_active:
        user_to_update.activate()
    else:
        user_to_update.deactivate()
    
    return jsonify({
        'message': f"User {user_to_update.username} {'activated' if is_active else 'deactivated'} successfully",
        'user': user_to_update.to_dict()
    }), 200

@auth.route('/api/auth/password', methods=['PUT'])
@flask_jwt_required()
def update_password():
    """Update the current user's password"""
    # Get request data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Validate inputs
    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400
    
    # Verify current password
    user = current_user
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Set new password
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"}), 200

# Google OAuth2 route
@auth.route('/api/auth/google', methods=['GET'])
def google_login():
    # Get Google OAuth2 configuration
    google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not google_client_id:
        return jsonify({'error': 'Google OAuth is not configured'}), 500
    
    # Generate a random state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    
    # Redirect to Google's OAuth 2.0 server
    redirect_uri = request.url_root.rstrip('/') + url_for('auth.google_callback')
    
    params = {
        'client_id': google_client_id,
        'redirect_uri': redirect_uri,
        'scope': 'openid email profile',
        'state': state,
        'response_type': 'code',
        'prompt': 'select_account'
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    from urllib.parse import urlencode
    auth_url += '?' + urlencode(params)
    
    return jsonify({'auth_url': auth_url})

@auth.route('/api/auth/google/callback', methods=['GET'])
def google_callback():
    # Verify state parameter to prevent CSRF
    state = request.args.get('state')
    if not state or session.pop('oauth_state', None) != state:
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code not provided'}), 400
    
    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = request.url_root.rstrip('/') + url_for('auth.google_callback')
    
    token_data = {
        'code': code,
        'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
        'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info using the access token
        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        userinfo_response = requests.get(
            userinfo_url,
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # Check if user exists
        user = User.query.filter_by(google_id=userinfo['sub']).first()
        
        if not user:
            # Check if email exists
            user = User.query.filter_by(email=userinfo['email']).first()
            if user:
                # Update existing user with Google ID
                user.google_id = userinfo['sub']
                user.picture = userinfo.get('picture')
            else:
                # Create new user
                username = userinfo['email'].split('@')[0]
                # Ensure username is unique
                base_username = username
                count = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{count}"
                    count += 1
                
                user = User(
                    username=username,
                    email=userinfo['email'],
                    google_id=userinfo['sub'],
                    picture=userinfo.get('picture'),
                    is_active=True  # Auto-activate Google users
                )
                
            db.session.add(user)
            db.session.commit()
        
        # Generate JWT token
        token = create_access_token(identity=user.id, additional_claims={"sub": str(user.id)})
        
        # Return token in query parameters for the frontend to consume
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        redirect_url = f"{frontend_url}/google-auth-callback?token={token}"
        
        return redirect(redirect_url)
    
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error in Google OAuth: {str(e)}")
        return jsonify({'error': 'Failed to authenticate with Google'}), 500
