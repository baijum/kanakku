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
from ..utils.logging_utils import (
    log_db_error,
    log_debug,
    log_service_entry,
    log_service_exit,
)

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
    log_service_entry(
        "GmailMessageService", "load_processed_gmail_msgids", user_id=user_id
    )

    try:
        session = db_session or db.session

        log_debug(
            "Querying processed Gmail messages from database",
            extra_data={"user_id": user_id},
            module_name="GmailMessageService",
        )

        # Query all processed Gmail message IDs for the user
        processed_messages = (
            session.query(ProcessedGmailMessage.gmail_message_id)
            .filter_by(user_id=user_id)
            .all()
        )

        # Extract message IDs into a set
        msgids = {msg.gmail_message_id for msg in processed_messages}

        log_debug(
            "Successfully loaded processed Gmail Message IDs",
            extra_data={
                "user_id": user_id,
                "count": len(msgids),
                "sample_ids": list(msgids)[:5] if msgids else [],
            },
            module_name="GmailMessageService",
        )

        log_service_exit(
            "GmailMessageService",
            "load_processed_gmail_msgids",
            f"loaded {len(msgids)} message IDs",
        )
        return msgids

    except Exception as e:
        log_db_error(e, operation="load", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "load_processed_gmail_msgids", "failed with error"
        )
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
    log_service_entry(
        "GmailMessageService",
        "save_processed_gmail_msgid",
        user_id=user_id,
        gmail_message_id=gmail_message_id,
    )

    try:
        session = db_session or db.session

        log_debug(
            "Creating new processed message record",
            extra_data={"user_id": user_id, "gmail_message_id": gmail_message_id},
            module_name="GmailMessageService",
        )

        # Create new processed message record
        processed_message = ProcessedGmailMessage(
            user_id=user_id,
            gmail_message_id=gmail_message_id,
            processed_at=datetime.now(timezone.utc),
        )

        session.add(processed_message)
        session.commit()

        log_debug(
            "Successfully saved processed Gmail Message ID",
            extra_data={"user_id": user_id, "gmail_message_id": gmail_message_id},
            module_name="GmailMessageService",
        )

        log_service_exit("GmailMessageService", "save_processed_gmail_msgid", "success")
        return True

    except IntegrityError:
        # Handle duplicate entries gracefully
        session.rollback()
        log_debug(
            "Gmail Message ID already exists (duplicate entry)",
            extra_data={"user_id": user_id, "gmail_message_id": gmail_message_id},
            module_name="GmailMessageService",
        )
        log_service_exit(
            "GmailMessageService",
            "save_processed_gmail_msgid",
            "duplicate entry (success)",
        )
        return True  # Consider it successful since the message is already marked as processed

    except Exception as e:
        session.rollback()
        log_db_error(e, operation="save", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "save_processed_gmail_msgid", "failed with error"
        )
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
    log_service_entry(
        "GmailMessageService",
        "save_processed_gmail_msgids",
        user_id=user_id,
        msgids_count=len(msgids),
    )

    if not msgids:
        log_debug(
            "No Gmail Message IDs to save",
            extra_data={"user_id": user_id},
            module_name="GmailMessageService",
        )
        log_service_exit(
            "GmailMessageService", "save_processed_gmail_msgids", "no messages to save"
        )
        return 0

    try:
        session = db_session or db.session

        log_debug(
            "Loading existing message IDs to avoid duplicates",
            extra_data={"user_id": user_id, "new_msgids_count": len(msgids)},
            module_name="GmailMessageService",
        )

        # Get existing message IDs for this user to avoid duplicates
        existing_msgids = load_processed_gmail_msgids(user_id, session)
        new_msgids = msgids - existing_msgids

        if not new_msgids:
            log_debug(
                "All Gmail Message IDs already exist",
                extra_data={"user_id": user_id, "total_msgids": len(msgids)},
                module_name="GmailMessageService",
            )
            log_service_exit(
                "GmailMessageService",
                "save_processed_gmail_msgids",
                "all messages already exist",
            )
            return 0

        log_debug(
            "Creating bulk insert for new message IDs",
            extra_data={
                "user_id": user_id,
                "new_count": len(new_msgids),
                "existing_count": len(existing_msgids),
            },
            module_name="GmailMessageService",
        )

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

        log_debug(
            "Successfully saved new processed Gmail Message IDs",
            extra_data={"user_id": user_id, "saved_count": len(new_records)},
            module_name="GmailMessageService",
        )

        log_service_exit(
            "GmailMessageService",
            "save_processed_gmail_msgids",
            f"saved {len(new_records)} new messages",
        )
        return len(new_records)

    except Exception as e:
        session.rollback()
        log_db_error(e, operation="bulk_save", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "save_processed_gmail_msgids", "failed with error"
        )
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
    log_service_entry(
        "GmailMessageService",
        "is_gmail_message_processed",
        user_id=user_id,
        gmail_message_id=gmail_message_id,
    )

    try:
        session = db_session or db.session

        log_debug(
            "Checking if Gmail message has been processed",
            extra_data={"user_id": user_id, "gmail_message_id": gmail_message_id},
            module_name="GmailMessageService",
        )

        # Check if the message ID exists for this user
        exists = (
            session.query(ProcessedGmailMessage)
            .filter_by(user_id=user_id, gmail_message_id=gmail_message_id)
            .first()
            is not None
        )

        log_debug(
            f"Gmail Message processed status: {'processed' if exists else 'not processed'}",
            extra_data={
                "user_id": user_id,
                "gmail_message_id": gmail_message_id,
                "exists": exists,
            },
            module_name="GmailMessageService",
        )

        log_service_exit(
            "GmailMessageService", "is_gmail_message_processed", f"result: {exists}"
        )
        return exists

    except Exception as e:
        log_db_error(e, operation="check", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "is_gmail_message_processed", "failed with error"
        )
        return False


