from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask import request, g, current_app
import functools

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    user = db.session.get(User, user_id)
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from .models import User

    identity = jwt_data["sub"]
    return db.session.get(User, identity)


# Custom decorator for API token authentication
def api_token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        from .models import ApiToken, User
        from flask_jwt_extended import verify_jwt_in_request, current_user
        from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError

        # First try JWT token authentication
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except (NoAuthorizationError, InvalidHeaderError) as e:
            # JWT authentication failed, try API token
            auth_header = request.headers.get('Authorization', '').strip()
            
            # If no Authorization header is provided
            if not auth_header:
                return {"error": "Authentication required"}, 401
            
            # Check if it's an API token (Token prefix)
            if auth_header.startswith('Token '):
                token_value = auth_header.split(' ', 1)[1].strip()
                
                # Look up the token
                api_token = ApiToken.query.filter_by(token=token_value).first()
                
                # If token exists and is valid
                if api_token and api_token.is_valid():
                    # Set custom current user using the recommended db.session.get approach
                    user = db.session.get(User, api_token.user_id)
                    if user:
                        g.current_user = user
                        
                        # Update last used timestamp
                        api_token.update_last_used()
                        
                        return f(*args, **kwargs)
            
            # Authentication failed
            return {"error": "Authentication required"}, 401
        except Exception as e:
            # Some other error occurred with JWT verification
            current_app.logger.error(f"Authentication error: {str(e)}")
            return {"error": f"Authentication error: {str(e)}"}, 401
    
    return decorated_function


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT token"""
    return {"error": "Invalid token"}, 401


@jwt.expired_token_loader
def expired_token_callback(_jwt_header, _jwt_data):
    """Handle expired JWT token"""
    return {"error": "Token has expired"}, 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    """Handle missing JWT token"""
    return {"error": "Missing or invalid authentication"}, 401
