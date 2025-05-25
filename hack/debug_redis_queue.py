#!/usr/bin/env python3
"""
Complete Redis Queue Debugging Script for Kanakku
"""

import os
import sys
import redis
from rq import Queue, Worker
from rq.job import Job
from datetime import datetime
import argparse


def main():
    parser = argparse.ArgumentParser(description="Debug Redis Queue issues")
    parser.add_argument(
        "--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    parser.add_argument(
        "--action",
        choices=["status", "clear-failed", "clear-all", "test-job"],
        default="status",
        help="Action to perform",
    )
    parser.add_argument("--job-id", help="Specific job ID to inspect")

    args = parser.parse_args()

    try:
        redis_conn = redis.from_url(args.redis_url)
        redis_conn.ping()
        print(f"✅ Connected to Redis at {args.redis_url}")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return 1

    if args.action == "status":
        show_status(redis_conn)
    elif args.action == "clear-failed":
        clear_failed_jobs(redis_conn)
    elif args.action == "clear-all":
        clear_all_jobs(redis_conn)
    elif args.action == "test-job":
        enqueue_test_job(redis_conn)

    if args.job_id:
        inspect_job(redis_conn, args.job_id)

    return 0


def show_status(redis_conn):
    """Show comprehensive queue status."""
    print("\n" + "=" * 60)
    print("REDIS QUEUE STATUS")
    print("=" * 60)

    # Queue status
    queues = ["default", "email_processing", "failed"]
    for queue_name in queues:
        queue = Queue(queue_name, connection=redis_conn)
        print(f"\n📊 {queue_name.upper()} Queue: {len(queue)} jobs")

        if len(queue) > 0:
            for i, job_id in enumerate(queue.job_ids[:3]):
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    print(
                        f"   {i+1}. {job_id[:12]}... | {job.func_name} | {job.get_status()}"
                    )
                except Exception:
                    print(f"   {i+1}. {job_id[:12]}... | Error fetching job")

    # Worker status
    workers = Worker.all(connection=redis_conn)
    print(f"\n👷 WORKERS: {len(workers)} active")
    for worker in workers:
        status = "🟢 Active" if worker.get_state() == "busy" else "🟡 Idle"
        print(f"   {worker.name} | {status}")

    # Memory usage
    memory_info = redis_conn.info("memory")
    print(f"\n💾 MEMORY: {memory_info['used_memory_human']} used")


def clear_failed_jobs(redis_conn):
    """Clear all failed jobs."""
    failed_queue = Queue("failed", connection=redis_conn)
    count = len(failed_queue)

    if count == 0:
        print("No failed jobs to clear.")
        return

    confirm = input(f"Clear {count} failed jobs? (y/N): ")
    if confirm.lower() == "y":
        failed_queue.empty()
        print(f"✅ Cleared {count} failed jobs.")
    else:
        print("Cancelled.")


def clear_all_jobs(redis_conn):
    """Clear all RQ data (DANGEROUS)."""
    keys = redis_conn.keys("rq:*")
    count = len(keys)

    print(f"⚠️  WARNING: This will delete ALL RQ data ({count} keys)")
    confirm = input("Type 'DELETE ALL' to confirm: ")

    if confirm == "DELETE ALL":
        if keys:
            redis_conn.delete(*keys)
        print(f"✅ Deleted {count} RQ keys.")
    else:
        print("Cancelled.")


def enqueue_test_job(redis_conn):
    """Enqueue a test job."""

    def test_function():
        import time

        time.sleep(2)
        return f"Test completed at {datetime.now()}"

    queue = Queue("email_processing", connection=redis_conn)
    job = queue.enqueue(test_function)
    print(f"✅ Enqueued test job: {job.id}")
    print(f"   Monitor with: python debug_redis_queue.py --job-id {job.id}")


def inspect_job(redis_conn, job_id):
    """Inspect a specific job."""
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        print(f"\n🔍 JOB DETAILS: {job_id}")
        print(f"   Function: {job.func_name}")
        print(f"   Status: {job.get_status()}")
        print(f"   Created: {job.created_at}")
        print(f"   Started: {job.started_at}")
        print(f"   Ended: {job.ended_at}")
        print(f"   Args: {job.args}")
        print(f"   Result: {job.result}")
        if job.exc_info:
            print(f"   Error: {job.exc_info}")
    except Exception as e:
        print(f"❌ Error fetching job {job_id}: {e}")


if __name__ == "__main__":
    sys.exit(main())
