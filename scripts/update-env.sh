#!/bin/bash
set -e

DEPLOY_PATH="/opt/kanakku"
SERVICE_USER="kanakku"
ENV_FILE="$DEPLOY_PATH/.env"

echo "Updating environment file with Google OAuth credentials..."

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Creating new .env file..."
  # Generate secure keys
  FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  CSRF_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

  # Create basic .env file
  sudo cat > "$ENV_FILE" << ENVEOF
# Kanakku Environment Configuration
FLASK_ENV=production
SECRET_KEY=$FLASK_SECRET
JWT_SECRET_KEY=$JWT_SECRET
CSRF_SECRET_KEY=$CSRF_SECRET

# Database Configuration (will be updated by admin)
DATABASE_URL=postgresql://kanakku:password@localhost:5432/kanakku

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Frontend URL
FRONTEND_URL=https://${DOMAIN:-localhost}

# Backend URL
BACKEND_URL=https://api.${DOMAIN:-localhost}

# API Configuration
API_RATE_LIMIT=1000 per hour
ENVEOF
fi

# Update or add Google OAuth credentials
if [ -n "$GOOGLE_CLIENT_ID" ] && [ -n "$GOOGLE_CLIENT_SECRET" ]; then
  echo "Adding Google OAuth credentials to .env file..."

  # Remove existing Google credentials and comments if they exist
  sudo sed -i '/^GOOGLE_CLIENT_ID=/d' "$ENV_FILE"
  sudo sed -i '/^GOOGLE_CLIENT_SECRET=/d' "$ENV_FILE"
  sudo sed -i '/^# Google OAuth Configuration$/d' "$ENV_FILE"

  # Add new Google credentials
  echo "" | sudo tee -a "$ENV_FILE" > /dev/null
  echo "# Google OAuth Configuration" | sudo tee -a "$ENV_FILE" > /dev/null
  echo "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" | sudo tee -a "$ENV_FILE" > /dev/null
  echo "GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET" | sudo tee -a "$ENV_FILE" > /dev/null

  echo "Google OAuth credentials updated successfully"
else
  echo "Warning: Google OAuth credentials not provided in environment variables"
fi

# Update domain if provided
if [ -n "$DOMAIN" ]; then
  echo "Updating domain to: $DOMAIN"

  # Update FRONTEND_URL if it exists, otherwise add it
  if grep -q "^FRONTEND_URL=" "$ENV_FILE"; then
    sudo sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN|" "$ENV_FILE"
  else
    echo "FRONTEND_URL=https://$DOMAIN" | sudo tee -a "$ENV_FILE" > /dev/null
  fi

  # Update BACKEND_URL if it exists, otherwise add it
  if grep -q "^BACKEND_URL=" "$ENV_FILE"; then
    sudo sed -i "s|BACKEND_URL=.*|BACKEND_URL=https://api.$DOMAIN|" "$ENV_FILE"
  else
    echo "BACKEND_URL=https://api.$DOMAIN" | sudo tee -a "$ENV_FILE" > /dev/null
  fi
fi

# Set proper permissions
sudo chown "$SERVICE_USER:$SERVICE_USER" "$ENV_FILE"
sudo chmod 600 "$ENV_FILE"

echo "Environment file updated successfully"
