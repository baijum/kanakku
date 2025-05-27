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
DOMAIN=${DOMAIN:-"kanakku.muthukadan.net"}
API_URL="https://api.${DOMAIN}/"
echo "Setting API base URL to: ${API_URL}"
REACT_APP_API_URL="${API_URL}" npm run build

echo "Frontend build complete. Output is in the ./build directory."
echo "To deploy, copy the contents of the build directory to your web server."

echo "Production build complete with API URL: ${API_URL}"
