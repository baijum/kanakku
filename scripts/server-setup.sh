#!/bin/bash

# Kanakku Server Setup Script for Debian Linux
# This script prepares a Debian server for hosting the Kanakku application
# Run with: sudo bash server-setup.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
KANAKKU_USER="kanakku"
KANAKKU_HOME="/opt/kanakku"
POSTGRES_VERSION="15"
REDIS_VERSION="7"
NGINX_VERSION="latest"
PYTHON_VERSION="3.11"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

log "Starting Kanakku server setup on Debian Linux..."

# Update system packages
log "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
log "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    libpq-dev \
    pkg-config \
    supervisor \
    ufw \
    fail2ban \
    logrotate

# Install Python 3.11 if not available
log "Setting up Python ${PYTHON_VERSION}..."
if ! python3.11 --version &> /dev/null; then
    # Python 3.11 is available in Debian 12 repositories
    apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Create kanakku user
log "Creating kanakku user..."
if ! id "$KANAKKU_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash -d "$KANAKKU_HOME" "$KANAKKU_USER"
    log "Created user: $KANAKKU_USER"
else
    log "User $KANAKKU_USER already exists"
fi

# Create necessary directories
log "Creating application directories..."
mkdir -p "$KANAKKU_HOME"/{logs,backups,config}
mkdir -p /var/www/kanakku
mkdir -p /var/log/kanakku

# Set permissions
chown -R "$KANAKKU_USER:$KANAKKU_USER" "$KANAKKU_HOME"
chown -R www-data:www-data /var/www/kanakku
chown -R "$KANAKKU_USER:$KANAKKU_USER" /var/log/kanakku

