from flask import Flask, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager # Remove if not used for API
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .extensions import db # Remove login_manager if unused
from .config import config
from .models import User

# Initialize JWTManager globally (or within create_app)
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions that don't depend on app context first
    db.init_app(app)
    jwt.init_app(app)
    # login_manager.init_app(app) # Remove if not used
    # login_manager.login_view = 'auth.login' # Remove if not used

    # --- Define JWT User Loader Directly Here --- 
    # This ensures it's configured before blueprints might use it
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # Handle both string and integer IDs - convert to int if string
        user_id = int(identity) if isinstance(identity, str) else identity
        return User.query.filter_by(id=user_id).one_or_none()
    # --------------------------------------------

    # Now work within the app context for DB creation and blueprints
    with app.app_context():
        # Import models needed for create_all
        from .models import Transaction, Account 
        db.create_all()
        
        # Register blueprints
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)
        from .ledger import ledger as ledger_blueprint
        app.register_blueprint(ledger_blueprint)
        from .reports import reports as reports_blueprint
        app.register_blueprint(reports_blueprint)
        from .transactions import transactions as transactions_blueprint
        app.register_blueprint(transactions_blueprint)
        from .accounts import accounts as accounts_blueprint
        app.register_blueprint(accounts_blueprint)
        from .errors import errors as errors_blueprint
        app.register_blueprint(errors_blueprint)
        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint)
        
        # Register error handlers (remain inside app_context)
        @app.errorhandler(404)
        def not_found_error(error):
            return jsonify({'error': 'Not found'}), 404

        @app.errorhandler(405)
        def method_not_allowed_error(error):
            return jsonify({'error': 'Method not allowed'}), 405
            
        @app.errorhandler(422)
        def unprocessable_entity_error(error):
            return jsonify({'error': 'Unprocessable Entity - Invalid data provided'}), 422

        @app.errorhandler(500)
        def internal_error(error):
            # Ensure rollback happens within the session context
            try:
                db.session.rollback()
            except Exception as rollback_error:
                app.logger.error(f"Error during rollback: {rollback_error}")
            return jsonify({'error': 'Internal server error'}), 500
            
    return app
