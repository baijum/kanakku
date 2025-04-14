from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    user = db.session.get(User, user_id)
    return user
