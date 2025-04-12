from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

from .extensions import db, login_manager
from .config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from .models import User, Transaction, Account
        
        # Create database tables - ensure this happens for testing as well
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
        
        # Register error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return jsonify({'error': 'Not found'}), 404

        @app.errorhandler(405)
        def method_not_allowed_error(error):
            return jsonify({'error': 'Method not allowed'}), 405

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
            
    return app
