#!/usr/bin/env python3
"""
Job utility functions for email automation.
Provides deduplication and status checking for email processing jobs.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from rq import Queue
from rq.job import Job
from rq.registry import StartedJobRegistry, ScheduledJobRegistry

logger = logging.getLogger(__name__)


def generate_job_id(user_id: int, timestamp: Optional[datetime] = None) -> str:
    """
    Generate a consistent job ID for a user's email processing job.

    Args:
        user_id: The user ID
        timestamp: Optional timestamp, defaults to current time

    Returns:
        Formatted job ID string
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    return f"email_process_{user_id}_{int(timestamp.timestamp())}"


def is_user_job_running(redis_conn, user_id: int) -> bool:
    """
    Check if an email processing job is already running for this user.

    Args:
        redis_conn: Redis connection
        user_id: The user ID to check

    Returns:
        True if a job is currently running for this user
    """
    try:
        started_registry = StartedJobRegistry(connection=redis_conn)

        for job_id in started_registry.get_job_ids():
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if (
                    job.func_name
                    == "banktransactions.email_automation.workers.email_processor.process_user_emails_standalone"
                    and len(job.args) > 0
                    and job.args[0] == user_id
                ):
                    logger.info(f"Found running job {job_id} for user {user_id}")
                    return True
            except Exception as e:
                logger.debug(f"Error checking job {job_id}: {e}")
                continue

        return False

    except Exception as e:
        logger.error(f"Error checking running jobs for user {user_id}: {e}")
        return False


def is_user_job_scheduled(redis_conn, user_id: int) -> bool:
    """
    Check if an email processing job is already scheduled for this user.

    Args:
        redis_conn: Redis connection
        user_id: The user ID to check

    Returns:
        True if a job is scheduled for this user
    """
    try:
        scheduled_registry = ScheduledJobRegistry(connection=redis_conn)

        for job_id in scheduled_registry.get_job_ids():
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if (
                    job.func_name
                    == "banktransactions.email_automation.workers.email_processor.process_user_emails_standalone"
                    and len(job.args) > 0
                    and job.args[0] == user_id
                ):
                    logger.info(f"Found scheduled job {job_id} for user {user_id}")
                    return True
            except Exception as e:
                logger.debug(f"Error checking scheduled job {job_id}: {e}")
                continue

        return False

    except Exception as e:
        logger.error(f"Error checking scheduled jobs for user {user_id}: {e}")
        return False


def is_user_job_queued(
    redis_conn, user_id: int, queue_name: str = "email_processing"
) -> bool:
    """
    Check if an email processing job is already queued for this user.

    Args:
        redis_conn: Redis connection
        user_id: The user ID to check
        queue_name: Name of the queue to check

    Returns:
        True if a job is queued for this user
    """
    try:
        queue = Queue(queue_name, connection=redis_conn)

        for job_id in queue.job_ids:
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if (
                    job.func_name
                    == "banktransactions.email_automation.workers.email_processor.process_user_emails_standalone"
                    and len(job.args) > 0
                    and job.args[0] == user_id
                ):
                    logger.info(f"Found queued job {job_id} for user {user_id}")
                    return True
            except Exception as e:
                logger.debug(f"Error checking queued job {job_id}: {e}")
                continue

        return False

    except Exception as e:
        logger.error(f"Error checking queued jobs for user {user_id}: {e}")
        return False


def has_user_job_pending(
    redis_conn, user_id: int, queue_name: str = "email_processing"
) -> bool:
    """
    Check if a user has any pending email processing job (queued, scheduled, or running).

    Args:
        redis_conn: Redis connection
        user_id: The user ID to check
        queue_name: Name of the queue to check

    Returns:
        True if any job is pending for this user
    """
    return (
        is_user_job_running(redis_conn, user_id)
        or is_user_job_scheduled(redis_conn, user_id)
        or is_user_job_queued(redis_conn, user_id, queue_name)
    )


def get_user_job_status(
    redis_conn, user_id: int, queue_name: str = "email_processing"
) -> dict:
    """
    Get comprehensive job status for a user.

    Args:
        redis_conn: Redis connection
        user_id: The user ID to check
        queue_name: Name of the queue to check

    Returns:
        Dictionary with job status information
    """
    status = {
        "user_id": user_id,
        "has_running_job": is_user_job_running(redis_conn, user_id),
        "has_scheduled_job": is_user_job_scheduled(redis_conn, user_id),
        "has_queued_job": is_user_job_queued(redis_conn, user_id, queue_name),
        "has_any_pending": False,
    }

    status["has_any_pending"] = (
        status["has_running_job"]
        or status["has_scheduled_job"]
        or status["has_queued_job"]
    )

    return status
