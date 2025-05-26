#!/usr/bin/env python3
"""
Debug Encryption Script

This script helps debug encryption issues with the email configuration.
"""

import logging
import os
import sys

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
logger.debug("Loading environment variables...")
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
logger.debug("Environment variables loaded")

# Set up project paths
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.debug(f"Added project root to sys.path: {project_root}")

logger.debug("Importing shared modules...")
from shared.imports import EmailConfiguration, database_session, setup_project_paths

logger.debug("Setting up project paths...")
setup_project_paths()
logger.debug("Project paths setup completed")


def create_flask_app():
    """Create a minimal Flask app for testing."""
    logger.debug("Creating Flask app for testing...")
    from flask import Flask

    app = Flask(__name__)
    logger.debug("Flask app instance created")

    # Set required configuration
    logger.debug("Setting Flask app configuration...")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL")
    app.config["ENCRYPTION_KEY"] = os.getenv("ENCRYPTION_KEY")
    app.config["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    app.config["SECRET_KEY"] = "test-secret-key"

    logger.debug("Flask app configuration completed")
    logger.debug(f"DATABASE_URL present: {bool(app.config['DATABASE_URL'])}")
    logger.debug(f"REDIS_URL present: {bool(app.config['REDIS_URL'])}")
    logger.debug(f"ENCRYPTION_KEY present: {bool(app.config['ENCRYPTION_KEY'])}")
    logger.debug(f"GOOGLE_API_KEY present: {bool(app.config['GOOGLE_API_KEY'])}")

    return app


def debug_encryption():
    """Debug the encryption issue."""
    logger.debug("Starting debug_encryption function")
    print("=== Debugging Encryption ===")

    # Create Flask app context
    logger.debug("Creating Flask app...")
    app = create_flask_app()

    with app.app_context():
        logger.debug("Entered Flask app context")

        logger.debug("Importing encryption utilities...")
        from app.utils.encryption import (
            decrypt_value,
            encrypt_value,
            get_encryption_key,
        )

        logger.debug("Encryption utilities imported successfully")

        # Check encryption key
        logger.debug("Getting encryption key...")
        encryption_key = get_encryption_key()
        print(f"Encryption key: {encryption_key}")
        print(
            f"Encryption key length: {len(encryption_key) if encryption_key else 'None'}"
        )
        logger.debug(f"Encryption key retrieved: {bool(encryption_key)}")
        logger.debug(
            f"Encryption key length: {len(encryption_key) if encryption_key else 'None'}"
        )
        print()

        # Test encryption/decryption with a test value
        test_password = "test_password_123"
        print(f"Testing encryption with: '{test_password}'")
        logger.debug("Starting encryption test with test password")

        try:
            logger.debug("Attempting to encrypt test password...")
            encrypted = encrypt_value(test_password)
            print(f"Encrypted value: {encrypted}")
            print(f"Encrypted value length: {len(encrypted) if encrypted else 'None'}")
            logger.debug(f"Encryption successful: {bool(encrypted)}")
            logger.debug(
                f"Encrypted value length: {len(encrypted) if encrypted else 'None'}"
            )

            logger.debug("Attempting to decrypt test password...")
            decrypted = decrypt_value(encrypted)
            print(f"Decrypted value: {decrypted}")
            test_passed = decrypted == test_password
            print(
                f"Encryption/decryption test: {'✓ PASSED' if test_passed else '✗ FAILED'}"
            )
            logger.debug(f"Decryption successful: {bool(decrypted)}")
            logger.debug(f"Encryption/decryption test passed: {test_passed}")
        except Exception as e:
            print(f"Encryption test failed: {e}")
            logger.error(f"Encryption test failed: {e}")
            logger.debug(
                f"Encryption test exception details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

        print()

        # Check database configuration using shared utilities
        logger.debug("Starting database configuration check...")
        try:
            logger.debug("Creating database session...")
            with database_session() as session:
                logger.debug("Database session created successfully")

                logger.debug("Querying for email configuration for user 1...")
                config = session.query(EmailConfiguration).filter_by(user_id=1).first()

                if config:
                    logger.debug(f"Email configuration found for user {config.user_id}")
                    print(f"Email config found for user {config.user_id}:")
                    print(f"  Email: {config.email_address}")
                    print(f"  IMAP Server: {config.imap_server}")
                    print(f"  IMAP Port: {config.imap_port}")
                    print(f"  Enabled: {config.is_enabled}")
                    print(f"  App password (encrypted): {config.app_password}")
                    print(
                        f"  App password length: {len(config.app_password) if config.app_password else 'None'}"
                    )

                    logger.debug(
                        f"Configuration details - Email: {config.email_address}"
                    )
                    logger.debug(
                        f"Configuration details - IMAP: {config.imap_server}:{config.imap_port}"
                    )
                    logger.debug(
                        f"Configuration details - Enabled: {config.is_enabled}"
                    )
                    logger.debug(
                        f"Configuration details - App password length: {len(config.app_password) if config.app_password else 'None'}"
                    )
                    print()

                    # Try to decrypt the stored password
                    print("Attempting to decrypt stored password...")
                    logger.debug("Attempting to decrypt stored app password...")
                    try:
                        decrypted_password = decrypt_value(config.app_password)
                        if decrypted_password:
                            print(
                                f"✓ Successfully decrypted password (length: {len(decrypted_password)})"
                            )
                            logger.debug(
                                f"Successfully decrypted stored password (length: {len(decrypted_password)})"
                            )
                            # Don't print the actual password for security
                        else:
                            print("✗ Decryption returned None/empty")
                            logger.warning(
                                "Decryption returned None/empty for stored password"
                            )
                    except Exception as e:
                        print(f"✗ Decryption failed: {e}")
                        logger.error(f"Decryption of stored password failed: {e}")
                        logger.debug(
                            f"Decryption exception details: {type(e).__name__}: {str(e)}",
                            exc_info=True,
                        )

                    print()

                    # Test re-encryption with a dummy password
                    print("Testing re-encryption with dummy password...")
                    logger.debug("Testing re-encryption with dummy password...")
                    dummy_password = "dummy_app_password_for_testing"
                    try:
                        logger.debug("Encrypting dummy password...")
                        new_encrypted = encrypt_value(dummy_password)
                        print(f"New encrypted value: {new_encrypted}")
                        logger.debug(
                            f"Dummy password encrypted successfully: {bool(new_encrypted)}"
                        )

                        # Test decryption of new value
                        logger.debug("Decrypting newly encrypted dummy password...")
                        new_decrypted = decrypt_value(new_encrypted)
                        re_encryption_passed = new_decrypted == dummy_password
                        print(
                            f"Re-encryption test: {'✓ PASSED' if re_encryption_passed else '✗ FAILED'}"
                        )
                        logger.debug(
                            f"Re-encryption test passed: {re_encryption_passed}"
                        )

                        # Optionally update the database with the test password
                        print(
                            "\nWould you like to update the database with the test password? (This is for testing only)"
                        )
                        print("The test password is: 'dummy_app_password_for_testing'")
                        logger.debug(
                            "Prompted user about updating database with test password"
                        )

                    except Exception as e:
                        print(f"Re-encryption test failed: {e}")
                        logger.error(f"Re-encryption test failed: {e}")
                        logger.debug(
                            f"Re-encryption exception details: {type(e).__name__}: {str(e)}",
                            exc_info=True,
                        )

                else:
                    print("No email configuration found for user 1")
                    logger.warning("No email configuration found for user 1")

        except Exception as e:
            print(f"Database error: {e}")
            logger.error(f"Database error: {e}")
            logger.debug(
                f"Database exception details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

    logger.debug("debug_encryption function completed")


def main():
    logger.debug("Starting main function")

    # Check required environment variables
    logger.debug("Checking required environment variables...")
    required_vars = ["DATABASE_URL", "ENCRYPTION_KEY"]
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        logger.debug(f"Environment variable {var}: {'present' if value else 'missing'}")
        if not value:
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"ERROR: Missing environment variables: {missing_vars}"
        print(error_msg)
        logger.error(error_msg)
        return

    logger.debug("All required environment variables present")
    debug_encryption()
    logger.debug("main function completed")


if __name__ == "__main__":
    # Set up basic logging for this script
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.debug("Debug encryption script started")
    main()
    logger.debug("Debug encryption script finished")
