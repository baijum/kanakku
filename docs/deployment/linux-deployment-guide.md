# Kanakku Email Automation - Linux Deployment Guide

This guide covers deploying the Kanakku email automation system on Linux servers. The system has been thoroughly tested and works perfectly on Linux without the macOS-specific forking issues.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Server Setup](#server-setup)
3. [Application Deployment](#application-deployment)
4. [Database Setup](#database-setup)
5. [Redis Setup](#redis-setup)
6. [Environment Configuration](#environment-configuration)
7. [Service Configuration](#service-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8+ (or equivalent)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: Stable internet connection

### Recommended for Production
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed connection with low latency

### Software Dependencies
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Nginx
- Supervisor (for process management)
- Git

## Server Setup

### 1. Update System Packages

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# or for newer versions
sudo dnf update -y
```

### 2. Install Required Packages

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib \
    redis-server nginx supervisor git curl wget htop

# CentOS/RHEL
sudo yum install -y python3 python3-pip postgresql postgresql-server postgresql-contrib \
    redis nginx supervisor git curl wget htop
```

### 3. Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash kanakku
sudo usermod -aG sudo kanakku  # Optional: if you need sudo access

# Switch to application user
sudo su - kanakku
```

## Application Deployment

### 1. Clone Repository

```bash
# As kanakku user
cd /home/kanakku
git clone https://github.com/your-org/kanakku.git
cd kanakku
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies

```bash
# Install all dependencies using unified setup
pip install -e ".[dev]"
```

### 4. Set Up Directory Structure

```bash
# Create necessary directories
mkdir -p /home/kanakku/kanakku/logs
mkdir -p /home/kanakku/kanakku/data
mkdir -p /home/kanakku/kanakku/backups

# Set proper permissions
chmod 755 /home/kanakku/kanakku/logs
chmod 755 /home/kanakku/kanakku/data
chmod 700 /home/kanakku/kanakku/backups
```

## Database Setup

### 1. Configure PostgreSQL

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb kanakku_prod
createuser kanakku_user

# Set password and permissions
psql -c "ALTER USER kanakku_user PASSWORD 'your_secure_password_here';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE kanakku_prod TO kanakku_user;"
psql -c "ALTER USER kanakku_user CREATEDB;"  # For running migrations

# Exit postgres user
exit
```

### 2. Configure PostgreSQL Settings

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf

# Key settings to modify:
# listen_addresses = 'localhost'
# max_connections = 100
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
# maintenance_work_mem = 64MB

# Edit pg_hba.conf for authentication
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Add line for local connections:
# local   kanakku_prod    kanakku_user                    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

### 3. Run Database Migrations

```bash
# As kanakku user, in the project directory
cd /home/kanakku/kanakku
source venv/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://kanakku_user:your_secure_password_here@localhost:5432/kanakku_prod"
export FLASK_APP=backend/app

# Run migrations
cd backend
flask db upgrade

# Verify database setup
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT version();')
    print('Database connection successful:', result.fetchone()[0])
"
```

## Redis Setup

### 1. Configure Redis

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings:
# bind 127.0.0.1
# port 6379
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping  # Should return PONG
```

## Environment Configuration

### 1. Create Production Environment File

```bash
# Create environment file
sudo nano /home/kanakku/kanakku/.env.production

# Add the following content:
```

```bash
# Database Configuration
DATABASE_URL=postgresql://kanakku_user:your_secure_password_here@localhost:5432/kanakku_prod

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Keys (Generate strong keys!)
SECRET_KEY=your_super_secret_key_here_64_chars_minimum_for_production_use
JWT_SECRET_KEY=your_jwt_secret_key_here_also_64_chars_minimum_for_security
ENCRYPTION_KEY=your_base64_encryption_key_here_44_chars_for_fernet_encryption

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_for_llm_processing

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_notification_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/kanakku/kanakku/logs/app.log

# Security Headers
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

### 2. Generate Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"

# Generate ENCRYPTION_KEY (for Fernet encryption)
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### 3. Set File Permissions

```bash
# Secure the environment file
sudo chown kanakku:kanakku /home/kanakku/kanakku/.env.production
sudo chmod 600 /home/kanakku/kanakku/.env.production
```

## Service Configuration

### 1. Create Systemd Service Files

#### Flask Backend Service

```bash
sudo nano /etc/systemd/system/kanakku-backend.service
```

```ini
[Unit]
Description=Kanakku Flask Backend
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=kanakku
Group=kanakku
WorkingDirectory=/home/kanakku/kanakku/backend
Environment=PATH=/home/kanakku/kanakku/venv/bin
EnvironmentFile=/home/kanakku/kanakku/.env.production
ExecStart=/home/kanakku/kanakku/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Email Automation Scheduler Service

```bash
sudo nano /etc/systemd/system/kanakku-scheduler.service
```

```ini
[Unit]
Description=Kanakku Email Automation Scheduler
After=network.target postgresql.service redis.service kanakku-backend.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=kanakku
Group=kanakku
WorkingDirectory=/home/kanakku/kanakku/banktransactions/email_automation
Environment=PATH=/home/kanakku/kanakku/venv/bin
EnvironmentFile=/home/kanakku/kanakku/.env.production
ExecStart=/home/kanakku/kanakku/venv/bin/kanakku-scheduler --interval 300
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

#### Email Automation Worker Service

```bash
sudo nano /etc/systemd/system/kanakku-worker.service
```

```ini
[Unit]
Description=Kanakku Email Automation Worker
After=network.target postgresql.service redis.service kanakku-backend.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=kanakku
Group=kanakku
WorkingDirectory=/home/kanakku/kanakku/banktransactions/email_automation
Environment=PATH=/home/kanakku/kanakku/venv/bin
EnvironmentFile=/home/kanakku/kanakku/.env.production
ExecStart=/home/kanakku/kanakku/venv/bin/kanakku-worker --queue-name email_processing --worker-name production_worker
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### 2. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/kanakku
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Frontend (React build)
    location / {
        root /home/kanakku/kanakku/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

### 3. Enable and Start Services

```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/kanakku /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
sudo systemctl enable nginx

# Enable and start Kanakku services
sudo systemctl daemon-reload
sudo systemctl enable kanakku-backend kanakku-scheduler kanakku-worker
sudo systemctl start kanakku-backend kanakku-scheduler kanakku-worker

# Check service status
sudo systemctl status kanakku-backend
sudo systemctl status kanakku-scheduler
sudo systemctl status kanakku-worker
```

## Monitoring and Logging

### 1. Configure Log Rotation

```bash
sudo nano /etc/logrotate.d/kanakku
```

```
/home/kanakku/kanakku/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 kanakku kanakku
    postrotate
        systemctl reload kanakku-backend kanakku-scheduler kanakku-worker
    endscript
}
```

### 2. Set Up Health Checks

```bash
# Create health check script
sudo nano /home/kanakku/kanakku/scripts/health_check.sh
```

```bash
#!/bin/bash

# Health check script for Kanakku services
LOG_FILE="/home/kanakku/kanakku/logs/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting health check..." >> $LOG_FILE

# Check backend service
if systemctl is-active --quiet kanakku-backend; then
    echo "[$DATE] Backend service: OK" >> $LOG_FILE
else
    echo "[$DATE] Backend service: FAILED" >> $LOG_FILE
    systemctl restart kanakku-backend
fi

# Check scheduler service
if systemctl is-active --quiet kanakku-scheduler; then
    echo "[$DATE] Scheduler service: OK" >> $LOG_FILE
else
    echo "[$DATE] Scheduler service: FAILED" >> $LOG_FILE
    systemctl restart kanakku-scheduler
fi

# Check worker service
if systemctl is-active --quiet kanakku-worker; then
    echo "[$DATE] Worker service: OK" >> $LOG_FILE
else
    echo "[$DATE] Worker service: FAILED" >> $LOG_FILE
    systemctl restart kanakku-worker
fi

# Check database connectivity
if sudo -u kanakku PGPASSWORD=your_secure_password_here psql -h localhost -U kanakku_user -d kanakku_prod -c "SELECT 1;" > /dev/null 2>&1; then
    echo "[$DATE] Database: OK" >> $LOG_FILE
else
    echo "[$DATE] Database: FAILED" >> $LOG_FILE
fi

# Check Redis connectivity
if redis-cli ping > /dev/null 2>&1; then
    echo "[$DATE] Redis: OK" >> $LOG_FILE
else
    echo "[$DATE] Redis: FAILED" >> $LOG_FILE
fi

echo "[$DATE] Health check completed." >> $LOG_FILE
```

```bash
# Make script executable
chmod +x /home/kanakku/kanakku/scripts/health_check.sh

# Add to crontab for regular checks
sudo crontab -e
# Add line: */5 * * * * /home/kanakku/kanakku/scripts/health_check.sh
```

### 3. Set Up Monitoring Dashboard

```bash
# Install monitoring tools (optional)
sudo apt install -y htop iotop nethogs

# Create monitoring script
sudo nano /home/kanakku/kanakku/scripts/monitor.sh
```

```bash
#!/bin/bash

echo "=== Kanakku System Monitor ==="
echo "Date: $(date)"
echo ""

echo "=== System Resources ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 $3 $4 $5 $6 $7 $8}'
echo ""

echo "Memory Usage:"
free -h
echo ""

echo "Disk Usage:"
df -h /
echo ""

echo "=== Service Status ==="
systemctl status kanakku-backend --no-pager -l
systemctl status kanakku-scheduler --no-pager -l
systemctl status kanakku-worker --no-pager -l
echo ""

echo "=== Recent Logs ==="
echo "Backend logs (last 10 lines):"
tail -10 /home/kanakku/kanakku/logs/app.log
echo ""

echo "Worker logs (last 10 lines):"
tail -10 /home/kanakku/kanakku/banktransactions/logs/worker.log
echo ""

echo "=== Queue Status ==="
sudo -u kanakku bash -c "
cd /home/kanakku/kanakku
source venv/bin/activate
source .env.production
python3 -c \"
import redis
from rq import Queue
r = redis.from_url('$REDIS_URL')
q = Queue('email_processing', connection=r)
print(f'Email processing queue: {len(q)} jobs pending')
\"
"
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check firewall status
sudo ufw status verbose
```

### 2. SSL Certificate Setup

```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Set up automatic renewal
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Security Updates

```bash
# Enable automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure automatic updates
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
# Ensure security updates are enabled
```

## Backup Strategy

### 1. Database Backup Script

```bash
sudo nano /home/kanakku/kanakku/scripts/backup_db.sh
```

```bash
#!/bin/bash

BACKUP_DIR="/home/kanakku/kanakku/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="kanakku_prod"
DB_USER="kanakku_user"

# Create backup
PGPASSWORD=your_secure_password_here pg_dump -h localhost -U $DB_USER $DB_NAME > $BACKUP_DIR/kanakku_db_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/kanakku_db_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "kanakku_db_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: kanakku_db_$DATE.sql.gz"
```

```bash
# Make script executable
chmod +x /home/kanakku/kanakku/scripts/backup_db.sh

# Schedule daily backups
sudo crontab -e
# Add line: 0 2 * * * /home/kanakku/kanakku/scripts/backup_db.sh
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start

```bash
# Check service logs
sudo journalctl -u kanakku-backend -f
sudo journalctl -u kanakku-scheduler -f
sudo journalctl -u kanakku-worker -f

# Check application logs
tail -f /home/kanakku/kanakku/logs/app.log
tail -f /home/kanakku/kanakku/banktransactions/logs/worker.log
```

#### 2. Database Connection Issues

```bash
# Test database connection
sudo -u kanakku PGPASSWORD=your_password psql -h localhost -U kanakku_user -d kanakku_prod -c "SELECT version();"

# Check PostgreSQL status
sudo systemctl status postgresql
sudo journalctl -u postgresql -f
```

#### 3. Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Check Redis status
sudo systemctl status redis-server
sudo journalctl -u redis-server -f
```

#### 4. Email Processing Issues

```bash
# Check worker queue status
sudo -u kanakku bash -c "
cd /home/kanakku/kanakku
source venv/bin/activate
source .env.production
python3 -c \"
import redis
from rq import Queue
r = redis.from_url('$REDIS_URL')
q = Queue('email_processing', connection=r)
print(f'Queue length: {len(q)}')
print(f'Job IDs: {q.job_ids}')
\"
"

# Check failed jobs
sudo -u kanakku bash -c "
cd /home/kanakku/kanakku/banktransactions/email_automation
source ../../venv/bin/activate
source ../../.env.production
python3 check_failed.py
"
```

### Performance Tuning

#### 1. Database Optimization

```sql
-- Connect to database and run these queries for optimization
-- Analyze table statistics
ANALYZE;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;

-- Monitor slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 2. Redis Optimization

```bash
# Monitor Redis performance
redis-cli info memory
redis-cli info stats

# Check slow queries
redis-cli slowlog get 10
```

## Deployment Checklist

- [ ] Server provisioned and updated
- [ ] All required packages installed
- [ ] Application user created
- [ ] Repository cloned and dependencies installed
- [ ] PostgreSQL configured and database created
- [ ] Redis configured and running
- [ ] Environment variables set securely
- [ ] Database migrations run successfully
- [ ] Systemd services created and enabled
- [ ] Nginx configured with SSL
- [ ] Firewall configured
- [ ] SSL certificates obtained
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] Health checks configured
- [ ] Security hardening applied
- [ ] Performance tuning completed
- [ ] All services tested and running

## Maintenance

### Regular Tasks

1. **Daily**: Check service status and logs
2. **Weekly**: Review system resources and performance
3. **Monthly**: Update system packages and review security
4. **Quarterly**: Review and test backup/restore procedures

### Update Procedure

```bash
# 1. Backup database
/home/kanakku/kanakku/scripts/backup_db.sh

# 2. Pull latest code
cd /home/kanakku/kanakku
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -e ".[dev]"

# 4. Run migrations
cd backend
flask db upgrade

# 5. Restart services
sudo systemctl restart kanakku-backend kanakku-scheduler kanakku-worker

# 6. Verify deployment
sudo systemctl status kanakku-backend kanakku-scheduler kanakku-worker
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check system resources
4. Consult the project documentation
5. Contact the development team

**Note**: This deployment guide assumes a production environment. Always test deployments in a staging environment first. 