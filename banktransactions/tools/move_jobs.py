#!/usr/bin/env python3
"""
Temporary script to move email processing jobs from default queue to email_processing queue
"""

import logging
import os

import redis
from rq import Queue
from rq.job import Job

logger = logging.getLogger(__name__)


def move_jobs():
    logger.debug("Starting move_jobs function")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    logger.debug(f"Using Redis URL: {redis_url}")

    logger.debug("Connecting to Redis...")
    redis_conn = redis.from_url(redis_url)

    try:
        # Test Redis connection
        logger.debug("Testing Redis connection...")
        redis_conn.ping()
        logger.debug("Redis connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        logger.debug(
            f"Redis connection error details: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        return

    logger.debug("Creating queue instances...")
    default_queue = Queue("default", connection=redis_conn)
    email_queue = Queue("email_processing", connection=redis_conn)
    logger.debug("Queue instances created successfully")

    default_queue_length = len(default_queue)
    email_queue_length = len(email_queue)

    print(f"Jobs in default queue: {default_queue_length}")
    print(f"Jobs in email_processing queue: {email_queue_length}")

    logger.debug(
        f"Initial queue lengths - default: {default_queue_length}, email_processing: {email_queue_length}"
    )

    # Move jobs from default to email_processing queue
    logger.debug("Starting job movement process...")
    moved_count = 0
    error_count = 0

    job_ids = list(
        default_queue.job_ids
    )  # Create a copy to avoid modification during iteration
    logger.debug(f"Found {len(job_ids)} jobs in default queue to process")

    for i, job_id in enumerate(job_ids, 1):
        logger.debug(f"Processing job {i}/{len(job_ids)}: {job_id}")

        try:
            logger.debug(f"Fetching job {job_id}...")
            job = Job.fetch(job_id, connection=redis_conn)
            logger.debug(f"Job fetched successfully: {job.func_name}")

            if "process_user_emails_standalone" in job.func_name:
                logger.debug(f"Job {job_id} is an email processing job, moving...")

                # Remove from default queue
                logger.debug(f"Removing job {job_id} from default queue...")
                default_queue.remove(job_id)
                logger.debug(f"Job {job_id} removed from default queue")

                # Add to email_processing queue
                logger.debug(f"Adding job {job_id} to email_processing queue...")
                email_queue.enqueue_job(job)
                logger.debug(f"Job {job_id} added to email_processing queue")

                moved_count += 1
                print(f"Moved job {job_id} to email_processing queue")
                logger.debug(f"Successfully moved job {job_id}")
            else:
                logger.debug(f"Job {job_id} is not an email processing job, skipping")

        except Exception as e:
            error_count += 1
            error_msg = f"Error moving job {job_id}: {e}"
            print(error_msg)
            logger.error(error_msg)
            logger.debug(
                f"Job movement error details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

    # Final queue lengths
    final_default_length = len(default_queue)
    final_email_length = len(email_queue)

    print(f"Moved {moved_count} jobs to email_processing queue")
    print(f"Jobs in default queue after move: {final_default_length}")
    print(f"Jobs in email_processing queue after move: {final_email_length}")

    logger.debug("Job movement completed:")
    logger.debug(f"  Jobs moved: {moved_count}")
    logger.debug(f"  Errors encountered: {error_count}")
    logger.debug(f"  Final default queue length: {final_default_length}")
    logger.debug(f"  Final email_processing queue length: {final_email_length}")

    if error_count > 0:
        logger.warning(f"Job movement completed with {error_count} errors")
    else:
        logger.debug("Job movement completed successfully without errors")


if __name__ == "__main__":
    # Set up basic logging for this script
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.debug("Move jobs script started")
    move_jobs()
    logger.debug("Move jobs script finished")
