#!/usr/bin/env python3
"""
Comprehensive Redis Queue Inspector for Kanakku
"""

import os
import sys
import redis
from rq import Queue, Worker
from rq.job import Job
from datetime import datetime
import json

def inspect_redis_queues():
    """Inspect all Redis queues and provide detailed status."""
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    try:
        redis_conn = redis.from_url(redis_url)
        redis_conn.ping()
        print("✅ Connected to Redis")
        
        # Define known queues
        queue_names = ['default', 'email_processing', 'test_queue']
        
        print("\n" + "="*60)
        print("QUEUE STATUS REPORT")
        print("="*60)
        
        for queue_name in queue_names:
            queue = Queue(queue_name, connection=redis_conn)
            job_count = len(queue)
            
            print(f"\n📊 Queue: {queue_name}")
            print(f"   Jobs in queue: {job_count}")
            
            if job_count > 0:
                print(f"   Job IDs: {queue.job_ids[:5]}")  # Show first 5
                
                # Show details for first few jobs
                for i, job_id in enumerate(queue.job_ids[:3]):
                    try:
                        job = Job.fetch(job_id, connection=redis_conn)
                        print(f"   Job {i+1} ({job_id[:8]}...):")
                        print(f"     Status: {job.get_status()}")
                        print(f"     Function: {job.func_name}")
                        print(f"     Created: {job.created_at}")
                        print(f"     Args: {job.args}")
                    except Exception as e:
                        print(f"     Error fetching job: {e}")
        
        # Check failed jobs
        print(f"\n❌ FAILED JOBS")
        failed_queue = Queue('failed', connection=redis_conn)
        failed_count = len(failed_queue)
        print(f"   Failed jobs: {failed_count}")
        
        if failed_count > 0:
            for i, job_id in enumerate(failed_queue.job_ids[:3]):
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    print(f"   Failed Job {i+1} ({job_id[:8]}...):")
                    print(f"     Function: {job.func_name}")
                    print(f"     Failed at: {job.ended_at}")
                    print(f"     Error: {job.exc_info}")
                except Exception as e:
                    print(f"     Error fetching failed job: {e}")
        
        # Check workers
        print(f"\n👷 WORKERS")
        workers = Worker.all(connection=redis_conn)
        print(f"   Active workers: {len(workers)}")
        
        for worker in workers:
            print(f"   Worker: {worker.name}")
            print(f"     State: {worker.get_state()}")
            print(f"     Queues: {[q.name for q in worker.queues]}")
            print(f"     Current job: {worker.get_current_job()}")
            print(f"     Last heartbeat: {worker.last_heartbeat}")
        
        # Redis memory usage
        print(f"\n💾 REDIS MEMORY")
        memory_info = redis_conn.info('memory')
        print(f"   Used memory: {memory_info['used_memory_human']}")
        print(f"   Peak memory: {memory_info['used_memory_peak_human']}")
        
        # RQ statistics
        print(f"\n📈 RQ STATISTICS")
        all_keys = redis_conn.keys('rq:*')
        print(f"   Total RQ keys: {len(all_keys)}")
        
        job_keys = redis_conn.keys('rq:job:*')
        print(f"   Total jobs: {len(job_keys)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_redis_queues() 