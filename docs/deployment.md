# Kanakku Deployment Guide

This guide explains how to deploy the Kanakku application to a Debian Linux server using GitHub Actions CI/CD pipeline with Nginx as a reverse proxy.

## Architecture Overview

The deployment consists of:
- **Frontend**: React application served by Nginx
- **Backend**: Flask application running with Gunicorn
- **Email Worker**: Background email processing service
- **Email Scheduler**: Periodic email automation scheduler
- **Admin Server**: Administrative server for system management and log access
- **Database**: Self-hosted PostgreSQL
- **Cache**: Self-hosted Redis
- **Reverse Proxy**: Nginx with SSL termination
- **Process Management**: Systemd services

## Prerequisites

### Server Requirements

- Debian 11+ or Ubuntu 20.04+ server
- Minimum 2GB RAM, 2 CPU cores
- 20GB+ disk space
- Root or sudo access
- Public IP address
- Domain name (recommended for SSL)

### GitHub Repository Setup

- GitHub repository with admin access
- Ability to configure repository secrets
- SSH access to your server

## Server Setup

### 1. Initial Server Preparation

Run the automated server setup script on your Debian server:

```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/baijum/kanakku/main/scripts/server-setup.sh
sudo bash server-setup.sh
```

This script will:
- Install and configure PostgreSQL, Redis, Nginx
- Create the `kanakku` user and directories
- Set up firewall and security configurations
- Generate secure environment variables
- Create helper scripts for deployment management

### 2. Manual Server Configuration

If you prefer manual setup or need to customize the installation:

#### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git python3.11 python3.11-venv python3-pip \
    postgresql-15 redis-server nginx certbot python3-certbot-nginx \
    build-essential libpq-dev pkg-config ufw fail2ban

# Create kanakku user
sudo useradd -r -m -s /bin/bash -d /opt/kanakku kanakku
sudo mkdir -p /opt/kanakku/{logs,backups,config}
sudo mkdir -p /var/www/kanakku
sudo chown -R kanakku:kanakku /opt/kanakku
sudo chown -R www-data:www-data /var/www/kanakku
```

#### Configure PostgreSQL

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE USER kanakku WITH PASSWORD 'your_secure_password';
CREATE DATABASE kanakku OWNER kanakku;
GRANT ALL PRIVILEGES ON DATABASE kanakku TO kanakku;
CREATE DATABASE kanakku_test OWNER kanakku;
GRANT ALL PRIVILEGES ON DATABASE kanakku_test TO kanakku;
\q
EOF
```

#### Configure Environment Variables

```bash
# Create environment file
sudo nano /opt/kanakku/.env
```

Add the following configuration:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key
JWT_SECRET_KEY=your-generated-jwt-secret
CSRF_SECRET_KEY=your-generated-csrf-secret

# Database Configuration
DATABASE_URL=postgresql://kanakku:your_password@localhost:5432/kanakku

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# API Configuration
API_RATE_LIMIT=1000 per hour

# Email Automation (optional)
GOOGLE_API_KEY=your-gemini-api-key
ENCRYPTION_KEY=your-32-byte-base64-encryption-key

# Admin Server Configuration
KANAKKU_DEPLOY_HOST=localhost
KANAKKU_DEPLOY_USER=kanakku
KANAKKU_SSH_KEY_PATH=/opt/kanakku/.ssh/id_rsa
KANAKKU_SSH_PORT=22
```

### 3. Admin Server Setup

The Admin Server provides administrative access to production logs and system management. It runs as a systemd service and allows secure log access via SSH.

#### SSH Key Configuration for Admin Server

```bash
# Generate SSH key for Admin Server (if not already done)
sudo -u kanakku ssh-keygen -t rsa -b 4096 -f /opt/kanakku/.ssh/id_rsa -N ""

# Set proper permissions
sudo chmod 600 /opt/kanakku/.ssh/id_rsa
sudo chmod 644 /opt/kanakku/.ssh/id_rsa.pub
sudo chown kanakku:kanakku /opt/kanakku/.ssh/id_rsa*

