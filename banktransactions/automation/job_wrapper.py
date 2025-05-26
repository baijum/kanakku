#!/usr/bin/env python3
"""
Job wrapper for email automation tasks.
This module provides a simple interface that SpawnWorker can reliably import.
"""

import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_python_path():
    """Set up Python path for the spawned process."""
    logger.debug("Starting Python path setup for spawned process")

    # Get the absolute path to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    backend_path = os.path.join(project_root, "backend")
    banktransactions_path = os.path.join(project_root, "banktransactions")

    logger.debug(f"Current directory: {current_dir}")
    logger.debug(f"Project root: {project_root}")
    logger.debug(f"Backend path: {backend_path}")
    logger.debug(f"Banktransactions path: {banktransactions_path}")

    # Add to Python path if not already there
    paths_to_add = [project_root, backend_path, banktransactions_path]
    added_paths = []

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
            added_paths.append(path)
            logger.debug(f"Added to sys.path: {path}")
        else:
            logger.debug(f"Path already in sys.path: {path}")

    logger.debug(f"Total paths added to sys.path: {len(added_paths)}")

    # Also ensure the current working directory is the project root
    current_cwd = os.getcwd()
    logger.debug(f"Current working directory: {current_cwd}")

    if current_cwd != project_root:
        logger.debug(f"Changing working directory from {current_cwd} to {project_root}")
        os.chdir(project_root)
        logger.debug("Working directory changed successfully")
    else:
        logger.debug("Working directory already set to project root")

    logger.debug("Python path setup completed")


# Set up the path immediately when this module is imported
logger.debug("Job wrapper module imported, setting up Python path...")
setup_python_path()
logger.debug("Python path setup completed during module import")

# Now we can safely import the actual function
logger.debug("Attempting to import email processor function...")
try:
    from banktransactions.automation.email_processor import (
        process_user_emails_standalone as _process_emails,
    )

    logger.debug("Successfully imported process_user_emails_standalone")
except ImportError as e:
    logger.error(f"Failed to import email processor: {e}")
    logger.debug(f"Import error details: {type(e).__name__}: {str(e)}")

    # Debug information for troubleshooting
    current_cwd = os.getcwd()
    logger.debug(f"Current working directory: {current_cwd}")
    logger.debug(f"Python path: {sys.path}")
    logger.debug("Looking for: banktransactions.automation.email_processor")

    # Try to find the file manually
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_file = os.path.join(current_dir, "email_processor.py")
    logger.debug(f"Expected file location: {expected_file}")
    logger.debug(f"File exists: {os.path.exists(expected_file)}")

    # List the contents of the current directory
    if os.path.exists(current_dir):
        try:
            dir_contents = os.listdir(current_dir)
            logger.debug(f"Contents of automation directory: {dir_contents}")
        except Exception as list_error:
            logger.debug(f"Error listing directory contents: {list_error}")
    else:
        logger.debug(f"Automation directory does not exist: {current_dir}")

    raise


def process_user_emails_standalone(user_id: int):
    """
    Wrapper function for email processing that can be reliably imported by SpawnWorker.

    Args:
        user_id (int): The user ID to process emails for

    Returns:
        dict: Result of email processing
    """
    logger.debug(f"Job wrapper called for user_id: {user_id}")
    logger.debug("Calling underlying email processor function...")

    try:
        result = _process_emails(user_id)
        logger.debug(f"Email processing completed for user {user_id}")
        logger.debug(f"Result status: {result.get('status', 'unknown')}")
        logger.debug(f"Processed count: {result.get('processed_count', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Error in job wrapper for user {user_id}: {e}")
        logger.debug(
            f"Job wrapper exception details: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        raise
