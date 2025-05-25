#!/usr/bin/env python3
"""
Email processor for automated email parsing and transaction creation.
Adapted from the working main.py implementation.
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
from typing import Dict

from rq import get_current_job
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import encryption utilities directly
from cryptography.fernet import Fernet
import base64

# Import the working banktransactions modules
from banktransactions.core.imap_client import get_bank_emails
from banktransactions.core.processed_ids_db import (
    load_processed_gmail_msgids,
    save_processed_gmail_msgid,
)

logger = logging.getLogger(__name__)


def get_encryption_key_standalone():
    """
    Get the encryption key from environment variables without Flask context.
    """
    logger.debug("Getting encryption key from environment variables")
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        logger.warning("No encryption key found in environment. Using temporary key.")
        logger.debug("Generating temporary encryption key")
        key = Fernet.generate_key().decode()

    # Ensure the key is properly formatted for Fernet
    if not key.endswith("="):
        logger.debug("Padding encryption key for proper formatting")
        # Pad the key if necessary
        key = key + "=" * (-len(key) % 4)

    try:
        # Attempt to decode and validate the key
        logger.debug("Validating encryption key format")
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            raise ValueError("Invalid key length")
        logger.debug("Encryption key validation successful")
    except Exception as e:
        logger.error(f"Invalid encryption key: {str(e)}")
        logger.debug("Generating new temporary key due to validation failure")
        # Generate a temporary key for this session
        key = Fernet.generate_key().decode()

    return key


def decrypt_value_standalone(encrypted_value):
    """
    Decrypt an encrypted value without Flask context.
    """
    logger.debug(
        f"Attempting to decrypt value (length: {len(encrypted_value) if encrypted_value else 0})"
    )
    if not encrypted_value:
        logger.debug("No encrypted value provided, returning None")
        return None

    key = get_encryption_key_standalone()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    try:
        logger.debug("Decrypting value using Fernet")
        decrypted_data = f.decrypt(encrypted_value.encode())
        decrypted_result = decrypted_data.decode()
        logger.debug("Value decryption successful")
        return decrypted_result
    except Exception as e:
        logger.error(f"Failed to decrypt value: {str(e)}")
        logger.debug(
            f"Decryption failed with encrypted_value type: {type(encrypted_value)}"
        )
        return None


def process_user_emails_standalone(user_id: int) -> Dict:
    """
    Standalone function to process emails for a user using the proven working logic from main.py.
    This creates its own database session without Flask app context.
    """
    logger.debug(f"Starting email processing for user_id: {user_id}")
    try:
        # Import models and utilities directly without Flask context
        # We need to set up the database models manually
        logger.debug("Importing SQLAlchemy components and setting up models")
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text

        # Create a standalone model definition
        Base = declarative_base()

        class EmailConfiguration(Base):
            __tablename__ = "user_email_configurations"

            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, nullable=False)
            is_enabled = Column(Boolean, default=False)
            imap_server = Column(String(255), default="imap.gmail.com")
            imap_port = Column(Integer, default=993)
            email_address = Column(String(255), nullable=False)
            app_password = Column(String(255), nullable=False)
            polling_interval = Column(String(50), default="hourly")
            last_check_time = Column(DateTime, nullable=True)
            sample_emails = Column(Text, nullable=True)
            last_processed_email_id = Column(String(255), nullable=True)
            created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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

            # Decrypt the app password using standalone function
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
