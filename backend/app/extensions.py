from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager

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
