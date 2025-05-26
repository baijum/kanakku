# Email Automation Scheduler Documentation

## Overview

The `run_scheduler.py` script is responsible for managing periodic email processing jobs in the Kanakku email automation system. It schedules background jobs for users who have enabled email automation based on their configured polling intervals.

## How It Works

1. **Connects to Redis and Database**: Establishes connections to Redis (for job queuing) and PostgreSQL (for user configurations)
2. **Finds Enabled Configurations**: Queries the database for users with `is_enabled=True` in their email configurations
3. **Calculates Next Run Times**: Based on each user's `polling_interval` (hourly/daily) and `last_check_time`
4. **Schedules Jobs**: Uses Redis Queue Scheduler to enqueue email processing jobs at the calculated times
5. **Repeats**: Runs this process every `--interval` seconds (default: 300 seconds / 5 minutes)

## Usage

### Basic Usage

```bash
cd banktransactions/email_automation
python run_scheduler.py
```

### With Options

```bash
python run_scheduler.py --redis-url redis://localhost:6379/0 --interval 300
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--redis-url` | `redis://localhost:6379/0` | Redis server URL for job queuing |
| `--interval` | `300` | Scheduling check interval in seconds |

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/kanakku` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis server URL |
| `ENCRYPTION_KEY` | None | 32-byte base64 key for decrypting email passwords |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Setup Examples

### Development Setup

```bash
# Set environment variables
export DATABASE_URL="postgresql://kanakku_dev:secret123@localhost:5432/kanakku_dev_db1"
export REDIS_URL="redis://localhost:6379/0"
export ENCRYPTION_KEY="bKlSA7Wd7Ptz9QJ4gZ5gGPvr-OPlTiejjcfbMvYGLvg="

# Navigate to correct directory
cd banktransactions/email_automation

# Start scheduler with 1-minute interval for testing
python run_scheduler.py --interval 60
```

### Production Setup

```bash
# Set environment variables (use your actual values)
export DATABASE_URL="postgresql://kanakku_prod:secure_password@db.example.com:5432/kanakku_prod"
export REDIS_URL="redis://redis.example.com:6379/0"
export ENCRYPTION_KEY="your_production_encryption_key_here"

# Navigate to correct directory
cd banktransactions/email_automation

# Start scheduler with default 5-minute interval
python run_scheduler.py
```

### Using .env File

Create a `.env` file in the `banktransactions/email_automation` directory:

```bash
# .env file
DATABASE_URL=postgresql://kanakku_dev:secret123@localhost:5432/kanakku_dev_db1
REDIS_URL=redis://localhost:6379/0
ENCRYPTION_KEY=bKlSA7Wd7Ptz9QJ4gZ5gGPvr-OPlTiejjcfbMvYGLvg=
LOG_LEVEL=INFO
```

Then run:
```bash
cd banktransactions/email_automation
python run_scheduler.py
```

## Monitoring

### Check if Scheduler is Running

```bash
ps aux | grep run_scheduler
```

### View Logs

```bash
# Real-time logs
tail -f ../logs/scheduler.log

# Recent logs
cat ../logs/scheduler.log | tail -50
```

### Check Scheduled Jobs in Redis

```bash
# Check default queue length
redis-cli LLEN rq:queue:default

# Check scheduled jobs
redis-cli ZRANGE rq:scheduler:scheduled_jobs 0 -1 WITHSCORES

# Check all Redis keys related to RQ
redis-cli KEYS "rq:*"
```

### Sample Log Output

```
2025-05-24 05:56:01,322 - INFO - Connected to Redis at redis://localhost:6379/0
2025-05-24 05:56:01,329 - INFO - Connected to database
2025-05-24 05:56:01,329 - INFO - Starting scheduler with 60s interval
2025-05-24 05:56:01,329 - INFO - Scheduler is ready. Press Ctrl+C to stop.
2025-05-24 05:56:01,409 - INFO - Scheduled job for user 1 at 2025-05-24 00:26:01.406871
```

## Troubleshooting

### Common Errors

#### 1. ModuleNotFoundError: No module named 'banktransactions'

**Error:**
```
ModuleNotFoundError: No module named 'banktransactions'
```

**Solution:**
Always run the scheduler from the correct directory:
```bash
cd banktransactions/email_automation
python run_scheduler.py
```

#### 2. DATABASE_URL environment variable not set

**Error:**
```
ValueError: DATABASE_URL environment variable not set
```

**Solution:**
Set the DATABASE_URL environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/kanakku"
```

#### 3. Redis Connection Failed

**Error:**
```
redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused.
```

**Solution:**
Start Redis server:
```bash
redis-server
```

Or check if Redis is running:
```bash
redis-cli ping  # Should return "PONG"
```

#### 4. Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution:**
- Check if PostgreSQL is running
- Verify DATABASE_URL is correct
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

### Debug Mode

Enable debug logging for more detailed output:

```bash
export LOG_LEVEL=DEBUG
python run_scheduler.py --interval 60
```

### Testing the Scheduler

Run the system test to verify everything is configured correctly:

```bash
cd banktransactions/email_automation
python test_system.py
```

## Integration with Email Worker

The scheduler works in conjunction with the email worker (`run_worker.py`):

1. **Scheduler**: Enqueues jobs at scheduled times
2. **Worker**: Processes the enqueued jobs (actual email processing)

Both should be running for the email automation system to work:

```bash
# Terminal 1: Start the worker
cd banktransactions/email_automation
python run_worker.py

# Terminal 2: Start the scheduler
cd banktransactions/email_automation
python run_scheduler.py
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/kanakku-email-scheduler.service`:

```ini
[Unit]
Description=Kanakku Email Scheduler
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=kanakku
WorkingDirectory=/path/to/kanakku/banktransactions/email_automation
ExecStart=/path/to/venv/bin/python run_scheduler.py
Restart=always
RestartSec=10
Environment=DATABASE_URL=postgresql://user:pass@localhost:5432/kanakku
Environment=REDIS_URL=redis://localhost:6379/0
Environment=ENCRYPTION_KEY=your_encryption_key_here

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kanakku-email-scheduler
sudo systemctl start kanakku-email-scheduler
sudo systemctl status kanakku-email-scheduler
```

## Performance Considerations

### Scheduling Interval

- **Development**: 60 seconds for quick testing
- **Production**: 300 seconds (5 minutes) is usually sufficient
- **High Volume**: Consider reducing to 120 seconds (2 minutes)

### Resource Usage

The scheduler is lightweight and typically uses:
- **Memory**: ~50-100 MB
- **CPU**: Minimal (only active during scheduling checks)
- **Network**: Low (only database and Redis queries)

### Scaling

For high-volume deployments:
- Run multiple scheduler instances with different intervals
- Use Redis Cluster for job queue scaling
- Monitor queue lengths and adjust intervals accordingly

## Security Considerations

1. **Environment Variables**: Never commit `.env` files with real credentials
2. **Database Access**: Use dedicated database user with minimal permissions
3. **Redis Security**: Configure Redis authentication in production
4. **Encryption Key**: Generate strong encryption keys and rotate regularly
5. **Logging**: Ensure logs don't contain sensitive information

## Contributing

When modifying the scheduler:

1. Test with `python test_system.py`
2. Verify import paths work from the correct directory
3. Update this documentation for any new features
4. Add appropriate error handling and logging
5. Test with both development and production-like configurations 