# Add public key to authorized_keys for the kanakku user
sudo -u kanakku cat /opt/kanakku/.ssh/id_rsa.pub >> /opt/kanakku/.ssh/authorized_keys
sudo chmod 600 /opt/kanakku/.ssh/authorized_keys
sudo chown kanakku:kanakku /opt/kanakku/.ssh/authorized_keys
```

#### Admin Server Environment Configuration

Add the following to `/opt/kanakku/.env`:

```env
# Admin Server Configuration
KANAKKU_DEPLOY_HOST=localhost
KANAKKU_DEPLOY_USER=kanakku
KANAKKU_SSH_KEY_PATH=/opt/kanakku/.ssh/id_rsa
KANAKKU_SSH_PORT=22
```

#### Test Admin Server Configuration

```bash
# Test the Admin Server setup
cd /opt/kanakku/adminserver
sudo -u kanakku ./deploy-production.sh
```

### 4. Configure Monitoring Dashboard Authentication

Set up HTTP Basic Authentication for the monitoring dashboard:

```bash
# Navigate to the project directory
cd /opt/kanakku

# Run the htpasswd setup script
sudo ./scripts/create-htpasswd.sh

# Follow the prompts to create a username and password
# The script will create /etc/nginx/.htpasswd automatically
```

**Important:** This step should be completed before configuring nginx, as the nginx configuration references the htpasswd file.

**Security Notes:**
- Use a strong, unique password for monitoring access
- This will be required to access `https://monitor.yourdomain.com`
- Keep credentials secure and share only with authorized personnel

## GitHub Actions Setup

### 1. Configure Repository Secrets

Add the following secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DEPLOY_HOST` | Server IP address | `192.168.1.100` |
| `DEPLOY_USER` | SSH user with sudo privileges | `root` or `ubuntu` |
| `DEPLOY_SSH_KEY` | Private SSH key for server access | Contents of private key file |

### 2. SSH Key Setup

Generate SSH key pair on your server:

```bash
# Generate SSH key for deployment
sudo -u kanakku ssh-keygen -t rsa -b 4096 -f /opt/kanakku/.ssh/id_rsa -N ""

# Display the private key (copy this to GitHub secrets)
sudo cat /opt/kanakku/.ssh/id_rsa

# Add public key to authorized_keys for your deploy user
cat /opt/kanakku/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

### 3. Test SSH Connection

Verify that GitHub Actions can connect to your server:

```bash
# Test from your local machine or another server
ssh -i /path/to/private/key deploy_user@your_server_ip "echo 'Connection successful'"
```

## Domain and SSL Configuration

### 1. DNS Configuration

Point your domain to your server:

```
A    yourdomain.com        192.168.1.100
A    api.yourdomain.com    192.168.1.100
A    monitor.yourdomain.com 192.168.1.100
```

### 2. SSL Certificate Setup

```bash
# Install SSL certificates using Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com -d monitor.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 3. Update Environment Configuration

Update the domain in your environment file:

```bash
sudo nano /opt/kanakku/.env
```

Change:
```env
FRONTEND_URL=https://yourdomain.com
```

## Deployment Process

### Automatic Deployment

The CI/CD pipeline automatically deploys when you push to the `main` branch:

1. **Test Phase**: Runs all backend and frontend tests
2. **Build Phase**: Builds the React frontend and prepares deployment artifacts
3. **Deploy Phase**: Deploys to your server via SSH
4. **Health Check**: Verifies that all services are running correctly

### Manual Deployment

You can also trigger deployment manually:

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Select "Deploy to Production" workflow
4. Click "Run workflow"
5. Optionally check "Force deployment" to skip test failures

### Deployment Steps

The deployment process:

1. **Backup**: Creates a timestamped backup of the current deployment
2. **Stop Services**: Gracefully stops the application services
3. **Update Code**: Copies new application files to the server
4. **Install Dependencies**: Updates Python packages and rebuilds virtual environment
5. **Database Migration**: Runs any pending database migrations
6. **Start Services**: Starts all application services
7. **Health Check**: Verifies deployment success

## Service Management

### Systemd Services

The application runs as systemd services:

- `kanakku`: Main Flask application
- `kanakku-worker`: Email automation worker
- `kanakku-scheduler`: Email automation scheduler
- `kanakku-admin-server`: Admin server for system management and log access

```bash
# Check service status
sudo systemctl status kanakku
sudo systemctl status kanakku-worker
sudo systemctl status kanakku-scheduler
sudo systemctl status kanakku-admin-server
sudo systemctl status nginx

