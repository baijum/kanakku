#!/bin/bash

# Kanakku Admin MCP Server Setup Script
# This script sets up the Admin server for accessing Kanakku production systems from Cursor

set -e

echo "Setting up Kanakku Admin MCP Server..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8+ is required. Found version $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make the server executable
chmod +x admin_server.py

# Check for SSH configuration
echo ""
echo "=== SSH Configuration Required ==="
echo "Please ensure you have the following environment variables set:"
echo ""
echo "1. KANAKKU_DEPLOY_HOST - Your production server IP/hostname"
echo "2. KANAKKU_DEPLOY_USER - SSH user (default: root)"
echo "3. KANAKKU_SSH_KEY_PATH - Path to SSH private key (default: ~/.ssh/kanakku_deploy)"
echo "4. KANAKKU_SSH_PORT - SSH port (default: 22)"
echo ""

# Check if SSH key exists
SSH_KEY_PATH="${KANAKKU_SSH_KEY_PATH:-~/.ssh/kanakku_deploy}"
SSH_KEY_PATH_EXPANDED=$(eval echo "$SSH_KEY_PATH")

if [ ! -f "$SSH_KEY_PATH_EXPANDED" ]; then
    echo "Warning: SSH key not found at $SSH_KEY_PATH_EXPANDED"
    echo ""
    echo "To generate an SSH key for deployment access:"
    echo "  ssh-keygen -t rsa -b 4096 -f $SSH_KEY_PATH_EXPANDED"
    echo "  ssh-copy-id -i $SSH_KEY_PATH_EXPANDED.pub user@your-server"
    echo ""
fi

# Test connection if host is set
if [ -n "$KANAKKU_DEPLOY_HOST" ]; then
    echo "Testing SSH connection to $KANAKKU_DEPLOY_HOST..."

    SSH_USER="${KANAKKU_DEPLOY_USER:-root}"
    SSH_PORT="${KANAKKU_SSH_PORT:-22}"

    if ssh -i "$SSH_KEY_PATH_EXPANDED" -p "$SSH_PORT" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SSH_USER@$KANAKKU_DEPLOY_HOST" "echo 'Connection successful'" 2>/dev/null; then
        echo "✅ SSH connection successful!"
    else
        echo "❌ SSH connection failed. Please check your configuration."
        echo ""
        echo "Debug steps:"
        echo "1. Verify server is accessible: ping $KANAKKU_DEPLOY_HOST"
        echo "2. Test SSH manually: ssh -i $SSH_KEY_PATH_EXPANDED -p $SSH_PORT $SSH_USER@$KANAKKU_DEPLOY_HOST"
        echo "3. Check firewall settings on the server"
        echo "4. Ensure SSH key is added to authorized_keys on the server"
    fi
else
    echo "KANAKKU_DEPLOY_HOST not set. Skipping connection test."
fi

echo ""
echo "=== Cursor Integration ==="
echo "To integrate with Cursor, add the following to your Cursor settings:"
echo ""
echo "1. Open Cursor Settings (Cmd/Ctrl + ,)"
echo "2. Search for 'MCP' or 'Model Context Protocol'"
echo "3. Add the configuration from cursor-mcp-config.json"
echo "4. Update the environment variables with your actual values"
echo ""

# Create example environment file
cat > .env.example << EOF
# Kanakku Production Server Configuration
KANAKKU_DEPLOY_HOST=your-production-server-ip
KANAKKU_DEPLOY_USER=root
KANAKKU_SSH_KEY_PATH=~/.ssh/kanakku_deploy
KANAKKU_SSH_PORT=22
EOF

echo "Example environment file created: .env.example"
echo ""
echo "=== Testing the Server ==="
echo "To test the Admin server manually:"
echo "  source venv/bin/activate"
echo "  export KANAKKU_DEPLOY_HOST=your-server-ip"
echo "  python admin_server.py"
echo ""
echo "Setup complete! 🎉"
