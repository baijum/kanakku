#!/usr/bin/env python3
"""
Database-based Gmail Message ID processing module.

This module provides the same interface as the original processed_ids.py but uses
database storage instead of file-based storage for better scalability and user isolation.
"""

import logging
import os
import sys
from typing import Optional, Set

try:
    # Set up project paths and import Flask app context and database service using shared imports
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from app import create_app
    from app.extensions import db
    from shared.imports import (
        clear_processed_gmail_msgids as db_clear_processed_gmail_msgids,
    )
    from shared.imports import (
        get_processed_message_count as db_get_processed_message_count,
    )
    from shared.imports import (
        is_gmail_message_processed as db_is_gmail_message_processed,
    )
    from shared.imports import (
        load_processed_gmail_msgids as db_load_processed_gmail_msgids,
    )
    from shared.imports import (
        save_processed_gmail_msgid as db_save_processed_gmail_msgid,
    )
    from shared.imports import (
        save_processed_gmail_msgids as db_save_processed_gmail_msgids,
    )

    # Create Flask app context for database operations
    app = create_app()

except ImportError as e:
    logging.warning(f"Could not import Flask app or database service: {e}")
    logging.warning(
        "Database service not available - processed IDs functionality will be limited"
    )
    app = None


def load_processed_gmail_msgids(
    user_id: Optional[int] = None, filepath: Optional[str] = None
) -> Set[str]:
    """
    Load processed Gmail Message IDs.

    Args:
        user_id (int, optional): The ID of the user (required for database mode)
        filepath (str, optional): File path for file-based fallback (deprecated)

    Returns:
        Set[str]: Set of processed Gmail Message IDs
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                return db_load_processed_gmail_msgids(user_id)
        except Exception as e:
            logging.error(
                f"Error loading processed Gmail Message IDs from database for user {user_id}: {e}"
            )
            logging.warning("Falling back to file-based approach")

    # Database not available and no fallback
    logging.error("Database service not available and no fallback method")
    return set()


def save_processed_gmail_msgids(
    msgids: Set[str], user_id: Optional[int] = None, filepath: Optional[str] = None
) -> bool:
    """
    Save processed Gmail Message IDs.

    Args:
        msgids (Set[str]): Set of Gmail Message IDs to save
        user_id (int, optional): The ID of the user (required for database mode)
        filepath (str, optional): File path for file-based fallback (deprecated)

    Returns:
        bool: True if saved successfully, False otherwise
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                saved_count = db_save_processed_gmail_msgids(user_id, msgids)
                logging.info(
                    f"Saved {saved_count} new processed Gmail Message IDs to database for user {user_id}"
                )
                return True
        except Exception as e:
            logging.error(
                f"Error saving processed Gmail Message IDs to database for user {user_id}: {e}"
            )
            logging.warning("Falling back to file-based approach")

    # Database not available and no fallback
    logging.error("Database service not available and no fallback method")
    return False


def save_processed_gmail_msgid(
    gmail_message_id: str, user_id: Optional[int] = None
) -> bool:
    """
    Save a single processed Gmail Message ID.

    Args:
        gmail_message_id (str): The Gmail Message ID to save
        user_id (int, optional): The ID of the user (required for database mode)

    Returns:
        bool: True if saved successfully, False otherwise
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                return db_save_processed_gmail_msgid(user_id, gmail_message_id)
        except Exception as e:
            logging.error(
                f"Error saving processed Gmail Message ID {gmail_message_id} to database for user {user_id}: {e}"
            )
            return False
    else:
        logging.error(
            "Database approach not available and single message save not supported in file mode"
        )
        return False


def is_gmail_message_processed(
    gmail_message_id: str,
    user_id: Optional[int] = None,
    processed_msgids: Optional[Set[str]] = None,
) -> bool:
    """
    Check if a Gmail Message ID has been processed.

    Args:
        gmail_message_id (str): The Gmail Message ID to check
        user_id (int, optional): The ID of the user (required for database mode)
        processed_msgids (Set[str], optional): Set of processed message IDs for file-based fallback

    Returns:
        bool: True if the message has been processed, False otherwise
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                return db_is_gmail_message_processed(user_id, gmail_message_id)
        except Exception as e:
            logging.error(
                f"Error checking processed status for Gmail Message ID {gmail_message_id} and user {user_id}: {e}"
            )
            return False
    elif processed_msgids is not None:
        # Fall back to checking in-memory set
        return gmail_message_id in processed_msgids
    else:
        logging.error("Neither database approach nor processed_msgids set available")
        return False


def get_processed_message_count(user_id: Optional[int] = None) -> int:
    """
    Get the total count of processed Gmail messages.

    Args:
        user_id (int, optional): The ID of the user (required for database mode)

    Returns:
        int: Total count of processed messages
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                return db_get_processed_message_count(user_id)
        except Exception as e:
            logging.error(
                f"Error getting processed message count for user {user_id}: {e}"
            )
            return 0
    else:
        logging.error("Database approach not available")
        return 0


def clear_processed_gmail_msgids(user_id: Optional[int] = None) -> bool:
    """
    Clear all processed Gmail Message IDs.

    Args:
        user_id (int, optional): The ID of the user (required for database mode)

    Returns:
        bool: True if cleared successfully, False otherwise
    """
    if app and user_id is not None:
        # Use database-based approach
        try:
            with app.app_context():
                return db_clear_processed_gmail_msgids(user_id)
        except Exception as e:
            logging.error(
                f"Error clearing processed Gmail Message IDs for user {user_id}: {e}"
            )
            return False
    else:
        logging.error("Database approach not available")
        return False


# Backward compatibility: maintain the original interface for existing code
# These functions will work with the file-based approach if database is not available
def load_processed_gmail_msgids_file(filepath: Optional[str] = None) -> Set[str]:
    """Load processed Gmail Message IDs from file (backward compatibility)."""
    return load_processed_gmail_msgids(user_id=None, filepath=filepath)


def save_processed_gmail_msgids_file(
    msgids: Set[str], filepath: Optional[str] = None
) -> None:
    """Save processed Gmail Message IDs to file (backward compatibility)."""
    save_processed_gmail_msgids(msgids, user_id=None, filepath=filepath)
