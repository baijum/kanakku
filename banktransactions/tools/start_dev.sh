#!/bin/bash

# Email Automation Development Startup Script
# This script starts all necessary services for email automation development

set -e

echo "🚀 Starting Email Automation Development Environment"
echo "=================================================="

# Check if Redis is running
echo "📡 Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   redis-server"
    exit 1
fi

# Check environment variables
echo "🔧 Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set - AI parsing will not work"
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "⚠️  ENCRYPTION_KEY not set - using temporary key"
fi

echo "✅ Environment check complete"

# Test the system
echo "🧪 Running system tests..."
python test_system.py
if [ $? -ne 0 ]; then
    echo "❌ System tests failed. Please check the configuration."
    exit 1
fi

echo "✅ System tests passed"

# Start services in background
echo "🔄 Starting email automation services..."

# Start worker
echo "Starting email worker..."
python run_worker.py --worker-name "dev_worker" &
WORKER_PID=$!

# Start scheduler (optional)
if [ "$1" = "--with-scheduler" ]; then
    echo "Starting scheduler..."
    python run_scheduler.py --interval 60 &
    SCHEDULER_PID=$!
fi

echo "✅ Services started successfully"
echo ""
echo "📊 Service Status:"
echo "   Worker PID: $WORKER_PID"
if [ ! -z "$SCHEDULER_PID" ]; then
    echo "   Scheduler PID: $SCHEDULER_PID"
fi
echo ""
echo "📝 Logs:"
echo "   Worker logs: ../logs/worker.log"
if [ ! -z "$SCHEDULER_PID" ]; then
    echo "   Scheduler logs: ../logs/scheduler.log"
fi
echo ""
echo "🌐 Web Interface:"
echo "   Configure email automation at: http://localhost:3000/profile"
echo ""
echo "⏹️  To stop services, press Ctrl+C"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $WORKER_PID 2>/dev/null; [ ! -z "$SCHEDULER_PID" ] && kill $SCHEDULER_PID 2>/dev/null; echo "✅ Services stopped"; exit 0' INT

# Keep script running
wait
