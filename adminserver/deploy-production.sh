#!/bin/bash

# Exit on any error
set -e

echo "Preparing Kanakku Admin Server for production deployment..."

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install production dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Set up environment variables template if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "Creating environment template..."
    cat > .env.example << 'EOF'
# Admin Server Configuration
KANAKKU_DEPLOY_HOST=your-production-server-ip
KANAKKU_DEPLOY_USER=root
KANAKKU_SSH_KEY_PATH=/opt/kanakku/.ssh/id_rsa
KANAKKU_SSH_PORT=22

# Optional: Logging configuration
MCP_LOG_LEVEL=INFO
MCP_LOG_FILE=/opt/kanakku/adminserver/logs/admin-server.log
EOF
fi

# Test the server configuration (if environment is set up)
if [ -f ".env" ]; then
    echo "Testing Admin server configuration..."
    source .env
    if [ -n "$KANAKKU_DEPLOY_HOST" ]; then
        echo "Running connection test..."
        python test-connection.py || echo "Warning: Connection test failed. Please verify configuration."
    else
        echo "Warning: KANAKKU_DEPLOY_HOST not set. Skipping connection test."
    fi
else
    echo "Warning: .env file not found. Please configure environment variables."
    echo "Copy .env.example to .env and update with your server details."
fi

echo "Admin Server preparation complete."
echo ""
echo "To deploy as a systemd service:"
echo "1. Copy files to /opt/kanakku/adminserver/"
echo "2. Copy ../kanakku-admin-server.service to /etc/systemd/system/"
echo "3. Run: sudo systemctl daemon-reload"
echo "4. Run: sudo systemctl enable kanakku-admin-server"
echo "5. Run: sudo systemctl start kanakku-admin-server"
echo ""
echo "To check status: sudo systemctl status kanakku-admin-server"
echo "To view logs: sudo journalctl -u kanakku-admin-server -f"
