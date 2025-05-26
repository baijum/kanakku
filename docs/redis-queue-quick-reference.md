# Redis Queue Quick Reference

Quick commands and scripts for debugging Redis Queue issues in kanakku.

## 🚀 Quick Start

```bash
# Check overall system health
./hack/health_check.sh

# Show detailed queue status
python hack/debug_redis_queue.py --action status

# Inspect all queues comprehensively
python hack/inspect_queues.py
```

## 🔧 Common Commands

### Redis CLI Commands
```bash
# Test Redis connection
redis-cli ping

# Check queue lengths
redis-cli LLEN rq:queue:email_processing
redis-cli LLEN rq:queue:failed

# List all RQ keys
redis-cli KEYS "rq:*"

# View jobs in queue
redis-cli LRANGE rq:queue:email_processing 0 9

# Get job details
redis-cli HGETALL rq:job:JOB_ID
```

### Python Debugging Scripts
```bash
# Show queue status
python hack/debug_redis_queue.py --action status

# Clear failed jobs
python hack/debug_redis_queue.py --action clear-failed

# Enqueue test job
python hack/debug_redis_queue.py --action test-job

# Inspect specific job
python hack/debug_redis_queue.py --job-id abc123def456

# Comprehensive queue inspection
python hack/inspect_queues.py
```

## 🐛 Common Issues

### Directory Not Found
```bash
# ❌ Wrong: cd ../banktransactions/email_automation
# ✅ Correct:
cd banktransactions/email_automation
```

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping
systemctl status redis

# Start Redis
redis-server
# or
systemctl start redis
```

### Worker Issues
```bash
# Check active workers
redis-cli KEYS "rq:worker:*"

# Start worker (using executable script)
kanakku-worker --redis-url redis://localhost:6379/0

# Or start worker (direct Python execution)
cd banktransactions/email_automation
python run_worker.py --redis-url redis://localhost:6379/0
```

### Environment Variables
```bash
# Required variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
export REDIS_URL="redis://localhost:6379/0"
export GOOGLE_API_KEY="your_key"
export ENCRYPTION_KEY="your_key"
```

## 📊 Monitoring

### Real-time Monitoring
```bash
# Watch queue lengths
watch -n 2 'redis-cli LLEN rq:queue:email_processing'

# Monitor worker logs
tail -f banktransactions/logs/worker.log

# Watch Redis memory
watch -n 5 'redis-cli INFO memory | grep used_memory_human'
```

### Log Analysis
```bash
# Recent errors
grep -i error banktransactions/logs/worker.log | tail -20

# Jobs processed today
grep "$(date +%Y-%m-%d)" banktransactions/logs/worker.log | wc -l

# Slow jobs
grep -E "Job.*took [3-9][0-9]\.[0-9]+ seconds" banktransactions/logs/worker.log
```

## 🧪 Testing

### Test Email System
```bash
cd banktransactions/email_automation
python test_system.py
```

### Manual Job Testing
```bash
python -c "
import os, redis
from rq import Queue
redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
queue = Queue('email_processing', connection=redis_conn)
def test_job(): return 'Test completed'
job = queue.enqueue(test_job)
print(f'Job ID: {job.id}')
"
```

## 🔍 Troubleshooting Checklist

- [ ] In correct directory (`kanakku/banktransactions/email_automation/`)
- [ ] Virtual environment activated
- [ ] Environment variables set
- [ ] Redis server running
- [ ] PostgreSQL server running
- [ ] Workers running and responsive
- [ ] No excessive failed jobs
- [ ] Logs show recent activity

## 📞 Getting Help

1. Run comprehensive debug: `python hack/debug_redis_queue.py --action status > debug.txt`
2. Check recent logs: `tail -100 banktransactions/logs/worker.log >> debug.txt`
3. Check `fixes/` directory for similar issues
4. Include environment details when reporting issues

## 🔗 Related Files

- [Full Debugging Guide](redis-queue-debugging.md)
- [Email Automation README](../banktransactions/email_automation/README.md)
- [Fixes Directory](../fixes/)
- [Architecture Documentation](ARCHITECTURE.md) 