#!/bin/bash
# Kanakku Email Automation Health Check Script

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

# Check Redis memory usage
MEMORY_USED=$(redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
echo "💾 Redis Memory: $MEMORY_USED used"

# Check if email automation directory exists
if [ -d "banktransactions/email_automation" ]; then
    echo "✅ Email automation directory: Found"
else
    echo "❌ Email automation directory: Not found"
fi

# Check log files
if [ -f "banktransactions/logs/worker.log" ]; then
    RECENT_ERRORS=$(grep -c "ERROR" banktransactions/logs/worker.log | tail -100)
    echo "📝 Recent worker errors: $RECENT_ERRORS"
else
    echo "⚠️  Worker log file not found"
fi

echo "========================================"
echo "Health check completed at $(date)"
