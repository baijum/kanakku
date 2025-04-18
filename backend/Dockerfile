FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install ledger (if needed for your deployment)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ledger \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory if it doesn't exist
RUN mkdir -p instance

# Run as non-root user
RUN groupadd -r kanakku && useradd -r -g kanakku kanakku
RUN chown -R kanakku:kanakku /app
USER kanakku

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:create_app()"] 