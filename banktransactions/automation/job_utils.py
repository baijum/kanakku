#!/usr/bin/env python3
"""
Job utility functions for email automation.
Provides deduplication and status checking for email processing jobs.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Optional

from rq import Queue, Worker
from rq.job import Job
from rq.registry import FailedJobRegistry, FinishedJobRegistry, ScheduledJobRegistry

logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logger.debug(f"Added project root to sys.path: {project_root}")


def generate_job_id(user_id: int, scheduled_time: datetime) -> str:
    """
    Generate a consistent job ID for a user and scheduled time.

    Args:
        user_id (int): The user ID
        scheduled_time (datetime): The scheduled execution time

    Returns:
        str: A consistent job ID
    """
    logger.debug(f"Generating job ID for user {user_id} at {scheduled_time}")
    # Format: email_processing_user_{user_id}_{timestamp}
    timestamp = scheduled_time.strftime("%Y%m%d_%H%M%S")
    job_id = f"email_processing_user_{user_id}_{timestamp}"
    logger.debug(f"Generated job ID: {job_id}")
    return job_id


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
        started_registry = ScheduledJobRegistry(connection=redis_conn)

        for job_id in started_registry.get_job_ids():
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if (
                    job.func_name
                    == "banktransactions.automation.email_processor.process_user_emails_standalone"
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
                    == "banktransactions.automation.email_processor.process_user_emails_standalone"
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
                    == "banktransactions.automation.email_processor.process_user_emails_standalone"
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


def has_user_job_pending(redis_conn, user_id: int) -> bool:
    """
    Check if a user has any pending jobs (running, queued, or scheduled).

    Args:
        redis_conn: Redis connection
        user_id (int): The user ID

    Returns:
        bool: True if user has pending jobs, False otherwise
    """
    logger.debug(f"Checking if user {user_id} has pending jobs")
    try:
        status = get_user_job_status(redis_conn, user_id)
        logger.debug(f"Retrieved job status for user {user_id}: {status}")

        # Check if any jobs are running, queued, or scheduled
        has_pending = bool(
            status.get("running", [])
            or status.get("queued", [])
            or status.get("scheduled", [])
        )

        logger.debug(f"User {user_id} has pending jobs: {has_pending}")
        return has_pending

    except Exception as e:
        logger.error(f"Error checking scheduled job: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return False


def get_user_job_status(redis_conn, user_id: int) -> Dict:
    """
    Get the status of jobs for a specific user.

    Args:
        redis_conn: Redis connection
        user_id (int): The user ID

    Returns:
        Dict: Job status information
    """
    logger.debug(f"Getting job status for user {user_id}")
    try:
        queue = Queue("email_processing", connection=redis_conn)
        logger.debug("Created queue connection for email_processing")

        # Check for running jobs
        logger.debug("Checking for running jobs...")
        workers = Worker.all(connection=redis_conn)
        running_jobs = []
        for worker in workers:
            if worker.get_current_job():
                current_job = worker.get_current_job()
                if current_job and f"user_{user_id}_" in current_job.id:
                    running_jobs.append(current_job.id)
                    logger.debug(f"Found running job: {current_job.id}")

        # Check for queued jobs
        logger.debug("Checking for queued jobs...")
        queued_jobs = []
        for job in queue.jobs:
            if f"user_{user_id}_" in job.id:
                queued_jobs.append(job.id)
                logger.debug(f"Found queued job: {job.id}")

        # Check for scheduled jobs
        logger.debug("Checking for scheduled jobs...")
        scheduled_registry = ScheduledJobRegistry(queue=queue)
        scheduled_jobs = []
        for job_id in scheduled_registry.get_job_ids():
            if f"user_{user_id}_" in job_id:
                scheduled_jobs.append(job_id)
                logger.debug(f"Found scheduled job: {job_id}")

        # Check for failed jobs
        logger.debug("Checking for failed jobs...")
        failed_registry = FailedJobRegistry(queue=queue)
        failed_jobs = []
        for job_id in failed_registry.get_job_ids():
            if f"user_{user_id}_" in job_id:
                failed_jobs.append(job_id)
                logger.debug(f"Found failed job: {job_id}")

        # Check for finished jobs
        logger.debug("Checking for finished jobs...")
        finished_registry = FinishedJobRegistry(queue=queue)
        finished_jobs = []
        for job_id in finished_registry.get_job_ids():
            if f"user_{user_id}_" in job_id:
                finished_jobs.append(job_id)
                logger.debug(f"Found finished job: {job_id}")

        # Calculate if user has any pending jobs
        has_any_pending = bool(running_jobs or queued_jobs or scheduled_jobs)

        status = {
            "running": running_jobs,
            "queued": queued_jobs,
            "scheduled": scheduled_jobs,
            "failed": failed_jobs,
            "finished": finished_jobs,
            "has_any_pending": has_any_pending,
        }

        logger.debug(f"Job status summary for user {user_id}: {status}")
        return status

    except Exception as e:
        logger.error(f"Error getting job status for user {user_id}: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return {}


def get_job_details(redis_conn, job_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific job.

    Args:
        redis_conn: Redis connection
        job_id (str): The job ID

    Returns:
        Optional[Dict]: Job details or None if not found
    """
    logger.debug(f"Getting details for job {job_id}")
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        logger.debug(f"Successfully fetched job {job_id}")

        details = {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
            "result": job.result,
            "exc_info": job.exc_info,
            "meta": job.meta,
        }

        logger.debug(
            f"Job details for {job_id}: status={details['status']}, created_at={details['created_at']}"
        )
        return details

    except Exception as e:
        logger.error(f"Error checking queued job {job_id}: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return None


def cleanup_old_jobs(redis_conn, max_age_hours: int = 24) -> Dict:
    """
    Clean up old finished and failed jobs.

    Args:
        redis_conn: Redis connection
        max_age_hours (int): Maximum age of jobs to keep in hours

    Returns:
        Dict: Cleanup statistics
    """
    logger.debug(f"Starting cleanup of jobs older than {max_age_hours} hours")
    try:
        queue = Queue("email_processing", connection=redis_conn)
        logger.debug("Created queue connection for cleanup")

        # Clean up finished jobs
        logger.debug("Cleaning up finished jobs...")
        finished_registry = FinishedJobRegistry(queue=queue)
        finished_cleaned = finished_registry.cleanup(
            max_age_hours * 3600
        )  # Convert to seconds
        logger.debug(f"Cleaned up {finished_cleaned} finished jobs")

        # Clean up failed jobs
        logger.debug("Cleaning up failed jobs...")
        failed_registry = FailedJobRegistry(queue=queue)
        failed_cleaned = failed_registry.cleanup(
            max_age_hours * 3600
        )  # Convert to seconds
        logger.debug(f"Cleaned up {failed_cleaned} failed jobs")

        stats = {
            "finished_jobs_cleaned": finished_cleaned,
            "failed_jobs_cleaned": failed_cleaned,
            "total_cleaned": finished_cleaned + failed_cleaned,
        }

        logger.debug(f"Cleanup completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error during job cleanup: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return {"error": str(e)}


def get_queue_stats(redis_conn) -> Dict:
    """
    Get statistics about the email processing queue.

    Args:
        redis_conn: Redis connection

    Returns:
        Dict: Queue statistics
    """
    logger.debug("Getting queue statistics")
    try:
        queue = Queue("email_processing", connection=redis_conn)
        logger.debug("Created queue connection for statistics")

        # Get basic queue info
        logger.debug("Gathering basic queue information...")
        stats = {
            "name": queue.name,
            "length": len(queue),
            "is_empty": queue.is_empty(),
        }

        # Get registry counts
        logger.debug("Gathering registry counts...")
        scheduled_registry = ScheduledJobRegistry(queue=queue)
        failed_registry = FailedJobRegistry(queue=queue)
        finished_registry = FinishedJobRegistry(queue=queue)

        stats.update(
            {
                "scheduled_count": len(scheduled_registry),
                "failed_count": len(failed_registry),
                "finished_count": len(finished_registry),
            }
        )

        # Get worker info
        logger.debug("Gathering worker information...")
        workers = Worker.all(connection=redis_conn)
        active_workers = [w for w in workers if w.state == "busy"]

        stats.update(
            {
                "total_workers": len(workers),
                "active_workers": len(active_workers),
                "idle_workers": len(workers) - len(active_workers),
            }
        )

        logger.debug(f"Queue statistics: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return {"error": str(e)}
