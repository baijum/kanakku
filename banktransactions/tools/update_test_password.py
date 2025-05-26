#!/usr/bin/env python3
"""
Update Test Password Script

This script updates the email configuration with a test password for testing purposes.
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

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
sys.path.append(os.path.join(project_root, "backend"))
logger.debug(f"Added project paths to sys.path: {project_root}")


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


def update_test_password():
    """Update the email configuration with a test password."""
    logger.debug("Starting update_test_password function")
    print("=== Updating Test Password ===")

    # Create Flask app context
    logger.debug("Creating Flask app...")
    app = create_flask_app()

    with app.app_context():
        logger.debug("Entered Flask app context")

        logger.debug("Importing Flask models and encryption utilities...")
        from app.models import EmailConfiguration
        from app.utils.encryption import decrypt_value, encrypt_value

        logger.debug("Flask modules imported successfully")

        # Test password for Gmail (this would normally be a real app password)
        test_password = "dummy_gmail_app_password_for_testing"
        logger.debug(f"Test password defined: {len(test_password)} characters")

        print(f"Test password: {test_password}")
        print(
            "Note: This is a dummy password for testing. In real usage, you would need a valid Gmail app password."
        )
        print()

        # Encrypt the test password
        logger.debug("Starting encryption of test password...")
        try:
            encrypted_password = encrypt_value(test_password)
            print(f"Encrypted password: {encrypted_password}")
            logger.debug(
                f"Test password encrypted successfully: {bool(encrypted_password)}"
            )
            logger.debug(
                f"Encrypted password length: {len(encrypted_password) if encrypted_password else 'None'}"
            )

            # Verify encryption works
            logger.debug("Verifying encryption by decrypting...")
            decrypted_test = decrypt_value(encrypted_password)
            encryption_verified = decrypted_test == test_password

            if encryption_verified:
                print("✓ Encryption verification passed")
                logger.debug("Encryption verification successful")
            else:
                print("✗ Encryption verification failed")
                logger.error("Encryption verification failed")
                logger.debug(f"Expected: {test_password}, Got: {decrypted_test}")
                return

        except Exception as e:
            error_msg = f"Encryption failed: {e}"
            print(error_msg)
            logger.error(error_msg)
            logger.debug(
                f"Encryption exception details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            return

        # Update database using shared utilities
        logger.debug("Importing shared database utilities...")
        from shared.imports import (
            EmailConfiguration as SharedEmailConfiguration,
        )
        from shared.imports import (
            database_session,
        )

        logger.debug("Shared database utilities imported successfully")

        try:
            logger.debug("Creating database session...")
            with database_session() as session:
                logger.debug("Database session created successfully")

                logger.debug("Querying for email configuration for user 1...")
                config = (
                    session.query(SharedEmailConfiguration).filter_by(user_id=1).first()
                )

                if config:
                    logger.debug(f"Email configuration found for user {config.user_id}")
                    print(
                        f"\nUpdating email config for user {config.user_id} ({config.email_address})"
                    )
                    logger.debug(
                        f"Configuration details - Email: {config.email_address}"
                    )
                    logger.debug(
                        f"Configuration details - IMAP: {config.imap_server}:{config.imap_port}"
                    )

                    # Store old password for reference
                    old_password = config.app_password
                    logger.debug(
                        f"Old encrypted password length: {len(old_password) if old_password else 'None'}"
                    )

                    # Update with new encrypted password
                    logger.debug(
                        "Updating configuration with new encrypted password..."
                    )
                    config.app_password = encrypted_password
                    # Note: session.commit() is handled automatically by the context manager
                    logger.debug(
                        "Configuration updated (will be committed automatically)"
                    )

                    print("✓ Database updated successfully")
                    print(f"Old encrypted password: {old_password}")
                    print(f"New encrypted password: {encrypted_password}")

                    # Verify the update
                    print("\nVerifying database update...")
                    logger.debug("Verifying database update by re-querying...")
                    updated_config = (
                        session.query(SharedEmailConfiguration)
                        .filter_by(user_id=1)
                        .first()
                    )
                    logger.debug("Re-query completed")

                    try:
                        logger.debug(
                            "Attempting to decrypt updated password from database..."
                        )
                        verified_password = decrypt_value(updated_config.app_password)
                        verification_passed = verified_password == test_password

                        if verification_passed:
                            print("✓ Database verification passed")
                            print(
                                "The email automation can now be tested with this dummy password."
                            )
                            print(
                                "\nNOTE: This will fail when trying to connect to Gmail since it's not a real app password."
                            )
                            print(
                                "But it will test the encryption/decryption and connection logic."
                            )
                            logger.debug("Database verification successful")
                        else:
                            print("✗ Database verification failed")
                            logger.error("Database verification failed")
                            logger.debug(
                                f"Expected: {test_password}, Got: {verified_password}"
                            )
                    except Exception as e:
                        error_msg = f"✗ Database verification failed: {e}"
                        print(error_msg)
                        logger.error(error_msg)
                        logger.debug(
                            f"Database verification exception: {type(e).__name__}: {str(e)}",
                            exc_info=True,
                        )

                else:
                    print("No email configuration found for user 1")
                    logger.warning("No email configuration found for user 1")

        except Exception as e:
            error_msg = f"Database error: {e}"
            print(error_msg)
            logger.error(error_msg)
            logger.debug(
                f"Database exception details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

    logger.debug("update_test_password function completed")


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

    print("This script will update the email configuration with a test password.")
    print("This is for testing purposes only and will replace the existing password.")
    print()

    logger.debug("Prompting user for confirmation...")
    response = input("Do you want to continue? (y/N): ").strip().lower()
    logger.debug(f"User response: {response}")

    if response in ["y", "yes"]:
        logger.debug("User confirmed, proceeding with password update")
        update_test_password()
    else:
        print("Operation cancelled.")
        logger.debug("User cancelled operation")

    logger.debug("main function completed")


if __name__ == "__main__":
    # Set up basic logging for this script
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.debug("Update test password script started")
    main()
    logger.debug("Update test password script finished")