# Start/stop services
sudo systemctl start kanakku
sudo systemctl stop kanakku
sudo systemctl restart kanakku

# View logs
sudo journalctl -u kanakku -f
sudo journalctl -u kanakku-worker -f
sudo journalctl -u kanakku-scheduler -f
sudo journalctl -u kanakku-admin-server -f
```

### Application Logs

Application logs are stored in multiple locations:

```bash
# Application logs
tail -f /opt/kanakku/logs/kanakku.log
tail -f /opt/kanakku/logs/error.log

# System logs
sudo journalctl -u kanakku -f
sudo journalctl -u nginx -f

# Health check logs
tail -f /var/log/kanakku/health-check.log
```

### Helper Scripts

Use the provided helper scripts for common tasks:

```bash
# Check application status
sudo /opt/kanakku/deploy-helper.sh status

# Create manual backup
sudo /opt/kanakku/deploy-helper.sh backup

# Restart all services
sudo /opt/kanakku/deploy-helper.sh restart

# View application logs
sudo /opt/kanakku/deploy-helper.sh logs

# Run health check
sudo /opt/kanakku/health-check.sh

# Admin server management
sudo /opt/kanakku/scripts/admin-server-helper.sh status
sudo /opt/kanakku/scripts/admin-server-helper.sh logs
```

### Admin Server Management

The Admin Server has its own dedicated helper script for management:

```bash
# Check Admin Server status
sudo /opt/kanakku/scripts/admin-server-helper.sh status

# Start/stop/restart Admin Server
sudo /opt/kanakku/scripts/admin-server-helper.sh start
sudo /opt/kanakku/scripts/admin-server-helper.sh stop
sudo /opt/kanakku/scripts/admin-server-helper.sh restart

# View Admin Server logs
sudo /opt/kanakku/scripts/admin-server-helper.sh logs

# Test Admin Server connection
sudo /opt/kanakku/scripts/admin-server-helper.sh test

# Deploy/update Admin Server
sudo /opt/kanakku/scripts/admin-server-helper.sh deploy
```

## Monitoring and Maintenance

### Health Monitoring

The system includes automated health checks:

- **Cron Job**: Runs health checks every 5 minutes
- **Service Monitoring**: Checks if all services are running
- **API Health**: Verifies backend API responses
- **Database Connectivity**: Tests PostgreSQL connection
- **Cache Connectivity**: Tests Redis connection

### Monitoring Dashboard Authentication

The monitoring dashboard at `https://monitor.yourdomain.com` requires HTTP Basic Authentication for security. Set up user credentials using the provided script:

```bash
# Navigate to the project directory
cd /opt/kanakku

# Run the htpasswd setup script
sudo ./scripts/create-htpasswd.sh

# Follow the prompts to create a username and password
# The script will create /etc/nginx/.htpasswd automatically

# Restart nginx to apply the authentication
sudo systemctl restart nginx
```

**Security Best Practices:**
- Use strong, unique passwords for monitoring access
- Limit monitoring access to authorized personnel only
- Consider implementing IP whitelisting for additional security
- Monitor nginx access logs for unauthorized access attempts
- Regularly update passwords and remove unused accounts

**Managing Users:**
```bash
# Add a new user
sudo htpasswd /etc/nginx/.htpasswd new_username

# Change existing user's password
sudo htpasswd /etc/nginx/.htpasswd existing_username

# Remove a user
sudo htpasswd -D /etc/nginx/.htpasswd username_to_remove

# List all users
sudo cut -d: -f1 /etc/nginx/.htpasswd
```

For detailed information about the htpasswd script and user management, see [`scripts/README.md`](../scripts/README.md).

### Log Rotation

Logs are automatically rotated:

- **Daily rotation** for application logs
- **52-day retention** (configurable)
- **Compression** of old logs
- **Automatic cleanup** of old backups (30+ days)

### Backup Management

Automated backups:

