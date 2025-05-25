#!/usr/bin/env python3
"""
Direct Email Processing Test Script

This script tests the email processing functionality directly without using RQ,
bypassing the macOS forking issues.
"""

import os
import sys
import json
from datetime import datetime, timezone
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
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL")
    app.config["ENCRYPTION_KEY"] = os.getenv("ENCRYPTION_KEY")
    app.config["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    app.config["SECRET_KEY"] = "test-secret-key"

    return app


def test_direct_email_processing():
    """Test email processing directly without RQ."""
    print("Testing direct email processing...")

    # Create Flask app context
    app = create_flask_app()

    with app.app_context():
        # Import required modules (inside app context)
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models import EmailConfiguration
        from app.utils.encryption import decrypt_value
        from banktransactions.imap_client import CustomIMAPClient
        from banktransactions.email_parser import extract_transaction_details
        from banktransactions.api_client import APIClient

        # Test with user ID 1
        user_id = 1
        print(f"Processing emails for user {user_id}...")

        db_session = None
        imap_client = None

        try:
            # Create database session
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable not set")

            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            db_session = Session()

            # Get user's email configuration
            config = (
                db_session.query(EmailConfiguration).filter_by(user_id=user_id).first()
            )
            if not config or not config.is_enabled:
                return {
                    "status": "skipped",
                    "reason": "configuration_not_found_or_disabled",
                }

            print(f"Found email config for {config.email_address}")

            # Decrypt the app password
            decrypted_password = decrypt_value(config.app_password)
            if not decrypted_password:
                return {
                    "status": "error",
                    "error": "Failed to decrypt app password",
                }

            print("✓ Successfully decrypted app password")

            # Initialize IMAP client
            imap_client = CustomIMAPClient(
                server=config.imap_server,
                port=config.imap_port,
                username=config.email_address,
                password=decrypted_password,
            )

            print(f"Connecting to {config.imap_server}:{config.imap_port}...")

            # Connect to email server
            imap_client.connect()
            print("✓ Successfully connected to email server")

            # Get unread emails since last check
            last_check = config.last_check_time or datetime.min
            print(f"Checking for emails since: {last_check}")

            emails = imap_client.get_unread_emails(since=last_check)
            print(f"Found {len(emails)} unread emails")

            processed_count = 0
            errors = []
            api_client = APIClient()

            for i, email in enumerate(emails):
                print(f"\nProcessing email {i+1}/{len(emails)}:")
                print(f"  Subject: {email.get('subject', 'No subject')}")
                print(f"  From: {email.get('from', 'Unknown sender')}")
                print(f"  Date: {email.get('date', 'Unknown date')}")

                try:
                    # Extract transaction details
                    body = email["body"]

                    # Get sample emails for few-shot prompting
                    sample_emails = []
                    if config.sample_emails:
                        try:
                            sample_emails = json.loads(config.sample_emails)
                        except json.JSONDecodeError:
                            print("  Warning: Failed to parse sample emails")

                    # Use the LLM-based parser
                    transaction_data = extract_transaction_details(
                        body, sample_emails=sample_emails
                    )

                    if transaction_data and transaction_data.get("amount") != "Unknown":
                        print(
                            f"  ✓ Extracted transaction: {transaction_data.get('amount')} {transaction_data.get('currency', 'USD')}"
                        )

                        # Add metadata
                        transaction_data.update(
                            {
                                "email_id": email["id"],
                                "email_date": (
                                    email["date"].isoformat()
                                    if email.get("date")
                                    else None
                                ),
                                "email_subject": email.get("subject", ""),
                                "email_from": email.get("from", ""),
                            }
                        )

                        # Create transaction via API
                        response = api_client.create_transaction(
                            user_id=user_id, transaction_data=transaction_data
                        )

                        if response.get("success"):
                            processed_count += 1
                            # Mark email as processed
                            imap_client.mark_as_processed(email["id"])
                            print("  ✓ Successfully created transaction")
                        else:
                            error_msg = f"Failed to create transaction: {response.get('error', 'Unknown error')}"
                            print(f"  ✗ {error_msg}")
                            errors.append(error_msg)
                    else:
                        print("  - Skipped: no valid transaction data found")

                except Exception as e:
                    error_msg = (
                        f"Error processing email {email.get('id', 'unknown')}: {str(e)}"
                    )
                    print(f"  ✗ {error_msg}")
                    errors.append(error_msg)

            # Update last check time
            config.last_check_time = datetime.now(timezone.utc)
            db_session.commit()
            print(f"\n✓ Updated last check time to {config.last_check_time}")

            result = {
                "status": "success",
                "processed_count": processed_count,
                "total_emails": len(emails),
                "errors": errors,
            }

            print(f"Result: {result}")
            return result

        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "error": str(e)}
        finally:
            if imap_client:
                try:
                    imap_client.disconnect()
                    print("✓ Disconnected from email server")
                except:
                    pass
            if db_session:
                db_session.close()


def check_email_config():
    """Check the email configuration in the database."""
    print("Checking email configuration...")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import EmailConfiguration

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        configs = session.query(EmailConfiguration).all()
        print(f"Found {len(configs)} email configurations:")
        for config in configs:
            print(
                f"  User {config.user_id}: enabled={config.is_enabled}, email={config.email_address}, last_check={config.last_check_time}"
            )
    except Exception as e:
        print(f"Error checking config: {e}")
    finally:
        session.close()


def main():
    print("=== Direct Email Processing Test ===")
    print()

    # Check required environment variables
    required_vars = ["DATABASE_URL", "REDIS_URL", "ENCRYPTION_KEY", "GOOGLE_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"ERROR: Missing environment variables: {missing_vars}")
        print("Please set these variables before running the test.")
        return

    print("✓ All required environment variables are set")
    print()

    # Check email configuration
    check_email_config()
    print()

    # Test direct email processing
    result = test_direct_email_processing()
    print()

    if result.get("status") == "success":
        print("✓ Email processing completed successfully!")
        print(
            f"  Processed: {result.get('processed_count', 0)} out of {result.get('total_emails', 0)} emails"
        )
        if result.get("errors"):
            print(f"  Errors: {len(result.get('errors'))} errors occurred")
            for error in result.get("errors"):
                print(f"    - {error}")
    elif result.get("status") == "skipped":
        print(f"⚠ Email processing skipped: {result.get('reason')}")
    else:
        print(f"✗ Email processing failed: {result.get('error')}")


if __name__ == "__main__":
    main()
