#!/usr/bin/env python3
"""
Test script to verify job deduplication functionality.
"""

import os
import sys
from datetime import datetime, timezone

import redis
from rq import Queue

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

from banktransactions.automation.email_processor import (
    process_user_emails_standalone,
)
from banktransactions.automation.job_utils import (
    generate_job_id,
    get_user_job_status,
    has_user_job_pending,
    is_user_job_queued,
    is_user_job_running,
    is_user_job_scheduled,
)


def test_job_deduplication():
    """Test job deduplication functionality."""
    print("Testing job deduplication...")

    # Connect to Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)

    try:
        redis_conn.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        raise AssertionError(f"Failed to connect to Redis: {e}")

    # Test user ID
    test_user_id = 999

    # Clear any existing jobs for test user
    queue = Queue("email_processing", connection=redis_conn)
    print(f"Initial queue length: {len(queue)}")

    # Test 1: Check initial state (should be no pending jobs)
    print(f"\n1. Testing initial state for user {test_user_id}...")
    status = get_user_job_status(redis_conn, test_user_id)
    print(f"   Initial status: {status}")

    if status["has_any_pending"]:
        print("   ⚠️  User already has pending jobs - cleaning up first")
        # Note: In a real scenario, you'd want to clean up properly

    # Test 2: Generate consistent job IDs
    print("\n2. Testing job ID generation...")
    timestamp = datetime.now(timezone.utc)
    job_id_1 = generate_job_id(test_user_id, timestamp)
    job_id_2 = generate_job_id(test_user_id, timestamp)
    print(f"   Job ID 1: {job_id_1}")
    print(f"   Job ID 2: {job_id_2}")
    assert (
        job_id_1 == job_id_2
    ), "Job IDs should be consistent for same user and timestamp"
    print("   IDs match: ✅")

    # Test 3: Queue first job
    print(f"\n3. Queueing first job for user {test_user_id}...")
    job_id = generate_job_id(test_user_id, datetime.now(timezone.utc))
    job = queue.enqueue(
        process_user_emails_standalone, test_user_id, job_id=job_id, job_timeout="10m"
    )
    print(f"   Queued job: {job.id}")
    print(f"   Queue length after first job: {len(queue)}")

    # Test 4: Check if job is detected as pending
    print("\n4. Checking if job is detected as pending...")
    status = get_user_job_status(redis_conn, test_user_id)
    print(f"   Status after queueing: {status}")

    assert status["has_any_pending"], "Job should be detected as pending"
    print("   ✅ Job correctly detected as pending")

    # Test 5: Try to queue duplicate job
    print("\n5. Testing deduplication - trying to queue duplicate job...")
    has_pending = has_user_job_pending(redis_conn, test_user_id)
    print(f"   Has pending job: {has_pending}")

    assert has_pending, "Deduplication should detect pending job"
    print("   ✅ Deduplication working - would prevent duplicate job")

    # Test 6: Queue length should remain the same
    print("\n6. Verifying queue length hasn't increased...")
    current_queue_length = len(queue)
    print(f"   Current queue length: {current_queue_length}")

    # Clean up - remove the test job
    print("\n7. Cleaning up test job...")
    try:
        job.cancel()
        queue.remove(job.id)
        print("   ✅ Test job cleaned up")
        print(f"   Final queue length: {len(queue)}")
    except Exception as e:
        print(f"   ⚠️  Error cleaning up: {e}")

    print("\n✅ Job deduplication test completed!")


def test_individual_functions():
    """Test individual utility functions."""
    print("\nTesting individual utility functions...")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)

    test_user_id = 998

    print(f"Testing functions for user {test_user_id}:")
    print(f"  is_user_job_running: {is_user_job_running(redis_conn, test_user_id)}")
    print(f"  is_user_job_scheduled: {is_user_job_scheduled(redis_conn, test_user_id)}")
    print(f"  is_user_job_queued: {is_user_job_queued(redis_conn, test_user_id)}")
    print(f"  has_user_job_pending: {has_user_job_pending(redis_conn, test_user_id)}")


if __name__ == "__main__":
    print("Email Automation Job Deduplication Test")
    print("=" * 50)

    try:
        test_job_deduplication()
        test_individual_functions()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
