#!/bin/bash

set -e

# Print with colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running linting checks for Kanakku...${NC}"

# Check if frontend and backend directories exist
if [ ! -d "frontend" ]; then
  echo -e "${RED}Error: frontend directory not found${NC}"
  exit 1
fi

if [ ! -d "backend" ]; then
  echo -e "${RED}Error: backend directory not found${NC}"
  exit 1
fi

# Frontend linting
echo -e "\n${YELLOW}Running frontend linting...${NC}"
cd frontend
if [ -f "package.json" ]; then
  echo "Running ESLint..."
  npx eslint 'src/**/*.{js,jsx,ts,tsx}' --max-warnings=0 || { echo -e "${RED}Frontend linting failed${NC}"; exit 1; }
else
  echo -e "${RED}Error: package.json not found in frontend directory${NC}"
  exit 1
fi
cd ..

# Backend linting
echo -e "\n${YELLOW}Running backend linting...${NC}"
cd backend
if [ -f "requirements.txt" ]; then
  # Check if ruff is installed
  if ! pip list | grep -q ruff; then
    echo "Installing ruff..."
    pip install ruff
  fi
  
  # Check if black is installed
  if ! pip list | grep -q black; then
    echo "Installing black..."
    pip install black
  fi
  
  echo "Running Ruff linter..."
  ruff check . || { echo -e "${RED}Backend linting failed${NC}"; exit 1; }
  
  echo "Running Black formatter check..."
  black --check . || { echo -e "${RED}Black formatting check failed${NC}"; exit 1; }
  
  # Optional: Check type hints with mypy if available
  if command -v mypy >/dev/null 2>&1; then
    echo "Running mypy type checker..."
    # Install required type stubs
    echo "Installing required type stubs for mypy..."
    pip install types-requests types-Flask-Cors types-Flask-Migrate || true
    mypy . || { echo -e "${YELLOW}Mypy type checking found issues. Please check mypy.ini configuration.${NC}"; }
  elif pip list | grep -q mypy; then
    echo "Mypy found in pip but not in PATH. Installing mypy..."
    pip install mypy
    # Install required type stubs
    echo "Installing required type stubs for mypy..."
    pip install types-requests types-Flask-Cors types-Flask-Migrate || true
    echo "Running mypy type checker..."
    mypy . || { echo -e "${YELLOW}Mypy type checking found issues. Please check mypy.ini configuration.${NC}"; }
  else
    echo "Mypy not found, skipping type checking. Install mypy for static type checking."
  fi
else
  echo -e "${RED}Error: requirements.txt not found in backend directory${NC}"
  exit 1
fi
cd ..

echo -e "\n${GREEN}All linting checks passed successfully!${NC}" 