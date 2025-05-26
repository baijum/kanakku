#!/usr/bin/env python3
"""
Email Automation Scheduler Script

This script runs the scheduler that manages periodic email processing jobs.
It should be run as a separate process from the main web application.

Usage:
    python run_scheduler.py [--redis-url redis://localhost:6379/0] [--interval 300]
"""

import argparse
import logging
import os
import sys
import time

import redis
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
# This will look for .env files in the following order:
# 1. Current directory
# 2. Parent directory (banktransactions/)
# 3. Project root directory
# Required variables: DATABASE_URL, REDIS_URL
# Optional variables: LOG_LEVEL
logger.debug("Loading environment variables...")
load_dotenv()

# Also try to load from parent directories for flexibility
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
logger.debug("Environment variables loaded")

# Set up project paths and use shared imports instead of path manipulation
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.debug(f"Added project root to sys.path: {project_root}")

logger.debug("Importing shared modules...")
from shared.imports import get_database_session, setup_project_paths

logger.debug("Shared modules imported successfully")

logger.debug("Setting up project paths...")
setup_project_paths()
logger.debug("Project paths setup completed")

logger.debug("Importing EmailScheduler...")
from banktransactions.automation.scheduler import EmailScheduler

logger.debug("EmailScheduler imported successfully")

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
log_file = os.path.join(log_dir, "scheduler.log")

# Create logs directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Set up logging handlers
handlers = [logging.StreamHandler(sys.stdout)]

# Try to add file handler, but don't fail if we can't
try:
    handlers.append(logging.FileHandler(log_file))
except (OSError, PermissionError) as e:
    # If we can't create the log file (e.g., in CI environments), just use console logging only.
    print(
        f"Warning: Could not create log file {log_file}: {e}. Using console logging only."
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)


def create_db_session():
    """Create a database session for the scheduler."""
    logger.debug("Creating database session for scheduler...")
    session = get_database_session()
    logger.debug(f"Database session created: {session is not None}")
    return session


def main():
    logger.debug("Starting main function")

    parser = argparse.ArgumentParser(description="Run email automation scheduler")
    parser.add_argument(
        "--redis-url",
        default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        help="Redis URL (default: redis://localhost:6379/0)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,  # 5 minutes
        help="Scheduling interval in seconds (default: 300)",
    )

    args = parser.parse_args()
    logger.debug(
        f"Command line arguments parsed: redis_url={args.redis_url}, interval={args.interval}"
    )

    try:
        # Connect to Redis
        logger.debug(f"Attempting to connect to Redis at {args.redis_url}")
        redis_conn = redis.from_url(args.redis_url)

        # Test Redis connection
        logger.debug("Testing Redis connection...")
        redis_conn.ping()
        logger.info(f"Connected to Redis at {args.redis_url}")
        logger.debug("Redis connection test successful")

        # Create database session
        logger.debug("Creating database session...")
        db_session = create_db_session()
        logger.info("Connected to database")
        logger.debug("Database session created successfully")

        # Create scheduler
        logger.debug("Creating EmailScheduler instance...")
        scheduler = EmailScheduler(redis_conn, db_session)
        logger.debug("EmailScheduler instance created successfully")

        logger.info(f"Starting scheduler with {args.interval}s interval")
        logger.info("Scheduler is ready. Press Ctrl+C to stop.")
        logger.debug("Entering main scheduler loop...")

        # Run scheduler loop
        loop_count = 0
        while True:
            try:
                loop_count += 1
                logger.debug(f"Starting scheduler loop iteration {loop_count}")

                scheduler.schedule_jobs()
                logger.debug("Scheduled jobs check completed")

                logger.debug(f"Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)

            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                logger.debug("KeyboardInterrupt received, breaking from main loop")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
                logger.debug(
                    f"Exception in loop iteration {loop_count}: {type(e).__name__}: {str(e)}"
                )
                logger.debug(
                    f"Continuing after error, sleeping for {args.interval} seconds..."
                )
                time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        logger.debug("KeyboardInterrupt received during startup")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}", exc_info=True)
        logger.debug(f"Startup exception details: {type(e).__name__}: {str(e)}")
        sys.exit(1)

    logger.debug("main function completed")


if __name__ == "__main__":
    main()
