#!/usr/bin/env python3
"""
Check failed jobs in Redis queue
"""

import os
import redis
from rq.registry import FailedJobRegistry
from rq.job import Job


def check_failed_jobs():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)

    failed_registry = FailedJobRegistry(connection=redis_conn)
    print(f"Failed jobs: {len(failed_registry)}")

    for job_id in failed_registry.get_job_ids():
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"Failed job: {job_id}")
            print(f"  Function: {job.func_name}")
            print(f"  Args: {job.args}")
            print(f"  Exception: {job.exc_info}")
            print("---")
        except Exception as e:
            print(f"Error fetching job {job_id}: {e}")


if __name__ == "__main__":
    check_failed_jobs()