# Install PostgreSQL
log "Installing PostgreSQL ${POSTGRES_VERSION}..."
if ! command -v psql &> /dev/null; then
    # Clean up any existing PostgreSQL repository configurations
    rm -f /etc/apt/sources.list.d/pgdg.list

    # Fix /tmp permissions if needed
    chmod 1777 /tmp

    # Create keyrings directory if it doesn't exist
    mkdir -p /usr/share/keyrings

    # Add PostgreSQL official repository using modern GPG key management
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

    # Clean apt cache and update with error handling
    apt clean
    rm -rf /var/lib/apt/lists/*

    # Update package lists
    if ! apt update; then
        warn "apt update failed, trying to install PostgreSQL from default repositories"
        apt install -y postgresql postgresql-client postgresql-contrib
    else
        apt install -y postgresql-${POSTGRES_VERSION} postgresql-client-${POSTGRES_VERSION} postgresql-contrib-${POSTGRES_VERSION}
    fi

    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql

    log "PostgreSQL installed and started"
else
    log "PostgreSQL already installed"
fi

# Configure PostgreSQL
log "Configuring PostgreSQL..."
sudo -u postgres psql -c "SELECT version();" || error "PostgreSQL is not running properly"

# Create database and user for Kanakku
read -p "Enter PostgreSQL password for kanakku user: " -s POSTGRES_PASSWORD
echo

sudo -u postgres psql << EOF
-- Create kanakku database user
CREATE USER kanakku WITH PASSWORD '$POSTGRES_PASSWORD';

-- Create kanakku database
CREATE DATABASE kanakku OWNER kanakku;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kanakku TO kanakku;

-- Create test database for CI/CD
CREATE DATABASE kanakku_test OWNER kanakku;
GRANT ALL PRIVILEGES ON DATABASE kanakku_test TO kanakku;

\q
EOF

log "PostgreSQL database and user created"

# Install Redis
log "Installing Redis ${REDIS_VERSION}..."
if ! command -v redis-server &> /dev/null; then
    apt install -y redis-server

    # Configure Redis
    sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

    # Start and enable Redis
    systemctl start redis-server
    systemctl enable redis-server

    log "Redis installed and configured"
else
    log "Redis already installed"
fi

# Test Redis
redis-cli ping || error "Redis is not running properly"

# Install Nginx
log "Installing Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install -y nginx

    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx

    log "Nginx installed and started"
else
    log "Nginx already installed"
fi

# Configure firewall
log "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80/tcp
ufw allow 443/tcp

# Configure fail2ban
log "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

systemctl restart fail2ban
systemctl enable fail2ban

# Set up log rotation
log "Configuring log rotation..."
cat > /etc/logrotate.d/kanakku << EOF
/var/log/kanakku/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 kanakku kanakku
    postrotate
        systemctl reload kanakku || true
        systemctl reload kanakku-worker || true
        systemctl reload kanakku-scheduler || true
    endscript
}

/opt/kanakku/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 kanakku kanakku
    postrotate
        systemctl reload kanakku || true
        systemctl reload kanakku-worker || true
        systemctl reload kanakku-scheduler || true
    endscript
}
EOF

# Install SSL certificate tools (Let's Encrypt)
log "Installing Certbot for SSL certificates..."
apt install -y certbot python3-certbot-nginx

# Create environment file template
log "Creating environment file template..."
cat > "$KANAKKU_HOME/.env.template" << EOF
# Kanakku Environment Configuration
# Copy this file to .env and fill in your values

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://kanakku:$POSTGRES_PASSWORD@localhost:5432/kanakku

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Frontend URL (update with your domain)
FRONTEND_URL=https://yourdomain.com

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# API Configuration
API_RATE_LIMIT=1000 per hour

# Security
CSRF_SECRET_KEY=your-csrf-secret-key-here
EOF

chown "$KANAKKU_USER:$KANAKKU_USER" "$KANAKKU_HOME/.env.template"

# Create deployment script
log "Creating deployment helper script..."
cat > "$KANAKKU_HOME/deploy-helper.sh" << 'EOF'
#!/bin/bash
# Helper script for manual deployment tasks

set -e

KANAKKU_HOME="/opt/kanakku"
KANAKKU_USER="kanakku"

case "$1" in
    backup)
        echo "Creating backup..."
        BACKUP_DIR="$KANAKKU_HOME/backups/manual_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp -r "$KANAKKU_HOME"/{backend,banktransactions,shared} "$BACKUP_DIR/" 2>/dev/null || true
        echo "Backup created at: $BACKUP_DIR"
        ;;

    restore)
        if [ -z "$2" ]; then
            echo "Usage: $0 restore <backup_directory>"
            exit 1
        fi
        echo "Restoring from backup: $2"
        systemctl stop kanakku kanakku-worker kanakku-scheduler kanakku-monitor
        cp -r "$2"/* "$KANAKKU_HOME/"
        chown -R "$KANAKKU_USER:$KANAKKU_USER" "$KANAKKU_HOME"
        systemctl start kanakku kanakku-worker kanakku-scheduler kanakku-monitor
        echo "Restore completed"
        ;;

    logs)
        echo "Recent application logs:"
        tail -f "$KANAKKU_HOME/logs/kanakku.log"
        ;;

    status)
        echo "Service Status:"
        systemctl status kanakku --no-pager
        systemctl status kanakku-worker --no-pager
        systemctl status kanakku-scheduler --no-pager
        systemctl status kanakku-monitor --no-pager
        systemctl status nginx --no-pager
        systemctl status postgresql --no-pager
        systemctl status redis-server --no-pager
        ;;

    restart)
        echo "Restarting services..."
        systemctl restart kanakku kanakku-worker kanakku-scheduler kanakku-monitor nginx
        echo "Services restarted"
        ;;

    *)
        echo "Usage: $0 {backup|restore|logs|status|restart}"
        echo "  backup          - Create a manual backup"
        echo "  restore <dir>   - Restore from backup directory"
        echo "  logs            - Show application logs"
        echo "  status          - Show service status"
        echo "  restart         - Restart all services"
        exit 1
        ;;
esac
EOF

chmod +x "$KANAKKU_HOME/deploy-helper.sh"

# Create health check script
log "Creating health check script..."
cat > "$KANAKKU_HOME/health-check.sh" << 'EOF'
#!/bin/bash
# Health check script for Kanakku application

set -e

# Check if services are running
services=("kanakku" "kanakku-worker" "kanakku-scheduler" "kanakku-monitor" "nginx" "postgresql" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        exit 1
    fi
done

# Check if application responds
if curl -f -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✓ Backend API is responding"
else
    echo "✗ Backend API is not responding"
    exit 1
fi

# Check database connection
if sudo -u kanakku psql -d kanakku -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ Database connection is working"
else
    echo "✗ Database connection failed"
    exit 1
fi

# Check Redis connection
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis connection is working"
else
    echo "✗ Redis connection failed"
    exit 1
fi

echo "All health checks passed!"
EOF

chmod +x "$KANAKKU_HOME/health-check.sh"

# Set up monitoring with basic system stats
log "Setting up basic monitoring..."
cat > /etc/cron.d/kanakku-monitoring << EOF
# Kanakku application monitoring
*/5 * * * * root /opt/kanakku/health-check.sh >> /var/log/kanakku/health-check.log 2>&1
0 2 * * * root find /opt/kanakku/backups -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
EOF

