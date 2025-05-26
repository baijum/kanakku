import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from rq_scheduler import Scheduler
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
logger.debug(f"Added project root to sys.path: {project_root}")

# Also add the backend app to the Python path
backend_path = os.path.join(project_root, "..", "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)
    logger.debug(f"Added backend path to sys.path: {backend_path}")

try:
    logger.debug("Attempting to import EmailConfiguration from app.models...")
    from app.models import EmailConfiguration

    logger.debug("Successfully imported EmailConfiguration from app.models")
except ImportError:
    logger.warning(
        "Failed to import EmailConfiguration from app.models, using fallback"
    )
    # Fallback: define a minimal EmailConfiguration class for standalone operation
    from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    logger.debug("Created declarative base for fallback EmailConfiguration")

    class EmailConfiguration(Base):
        __tablename__ = "user_email_configurations"

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, nullable=False)
        is_enabled = Column(Boolean, default=False)
        imap_server = Column(String(255), default="imap.gmail.com")
        imap_port = Column(Integer, default=993)
        email_address = Column(String(255), nullable=False)
        app_password = Column(String(255), nullable=False)
        polling_interval = Column(String(50), default="hourly")
        last_check_time = Column(DateTime, nullable=True)
        sample_emails = Column(Text, nullable=True)
        last_processed_email_id = Column(String(255), nullable=True)

    logger.debug("Created fallback EmailConfiguration class")

logger.debug("Importing automation modules...")
from banktransactions.automation.email_processor import (
    process_user_emails_standalone,
)
from banktransactions.automation.job_utils import (
    generate_job_id,
    get_user_job_status,
    has_user_job_pending,
)

logger.debug("Successfully imported automation modules")


class EmailScheduler:
    def __init__(self, redis_conn, db_session: Session):
        logger.debug("Initializing EmailScheduler...")
        self.scheduler = Scheduler(connection=redis_conn)
        self.redis_conn = redis_conn
        self.db = db_session
        logger.debug(
            f"EmailScheduler initialized with redis connection: {redis_conn is not None}"
        )
        logger.debug(
            f"EmailScheduler initialized with db session: {db_session is not None}"
        )

    def schedule_jobs(self):
        """Schedule email processing jobs for all enabled configurations."""
        logger.debug("Starting schedule_jobs method")
        try:
            # Get all enabled configurations
            logger.debug("Querying database for enabled email configurations...")
            configs = self.db.query(EmailConfiguration).filter_by(is_enabled=True).all()
            logger.debug(f"Found {len(configs)} enabled email configurations")

            for i, config in enumerate(configs, 1):
                logger.debug(
                    f"Processing configuration {i}/{len(configs)} for user {config.user_id}"
                )
                logger.debug(f"  Email: {config.email_address}")
                logger.debug(f"  IMAP Server: {config.imap_server}:{config.imap_port}")
                logger.debug(f"  Polling Interval: {config.polling_interval}")
                logger.debug(f"  Last Check Time: {config.last_check_time}")
                self._schedule_user_job(config)

            logger.debug("Completed schedule_jobs method")

        except Exception as e:
            logger.error(f"Error in schedule_jobs: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True
            )

    def _schedule_user_job(self, config: EmailConfiguration):
        """Schedule a job for a specific user's email configuration."""
        logger.debug(f"Starting _schedule_user_job for user {config.user_id}")
        try:
            # Check if user already has a pending job (running, scheduled, or queued)
            logger.debug(f"Checking if user {config.user_id} has pending jobs...")
            if has_user_job_pending(self.redis_conn, config.user_id):
                job_status = get_user_job_status(self.redis_conn, config.user_id)
                logger.info(
                    f"Skipping job scheduling for user {config.user_id} - job already pending: {job_status}"
                )
                logger.debug(f"Existing job status details: {job_status}")
                return

            logger.debug(f"No pending jobs found for user {config.user_id}")

            # Calculate next run time based on polling interval
            logger.debug("Calculating next run time...")
            next_run = self._calculate_next_run(config)

            if not next_run:
                logger.debug(
                    f"No next run time calculated for user {config.user_id}, skipping"
                )
                return

            logger.debug(f"Next run time calculated: {next_run}")

            # Generate consistent job ID
            job_id = generate_job_id(config.user_id, next_run)
            logger.debug(f"Generated job ID: {job_id}")

            # Schedule the job using the standalone function
            logger.debug("Scheduling job with RQ scheduler...")
            self.scheduler.enqueue_at(
                next_run,
                process_user_emails_standalone,
                config.user_id,
                job_id=job_id,
                queue_name="email_processing",
            )

            logger.info(
                f"Scheduled job {job_id} for user {config.user_id} ({config.email_address}) at {next_run}"
            )
            logger.debug(
                f"Job scheduling completed successfully for user {config.user_id}"
            )

        except Exception as e:
            logger.error(f"Error scheduling job for user {config.user_id}: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True
            )

    def _calculate_next_run(self, config: EmailConfiguration) -> datetime:
        """Calculate the next run time based on the polling interval."""
        logger.debug(f"Starting _calculate_next_run for user {config.user_id}")
        now = datetime.now(timezone.utc)
        logger.debug(f"Current time (UTC): {now}")
        logger.debug(f"Last check time: {config.last_check_time}")
        logger.debug(f"Polling interval: {config.polling_interval}")

        if not config.last_check_time:
            logger.debug("No last check time found, scheduling for immediate execution")
            return now

        interval = config.polling_interval.lower()
        logger.debug(f"Processing interval: {interval}")

        if interval == "hourly":
            next_run = config.last_check_time + timedelta(hours=1)
            logger.debug(f"Hourly interval: next run calculated as {next_run}")
        elif interval == "daily":
            next_run = config.last_check_time + timedelta(days=1)
            logger.debug(f"Daily interval: next run calculated as {next_run}")
        else:
            # Default to hourly if interval is not recognized
            logger.warning(
                f"Unrecognized polling interval '{interval}', defaulting to hourly"
            )
            next_run = config.last_check_time + timedelta(hours=1)
            logger.debug(f"Default hourly interval: next run calculated as {next_run}")

        # If the next run time is in the past, return now
        if next_run < now:
            logger.debug(
                f"Next run time {next_run} is in the past, scheduling for immediate execution"
            )
            return now

        logger.debug(f"Final next run time: {next_run}")
        return next_run
