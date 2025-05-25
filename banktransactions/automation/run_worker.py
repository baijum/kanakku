#!/usr/bin/env python3
"""
Email Automation Worker Script

This script runs RQ workers that process email automation jobs.
It should be run as a separate process from the main web application.

Usage:
    python run_worker.py [--queue-name email_processing] [--redis-url redis://localhost:6379/0]
"""

import os
import sys
import platform

# Fix for macOS forking issue - set this before any other imports
if platform.system() == "Darwin":  # macOS
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

import logging
import argparse
import redis
from rq import Queue, Worker, SimpleWorker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
# This will look for .env files in the following order:
# 1. Current directory
# 2. Parent directory (banktransactions/)
# 3. Project root directory
# Required variables: DATABASE_URL, REDIS_URL
# Optional variables: GOOGLE_API_KEY, ENCRYPTION_KEY, LOG_LEVEL
load_dotenv()

# Also try to load from parent directories for flexibility
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
# Also add the backend app to the Python path
sys.path.append(os.path.join(project_root, "backend"))

# Configure logging
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.DEBUG),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "..", "logs", "worker.log")
        ),
    ],
)
logger = logging.getLogger(__name__)


def create_db_session():
    """Create a database session for the worker."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def get_worker_class():
    """Get the appropriate worker class based on the operating system."""
    system = platform.system()
    if system == "Darwin":  # macOS
        logger.info("Detected macOS - using SimpleWorker to avoid forking issues")
        return SimpleWorker
    else:  # Linux, Windows, etc.
        logger.info(f"Detected {system} - using regular Worker for better performance")
        return Worker


def main():
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

    try:
        # Connect to Redis
        redis_conn = redis.from_url(args.redis_url)

        # Test Redis connection
        redis_conn.ping()
        logger.info(f"Connected to Redis at {args.redis_url}")

        # Create database session
        db_session = create_db_session()
        logger.info("Connected to database")

        # Create queue
        queue = Queue(args.queue_name, connection=redis_conn)

        # Choose worker class based on OS or force flag
        if args.force_simple_worker:
            worker_class = SimpleWorker
            worker_type = "SimpleWorker (forced)"
        else:
            worker_class = get_worker_class()
            worker_type = worker_class.__name__

        worker_name = args.worker_name or f"email_worker_{os.getpid()}"
        worker = worker_class([queue], connection=redis_conn, name=worker_name)

        logger.info(
            f"Starting {worker_type} '{worker_name}' for queue '{args.queue_name}'"
        )
        logger.info("Worker is ready to process jobs. Press Ctrl+C to stop.")

        # Start the worker
        worker.work()

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Error starting worker: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
