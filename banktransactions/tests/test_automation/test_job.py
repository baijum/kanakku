#!/usr/bin/env python3
"""
Test script to manually enqueue an email processing job
"""

import os
import sys
import redis
from rq import Queue

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

from banktransactions.email_automation.workers.email_processor import process_user_emails_standalone

def enqueue_test_job():
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    redis_conn = redis.from_url(redis_url)
    
    queue = Queue('email_processing', connection=redis_conn)
    job = queue.enqueue(process_user_emails_standalone, 1, job_timeout='10m')
    print(f'Enqueued job: {job.id}')
    print(f'Queue length: {len(queue)}')

if __name__ == "__main__":
    enqueue_test_job() 