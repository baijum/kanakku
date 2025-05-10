#!/bin/bash

# Exit on any error
set -e

echo "Building Kanakku frontend for production..."

# Ensure we're in the frontend directory
cd "$(dirname "$0")"

# Install dependencies
npm ci --production 

# Set the API URL to just the base URL without /api/v1/
# The frontend code will handle adding /api/v1/ to endpoints as needed
echo "Setting API base URL to: https://api.ledger.muthukadan.net/"
REACT_APP_API_URL="https://api.ledger.muthukadan.net/" npm run build

echo "Frontend build complete. Output is in the ./build directory."
echo "To deploy, copy the contents of the build directory to your web server."

echo "Production build complete with API URL: https://api.ledger.muthukadan.net/" 
