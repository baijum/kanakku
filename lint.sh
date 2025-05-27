#!/bin/bash

set -e

# Print with colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running linting checks for Kanakku...${NC}"

# Check which directories exist and should be linted
LINT_FRONTEND=false
LINT_PYTHON=false

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  LINT_FRONTEND=true
fi

if [ -d "backend" ] || [ -d "banktransactions" ] || [ -d "shared" ] || [ -d "adminserver" ] || [ -d "scripts" ] || [ -d "tools" ]; then
  LINT_PYTHON=true
fi

if [ "$LINT_FRONTEND" = false ] && [ "$LINT_PYTHON" = false ]; then
  echo -e "${RED}Error: No lintable directories found${NC}"
  exit 1
fi

# Frontend linting
if [ "$LINT_FRONTEND" = true ]; then
  echo -e "\n${YELLOW}Running frontend linting...${NC}"
  cd frontend

  # Check if node_modules exists, if not try to install dependencies
  if [ ! -d "node_modules" ]; then
    echo "Node modules not found, checking if yarn is available..."
    if command -v yarn >/dev/null 2>&1; then
      echo "Installing frontend dependencies with yarn..."
      yarn install --frozen-lockfile || { echo -e "${RED}Failed to install frontend dependencies${NC}"; exit 1; }
    elif command -v npm >/dev/null 2>&1; then
      echo "Installing frontend dependencies with npm..."
      npm ci || { echo -e "${RED}Failed to install frontend dependencies${NC}"; exit 1; }
    else
      echo -e "${RED}Error: Neither yarn nor npm found${NC}"
      exit 1
    fi
  fi

  echo "Running ESLint..."
  npx eslint 'src/**/*.{js,jsx,ts,tsx}' --max-warnings=0 || { echo -e "${RED}Frontend linting failed${NC}"; exit 1; }
  cd ..
else
  echo -e "\n${YELLOW}Skipping frontend linting (no frontend directory or package.json found)${NC}"
fi

# Python linting
if [ "$LINT_PYTHON" = true ]; then
  echo -e "\n${YELLOW}Running Python linting...${NC}"
  # Check if ruff is installed
  if ! python -c "import ruff" 2>/dev/null; then
    echo "Installing ruff..."
    pip install ruff
  fi

  # Check if black is installed
  if ! python -c "import black" 2>/dev/null; then
    echo "Installing black..."
    pip install black
  fi

  # Backend linting
  if [ -d "backend" ]; then
    echo -e "\n${YELLOW}Running backend linting...${NC}"
    echo "Running Ruff linter on backend..."
    ruff check backend/ || { echo -e "${RED}Backend linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on backend..."
    black --check backend/ || { echo -e "${RED}Backend Black formatting check failed${NC}"; exit 1; }
  fi

  # Banktransactions linting
  if [ -d "banktransactions" ]; then
    echo -e "\n${YELLOW}Running banktransactions linting...${NC}"
    echo "Running Ruff linter on banktransactions..."
    ruff check banktransactions/ || { echo -e "${RED}Banktransactions linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on banktransactions..."
    black --check banktransactions/ || { echo -e "${RED}Banktransactions Black formatting check failed${NC}"; exit 1; }
  fi

  # Shared linting
  if [ -d "shared" ]; then
    echo -e "\n${YELLOW}Running shared linting...${NC}"
    echo "Running Ruff linter on shared..."
    ruff check shared/ || { echo -e "${RED}Shared linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on shared..."
    black --check shared/ || { echo -e "${RED}Shared Black formatting check failed${NC}"; exit 1; }
  fi

  # Admin Server linting
  if [ -d "adminserver" ]; then
    echo -e "\n${YELLOW}Running adminserver linting...${NC}"
    echo "Running Ruff linter on adminserver..."
    ruff check adminserver/ || { echo -e "${RED}Admin Server linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on adminserver..."
    black --check adminserver/ || { echo -e "${RED}Admin Server Black formatting check failed${NC}"; exit 1; }
  fi

  # Scripts linting
  if [ -d "scripts" ]; then
    echo -e "\n${YELLOW}Running scripts linting...${NC}"
    echo "Running Ruff linter on scripts..."
    ruff check scripts/ || { echo -e "${RED}Scripts linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on scripts..."
    black --check scripts/ || { echo -e "${RED}Scripts Black formatting check failed${NC}"; exit 1; }
  fi

  # Tools linting
  if [ -d "tools" ]; then
    echo -e "\n${YELLOW}Running tools linting...${NC}"
    echo "Running Ruff linter on tools..."
    ruff check tools/ || { echo -e "${RED}Tools linting failed${NC}"; exit 1; }

    echo "Running Black formatter check on tools..."
    black --check tools/ || { echo -e "${RED}Tools Black formatting check failed${NC}"; exit 1; }
  fi
else
  echo -e "\n${YELLOW}Skipping Python linting (no Python directories found)${NC}"
fi

echo -e "\n${GREEN}All linting checks passed successfully!${NC}"
