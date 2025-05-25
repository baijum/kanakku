# Redis Queue Debugging Guide

This guide provides comprehensive debugging tools and techniques for Redis Queue (RQ) issues in the kanakku project, specifically for the email automation system.

> **Note**: All debugging scripts are located in the `hack/` directory. If you see references to `tools/` in older documentation, they should be updated to `hack/`.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Environment Setup](#environment-setup)
- [Redis Connection Testing](#redis-connection-testing)
- [Queue Inspection Tools](#queue-inspection-tools)
- [Worker Debugging](#worker-debugging)
- [Job Monitoring](#job-monitoring)
- [Common Issues & Solutions](#common-issues--solutions)
- [Debugging Scripts](#debugging-scripts)
- [Production Monitoring](#production-monitoring)

## Quick Diagnostics

### 1. Verify Project Structure

The email automation system is located in `banktransactions/email_automation/`. If you get "directory not found" errors:

```bash
# From project root (kanakku/)
ls -la banktransactions/email_automation/

# Expected files:
# - run_worker.py
# - run_scheduler.py
# - test_system.py
# - workers/ directory
```

### 2. Basic Health Check

```bash
# Test Redis connection
redis-cli ping
# Expected: PONG

# Check if Redis is running on correct port
netstat -tlnp | grep 6379
# Expected: tcp 0.0.0.0:6379 LISTEN

# Test database connection
psql $DATABASE_URL -c "SELECT 1;"
# Expected: 1 row returned
```

### 3. Quick Queue Status

```bash
# Check queue lengths
redis-cli LLEN rq:queue:default
redis-cli LLEN rq:queue:email_processing
redis-cli LLEN rq:queue:failed

# List all RQ-related keys
redis-cli KEYS "rq:*"
```

## Environment Setup

### Required Environment Variables

```bash
# Essential variables for email automation
export DATABASE_URL="postgresql://kanakku_dev:secret123@localhost:5432/kanakku_dev_db1"
export REDIS_URL="redis://localhost:6379/0"
export GOOGLE_API_KEY="your_gemini_api_key"
export ENCRYPTION_KEY="your_32_byte_base64_key"
```

### Correct Directory Navigation

```bash
# From project root (kanakku/)
cd banktransactions/email_automation

# NOT from parent directory:
# cd ../banktransactions/email_automation  # ❌ This will fail
```

### Virtual Environment

```bash
# Ensure you're in the correct virtual environment
which python
# Should point to your kanakku virtual environment

# Install required packages
pip install -r banktransactions/requirements.txt
```

## Redis Connection Testing

### 1. Basic Redis CLI Commands

```bash
# Connect to Redis
redis-cli -h localhost -p 6379 -n 0

# Test connection
redis> PING
# Expected: PONG

# Check Redis info
redis> INFO server
redis> INFO memory
redis> INFO clients
```

### 2. Python Connection Test

```python
#!/usr/bin/env python3
"""Test Redis connection from Python"""

import os
import redis

def test_redis_connection():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        redis_conn = redis.from_url(redis_url)
        redis_conn.ping()
        print(f"✅ Connected to Redis at {redis_url}")
        
        # Test basic operations
        redis_conn.set("test_key", "test_value")
        value = redis_conn.get("test_key")
        redis_conn.delete("test_key")
        
        print(f"✅ Redis operations working: {value.decode()}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    test_redis_connection()
```

## Queue Inspection Tools

### 1. Redis CLI Queue Commands

```bash
# List all queues
redis-cli KEYS "rq:queue:*"

# Check queue lengths
redis-cli LLEN rq:queue:default
redis-cli LLEN rq:queue:email_processing
redis-cli LLEN rq:queue:failed

# View jobs in queue (first 10)
redis-cli LRANGE rq:queue:email_processing 0 9

# View failed jobs
redis-cli LRANGE rq:queue:failed 0 -1

# Get job details (replace JOB_ID with actual ID)
redis-cli HGETALL rq:job:JOB_ID
```

### 2. RQ Dashboard (Web Interface)

Install and run RQ Dashboard for visual queue monitoring:

```bash
# Install RQ Dashboard
pip install rq-dashboard

# Run dashboard
rq-dashboard --redis-url redis://localhost:6379/0

# Access at: http://localhost:9181
```

### 3. Python Queue Inspection Script

```python
#!/usr/bin/env python3
"""
Comprehensive Redis Queue Inspector for Kanakku
Save as: hack/inspect_queues.py
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
```

## Worker Debugging

### 1. Starting Workers with Debug Logging

```bash
# Start worker with verbose logging
cd banktransactions/email_automation
python run_worker.py --redis-url redis://localhost:6379/0 --worker-name debug_worker

# Check worker logs
tail -f ../logs/worker.log

# Start worker with Python debugging
python -u run_worker.py --redis-url redis://localhost:6379/0 2>&1 | tee worker_debug.log
```

### 2. Worker Status Check Script

```python
#!/usr/bin/env python3
"""
Worker Status Checker
Save as: hack/check_workers.py
"""

import os
import redis
from rq import Worker
from datetime import datetime, timedelta

def check_worker_status():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)
    
    workers = Worker.all(connection=redis_conn)
    
    print(f"Found {len(workers)} workers:")
    
    for worker in workers:
        print(f"\nWorker: {worker.name}")
        print(f"  State: {worker.get_state()}")
        print(f"  Birth: {worker.birth_date}")
        print(f"  Last heartbeat: {worker.last_heartbeat}")
        
        # Check if worker is stale
        if worker.last_heartbeat:
            time_since_heartbeat = datetime.utcnow() - worker.last_heartbeat
            if time_since_heartbeat > timedelta(minutes=5):
                print(f"  ⚠️  Worker may be stale (last heartbeat {time_since_heartbeat} ago)")
        
        current_job = worker.get_current_job()
        if current_job:
            print(f"  Current job: {current_job.id}")
            print(f"  Job function: {current_job.func_name}")
            print(f"  Job started: {current_job.started_at}")

if __name__ == "__main__":
    check_worker_status()
```

### 3. Manual Worker Testing

```bash
# Test the email automation system
cd banktransactions/email_automation
python test_system.py

# Run a single test job
python -c "
import os, redis
from rq import Queue

redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
queue = Queue('email_processing', connection=redis_conn)

def test_job():
    return 'Test completed successfully'

job = queue.enqueue(test_job)
print(f'Enqueued test job: {job.id}')
"
```

## Job Monitoring

### 1. Real-time Queue Monitoring

```bash
# Watch queue length in real-time
watch -n 2 'echo "Queue lengths:"; redis-cli LLEN rq:queue:default; redis-cli LLEN rq:queue:email_processing; redis-cli LLEN rq:queue:failed'

# Monitor job processing
watch -n 5 'redis-cli KEYS "rq:job:*" | wc -l'
```

### 2. Job Lifecycle Tracking

```python
#!/usr/bin/env python3
"""
Job Lifecycle Tracker
Save as: hack/track_jobs.py
"""

import os
import redis
from rq.job import Job
import time
import sys

def track_job(job_id):
    """Track a specific job through its lifecycle."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        print(f"Tracking job: {job_id}")
        print(f"Function: {job.func_name}")
        print(f"Args: {job.args}")
        print(f"Created: {job.created_at}")
        print("-" * 40)
        
        while True:
            try:
                job.refresh()
                status = job.get_status()
                print(f"Status: {status} | {time.strftime('%H:%M:%S')}")
                
                if status in ['finished', 'failed']:
                    if status == 'finished':
                        print(f"Result: {job.result}")
                    else:
                        print(f"Error: {job.exc_info}")
                    break
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"Error tracking job: {e}")
                break
                
    except Exception as e:
        print(f"Job not found or error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python track_jobs.py <job_id>")
        sys.exit(1)
    
    track_job(sys.argv[1])
```

### 3. Failed Job Analysis

```python
#!/usr/bin/env python3
"""
Failed Job Analyzer
Save as: hack/analyze_failures.py
"""

import os
import redis
from rq import Queue
from rq.job import Job
import json
from collections import Counter

def analyze_failed_jobs():
    """Analyze patterns in failed jobs."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)
    
    failed_queue = Queue('failed', connection=redis_conn)
    
    if len(failed_queue) == 0:
        print("No failed jobs found.")
        return
    
    print(f"Analyzing {len(failed_queue)} failed jobs...")
    
    error_types = Counter()
    function_failures = Counter()
    
    for job_id in failed_queue.job_ids:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            
            # Count error types
            if job.exc_info:
                error_line = job.exc_info.split('\n')[-2] if job.exc_info else "Unknown"
                error_types[error_line] += 1
            
            # Count function failures
            function_failures[job.func_name] += 1
            
        except Exception as e:
            print(f"Error analyzing job {job_id}: {e}")
    
    print("\nMost common errors:")
    for error, count in error_types.most_common(5):
        print(f"  {count}x: {error}")
    
    print("\nFunctions with most failures:")
    for func, count in function_failures.most_common(5):
        print(f"  {count}x: {func}")

if __name__ == "__main__":
    analyze_failed_jobs()
```

## Common Issues & Solutions

### 1. "Directory not found" Error

**Problem**: `cd: no such file or directory: ../banktransactions/email_automation`

**Solution**:
```bash
# Ensure you're in the project root first
pwd  # Should show /path/to/kanakku

# Then navigate correctly
cd banktransactions/email_automation
```

### 2. Redis Connection Refused

**Problem**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379`

**Solutions**:
```bash
# Start Redis server
redis-server

# Check if Redis is running
systemctl status redis
# or
brew services start redis  # macOS

# Check Redis configuration
redis-cli CONFIG GET bind
redis-cli CONFIG GET port
```

### 3. Database Connection Issues

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check database URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database

# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Check if PostgreSQL is running
systemctl status postgresql
```

### 4. Jobs Stuck in Queue

**Problem**: Jobs remain in queue but aren't processed

**Debugging**:
```bash
# Check if workers are running
redis-cli KEYS "rq:worker:*"

# Check worker heartbeats
redis-cli HGETALL "rq:worker:worker_name"

# Restart workers
pkill -f run_worker.py
cd banktransactions/email_automation
python run_worker.py --redis-url redis://localhost:6379/0
```

### 5. Memory Issues

**Problem**: Redis running out of memory

**Solutions**:
```bash
# Check Redis memory usage
redis-cli INFO memory

# Clear old jobs (CAUTION: This deletes data)
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'rq:job:*')))" 0

# Set Redis memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 6. Pickling Errors

**Problem**: `Can't pickle <class 'sqlalchemy.orm.session.Session'>`

**Solution**: Use standalone functions instead of class methods:
```python
# ❌ Don't do this (legacy EmailProcessor class removed)
# job = queue.enqueue(EmailProcessor(db_session).process_emails, user_id)

# ✅ Do this instead
job = queue.enqueue(process_user_emails_standalone, user_id)
```

## Debugging Scripts

### Complete Debugging Script

Save this as `hack/debug_redis_queue.py`:

```python
#!/usr/bin/env python3
"""
Complete Redis Queue Debugging Script for Kanakku
"""

import os
import sys
import redis
from rq import Queue, Worker
from rq.job import Job
from datetime import datetime, timedelta
import argparse

def main():
    parser = argparse.ArgumentParser(description="Debug Redis Queue issues")
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    parser.add_argument("--action", choices=['status', 'clear-failed', 'clear-all', 'test-job'], 
                       default='status', help="Action to perform")
    parser.add_argument("--job-id", help="Specific job ID to inspect")
    
    args = parser.parse_args()
    
    try:
        redis_conn = redis.from_url(args.redis_url)
        redis_conn.ping()
        print(f"✅ Connected to Redis at {args.redis_url}")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return 1
    
    if args.action == 'status':
        show_status(redis_conn)
    elif args.action == 'clear-failed':
        clear_failed_jobs(redis_conn)
    elif args.action == 'clear-all':
        clear_all_jobs(redis_conn)
    elif args.action == 'test-job':
        enqueue_test_job(redis_conn)
    
    if args.job_id:
        inspect_job(redis_conn, args.job_id)
    
    return 0

def show_status(redis_conn):
    """Show comprehensive queue status."""
    print("\n" + "="*60)
    print("REDIS QUEUE STATUS")
    print("="*60)
    
    # Queue status
    queues = ['default', 'email_processing', 'failed']
    for queue_name in queues:
        queue = Queue(queue_name, connection=redis_conn)
        print(f"\n📊 {queue_name.upper()} Queue: {len(queue)} jobs")
        
        if len(queue) > 0:
            for i, job_id in enumerate(queue.job_ids[:3]):
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    print(f"   {i+1}. {job_id[:12]}... | {job.func_name} | {job.get_status()}")
                except:
                    print(f"   {i+1}. {job_id[:12]}... | Error fetching job")
    
    # Worker status
    workers = Worker.all(connection=redis_conn)
    print(f"\n👷 WORKERS: {len(workers)} active")
    for worker in workers:
        status = "🟢 Active" if worker.get_state() == 'busy' else "🟡 Idle"
        print(f"   {worker.name} | {status}")
    
    # Memory usage
    memory_info = redis_conn.info('memory')
    print(f"\n💾 MEMORY: {memory_info['used_memory_human']} used")

def clear_failed_jobs(redis_conn):
    """Clear all failed jobs."""
    failed_queue = Queue('failed', connection=redis_conn)
    count = len(failed_queue)
    
    if count == 0:
        print("No failed jobs to clear.")
        return
    
    confirm = input(f"Clear {count} failed jobs? (y/N): ")
    if confirm.lower() == 'y':
        failed_queue.empty()
        print(f"✅ Cleared {count} failed jobs.")
    else:
        print("Cancelled.")

def clear_all_jobs(redis_conn):
    """Clear all RQ data (DANGEROUS)."""
    keys = redis_conn.keys('rq:*')
    count = len(keys)
    
    print(f"⚠️  WARNING: This will delete ALL RQ data ({count} keys)")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm == 'DELETE ALL':
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
    
    queue = Queue('email_processing', connection=redis_conn)
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
```

### Usage Examples

```bash
# Show queue status
python hack/debug_redis_queue.py --action status

# Clear failed jobs
python hack/debug_redis_queue.py --action clear-failed

# Enqueue test job
python hack/debug_redis_queue.py --action test-job

# Inspect specific job
python hack/debug_redis_queue.py --job-id abc123def456

# Use custom Redis URL
python hack/debug_redis_queue.py --redis-url redis://localhost:6380/1 --action status
```

## Production Monitoring

### 1. Health Check Script

```bash
#!/bin/bash
# Save as: hack/health_check.sh

echo "🏥 Kanakku Email Automation Health Check"
echo "========================================"

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not responding"
fi

# Check database
if psql $DATABASE_URL -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database: Connected"
else
    echo "❌ Database: Connection failed"
fi

# Check workers
WORKER_COUNT=$(redis-cli KEYS "rq:worker:*" | wc -l)
echo "👷 Workers: $WORKER_COUNT active"

# Check queue lengths
DEFAULT_QUEUE=$(redis-cli LLEN rq:queue:default)
EMAIL_QUEUE=$(redis-cli LLEN rq:queue:email_processing)
FAILED_QUEUE=$(redis-cli LLEN rq:queue:failed)

echo "📊 Queues:"
echo "   Default: $DEFAULT_QUEUE jobs"
echo "   Email: $EMAIL_QUEUE jobs"
echo "   Failed: $FAILED_QUEUE jobs"

if [ $FAILED_QUEUE -gt 10 ]; then
    echo "⚠️  High number of failed jobs detected!"
fi
```

### 2. Monitoring Alerts

```python
#!/usr/bin/env python3
"""
Production Monitoring Script
Save as: hack/monitor_production.py
"""

import os
import redis
from rq import Queue, Worker
import smtplib
from email.mime.text import MIMEText

def check_system_health():
    """Check system health and send alerts if needed."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = redis.from_url(redis_url)
    
    alerts = []
    
    # Check worker count
    workers = Worker.all(connection=redis_conn)
    if len(workers) == 0:
        alerts.append("No workers are running!")
    
    # Check failed jobs
    failed_queue = Queue('failed', connection=redis_conn)
    if len(failed_queue) > 10:
        alerts.append(f"High number of failed jobs: {len(failed_queue)}")
    
    # Check queue backlog
    email_queue = Queue('email_processing', connection=redis_conn)
    if len(email_queue) > 100:
        alerts.append(f"Large queue backlog: {len(email_queue)} jobs")
    
    # Check Redis memory
    memory_info = redis_conn.info('memory')
    memory_usage = memory_info['used_memory'] / memory_info.get('maxmemory', float('inf'))
    if memory_usage > 0.8:
        alerts.append(f"High Redis memory usage: {memory_usage:.1%}")
    
    if alerts:
        send_alert(alerts)
    
    return len(alerts) == 0

def send_alert(alerts):
    """Send alert email (configure SMTP settings)."""
    message = "Kanakku Email Automation Alerts:\n\n" + "\n".join(f"- {alert}" for alert in alerts)
    print(f"ALERT: {message}")
    # Add email sending logic here

if __name__ == "__main__":
    check_system_health()
```

### 3. Log Analysis

```bash
# Analyze worker logs for errors
grep -i error banktransactions/logs/worker.log | tail -20

# Count job types processed today
grep "$(date +%Y-%m-%d)" banktransactions/logs/worker.log | grep "process_user_emails" | wc -l

# Find slow jobs (taking more than 30 seconds)
grep -E "Job.*took [3-9][0-9]\.[0-9]+ seconds" banktransactions/logs/worker.log
```

## Troubleshooting Checklist

When debugging Redis queue issues, follow this checklist:

### ✅ Environment Check
- [ ] Correct directory (`kanakku/banktransactions/email_automation/`)
- [ ] Virtual environment activated
- [ ] Required environment variables set
- [ ] Dependencies installed

### ✅ Service Check
- [ ] Redis server running
- [ ] PostgreSQL server running
- [ ] Network connectivity to services
- [ ] Correct ports accessible

### ✅ Queue Check
- [ ] Queues exist and accessible
- [ ] No excessive failed jobs
- [ ] Memory usage within limits
- [ ] Job serialization working

### ✅ Worker Check
- [ ] Workers running and responsive
- [ ] Worker heartbeats recent
- [ ] No stale worker processes
- [ ] Logs show activity

### ✅ Application Check
- [ ] Database migrations applied
- [ ] Email configurations valid
- [ ] API endpoints responding
- [ ] Authentication working

## Getting Help

If you're still experiencing issues after following this guide:

1. **Collect Information**:
   ```bash
   # Run the comprehensive debug script
   python hack/debug_redis_queue.py --action status > debug_output.txt
   
   # Include recent logs
   tail -100 banktransactions/logs/worker.log >> debug_output.txt
   ```

2. **Check the Fixes Directory**:
   Look in `fixes/` for similar issues that have been resolved before.

3. **Create a New Fix Document**:
   If you solve a new issue, document it in `fixes/` following the existing format.

4. **Environment Details**:
   Include your OS, Python version, Redis version, and PostgreSQL version when reporting issues.

---

**Last Updated**: $(date +%Y-%m-%d)  
**Maintainer**: Kanakku Development Team 