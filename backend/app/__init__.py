from flask import Flask
from flask_cors import CORS
import logging

from .extensions import db, login_manager, mail, jwt
from .config import Config

def create_app(config_name="default"):
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)

    # Configure CORS to allow any origin
    CORS(app, origins=["*", "http://localhost:3000"])

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error("Error creating database: {}".format(str(e)))

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
        from .preamble import preamble as preamble_blueprint
        app.register_blueprint(preamble_blueprint)
        from .errors import errors as errors_blueprint
        app.register_blueprint(errors_blueprint)
        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint)

    return app
