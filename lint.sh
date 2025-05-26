#!/bin/bash

set -e

# Print with colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running linting checks for Kanakku...${NC}"

# Check if required directories exist
if [ ! -d "frontend" ]; then
  echo -e "${RED}Error: frontend directory not found${NC}"
  exit 1
fi

if [ ! -d "backend" ]; then
  echo -e "${RED}Error: backend directory not found${NC}"
  exit 1
fi

if [ ! -d "banktransactions" ]; then
  echo -e "${RED}Error: banktransactions directory not found${NC}"
  exit 1
fi

if [ ! -d "shared" ]; then
  echo -e "${RED}Error: shared directory not found${NC}"
  exit 1
fi

if [ ! -d "mcp-server" ]; then
  echo -e "${RED}Error: mcp-server directory not found${NC}"
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

echo "Running Ruff linter on backend..."
ruff check backend/ || { echo -e "${RED}Backend linting failed${NC}"; exit 1; }

echo "Running Black formatter check on backend..."
black --check backend/ || { echo -e "${RED}Backend Black formatting check failed${NC}"; exit 1; }

# Banktransactions linting
echo -e "\n${YELLOW}Running banktransactions linting...${NC}"
echo "Running Ruff linter on banktransactions..."
ruff check banktransactions/ || { echo -e "${RED}Banktransactions linting failed${NC}"; exit 1; }

echo "Running Black formatter check on banktransactions..."
black --check banktransactions/ || { echo -e "${RED}Banktransactions Black formatting check failed${NC}"; exit 1; }

# Shared linting
echo -e "\n${YELLOW}Running shared linting...${NC}"
echo "Running Ruff linter on shared..."
ruff check shared/ || { echo -e "${RED}Shared linting failed${NC}"; exit 1; }

echo "Running Black formatter check on shared..."
black --check shared/ || { echo -e "${RED}Shared Black formatting check failed${NC}"; exit 1; }

# MCP Server linting
echo -e "\n${YELLOW}Running mcp-server linting...${NC}"
echo "Running Ruff linter on mcp-server..."
ruff check mcp-server/ || { echo -e "${RED}MCP Server linting failed${NC}"; exit 1; }

echo "Running Black formatter check on mcp-server..."
black --check mcp-server/ || { echo -e "${RED}MCP Server Black formatting check failed${NC}"; exit 1; }

echo -e "\n${GREEN}All linting checks passed successfully!${NC}"
