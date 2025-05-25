#!/usr/bin/env python3
"""
Email Automation Scheduler Script

This script runs the scheduler that manages periodic email processing jobs.
It should be run as a separate process from the main web application.

Usage:
    python run_scheduler.py [--redis-url redis://localhost:6379/0] [--interval 300]
"""

import os
import sys
import logging
import argparse
import time
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
# This will look for .env files in the following order:
# 1. Current directory
# 2. Parent directory (banktransactions/)
# 3. Project root directory
# Required variables: DATABASE_URL, REDIS_URL
# Optional variables: LOG_LEVEL
load_dotenv()

# Also try to load from parent directories for flexibility
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
# Also add the backend app to the Python path for model imports
backend_path = os.path.join(project_root, "..", "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from banktransactions.automation.scheduler import EmailScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "..", "logs", "scheduler.log")
        ),
    ],
)
logger = logging.getLogger(__name__)


def create_db_session():
    """Create a database session for the scheduler."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def main():
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

    try:
        # Connect to Redis
        redis_conn = redis.from_url(args.redis_url)

        # Test Redis connection
        redis_conn.ping()
        logger.info(f"Connected to Redis at {args.redis_url}")

        # Create database session
        db_session = create_db_session()
        logger.info("Connected to database")

        # Create scheduler
        scheduler = EmailScheduler(redis_conn, db_session)

        logger.info(f"Starting scheduler with {args.interval}s interval")
        logger.info("Scheduler is ready. Press Ctrl+C to stop.")

        # Run scheduler loop
        while True:
            try:
                scheduler.schedule_jobs()
                logger.debug("Scheduled jobs check completed")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
                time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
