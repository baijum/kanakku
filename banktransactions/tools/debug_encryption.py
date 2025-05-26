#!/usr/bin/env python3
"""
Debug Encryption Script

This script helps debug encryption issues with the email configuration.
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Set up project paths
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from shared.imports import EmailConfiguration, database_session, setup_project_paths

setup_project_paths()


def create_flask_app():
    """Create a minimal Flask app for testing."""
    from flask import Flask

    app = Flask(__name__)

    # Set required configuration
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL")
    app.config["ENCRYPTION_KEY"] = os.getenv("ENCRYPTION_KEY")
    app.config["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    app.config["SECRET_KEY"] = "test-secret-key"

    return app


def debug_encryption():
    """Debug the encryption issue."""
    print("=== Debugging Encryption ===")

    # Create Flask app context
    app = create_flask_app()

    with app.app_context():
        from app.utils.encryption import (
            decrypt_value,
            encrypt_value,
            get_encryption_key,
        )

        # Check encryption key
        encryption_key = get_encryption_key()
        print(f"Encryption key: {encryption_key}")
        print(
            f"Encryption key length: {len(encryption_key) if encryption_key else 'None'}"
        )
        print()

        # Test encryption/decryption with a test value
        test_password = "test_password_123"
        print(f"Testing encryption with: '{test_password}'")

        try:
            encrypted = encrypt_value(test_password)
            print(f"Encrypted value: {encrypted}")
            print(f"Encrypted value length: {len(encrypted) if encrypted else 'None'}")

            decrypted = decrypt_value(encrypted)
            print(f"Decrypted value: {decrypted}")
            print(
                f"Encryption/decryption test: {'✓ PASSED' if decrypted == test_password else '✗ FAILED'}"
            )
        except Exception as e:
            print(f"Encryption test failed: {e}")

        print()

        # Check database configuration using shared utilities
        try:
            with database_session() as session:
                config = session.query(EmailConfiguration).filter_by(user_id=1).first()
                if config:
                    print(f"Email config found for user {config.user_id}:")
                    print(f"  Email: {config.email_address}")
                    print(f"  IMAP Server: {config.imap_server}")
                    print(f"  IMAP Port: {config.imap_port}")
                    print(f"  Enabled: {config.is_enabled}")
                    print(f"  App password (encrypted): {config.app_password}")
                    print(
                        f"  App password length: {len(config.app_password) if config.app_password else 'None'}"
                    )
                    print()

                    # Try to decrypt the stored password
                    print("Attempting to decrypt stored password...")
                    try:
                        decrypted_password = decrypt_value(config.app_password)
                        if decrypted_password:
                            print(
                                f"✓ Successfully decrypted password (length: {len(decrypted_password)})"
                            )
                            # Don't print the actual password for security
                        else:
                            print("✗ Decryption returned None/empty")
                    except Exception as e:
                        print(f"✗ Decryption failed: {e}")

                    print()

                    # Test re-encryption with a dummy password
                    print("Testing re-encryption with dummy password...")
                    dummy_password = "dummy_app_password_for_testing"
                    try:
                        new_encrypted = encrypt_value(dummy_password)
                        print(f"New encrypted value: {new_encrypted}")

                        # Test decryption of new value
                        new_decrypted = decrypt_value(new_encrypted)
                        print(
                            f"Re-encryption test: {'✓ PASSED' if new_decrypted == dummy_password else '✗ FAILED'}"
                        )

                        # Optionally update the database with the test password
                        print(
                            "\nWould you like to update the database with the test password? (This is for testing only)"
                        )
                        print("The test password is: 'dummy_app_password_for_testing'")

                    except Exception as e:
                        print(f"Re-encryption test failed: {e}")

                else:
                    print("No email configuration found for user 1")

        except Exception as e:
            print(f"Database error: {e}")


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

    debug_encryption()


if __name__ == "__main__":
    main()
