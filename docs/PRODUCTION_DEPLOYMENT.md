# Kanakku Production Deployment Guide

This guide provides step-by-step instructions for deploying Kanakku in production.

## Prerequisites

- Web server with Ubuntu/Debian
- Domain names configured (main domain and API subdomain)
- SSL certificates obtained (Let's Encrypt recommended)
- PostgreSQL installed (or Docker for containerized deployment)

## Deployment Options

### Option 1: Traditional Deployment

1. **Prepare the Server**

   ```bash
   # Install required packages
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx postgresql
   
   # Install Ledger (if needed)
   sudo apt install -y ledger
   
   # Create a non-root user for running the application
   sudo useradd -m -s /bin/bash kanakku
   ```

2. **Clone the Repository**

   ```bash
   sudo mkdir -p /opt/kanakku
   sudo chown kanakku:kanakku /opt/kanakku
   
   # Clone as the kanakku user
   sudo -u kanakku git clone https://github.com/yourusername/kanakku.git /opt/kanakku
   ```

3. **Generate Strong Secret Keys**

   ```bash
   # Generate secure keys
   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   
   echo "Generated SECRET_KEY: $SECRET_KEY"
   echo "Generated JWT_SECRET_KEY: $JWT_SECRET_KEY"
   ```

4. **Configure Backend**

   ```bash
   cd /opt/kanakku/backend
   
   # Edit .env.production with actual values
   sudo -u kanakku nano .env.production
   
   # Replace placeholder values with actual ones:
   # - SECRET_KEY and JWT_SECRET_KEY with generated values
   # - SQLALCHEMY_DATABASE_URI with PostgreSQL connection string
   # - Update Google OAuth credentials
   # - Update mail server settings
   # - Set REACT_APP_API_URL to your actual API URL
   ```

5. **Deploy Backend**

   ```bash
   # Run the deployment script as kanakku user
   sudo -u kanakku bash /opt/kanakku/backend/deploy-production.sh
   
   # Set up systemd service
   sudo cp /opt/kanakku/kanakku.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable kanakku
   sudo systemctl start kanakku
   ```

6. **Deploy Frontend**

   ```bash
   cd /opt/kanakku/frontend
   
   # Create production .env file
   sudo -u kanakku bash -c 'echo "REACT_APP_API_URL=https://api.yourdomain.com/api" > .env.production'
   
   # Build the frontend
   sudo -u kanakku bash ./build-production.sh
   
   # Create directory for frontend files
   sudo mkdir -p /var/www/kanakku/frontend
   sudo cp -r build/* /var/www/kanakku/frontend/
   sudo chown -R www-data:www-data /var/www/kanakku
   ```

7. **Configure Nginx**

   ```bash
   # Copy and edit the Nginx configuration
   sudo cp /opt/kanakku/nginx-kanakku.conf /etc/nginx/sites-available/kanakku
   sudo nano /etc/nginx/sites-available/kanakku
   
   # Update the following in the configuration:
   # - Replace example.com with your actual domain
   # - Update SSL certificate paths
   # - Ensure the correct root directory is set
   
   # Enable the site
   sudo ln -s /etc/nginx/sites-available/kanakku /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Option 2: Docker Deployment

1. **Prepare the Server**

   ```bash
   # Install Docker and Docker Compose
   sudo apt update
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install -y docker-ce docker-compose
   ```

2. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/kanakku.git
   cd kanakku
   ```

3. **Configure Environment**

   ```bash
   # Set up environment variables
   nano backend/.env.production
   
   # Update the following in .env.production:
   # - Generate and set strong SECRET_KEY and JWT_SECRET_KEY
   # - Update Google OAuth credentials
   # - Update mail server settings
   
   # Update docker-compose.yml
   nano docker-compose.yml
   
   # Update the following:
   # - Set REACT_APP_API_URL in the frontend service
   # - Ensure proper volume configuration
   ```

4. **SSL Certificates**

   ```bash
   # Create directory for SSL certificates
   mkdir -p ssl
   
   # Copy your SSL certificates
   cp /path/to/your/fullchain.pem ssl/
   cp /path/to/your/privkey.pem ssl/
   
   # Update nginx-kanakku.conf
   nano nginx-kanakku.conf
   
   # Update the following:
   # - Replace example.com with your domain
   # - Update SSL certificate paths
   ```

5. **Start the Containers**

   ```bash
   # Start all containers
   docker-compose up -d
   
   # Check if all containers are running
   docker-compose ps
   ```

## Post-Deployment Verification

1. **Check Backend Health**

   ```bash
   curl https://api.yourdomain.com/api/v1/health
   ```

2. **Access the Frontend**

   Open your browser and navigate to `https://yourdomain.com`

3. **Test Key Features**

   - Register a new account
   - Log in with the created account
   - Create a new transaction
   - Generate a report

## Monitoring Setup

1. **Set Up Log Rotation**

   ```bash
   sudo nano /etc/logrotate.d/kanakku
   
   # Add the following configuration
   /opt/kanakku/backend/logs/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 kanakku kanakku
       sharedscripts
       postrotate
           systemctl reload kanakku >/dev/null 2>&1 || true
       endscript
   }
   ```

2. **Set Up Database Backups**

   ```bash
   # Create backup script
   sudo nano /opt/kanakku/backup-db.sh
   
   # Add backup commands
   #!/bin/bash
   BACKUP_DIR=/opt/kanakku/backups
   DATE=$(date +%Y%m%d_%H%M%S)
   mkdir -p $BACKUP_DIR
   pg_dump -U postgres kanakku > $BACKUP_DIR/kanakku_$DATE.sql
   
   # Make it executable and add to crontab
   sudo chmod +x /opt/kanakku/backup-db.sh
   sudo -u kanakku crontab -e
   
   # Add the following line for daily backups at 2 AM
   0 2 * * * /opt/kanakku/backup-db.sh
   ```

## Security Considerations

1. **Set Up Firewall**

   ```bash
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw enable
   ```

2. **Regular Updates**

   ```bash
   # Create update script
   sudo nano /opt/kanakku/update.sh
   
   # Add update commands
   #!/bin/bash
   cd /opt/kanakku
   git pull
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   flask db upgrade
   sudo systemctl restart kanakku
   cd ../frontend
   npm ci
   npm run build
   sudo cp -r build/* /var/www/kanakku/frontend/
   
   # Make it executable
   sudo chmod +x /opt/kanakku/update.sh
   ```

## Troubleshooting

1. **Check Backend Logs**

   ```bash
   sudo journalctl -u kanakku -f
   ```

2. **Check Nginx Logs**

   ```bash
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Database Connection Issues**

   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Check connectivity
   sudo -u postgres psql -c '\l'
   ```