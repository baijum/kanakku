#!/usr/bin/env python3
"""
Email processor for automated email parsing and transaction creation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env files
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, project_root)
# Also add the backend app to the Python path
sys.path.append(os.path.join(project_root, "backend"))

# Now import everything else
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from rq import get_current_job
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import Flask app creation function
from app import create_app

logger = logging.getLogger(__name__)


def process_user_emails_standalone(user_id: int) -> Dict:
    """
    Standalone function to process emails for a user.
    This creates its own database session and Flask app context.
    """
    try:
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Import models inside app context
            from app.models import EmailConfiguration
            from app.utils.encryption import decrypt_value
            from banktransactions.imap_client import IMAPClient
            from banktransactions.email_parser import (
                extract_transaction_details_pure_llm,
                detect_currency,
                convert_currency,
            )
            from banktransactions.api_client import APIClient
            
            # Create database session
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable not set")

            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            db_session = Session()

            try:
                # Process emails directly here instead of using EmailProcessor
                # Get the current job
                job = get_current_job()
                if not job:
                    raise Exception("No job context found")

                # Get user's email configuration
                config = (
                    db_session.query(EmailConfiguration).filter_by(user_id=user_id).first()
                )
                if not config or not config.is_enabled:
                    return {
                        "status": "skipped",
                        "reason": "configuration_not_found_or_disabled",
                    }

                # Decrypt the app password
                decrypted_password = decrypt_value(config.app_password)
                if not decrypted_password:
                    return {
                        "status": "error",
                        "error": "Failed to decrypt app password",
                    }

                # Initialize clients
                imap_client = IMAPClient(
                    server=config.imap_server,
                    port=config.imap_port,
                    username=config.email_address,
                    password=decrypted_password,
                )
                api_client = APIClient()

                try:
                    # Connect to email server
                    imap_client.connect()

                    # Get unread emails since last check
                    last_check = config.last_check_time or datetime.min
                    emails = imap_client.get_unread_emails(since=last_check)

                    processed_count = 0
                    errors = []

                    for email in emails:
                        try:
                            # Extract transaction details using the improved LLM-based parser
                            transaction_data = _extract_transaction_data(email, config)

                            if transaction_data and transaction_data.get("amount") != "Unknown":
                                # Create transaction via API
                                response = api_client.create_transaction(
                                    user_id=user_id, transaction_data=transaction_data
                                )

                                if response.get("success"):
                                    processed_count += 1
                                    # Mark email as processed
                                    imap_client.mark_as_processed(email["id"])
                                    logger.info(
                                        f"Successfully processed email {email['id']} for user {user_id}"
                                    )
                                else:
                                    error_msg = f"Failed to create transaction for email {email['id']}: {response.get('error', 'Unknown error')}"
                                    logger.error(error_msg)
                                    errors.append(error_msg)
                            else:
                                logger.info(
                                    f"Skipping email {email['id']} - no valid transaction data found"
                                )

                        except Exception as e:
                            logger.error(f"Error processing email {email['id']}: {str(e)}")
                            errors.append(f"Error processing email {email['id']}: {str(e)}")

                    # Update last check time
                    config.last_check_time = datetime.now(timezone.utc)
                    db_session.commit()

                    return {
                        "status": "success",
                        "processed_count": processed_count,
                        "errors": errors,
                    }

                finally:
                    if imap_client:
                        imap_client.disconnect()

            finally:
                if db_session:
                    db_session.close()

    except Exception as e:
        logger.error(f"Error in process_user_emails_standalone: {str(e)}")
        return {"status": "error", "error": str(e)}


def _extract_transaction_data(email: Dict, config) -> Optional[Dict]:
    """Extract transaction data from email using the improved LLM-based parser."""
    try:
        # Import here to ensure it's available
        from banktransactions.email_parser import extract_transaction_details_pure_llm
        
        # Clean the email body
        body = email["body"]

        # Get sample emails for few-shot prompting
        sample_emails = []
        if config.sample_emails:
            try:
                sample_emails = json.loads(config.sample_emails)
            except json.JSONDecodeError:
                logger.warning(
                    f"Failed to parse sample emails for user {config.user_id}"
                )

        # Use the improved LLM-based parser with few-shot examples
        transaction_data = extract_transaction_details_pure_llm(
            body, sample_emails=sample_emails
        )

        # Add additional metadata
        transaction_data.update(
            {
                "email_id": email["id"],
                "email_date": (
                    email["date"].isoformat() if email.get("date") else None
                ),
                "email_subject": email.get("subject", ""),
                "email_from": email.get("from", ""),
            }
        )

        return transaction_data

    except Exception as e:
        logger.error(f"Error in _extract_transaction_data: {str(e)}")
        return None
