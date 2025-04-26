#!/bin/bash

# Exit on any error
set -e

echo "Building Kanakku frontend for production..."

# Install dependencies
npm ci --production 

# Build the production bundle
REACT_APP_API_URL="https://api.ledger.muthukadan.net/" npm run build

echo "Frontend build complete. Output is in the ./build directory."
echo "To deploy, copy the contents of the build directory to your web server." 
