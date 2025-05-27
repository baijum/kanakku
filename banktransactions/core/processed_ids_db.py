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

logger = logging.getLogger(__name__)

try:
    logger.debug("Attempting to import Flask app and database dependencies...")
    # Set up project paths and import Flask app context and database service using shared imports
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.debug(f"Added project root to sys.path: {project_root}")

    # Import database utilities first to avoid circular imports
    # Import Flask app and extensions after shared imports
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
    logger.debug("Creating Flask app for database operations...")
    app = create_app()
    logger.debug("Flask app created successfully")

except ImportError as e:
    logger.warning(f"Could not import Flask app or database service: {e}")
    logger.warning(
        "Database service not available - processed IDs functionality will be limited"
    )
    logger.debug(f"Import error details: {type(e).__name__}: {str(e)}")
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
    logger.debug(f"Starting load_processed_gmail_msgids for user_id: {user_id}")
    logger.debug(f"Filepath parameter: {filepath}")
    logger.debug(f"App available: {app is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug(
            "Using database-based approach to load processed Gmail Message IDs"
        )
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                result = db_load_processed_gmail_msgids(user_id)
                logger.debug(
                    f"Successfully loaded {len(result)} processed Gmail Message IDs from database for user {user_id}"
                )
                return result
        except Exception as e:
            logger.error(
                f"Error loading processed Gmail Message IDs from database for user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            logger.warning("Falling back to file-based approach")

    # Database not available and no fallback
    logger.error("Database service not available and no fallback method")
    logger.debug("Returning empty set due to unavailable database service")
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
    logger.debug(f"Starting save_processed_gmail_msgids for user_id: {user_id}")
    logger.debug(f"Number of message IDs to save: {len(msgids)}")
    logger.debug(f"Filepath parameter: {filepath}")
    logger.debug(f"App available: {app is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug(
            "Using database-based approach to save processed Gmail Message IDs"
        )
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                saved_count = db_save_processed_gmail_msgids(user_id, msgids)
                logger.info(
                    f"Saved {saved_count} new processed Gmail Message IDs to database for user {user_id}"
                )
                logger.debug("Database save operation completed successfully")
                return True
        except Exception as e:
            logger.error(
                f"Error saving processed Gmail Message IDs to database for user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            logger.warning("Falling back to file-based approach")

    # Database not available and no fallback
    logger.error("Database service not available and no fallback method")
    logger.debug("Returning False due to unavailable database service")
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
    logger.debug(f"Starting save_processed_gmail_msgid for user_id: {user_id}")
    logger.debug(f"Gmail Message ID to save: {gmail_message_id}")
    logger.debug(f"App available: {app is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug("Using database-based approach to save single Gmail Message ID")
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                result = db_save_processed_gmail_msgid(user_id, gmail_message_id)
                if result:
                    logger.debug(
                        f"Successfully saved Gmail Message ID {gmail_message_id} to database for user {user_id}"
                    )
                else:
                    logger.warning(
                        f"Failed to save Gmail Message ID {gmail_message_id} to database for user {user_id}"
                    )
                return result
        except Exception as e:
            logger.error(
                f"Error saving processed Gmail Message ID {gmail_message_id} to database for user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            return False
    else:
        logger.error(
            "Database approach not available and single message save not supported in file mode"
        )
        logger.debug("Returning False due to unavailable database approach")
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
    logger.debug(f"Starting is_gmail_message_processed for user_id: {user_id}")
    logger.debug(f"Gmail Message ID to check: {gmail_message_id}")
    logger.debug(f"App available: {app is not None}")
    logger.debug(f"Processed msgids set provided: {processed_msgids is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug("Using database-based approach to check Gmail Message ID")
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                result = db_is_gmail_message_processed(user_id, gmail_message_id)
                logger.debug(
                    f"Database check result for Gmail Message ID {gmail_message_id}: {result}"
                )
                return result
        except Exception as e:
            logger.error(
                f"Error checking processed status for Gmail Message ID {gmail_message_id} and user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            return False
    elif processed_msgids is not None:
        # Fall back to checking in-memory set
        logger.debug("Using in-memory set fallback to check Gmail Message ID")
        result = gmail_message_id in processed_msgids
        logger.debug(
            f"In-memory check result for Gmail Message ID {gmail_message_id}: {result}"
        )
        return result
    else:
        logger.error("Neither database approach nor processed_msgids set available")
        logger.debug("Returning False due to no available checking method")
        return False


def get_processed_message_count(user_id: Optional[int] = None) -> int:
    """
    Get the total count of processed Gmail messages.

    Args:
        user_id (int, optional): The ID of the user (required for database mode)

    Returns:
        int: Total count of processed messages
    """
    logger.debug(f"Starting get_processed_message_count for user_id: {user_id}")
    logger.debug(f"App available: {app is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug("Using database-based approach to get processed message count")
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                count = db_get_processed_message_count(user_id)
                logger.debug(
                    f"Retrieved processed message count from database: {count}"
                )
                return count
        except Exception as e:
            logger.error(
                f"Error getting processed message count for user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            return 0

    logger.error("Database service not available for getting processed message count")
    logger.debug("Returning 0 due to unavailable database service")
    return 0


def clear_processed_gmail_msgids(user_id: Optional[int] = None) -> bool:
    """
    Clear all processed Gmail Message IDs for a user.

    Args:
        user_id (int, optional): The ID of the user (required for database mode)

    Returns:
        bool: True if cleared successfully, False otherwise
    """
    logger.debug(f"Starting clear_processed_gmail_msgids for user_id: {user_id}")
    logger.debug(f"App available: {app is not None}")

    if app and user_id is not None:
        # Use database-based approach
        logger.debug(
            "Using database-based approach to clear processed Gmail Message IDs"
        )
        try:
            with app.app_context():
                logger.debug("Created Flask app context")
                result = db_clear_processed_gmail_msgids(user_id)
                if result:
                    logger.debug(
                        f"Successfully cleared processed Gmail Message IDs for user {user_id}"
                    )
                else:
                    logger.warning(
                        f"Failed to clear processed Gmail Message IDs for user {user_id}"
                    )
                return result
        except Exception as e:
            logger.error(
                f"Error clearing processed Gmail Message IDs for user {user_id}: {e}"
            )
            logger.debug(
                f"Database error details: {type(e).__name__}: {str(e)}", exc_info=True
            )
            return False
    else:
        logger.error(
            "Database service not available for clearing processed Gmail Message IDs"
        )
        logger.debug("Returning False due to unavailable database service")
        return False


def load_processed_gmail_msgids_file(filepath: Optional[str] = None) -> Set[str]:
    """
    Load processed Gmail Message IDs from file (deprecated).
    This function is kept for backward compatibility but is deprecated.
    """
    logger.debug(f"Starting load_processed_gmail_msgids_file with filepath: {filepath}")
    logger.warning(
        "load_processed_gmail_msgids_file is deprecated - use database approach instead"
    )
    logger.debug("Returning empty set for deprecated file-based approach")
    return set()


def save_processed_gmail_msgids_file(
    msgids: Set[str], filepath: Optional[str] = None
) -> None:
    """
    Save processed Gmail Message IDs to file (deprecated).
    This function is kept for backward compatibility but is deprecated.
    """
    logger.debug(f"Starting save_processed_gmail_msgids_file with filepath: {filepath}")
    logger.debug(f"Number of message IDs to save: {len(msgids)}")
    logger.warning(
        "save_processed_gmail_msgids_file is deprecated - use database approach instead"
    )
    logger.debug("No operation performed for deprecated file-based approach")
