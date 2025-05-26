# Kanakku Executable Scripts

Kanakku provides convenient executable scripts for running the email automation worker and scheduler processes. These scripts are automatically installed when you install the package and can be run from anywhere in your system.

## Installation

The executable scripts are automatically installed when you install Kanakku:

```bash
# Install in development mode (recommended for development)
pip install -e ".[dev]"

# Or install normally
pip install .
```

After installation, the following commands will be available in your PATH:
- `kanakku-worker`
- `kanakku-scheduler`

## Worker Script (`kanakku-worker`)

The worker script processes email automation jobs from the Redis queue.

### Basic Usage

```bash
# Start worker with default settings
kanakku-worker

# Start worker with custom Redis URL
kanakku-worker --redis-url redis://localhost:6379/1

# Start worker with custom queue name
kanakku-worker --queue-name my_email_queue

# Start worker with custom name
kanakku-worker --worker-name production_worker_1
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--queue-name` | `email_processing` | Name of the Redis queue to process |
| `--redis-url` | `redis://localhost:6379/0` | Redis connection URL |
| `--worker-name` | Auto-generated | Custom worker name for identification |
| `--force-simple-worker` | `false` | Force SimpleWorker (useful for debugging) |

### Environment Variables

The worker script reads the following environment variables:

- `REDIS_URL`: Redis connection URL (overridden by `--redis-url`)
- `DATABASE_URL`: PostgreSQL connection string (required)
- `GOOGLE_API_KEY`: Google Gemini API key (required for AI processing)
- `ENCRYPTION_KEY`: 32-byte base64 key for encrypting email credentials
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Examples

```bash
# Production worker with custom settings
kanakku-worker \
  --queue-name email_processing \
  --redis-url redis://prod-redis:6379/0 \
  --worker-name prod_worker_1

# Development worker with debug logging
LOG_LEVEL=DEBUG kanakku-worker --force-simple-worker

# Worker for specific environment
REDIS_URL=redis://staging:6379/0 kanakku-worker
```

## Scheduler Script (`kanakku-scheduler`)

The scheduler script manages periodic email processing by scheduling jobs at regular intervals.

### Basic Usage

```bash
# Start scheduler with default 5-minute interval
kanakku-scheduler

# Start scheduler with custom interval (10 minutes)
kanakku-scheduler --interval 600

# Start scheduler with custom Redis URL
kanakku-scheduler --redis-url redis://localhost:6379/1
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--interval` | `300` | Scheduling interval in seconds |
| `--redis-url` | `redis://localhost:6379/0` | Redis connection URL |

### Environment Variables

The scheduler script reads the same environment variables as the worker:

- `REDIS_URL`: Redis connection URL (overridden by `--redis-url`)
- `DATABASE_URL`: PostgreSQL connection string (required)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Examples

```bash
# Production scheduler with 10-minute intervals
kanakku-scheduler --interval 600 --redis-url redis://prod-redis:6379/0

# Development scheduler with debug logging
LOG_LEVEL=DEBUG kanakku-scheduler --interval 60

# Scheduler for specific environment
REDIS_URL=redis://staging:6379/0 kanakku-scheduler
```

## Logging

Both scripts automatically configure logging to:

1. **Console output**: Real-time logs to stdout
2. **Log files**: 
   - Worker: `banktransactions/logs/worker.log`
   - Scheduler: `banktransactions/logs/scheduler.log`

Log files are created relative to the script's location, so ensure the `banktransactions/logs/` directory exists.

## Production Deployment

### Systemd Services

For production deployment, create systemd service files:

**Scheduler Service** (`/etc/systemd/system/kanakku-scheduler.service`):
```ini
[Unit]
Description=Kanakku Email Automation Scheduler
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=kanakku
Group=kanakku
EnvironmentFile=/home/kanakku/kanakku/.env.production
ExecStart=/home/kanakku/kanakku/venv/bin/kanakku-scheduler --interval 300
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

**Worker Service** (`/etc/systemd/system/kanakku-worker.service`):
```ini
[Unit]
Description=Kanakku Email Automation Worker
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=kanakku
Group=kanakku
EnvironmentFile=/home/kanakku/kanakku/.env.production
ExecStart=/home/kanakku/kanakku/venv/bin/kanakku-worker --queue-name email_processing --worker-name production_worker
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

## Legacy Direct Execution

You can still run the scripts directly if needed:

```bash
cd banktransactions/email_automation

# Direct Python execution
python run_worker.py --queue-name email_processing
python run_scheduler.py --interval 300
```

This approach requires being in the correct directory and manually managing the Python path.

## Troubleshooting

### Script Not Found

If you get "command not found" errors:

1. Ensure Kanakku is installed: `pip install -e ".[dev]"`
2. Check your virtual environment is activated
3. Verify the scripts are in your PATH: `which kanakku-worker`

### Import Errors

If you encounter import errors:

1. Ensure all dependencies are installed: `pip install -e ".[dev]"`
2. Check that environment variables are set correctly
3. Verify the database and Redis connections

### Permission Errors

For production deployments:

1. Ensure the user has write access to log directories
2. Check that the virtual environment is accessible
3. Verify environment file permissions

## Related Documentation

- [Development Setup Guide](DEVELOPMENT_SETUP.md) - Setting up the development environment
- [Redis Queue Quick Reference](redis-queue-quick-reference.md) - Debugging Redis queue issues
- [Linux Deployment Guide](deployment/linux-deployment-guide.md) - Production deployment instructions
- [Email Automation README](../banktransactions/email_automation/README.md) - Detailed email automation documentation 