# Create systemd service for automatic startup
log "Creating systemd services..."

# Note: The actual service files will be deployed by the CI/CD pipeline
# This just ensures the directory exists and sets up the environment

# Create systemd service directory if it doesn't exist
mkdir -p /etc/systemd/system

# Create placeholder for service files that will be deployed
log "Service files will be deployed by CI/CD pipeline:"
log "  - kanakku.service (Main application)"
log "  - kanakku-worker.service (Background worker)"
log "  - kanakku-scheduler.service (Scheduled tasks)"
log "  - kanakku-monitor.service (Monitoring dashboard)"

# Final setup steps
log "Performing final setup steps..."

# Generate secure keys for the environment file
FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
CSRF_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create the actual .env file with generated secrets
cat > "$KANAKKU_HOME/.env" << EOF
# Kanakku Environment Configuration
FLASK_ENV=production
SECRET_KEY=$FLASK_SECRET
JWT_SECRET_KEY=$JWT_SECRET
CSRF_SECRET_KEY=$CSRF_SECRET

# Database Configuration
DATABASE_URL=postgresql://kanakku:$POSTGRES_PASSWORD@localhost:5432/kanakku

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Frontend URL (update with your domain)
FRONTEND_URL=https://yourdomain.com

# Google OAuth Configuration (will be updated by CI/CD)
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# API Configuration
API_RATE_LIMIT=1000 per hour
EOF

chown "$KANAKKU_USER:$KANAKKU_USER" "$KANAKKU_HOME/.env"
chmod 600 "$KANAKKU_HOME/.env"

# Create SSH key for GitHub Actions (if not exists)
if [ ! -f "$KANAKKU_HOME/.ssh/id_rsa" ]; then
    log "Creating SSH key for deployment..."
    sudo -u "$KANAKKU_USER" mkdir -p "$KANAKKU_HOME/.ssh"
    sudo -u "$KANAKKU_USER" ssh-keygen -t rsa -b 4096 -f "$KANAKKU_HOME/.ssh/id_rsa" -N ""
    chmod 700 "$KANAKKU_HOME/.ssh"
    chmod 600 "$KANAKKU_HOME/.ssh/id_rsa"
    chmod 644 "$KANAKKU_HOME/.ssh/id_rsa.pub"
    chown -R "$KANAKKU_USER:$KANAKKU_USER" "$KANAKKU_HOME/.ssh"
fi

log "Server setup completed successfully!"
echo
echo "=============================================="
echo "IMPORTANT NEXT STEPS:"
echo "=============================================="
echo
echo "1. Update your domain in the environment file:"
echo "   sudo nano $KANAKKU_HOME/.env"
echo
echo "2. Configure your domain in the nginx config:"
echo "   The CI/CD pipeline will deploy the nginx config, but you may need to update the domain names"
echo
echo "3. Set up SSL certificates:"
echo "   sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com -d monitor.yourdomain.com"
echo
echo "4. Add the following secrets to your GitHub repository:"
echo "   - DEPLOY_HOST: $(hostname -I | awk '{print $1}')"
echo "   - DEPLOY_USER: root (or a user with sudo privileges)"
echo "   - DEPLOY_SSH_KEY: (copy the private key below)"
echo "   - GOOGLE_CLIENT_ID: (your Google OAuth client ID)"
echo "   - GOOGLE_CLIENT_SECRET: (your Google OAuth client secret)"
echo "   - DOMAIN: (your domain name, e.g., yourdomain.com)"
echo
echo "5. SSH Private Key for GitHub Actions:"
echo "   Copy this private key to your GitHub repository secrets as DEPLOY_SSH_KEY:"
echo "   ----------------------------------------"
cat "$KANAKKU_HOME/.ssh/id_rsa"
echo "   ----------------------------------------"
echo
echo "6. Add the public key to authorized_keys for the deploy user:"
echo "   cat $KANAKKU_HOME/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
echo
echo "7. Test the deployment by pushing to the main branch"
echo
echo "Server is ready for Kanakku deployment!"
echo "=============================================="
