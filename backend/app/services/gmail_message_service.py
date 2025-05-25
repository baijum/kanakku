"""
Gmail Message Service

This module provides database-based operations for managing processed Gmail Message IDs.
It replaces the file-based approach with database storage for better scalability and user isolation.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Set

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..extensions import db
from ..models import ProcessedGmailMessage

logger = logging.getLogger(__name__)


def load_processed_gmail_msgids(
    user_id: int, db_session: Optional[Session] = None
) -> Set[str]:
    """
    Load processed Gmail Message IDs for a specific user from the database.

    Args:
        user_id (int): The ID of the user
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        Set[str]: Set of processed Gmail Message IDs for the user
    """
    try:
        session = db_session or db.session

        # Query all processed Gmail message IDs for the user
        processed_messages = (
            session.query(ProcessedGmailMessage.gmail_message_id)
            .filter_by(user_id=user_id)
            .all()
        )

        # Extract message IDs into a set
        msgids = {msg.gmail_message_id for msg in processed_messages}

        logger.info(
            f"Loaded {len(msgids)} processed Gmail Message IDs for user {user_id}"
        )
        logger.debug(
            f"Processed message IDs for user {user_id}: {list(msgids)[:10]}..."
        )  # Log first 10 for debugging

        return msgids

    except Exception as e:
        logger.error(
            f"Error loading processed Gmail Message IDs for user {user_id}: {e}"
        )
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return set()  # Return empty set on error


def save_processed_gmail_msgid(
    user_id: int, gmail_message_id: str, db_session: Optional[Session] = None
) -> bool:
    """
    Save a single processed Gmail Message ID for a specific user to the database.

    Args:
        user_id (int): The ID of the user
        gmail_message_id (str): The Gmail Message ID to save
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        session = db_session or db.session

        # Create new processed message record
        processed_message = ProcessedGmailMessage(
            user_id=user_id,
            gmail_message_id=gmail_message_id,
            processed_at=datetime.now(timezone.utc),
        )

        session.add(processed_message)
        session.commit()

        logger.debug(
            f"Saved processed Gmail Message ID {gmail_message_id} for user {user_id}"
        )
        return True

    except IntegrityError:
        # Handle duplicate entries gracefully
        session.rollback()
        logger.debug(
            f"Gmail Message ID {gmail_message_id} already exists for user {user_id}"
        )
        return True  # Consider it successful since the message is already marked as processed

    except Exception as e:
        session.rollback()
        logger.error(
            f"Error saving processed Gmail Message ID {gmail_message_id} for user {user_id}: {e}"
        )
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return False


def save_processed_gmail_msgids(
    user_id: int, msgids: Set[str], db_session: Optional[Session] = None
) -> int:
    """
    Save multiple processed Gmail Message IDs for a specific user to the database.

    Args:
        user_id (int): The ID of the user
        msgids (Set[str]): Set of Gmail Message IDs to save
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        int: Number of new message IDs successfully saved
    """
    if not msgids:
        logger.debug(f"No Gmail Message IDs to save for user {user_id}")
        return 0

    try:
        session = db_session or db.session

        # Get existing message IDs for this user to avoid duplicates
        existing_msgids = load_processed_gmail_msgids(user_id, session)
        new_msgids = msgids - existing_msgids

        if not new_msgids:
            logger.debug(
                f"All {len(msgids)} Gmail Message IDs already exist for user {user_id}"
            )
            return 0

        # Create new processed message records for new IDs only
        new_records = []
        for msgid in new_msgids:
            processed_message = ProcessedGmailMessage(
                user_id=user_id,
                gmail_message_id=msgid,
                processed_at=datetime.now(timezone.utc),
            )
            new_records.append(processed_message)

        # Bulk insert new records
        session.add_all(new_records)
        session.commit()

        logger.info(
            f"Saved {len(new_records)} new processed Gmail Message IDs for user {user_id}"
        )
        return len(new_records)

    except Exception as e:
        session.rollback()
        logger.error(
            f"Error saving processed Gmail Message IDs for user {user_id}: {e}"
        )
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return 0


def is_gmail_message_processed(
    user_id: int, gmail_message_id: str, db_session: Optional[Session] = None
) -> bool:
    """
    Check if a Gmail Message ID has been processed for a specific user.

    Args:
        user_id (int): The ID of the user
        gmail_message_id (str): The Gmail Message ID to check
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        bool: True if the message has been processed, False otherwise
    """
    try:
        session = db_session or db.session

        # Check if the message ID exists for this user
        exists = (
            session.query(ProcessedGmailMessage)
            .filter_by(user_id=user_id, gmail_message_id=gmail_message_id)
            .first()
            is not None
        )

        logger.debug(
            f"Gmail Message ID {gmail_message_id} processed status for user {user_id}: {exists}"
        )
        return exists

    except Exception as e:
        logger.error(
            f"Error checking processed status for Gmail Message ID {gmail_message_id} and user {user_id}: {e}"
        )
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return False  # Assume not processed on error to avoid skipping messages


def get_processed_message_count(
    user_id: int, db_session: Optional[Session] = None
) -> int:
    """
    Get the total count of processed Gmail messages for a specific user.

    Args:
        user_id (int): The ID of the user
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        int: Total count of processed messages for the user
    """
    try:
        session = db_session or db.session

        count = session.query(ProcessedGmailMessage).filter_by(user_id=user_id).count()

        logger.debug(f"Total processed Gmail messages for user {user_id}: {count}")
        return count

    except Exception as e:
        logger.error(f"Error getting processed message count for user {user_id}: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return 0


def clear_processed_gmail_msgids(
    user_id: int, db_session: Optional[Session] = None
) -> bool:
    """
    Clear all processed Gmail Message IDs for a specific user.
    This is useful for testing or resetting a user's processed message history.

    Args:
        user_id (int): The ID of the user
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        bool: True if cleared successfully, False otherwise
    """
    try:
        session = db_session or db.session

        # Delete all processed messages for this user
        deleted_count = (
            session.query(ProcessedGmailMessage).filter_by(user_id=user_id).delete()
        )
        session.commit()

        logger.info(
            f"Cleared {deleted_count} processed Gmail Message IDs for user {user_id}"
        )
        return True

    except Exception as e:
        session.rollback()
        logger.error(
            f"Error clearing processed Gmail Message IDs for user {user_id}: {e}"
        )
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        return False
