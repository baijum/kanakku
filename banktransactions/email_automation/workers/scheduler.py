import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List

from rq_scheduler import Scheduler
from sqlalchemy.orm import Session

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, project_root)
# Also add the backend app to the Python path
sys.path.append(os.path.join(project_root, "backend"))

from app.models import EmailConfiguration
from banktransactions.email_automation.workers.email_processor import (
    process_user_emails_standalone,
)
from banktransactions.email_automation.workers.job_utils import (
    generate_job_id,
    has_user_job_pending,
    get_user_job_status,
)

logger = logging.getLogger(__name__)


class EmailScheduler:
    def __init__(self, redis_conn, db_session: Session):
        self.scheduler = Scheduler(connection=redis_conn)
        self.redis_conn = redis_conn
        self.db = db_session

    def schedule_jobs(self):
        """Schedule email processing jobs for all enabled configurations."""
        try:
            # Get all enabled configurations
            configs = self.db.query(EmailConfiguration).filter_by(is_enabled=True).all()

            for config in configs:
                self._schedule_user_job(config)

        except Exception as e:
            logger.error(f"Error in schedule_jobs: {str(e)}")

    def _schedule_user_job(self, config: EmailConfiguration):
        """Schedule a job for a specific user's email configuration."""
        try:
            # Check if user already has a pending job (running, scheduled, or queued)
            if has_user_job_pending(self.redis_conn, config.user_id):
                job_status = get_user_job_status(self.redis_conn, config.user_id)
                logger.info(f"Skipping job scheduling for user {config.user_id} - job already pending: {job_status}")
                return

            # Calculate next run time based on polling interval
            next_run = self._calculate_next_run(config)

            if not next_run:
                return

            # Generate consistent job ID
            job_id = generate_job_id(config.user_id, next_run)

            # Schedule the job using the standalone function
            self.scheduler.enqueue_at(
                next_run,
                process_user_emails_standalone,
                config.user_id,
                job_id=job_id,
                queue_name="email_processing",
            )

            logger.info(f"Scheduled job {job_id} for user {config.user_id} ({config.email_address}) at {next_run}")

        except Exception as e:
            logger.error(f"Error scheduling job for user {config.user_id}: {str(e)}")

    def _calculate_next_run(self, config: EmailConfiguration) -> datetime:
        """Calculate the next run time based on the polling interval."""
        now = datetime.utcnow()

        if not config.last_check_time:
            return now

        interval = config.polling_interval.lower()

        if interval == "hourly":
            next_run = config.last_check_time + timedelta(hours=1)
        elif interval == "daily":
            next_run = config.last_check_time + timedelta(days=1)
        else:
            # Default to hourly if interval is not recognized
            next_run = config.last_check_time + timedelta(hours=1)

        # If the next run time is in the past, return now
        if next_run < now:
            return now

        return next_run
