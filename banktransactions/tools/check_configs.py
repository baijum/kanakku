#!/usr/bin/env python3
"""
Check email configurations script.
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

# Set up project paths
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.debug(f"Added project root to sys.path: {project_root}")

logger.debug("Importing shared modules...")
from shared.imports import EmailConfiguration, database_session

logger.debug("Shared modules imported successfully")


def main():
    """Check email configurations."""
    logger.debug("Starting check_configs main function")

    try:
        logger.debug("Creating database session...")
        with database_session() as session:
            logger.debug("Database session created successfully")

            logger.debug("Querying all email configurations...")
            configs = session.query(EmailConfiguration).all()
            logger.debug(f"Found {len(configs)} email configurations")

            print(f"Found {len(configs)} email configurations:")
            print()

            for i, config in enumerate(configs, 1):
                logger.debug(
                    f"Processing configuration {i}/{len(configs)} for user {config.user_id}"
                )

                print(f"Configuration {i}:")
                print(f"  User ID: {config.user_id}")
                print(f"  Email: {config.email_address}")
                print(f"  IMAP Server: {config.imap_server}:{config.imap_port}")
                print(f"  Enabled: {config.is_enabled}")
                print(f"  Polling Interval: {config.polling_interval}")
                print(f"  Last Check: {config.last_check_time}")
                print(
                    f"  App Password Length: {len(config.app_password) if config.app_password else 'None'}"
                )
                print(f"  Sample Emails: {bool(config.sample_emails)}")
                print()

                logger.debug(f"Configuration details - User: {config.user_id}")
                logger.debug(f"Configuration details - Email: {config.email_address}")
                logger.debug(
                    f"Configuration details - IMAP: {config.imap_server}:{config.imap_port}"
                )
                logger.debug(f"Configuration details - Enabled: {config.is_enabled}")
                logger.debug(
                    f"Configuration details - Polling: {config.polling_interval}"
                )
                logger.debug(
                    f"Configuration details - Last Check: {config.last_check_time}"
                )
                logger.debug(
                    f"Configuration details - App Password Length: {len(config.app_password) if config.app_password else 'None'}"
                )
                logger.debug(
                    f"Configuration details - Has Sample Emails: {bool(config.sample_emails)}"
                )

    except Exception as e:
        error_msg = f"Error checking configurations: {e}"
        print(error_msg)
        logger.error(error_msg)
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)

    logger.debug("check_configs main function completed")


if __name__ == "__main__":
    # Set up basic logging for this script
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.debug("Check configs script started")
    main()
    logger.debug("Check configs script finished")
