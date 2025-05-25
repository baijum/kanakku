#!/usr/bin/env python3
"""
Update Test Password Script

This script updates the email configuration with a test password for testing purposes.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
sys.path.append(os.path.join(project_root, "backend"))

def create_flask_app():
    """Create a minimal Flask app for testing."""
    from flask import Flask
    
    app = Flask(__name__)
    
    # Set required configuration
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    app.config['REDIS_URL'] = os.getenv('REDIS_URL')
    app.config['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY')
    app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    return app

def update_test_password():
    """Update the email configuration with a test password."""
    print("=== Updating Test Password ===")
    
    # Create Flask app context
    app = create_flask_app()
    
    with app.app_context():
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models import EmailConfiguration
        from app.utils.encryption import encrypt_value, decrypt_value
        
        # Test password for Gmail (this would normally be a real app password)
        test_password = "dummy_gmail_app_password_for_testing"
        
        print(f"Test password: {test_password}")
        print("Note: This is a dummy password for testing. In real usage, you would need a valid Gmail app password.")
        print()
        
        # Encrypt the test password
        try:
            encrypted_password = encrypt_value(test_password)
            print(f"Encrypted password: {encrypted_password}")
            
            # Verify encryption works
            decrypted_test = decrypt_value(encrypted_password)
            if decrypted_test == test_password:
                print("✓ Encryption verification passed")
            else:
                print("✗ Encryption verification failed")
                return
                
        except Exception as e:
            print(f"Encryption failed: {e}")
            return
        
        # Update database
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            config = session.query(EmailConfiguration).filter_by(user_id=1).first()
            if config:
                print(f"\nUpdating email config for user {config.user_id} ({config.email_address})")
                
                # Store old password for reference
                old_password = config.app_password
                
                # Update with new encrypted password
                config.app_password = encrypted_password
                session.commit()
                
                print("✓ Database updated successfully")
                print(f"Old encrypted password: {old_password}")
                print(f"New encrypted password: {encrypted_password}")
                
                # Verify the update
                print("\nVerifying database update...")
                updated_config = session.query(EmailConfiguration).filter_by(user_id=1).first()
                try:
                    verified_password = decrypt_value(updated_config.app_password)
                    if verified_password == test_password:
                        print("✓ Database verification passed")
                        print("The email automation can now be tested with this dummy password.")
                        print("\nNOTE: This will fail when trying to connect to Gmail since it's not a real app password.")
                        print("But it will test the encryption/decryption and connection logic.")
                    else:
                        print("✗ Database verification failed")
                except Exception as e:
                    print(f"✗ Database verification failed: {e}")
                    
            else:
                print("No email configuration found for user 1")
                
        except Exception as e:
            print(f"Database error: {e}")
            session.rollback()
        finally:
            session.close()

def main():
    # Check required environment variables
    required_vars = ["DATABASE_URL", "ENCRYPTION_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {missing_vars}")
        return
    
    print("This script will update the email configuration with a test password.")
    print("This is for testing purposes only and will replace the existing password.")
    print()
    
    response = input("Do you want to continue? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        update_test_password()
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main() 