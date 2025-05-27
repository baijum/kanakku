#!/bin/bash

# Script to create .htpasswd file for Kanakku monitoring dashboard
# This file is used by nginx for basic authentication
#
# Usage: sudo ./scripts/create-htpasswd.sh
#
# This script:
# 1. Checks for root privileges (required for /etc/nginx/ access)
# 2. Installs htpasswd utility if not present (apache2-utils/httpd-tools)
# 3. Prompts for username and password
# 4. Creates /etc/nginx/.htpasswd with bcrypt-hashed credentials
# 5. Sets proper file permissions (644, root:root)
#
# The generated file is used by nginx configuration:
#   auth_basic "Kanakku Monitoring";
#   auth_basic_user_file /etc/nginx/.htpasswd;
#
# Author: Kanakku Development Team
# Documentation: See scripts/README.md

set -e

HTPASSWD_FILE="/etc/nginx/.htpasswd"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Kanakku Monitoring Authentication Setup ==="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Check if htpasswd utility is available
if ! command -v htpasswd &> /dev/null; then
    echo "htpasswd utility not found. Installing apache2-utils..."

    # Detect package manager and install
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y apache2-utils
    elif command -v yum &> /dev/null; then
        yum install -y httpd-tools
    elif command -v dnf &> /dev/null; then
        dnf install -y httpd-tools
    else
        echo "Error: Could not detect package manager. Please install apache2-utils/httpd-tools manually."
        exit 1
    fi
fi

# Get username
read -p "Enter username for monitoring dashboard: " username
if [[ -z "$username" ]]; then
    echo "Error: Username cannot be empty"
    exit 1
fi

# Create the htpasswd file
echo "Creating .htpasswd file at $HTPASSWD_FILE"

# Create directory if it doesn't exist
mkdir -p "$(dirname "$HTPASSWD_FILE")"

# Create or update the htpasswd file
htpasswd -c "$HTPASSWD_FILE" "$username"

# Set proper permissions
chmod 644 "$HTPASSWD_FILE"
chown root:root "$HTPASSWD_FILE"

echo
echo "✅ .htpasswd file created successfully!"
echo "📁 Location: $HTPASSWD_FILE"
echo "👤 Username: $username"
echo
echo "You can now access the monitoring dashboard at https://monitor.{{DOMAIN}}"
echo "Use the username and password you just created."
echo
echo "To add more users later, run:"
echo "  htpasswd $HTPASSWD_FILE <new_username>"
echo
echo "To change a user's password, run:"
echo "  htpasswd $HTPASSWD_FILE <existing_username>"
