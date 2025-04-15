#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Set Flask environment variables
export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run the Flask application
flask run --host=0.0.0.0 --port 8000 --debug