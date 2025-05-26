# Email Automation System

This directory contains the email automation system for Kanakku, which automatically processes bank transaction emails and creates transactions in the system.

## Architecture

The email automation system consists of several components:

1. **Backend API** (`backend/app/email_automation.py`) - REST API for managing email configurations
2. **Database Models** (`backend/app/models.py`) - EmailConfiguration model for storing user settings
3. **Worker System** (`workers/`) - Background job processing for email parsing
4. **Scheduler** (`run_scheduler.py`) - Periodic job scheduling
5. **Frontend UI** (`frontend/src/components/Auth/EmailAutomation.jsx`) - User interface for configuration

## Features

- **Secure Configuration**: Encrypted storage of Gmail app passwords
- **IMAP Integration**: Connects to Gmail via IMAP for email retrieval
- **AI-Powered Parsing**: Uses Google Gemini LLM for transaction extraction
- **Few-Shot Learning**: Improves accuracy with user-provided sample emails
- **Background Processing**: Redis Queue (RQ) for asynchronous email processing
- **Flexible Scheduling**: Configurable polling intervals (hourly, daily)
- **Status Monitoring**: Real-time status tracking and error reporting
- **Manual Triggers**: On-demand email processing

## Quick Start

### 1. Prerequisites Check
```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Check if PostgreSQL is accessible
psql $DATABASE_URL -c "SELECT 1;"  # Should return "1"
```

### 2. One-Command Setup
```bash
# Navigate to email automation directory
cd banktransactions/email_automation

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Set required environment variables
export DATABASE_URL="postgresql://kanakku_dev:secret123@localhost:5432/kanakku_dev_db1"
export REDIS_URL="redis://localhost:6379/0"
export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Test the system
python test_system.py

# Start the worker (in one terminal)
python run_worker.py &

# Start the scheduler (in another terminal)
python run_scheduler.py --interval 300
```

### 3. Verify Everything is Working
```bash
# Check if scheduler is running
ps aux | grep run_scheduler

# Check if worker is running  
ps aux | grep run_worker

# Check Redis queues
redis-cli LLEN rq:queue:default

# Check logs
tail -f ../logs/scheduler.log
tail -f ../logs/worker.log
```

## Setup Instructions

### 1. Prerequisites

- Redis server running
- PostgreSQL database
- Google Gemini API key
- Gmail account with app password

### 2. Environment Variables

The worker script automatically loads environment variables from `.env` files in the following order:
1. Current directory (`.env`)
2. Parent directory (`../env`)
3. Project root (`../../.env`)

Create a `.env` file with these variables:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/kanakku

# Google Gemini API (for LLM processing)
GOOGLE_API_KEY=your_gemini_api_key_here

# Encryption key for sensitive data (32-byte base64 encoded key)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_32_byte_base64_encoded_key

# Optional: Exchange Rate API
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key

# Optional: API Configuration (for transaction submission)
API_ENDPOINT=http://localhost:5000
API_KEY=your_api_key_here

# Optional: Logging Configuration
LOG_LEVEL=INFO

# Optional: Gmail Configuration (for email processing)
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
```

**Note**: You can also set these as system environment variables instead of using a `.env` file.

### 3. Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Go to Google Account → Security → App passwords
   - Generate a new app password for "Mail"
   - Use this password in the email automation configuration

### 4. Start the Services

#### Start Redis (if not already running)
```bash
redis-server
```

#### Start the Email Worker
```bash
cd banktransactions/email_automation
python run_worker.py
```

#### Start the Scheduler (optional, for automatic scheduling)
```bash
cd banktransactions/email_automation
python run_scheduler.py
```

## Usage

### 1. Configure Email Automation

1. Log into Kanakku web interface
2. Go to Profile Settings → Email Automation tab
3. Enter your Gmail credentials:
   - Email address
   - App password (generated from Google Account settings)
   - IMAP settings (defaults to Gmail)
   - Polling interval
4. Test the connection
5. Enable automation

### 2. Add Sample Emails (Recommended)

To improve AI accuracy:

1. In the Email Automation settings, expand "Sample Transaction Emails"
2. Add 3-5 sample bank transaction emails
3. These help the AI understand your bank's email format

### 3. Monitor Status

- Check the status section for last processing time
- View any errors in the system logs
- Use manual trigger for immediate processing

## API Endpoints

All endpoints require authentication via JWT token or API key.

### Configuration Management

- `GET /api/v1/email-automation/config` - Get user's email configuration
- `POST /api/v1/email-automation/config` - Create/update email configuration
- `PUT /api/v1/email-automation/config` - Update specific fields
- `DELETE /api/v1/email-automation/config` - Delete configuration

### Testing and Control

- `POST /api/v1/email-automation/test-connection` - Test email connection
- `GET /api/v1/email-automation/status` - Get automation status
- `POST /api/v1/email-automation/trigger` - Manually trigger processing

## Worker Commands

### Run Email Worker

```bash
python run_worker.py [options]

