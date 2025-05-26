#!/usr/bin/env python3
"""
Email Automation Worker Script

This script runs RQ workers that process email automation jobs.
It should be run as a separate process from the main web application.

Usage:
    python run_worker.py [--queue-name email_processing] [--redis-url redis://localhost:6379/0]
"""

import argparse
import logging
import os
import platform
import sys

logger = logging.getLogger(__name__)

# Fix for macOS forking issue - set this before any other imports
if platform.system() == "Darwin":  # macOS
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    logger.debug("Set OBJC_DISABLE_INITIALIZE_FORK_SAFETY for macOS compatibility")

import redis
from dotenv import load_dotenv
from rq import Queue, SimpleWorker, Worker

# Load environment variables from .env file
# This will look for .env files in the following order:
# 1. Current directory
# 2. Parent directory (banktransactions/)
# 3. Project root directory
# Required variables: DATABASE_URL, REDIS_URL
# Optional variables: GOOGLE_API_KEY, ENCRYPTION_KEY, LOG_LEVEL
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

# Configure logging
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
logger.debug(f"Setting log level to: {log_level}")

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
log_file = os.path.join(log_dir, "worker.log")

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
    level=getattr(logging, log_level, logging.DEBUG),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)


def create_db_session():
    """Create a database session for the worker."""
    logger.debug("Creating database session for worker...")
    session = get_database_session()
    logger.debug(f"Database session created: {session is not None}")
    return session


def get_worker_class():
    """Get the appropriate worker class based on the operating system."""
    logger.debug("Determining appropriate worker class...")
    system = platform.system()
    logger.debug(f"Detected operating system: {system}")

    if system == "Darwin":  # macOS
        logger.info("Detected macOS - using SimpleWorker to avoid forking issues")
        logger.debug("Selected SimpleWorker for macOS compatibility")
        return SimpleWorker
    else:  # Linux, Windows, etc.
        logger.info(f"Detected {system} - using regular Worker for better performance")
        logger.debug(f"Selected regular Worker for {system}")
        return Worker


def main():
    logger.debug("Starting main function")

    parser = argparse.ArgumentParser(description="Run email automation worker")
    parser.add_argument(
        "--queue-name",
        default="email_processing",
        help="Name of the Redis queue to process (default: email_processing)",
    )
    parser.add_argument(
        "--redis-url",
        default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        help="Redis URL (default: redis://localhost:6379/0)",
    )
    parser.add_argument(
        "--worker-name", default=None, help="Worker name (default: auto-generated)"
    )
    parser.add_argument(
        "--force-simple-worker",
        action="store_true",
        help="Force use of SimpleWorker regardless of OS (useful for debugging)",
    )

    args = parser.parse_args()
    logger.debug("Command line arguments parsed:")
    logger.debug(f"  queue_name: {args.queue_name}")
    logger.debug(f"  redis_url: {args.redis_url}")
    logger.debug(f"  worker_name: {args.worker_name}")
    logger.debug(f"  force_simple_worker: {args.force_simple_worker}")

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

        # Create queue
        logger.debug(f"Creating queue '{args.queue_name}'...")
        queue = Queue(args.queue_name, connection=redis_conn)
        logger.debug(f"Queue '{args.queue_name}' created successfully")
        try:
            logger.debug(f"Queue length: {len(queue)}")
        except (TypeError, AttributeError):
            logger.debug("Queue length: <unable to determine>")

        # Choose worker class based on OS or force flag
        logger.debug("Selecting worker class...")
        if args.force_simple_worker:
            worker_class = SimpleWorker
            worker_type = "SimpleWorker (forced)"
            logger.debug("Using SimpleWorker (forced by command line argument)")
        else:
            worker_class = get_worker_class()
            worker_type = worker_class.__name__
            logger.debug(f"Using {worker_type} based on OS detection")

        worker_name = args.worker_name or f"email_worker_{os.getpid()}"
        logger.debug(f"Worker name: {worker_name}")
        logger.debug(f"Process ID: {os.getpid()}")

        logger.debug("Creating worker instance...")
        worker = worker_class([queue], connection=redis_conn, name=worker_name)
        logger.debug("Worker instance created successfully")

        logger.info(
            f"Starting {worker_type} '{worker_name}' for queue '{args.queue_name}'"
        )
        logger.info("Worker is ready to process jobs. Press Ctrl+C to stop.")
        logger.debug("Starting worker.work() method...")

        # Start the worker
        worker.work()
        logger.debug("Worker.work() method completed")

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        logger.debug("KeyboardInterrupt received")
    except Exception as e:
        logger.error(f"Error starting worker: {str(e)}", exc_info=True)
        logger.debug(f"Startup exception details: {type(e).__name__}: {str(e)}")
        sys.exit(1)

    logger.debug("main function completed")


if __name__ == "__main__":
    main()
