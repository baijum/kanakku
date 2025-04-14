from datetime import datetime, date, timezone, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Date
from .extensions import db, login_manager
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Google Auth fields
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    picture = db.Column(db.String(500), nullable=True)
    
    # Define relationships once, with consistent backrefs
    transactions = db.relationship('Transaction', backref='user', lazy=True, foreign_keys='Transaction.user_id')
    accounts = db.relationship('Account', backref='user', lazy=True, foreign_keys='Account.user_id')
    preambles = db.relationship('Preamble', backref='user', lazy=True, foreign_keys='Preamble.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def activate(self):
        self.is_active = True
        db.session.commit()
    
    def deactivate(self):
        self.is_active = False
        db.session.commit()
        
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        return self.reset_token
    
    def verify_reset_token(self, token):
        if not self.reset_token or self.reset_token != token:
            return False
        if not self.reset_token_expires_at:
            return False
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        if self.reset_token_expires_at.tzinfo is None:
            self.reset_token_expires_at = self.reset_token_expires_at.replace(tzinfo=timezone.utc)
        return self.reset_token_expires_at > now
        
    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expires_at = None
        db.session.commit()

    def get_token(self):
        from flask import current_app
        import jwt
        from datetime import datetime, timezone, timedelta
        
        payload = {
            'user_id': self.id,
            'exp': datetime.now(timezone.utc) + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(days=1)),
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'picture': self.picture
        }

    def __repr__(self):
        return f'<User {self.email}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    payee = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships already defined via backref in User and Account models

    @staticmethod
    def from_dict(data):
        if isinstance(data['date'], str):
            data = data.copy()
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
        return Transaction(**data)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': self.amount,
            'currency': self.currency,
            'created_at': self.created_at.isoformat()
        }

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, income, expense
    currency = db.Column(db.String(3), default='INR')
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships already defined via backref in User model

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'currency': self.currency,
            'balance': self.balance,
            'created_at': self.created_at.isoformat()
        }

class Preamble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'content': self.content,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 