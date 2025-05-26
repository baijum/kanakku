#!/usr/bin/env python3
"""
Email processor for automated email parsing and transaction creation.
Adapted from the working main.py implementation.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env files
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

# Set up project paths and clean imports using shared package
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from shared.imports import (
    EmailConfiguration,
    decrypt_value_standalone,
    get_bank_emails,
    load_processed_gmail_msgids,
    save_processed_gmail_msgid,
)

# Standard library imports
import json
import logging
from datetime import datetime, timezone
from typing import Dict

from rq import get_current_job
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def process_user_emails_standalone(user_id: int) -> Dict:
    """
    Standalone function to process emails for a user using the proven working logic from main.py.
    This creates its own database session without Flask app context.
    """
    logger.debug(f"Starting email processing for user_id: {user_id}")
    try:
        # Create database session
        logger.debug("Setting up database connection")
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL environment variable not set")
            raise ValueError("DATABASE_URL environment variable not set")

        logger.debug(f"Creating database engine with URL: {db_url[:20]}...")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        logger.debug("Database session created successfully")

        try:
            # Get the current job (optional for manual testing)
            job = get_current_job()
            logger.debug(
                f"Current RQ job: {job.id if job else 'None (manual execution)'}"
            )

            # Get user's email configuration
            logger.debug(f"Fetching email configuration for user_id: {user_id}")
            config = (
                db_session.query(EmailConfiguration).filter_by(user_id=user_id).first()
            )
            if not config or not config.is_enabled:
                logger.debug(
                    f"Email configuration not found or disabled for user_id: {user_id}"
                )
                return {
                    "status": "skipped",
                    "reason": "configuration_not_found_or_disabled",
                }

            logger.debug(
                f"Found email configuration: server={config.imap_server}, port={config.imap_port}, email={config.email_address}"
            )
            logger.debug(f"Last check time: {config.last_check_time}")

            # Decrypt the app password using backend's encryption utility
            logger.debug("Decrypting app password")
            decrypted_password = decrypt_value_standalone(config.app_password)
            if not decrypted_password:
                logger.error("Failed to decrypt app password")
                return {
                    "status": "error",
                    "error": "Failed to decrypt app password",
                }
            logger.debug("App password decrypted successfully")

            # Load processed Gmail message IDs (using the database implementation)
            logger.debug("Loading processed Gmail message IDs from database")
            processed_gmail_msgids = load_processed_gmail_msgids(user_id=user_id)
            initial_msgid_count = len(processed_gmail_msgids)
            logger.debug(
                f"Loaded {initial_msgid_count} previously processed Gmail message IDs for user {user_id}"
            )

            # Get bank email addresses from sample emails or use default
            bank_emails = ["alerts@axisbank.com"]  # Default
            if config.sample_emails:
                try:
                    sample_emails = json.loads(config.sample_emails)
                    # Extract bank emails from sample emails if available
                    bank_emails_from_samples = []
                    for sample in sample_emails:
                        if isinstance(sample, dict) and "from" in sample:
                            bank_emails_from_samples.append(sample["from"])
                    if bank_emails_from_samples:
                        bank_emails = list(
                            set(bank_emails_from_samples)
                        )  # Remove duplicates
                        logger.debug(f"Using bank emails from samples: {bank_emails}")
                except json.JSONDecodeError:
                    logger.warning(
                        f"Failed to parse sample emails for user {config.user_id}"
                    )
                    logger.debug(
                        f"Sample emails JSON parse error for: {config.sample_emails[:100]}..."
                    )

            logger.debug(f"Processing emails from bank addresses: {bank_emails}")

            # Create a callback function to save individual Gmail message IDs to database
            def save_msgid_to_db(gmail_message_id):
                """Callback function to save individual Gmail message ID to database"""
                try:
                    result = save_processed_gmail_msgid(
                        gmail_message_id, user_id=user_id
                    )
                    if result:
                        logger.debug(
                            f"Saved Gmail Message ID {gmail_message_id} to database for user {user_id}"
                        )
                    else:
                        logger.warning(
                            f"Failed to save Gmail Message ID {gmail_message_id} to database for user {user_id}"
                        )
                    return result
                except Exception as e:
                    logger.error(
                        f"Error saving Gmail Message ID {gmail_message_id} to database for user {user_id}: {e}"
                    )
                    return False

            # Use the proven working email processing logic from main.py with database callback
            logger.debug("Calling get_bank_emails function with database callback")
            updated_msgids, newly_processed_count = get_bank_emails(
                username=config.email_address,
                password=decrypted_password,
                bank_email_list=bank_emails,
                processed_gmail_msgids=processed_gmail_msgids,
                save_msgid_callback=save_msgid_to_db,
            )

            logger.debug(
                f"Email processing completed: {newly_processed_count} new transactions processed"
            )

            # Update last check time
            logger.debug("Updating last check time in configuration")
            config.last_check_time = datetime.now(timezone.utc)
            db_session.commit()
            logger.debug("Configuration updated and committed")

            result = {
                "status": "success",
                "processed_count": newly_processed_count,
                "errors": [],
            }
            logger.debug(f"Email processing completed successfully: {result}")
            return result

        finally:
            if db_session:
                logger.debug("Closing database session")
                db_session.close()

    except Exception as e:
        logger.error(f"Error in process_user_emails_standalone: {str(e)}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return {"status": "error", "error": str(e)}