def get_processed_message_count(
    user_id: int, db_session: Optional[Session] = None
) -> int:
    """
    Get the total count of processed Gmail Message IDs for a specific user.

    Args:
        user_id (int): The ID of the user
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        int: Total count of processed Gmail Message IDs for the user
    """
    log_service_entry(
        "GmailMessageService", "get_processed_message_count", user_id=user_id
    )

    try:
        session = db_session or db.session

        log_debug(
            "Counting processed Gmail messages",
            extra_data={"user_id": user_id},
            module_name="GmailMessageService",
        )

        # Count all processed Gmail message IDs for the user
        count = session.query(ProcessedGmailMessage).filter_by(user_id=user_id).count()

        log_debug(
            "Successfully counted processed Gmail messages",
            extra_data={"user_id": user_id, "count": count},
            module_name="GmailMessageService",
        )

        log_service_exit(
            "GmailMessageService", "get_processed_message_count", f"count: {count}"
        )
        return count

    except Exception as e:
        log_db_error(e, operation="count", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "get_processed_message_count", "failed with error"
        )
        return 0


def clear_processed_gmail_msgids(
    user_id: int, db_session: Optional[Session] = None
) -> bool:
    """
    Clear all processed Gmail Message IDs for a specific user from the database.

    Args:
        user_id (int): The ID of the user
        db_session (Session, optional): Database session to use. If None, uses db.session

    Returns:
        bool: True if cleared successfully, False otherwise
    """
    log_service_entry(
        "GmailMessageService", "clear_processed_gmail_msgids", user_id=user_id
    )

    try:
        session = db_session or db.session

        log_debug(
            "Clearing all processed Gmail messages for user",
            extra_data={"user_id": user_id},
            module_name="GmailMessageService",
        )

        # Delete all processed Gmail message IDs for the user
        deleted_count = (
            session.query(ProcessedGmailMessage).filter_by(user_id=user_id).delete()
        )
        session.commit()

        log_debug(
            "Successfully cleared processed Gmail messages",
            extra_data={"user_id": user_id, "deleted_count": deleted_count},
            module_name="GmailMessageService",
        )

        log_service_exit(
            "GmailMessageService",
            "clear_processed_gmail_msgids",
            f"cleared {deleted_count} messages",
        )
        return True

    except Exception as e:
        session.rollback()
        log_db_error(e, operation="clear", model="ProcessedGmailMessage")
        log_service_exit(
            "GmailMessageService", "clear_processed_gmail_msgids", "failed with error"
        )
        return False
