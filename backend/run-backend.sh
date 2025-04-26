#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the Flask application
flask run --host=0.0.0.0 --port 8000 --debug