- **Deployment Backups**: Created before each deployment
- **Manual Backups**: Available via helper script
- **Automatic Cleanup**: Removes backups older than 30 days

### Security Features

- **Firewall**: UFW configured to allow only necessary ports
- **Fail2ban**: Protection against brute force attacks
- **SSL/TLS**: Automatic HTTPS redirection
- **Security Headers**: Comprehensive security headers in Nginx
- **Process Isolation**: Services run as dedicated user

## Troubleshooting

### Common Issues

#### Deployment Fails

1. Check GitHub Actions logs for specific error
2. Verify SSH connection: `ssh deploy_user@server_ip`
3. Check server disk space: `df -h`
4. Verify services are running: `sudo systemctl status kanakku`

#### Application Not Responding

1. Check service status: `sudo systemctl status kanakku`
2. View application logs: `tail -f /opt/kanakku/logs/kanakku.log`
3. Check database connection: `sudo -u kanakku psql -d kanakku -c "SELECT 1;"`
4. Verify Redis: `redis-cli ping`

#### SSL Certificate Issues

1. Check certificate status: `sudo certbot certificates`
2. Renew certificates: `sudo certbot renew`
3. Test Nginx configuration: `sudo nginx -t`
4. Reload Nginx: `sudo systemctl reload nginx`

#### Database Connection Issues

1. Check PostgreSQL status: `sudo systemctl status postgresql`
2. Verify database exists: `sudo -u postgres psql -l`
3. Test connection: `sudo -u kanakku psql -d kanakku`
4. Check environment variables: `sudo cat /opt/kanakku/.env`

### Recovery Procedures

#### Rollback Deployment

```bash
# List available backups
ls -la /opt/kanakku/backups/

# Restore from backup
sudo /opt/kanakku/deploy-helper.sh restore /opt/kanakku/backups/BACKUP_DIRECTORY
```

#### Emergency Recovery

```bash
# Stop all services
sudo systemctl stop kanakku kanakku-worker kanakku-scheduler kanakku-admin-server

# Restore from latest backup
LATEST_BACKUP=$(ls -t /opt/kanakku/backups/ | head -n1)
sudo cp -r "/opt/kanakku/backups/$LATEST_BACKUP"/* /opt/kanakku/
sudo chown -R kanakku:kanakku /opt/kanakku

# Start services
sudo systemctl start kanakku kanakku-worker kanakku-scheduler kanakku-admin-server
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
```

### Nginx Optimization

```nginx
# Add to nginx configuration for better performance
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Enable caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Application Scaling

For higher traffic, consider:

1. **Increase Gunicorn Workers**: Edit `kanakku.service` to add more workers
2. **Database Connection Pooling**: Configure PostgreSQL connection pooling
3. **Redis Optimization**: Tune Redis memory settings
4. **Load Balancing**: Add multiple application servers behind a load balancer

## Security Considerations

### Regular Maintenance

1. **System Updates**: `sudo apt update && sudo apt upgrade`
2. **Dependency Updates**: Monitor for security updates in Python packages
3. **SSL Certificate Renewal**: Automated via certbot
4. **Log Monitoring**: Regular review of application and security logs
5. **Backup Verification**: Periodic testing of backup restoration

### Security Hardening

1. **SSH Key Authentication**: Disable password authentication
2. **Firewall Rules**: Regularly review and update UFW rules
3. **Fail2ban Configuration**: Monitor and adjust fail2ban settings
4. **Application Security**: Regular security audits of the application code
5. **Database Security**: Regular review of database permissions and access

## Support and Maintenance

### Regular Tasks

- **Weekly**: Review application logs and performance metrics
- **Monthly**: Test backup restoration procedures
- **Quarterly**: Security audit and dependency updates
- **Annually**: SSL certificate renewal (if not automated)

### Monitoring Recommendations

Consider implementing additional monitoring:

- **Application Performance Monitoring** (APM)
- **Log aggregation** (ELK stack, Fluentd)
- **Metrics collection** (Prometheus, Grafana)
- **Uptime monitoring** (external service)
- **Security monitoring** (intrusion detection)

For additional support or questions about deployment, refer to the project documentation or create an issue in the GitHub repository. 