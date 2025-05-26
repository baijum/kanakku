#!/usr/bin/env python3
"""
Check failed jobs script.
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
from shared.imports import get_redis_connection

logger.debug("Shared modules imported successfully")


def main():
    """Check failed jobs."""
    logger.debug("Starting check_failed main function")

    try:
        logger.debug("Getting Redis connection...")
        redis_conn = get_redis_connection()
        logger.debug(f"Redis connection established: {redis_conn is not None}")

        logger.debug("Importing RQ modules...")
        from rq import Queue
        from rq.registry import FailedJobRegistry

        logger.debug("RQ modules imported successfully")

        logger.debug("Creating email processing queue...")
        queue = Queue("email_processing", connection=redis_conn)
        logger.debug("Email processing queue created")

        logger.debug("Creating failed job registry...")
        failed_registry = FailedJobRegistry(queue=queue)
        logger.debug("Failed job registry created")

        logger.debug("Getting failed job IDs...")
        failed_job_ids = failed_registry.get_job_ids()
        logger.debug(f"Found {len(failed_job_ids)} failed jobs")

        print(f"Found {len(failed_job_ids)} failed jobs:")
        print()

        if not failed_job_ids:
            print("No failed jobs found.")
            logger.debug("No failed jobs to process")
        else:
            logger.debug("Importing Job class...")
            from rq.job import Job

            logger.debug("Job class imported successfully")

            for i, job_id in enumerate(failed_job_ids, 1):
                logger.debug(
                    f"Processing failed job {i}/{len(failed_job_ids)}: {job_id}"
                )

                try:
                    logger.debug(f"Fetching job details for {job_id}...")
                    job = Job.fetch(job_id, connection=redis_conn)
                    logger.debug(f"Successfully fetched job {job_id}")

                    print(f"Failed Job {i}:")
                    print(f"  ID: {job.id}")
                    print(f"  Status: {job.get_status()}")
                    print(f"  Created: {job.created_at}")
                    print(f"  Started: {job.started_at}")
                    print(f"  Ended: {job.ended_at}")
                    print(f"  Function: {job.func_name}")
                    print(f"  Args: {job.args}")
                    print(f"  Exception: {job.exc_info}")
                    print()

                    logger.debug(f"Job details - Status: {job.get_status()}")
                    logger.debug(f"Job details - Function: {job.func_name}")
                    logger.debug(f"Job details - Args: {job.args}")
                    logger.debug(f"Job details - Created: {job.created_at}")
                    logger.debug(
                        f"Job details - Exception present: {bool(job.exc_info)}"
                    )

                except Exception as e:
                    error_msg = f"Error fetching job {job_id}: {e}"
                    print(error_msg)
                    logger.error(error_msg)
                    logger.debug(
                        f"Job fetch exception details: {type(e).__name__}: {str(e)}",
                        exc_info=True,
                    )

    except Exception as e:
        error_msg = f"Error checking failed jobs: {e}"
        print(error_msg)
        logger.error(error_msg)
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)

    logger.debug("check_failed main function completed")


if __name__ == "__main__":
    # Set up basic logging for this script
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.debug("Check failed jobs script started")
    main()
    logger.debug("Check failed jobs script finished")
