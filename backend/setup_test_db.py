#!/usr/bin/env python3

"""
Script to set up a test database with sample data for testing
"""

from app import create_app, db
from app.models import User, Book, BankAccountMapping, ExpenseAccountMapping, ApiToken
import os
import sys

def setup_test_db():
    """Set up a test database with sample data"""
    # Create a test SQLite database
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    # Create app with test config
    app = create_app("testing")
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create a test user
        user = User(
            email="admin@example.com",
            name="Admin User",
            is_admin=True,
            is_active=True
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a book
        book = Book(
            name="Default Book",
            user_id=user.id
        )
        db.session.add(book)
        db.session.commit()
        
        # Set as active book
        user.active_book_id = book.id
        db.session.commit()
        
        # Create an API token
        token = ApiToken(
            user_id=user.id,
            name="Bank Transaction API",
            token=ApiToken.generate_token()
        )
        db.session.add(token)
        db.session.commit()
        
        # Create sample bank account mappings
        bank_mappings = [
            BankAccountMapping(
                user_id=user.id,
                book_id=book.id,
                account_identifier="XX1648",
                ledger_account="Assets:Bank:Axis"
            ),
            BankAccountMapping(
                user_id=user.id,
                book_id=book.id,
                account_identifier="XX0907",
                ledger_account="Liabilities:CC:Axis"
            ),
            BankAccountMapping(
                user_id=user.id,
                book_id=book.id,
                account_identifier="XX9005",
                ledger_account="Liabilities:CC:ICICI"
            )
        ]
        
        for mapping in bank_mappings:
            db.session.add(mapping)
        
        # Create sample expense account mappings
        expense_mappings = [
            ExpenseAccountMapping(
                user_id=user.id,
                book_id=book.id,
                merchant_name="BAKE HOUSE",
                ledger_account="Expenses:Food:Restaurant",
                description="Restaurant at Kattangal"
            ),
            ExpenseAccountMapping(
                user_id=user.id,
                book_id=book.id,
                merchant_name="SUDEESHKUMA",
                ledger_account="Expenses:Groceries",
                description="Unni at West Manassery"
            ),
            ExpenseAccountMapping(
                user_id=user.id,
                book_id=book.id,
                merchant_name="Jio Prepaid",
                ledger_account="Expenses:Mobile:Baiju Jio",
                description="FIXME"
            )
        ]
        
        for mapping in expense_mappings:
            db.session.add(mapping)
            
        db.session.commit()
        
        print("Test database setup completed successfully!")
        print(f"User: admin@example.com with password: password123")
        print(f"API Token: {token.token}")
        print(f"Book ID: {book.id}")
        print(f"Database file: test.db")

if __name__ == "__main__":
    setup_test_db() 