#!/bin/bash

# Exit on any error
set -e

echo "Preparing Kanakku backend for production deployment..."

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install production dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Use production environment file
if [ -f ".env.production" ]; then
    echo "Using production environment variables..."
    cp .env.production .env
else
    echo "Warning: .env.production file not found. Using existing .env file."
fi

# Initialize database if it doesn't exist
if [ ! -f "instance/app.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Collect static files if applicable
# Uncomment if your framework needs this
# echo "Collecting static files..."
# flask static

echo "Backend preparation complete."
echo "To run in production, use a WSGI server like Gunicorn:"
echo "gunicorn 'app:create_app()' --bind 0.0.0.0:8000" 