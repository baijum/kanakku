#!/usr/bin/env python3
"""
Temporary script to move email processing jobs from default queue to email_processing queue
"""

import os
import redis
from rq import Queue
from rq.job import Job


def move_jobs():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)

    default_queue = Queue("default", connection=redis_conn)
    email_queue = Queue("email_processing", connection=redis_conn)

    print(f"Jobs in default queue: {len(default_queue)}")
    print(f"Jobs in email_processing queue: {len(email_queue)}")

    # Move jobs from default to email_processing queue
    moved_count = 0
    for job_id in default_queue.job_ids:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            if "process_user_emails_standalone" in job.func_name:
                # Remove from default queue
                default_queue.remove(job_id)
                # Add to email_processing queue
                email_queue.enqueue_job(job)
                moved_count += 1
                print(f"Moved job {job_id} to email_processing queue")
        except Exception as e:
            print(f"Error moving job {job_id}: {e}")

    print(f"Moved {moved_count} jobs to email_processing queue")
    print(f"Jobs in default queue after move: {len(default_queue)}")
    print(f"Jobs in email_processing queue after move: {len(email_queue)}")


if __name__ == "__main__":
    move_jobs()
