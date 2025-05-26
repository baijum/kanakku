#!/usr/bin/env python3
"""
Test script for the job wrapper function.
This tests that the wrapper can be imported and enqueued correctly.
"""

import os
import sys

import redis
from rq import Queue

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_wrapper():
    """Test the wrapper function import and job enqueuing."""
    try:
        # Import the wrapper function
        from banktransactions.automation.job_wrapper import (
            process_user_emails_standalone,
        )

        print("✓ Wrapper function imported successfully")

        # Connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)
        print("✓ Connected to Redis")

        # Create queue
        queue = Queue("email_processing", connection=redis_conn)
        print("✓ Queue created")

        # Enqueue job
        job = queue.enqueue(process_user_emails_standalone, 1, job_timeout="10m")
        print(f"✓ Job enqueued: {job.id}")
        print(f"✓ Queue length: {len(queue)}")

        # Use assertions instead of returning values
        assert job is not None, "Job should be created successfully"
        assert job.id is not None, "Job should have an ID"
        assert len(queue) > 0, "Queue should contain the enqueued job"

    except Exception as e:
        print(f"✗ Error: {e}")
        raise AssertionError(f"Test failed with error: {e}")


if __name__ == "__main__":
    success = test_wrapper()
    sys.exit(0 if success else 1)