Options:
  --queue-name EMAIL_QUEUE    Queue name (default: email_processing)
  --redis-url REDIS_URL       Redis URL (default: redis://localhost:6379/0)
  --worker-name WORKER_NAME   Worker name (default: auto-generated)
```

### Run Scheduler

The scheduler manages periodic email processing jobs for all enabled user configurations.

**Important**: Always run the scheduler from the `banktransactions/email_automation` directory.

```bash
cd banktransactions/email_automation
python run_scheduler.py [options]

Options:
  --redis-url REDIS_URL    Redis URL (default: redis://localhost:6379/0)
  --interval SECONDS       Scheduling interval in seconds (default: 300)
```

**Environment Variables Required:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis server URL (optional, defaults to redis://localhost:6379/0)
- `ENCRYPTION_KEY`: 32-byte base64 encoded key for encrypting sensitive data

**Example with environment variables:**
```bash
cd banktransactions/email_automation
export DATABASE_URL="postgresql://user:password@localhost:5432/kanakku"
export REDIS_URL="redis://localhost:6379/0"
export ENCRYPTION_KEY="your_32_byte_base64_encoded_key"
python run_scheduler.py --interval 300
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**What the scheduler does:**
- Checks for enabled email configurations every interval
- Schedules email processing jobs based on user polling intervals
- Uses Redis Queue (RQ) to manage background jobs
- Logs all scheduling activities

**Monitoring:**
- Scheduler logs: `../logs/scheduler.log`
- Check Redis queues: `redis-cli LLEN rq:queue:default`
- Monitor with: `ps aux | grep run_scheduler`

**📖 For detailed scheduler documentation, see [SCHEDULER.md](./SCHEDULER.md)**

## Database Schema

### EmailConfiguration Table

```sql
CREATE TABLE user_email_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    is_enabled BOOLEAN DEFAULT FALSE,
    imap_server VARCHAR(255) DEFAULT 'imap.gmail.com',
    imap_port INTEGER DEFAULT 993,
    email_address VARCHAR(255) NOT NULL,
    app_password VARCHAR(255) NOT NULL,  -- Encrypted
    polling_interval VARCHAR(50) DEFAULT 'hourly',
    last_check_time TIMESTAMP,
    sample_emails TEXT,  -- JSON array
    last_processed_email_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Security Considerations

1. **Encryption**: App passwords are encrypted using Fernet symmetric encryption
2. **API Authentication**: All endpoints require valid JWT or API tokens
3. **Input Validation**: All user inputs are validated and sanitized
4. **Error Handling**: Sensitive information is not exposed in error messages
5. **Logging**: Security events are logged for monitoring

## Troubleshooting

### Common Issues

1. **Scheduler/Worker Import Errors**
   - **Error**: `ModuleNotFoundError: No module named 'banktransactions'`
   - **Solution**: Always run scripts from the `banktransactions/email_automation` directory
   - **Example**: `cd banktransactions/email_automation && python run_scheduler.py`

2. **Database Connection Issues**
   - **Error**: `DATABASE_URL environment variable not set`
   - **Solution**: Set the DATABASE_URL environment variable
   - **Example**: `export DATABASE_URL="postgresql://user:password@localhost:5432/kanakku"`

3. **Encryption Key Issues**
   - **Error**: `Working outside of application context` or encryption failures
   - **Solution**: Generate and set ENCRYPTION_KEY environment variable
   - **Command**: `python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"`

4. **Connection Failed**
   - Verify Gmail app password is correct
   - Check 2FA is enabled on Gmail account
   - Ensure IMAP is enabled in Gmail settings

5. **Worker Not Processing**
   - Check Redis connection: `redis-cli ping`
   - Verify DATABASE_URL is correct
   - Check worker logs for errors
   - Ensure worker is running: `ps aux | grep run_worker`

6. **AI Parsing Issues**
   - Add more sample emails for better accuracy
   - Verify GOOGLE_API_KEY is set correctly
   - Check if email format is supported

### Log Files

- Worker logs: `banktransactions/logs/worker.log`
- Scheduler logs: `banktransactions/logs/scheduler.log`
- Application logs: `backend/logs/kanakku.log`

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Development

### Adding New Email Parsers

1. Extend `banktransactions/email_parser.py`
2. Add bank-specific parsing logic
3. Update the LLM prompts for better accuracy
4. Test with sample emails

### Extending the API

1. Add new endpoints to `backend/app/email_automation.py`
2. Update the frontend components as needed
3. Add appropriate tests

### Testing

Run the test suite:
```bash
cd banktransactions
python -m pytest tests/
```

## Production Deployment

### Systemd Services

Create systemd service files for production:

#### Email Worker Service
```ini
[Unit]
Description=Kanakku Email Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=kanakku
WorkingDirectory=/path/to/kanakku/banktransactions/email_automation
ExecStart=/path/to/venv/bin/python run_worker.py
Restart=always
RestartSec=10
Environment=DATABASE_URL=postgresql://...
Environment=REDIS_URL=redis://localhost:6379/0
Environment=GOOGLE_API_KEY=...

[Install]
WantedBy=multi-user.target
```

#### Scheduler Service
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
Environment=DATABASE_URL=postgresql://...
Environment=REDIS_URL=redis://localhost:6379/0

[Install]
WantedBy=multi-user.target
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure security best practices

## License

This project is licensed under the same license as the main Kanakku project. 