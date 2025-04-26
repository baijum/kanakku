# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Start development server: `npm start`
- Build for production: `npm run build`
- Run all tests: `npm test`
- Run a single test: `npm test -- --testMatch="**/fileName.test.jsx"`
- Eject from Create React App: `npm run eject`

## Code Style
- React functional components with hooks
- JSX files use .jsx extension
- Standard eslint config (extends react-app, react-app/jest)
- Material-UI (MUI) for UI components
- Use axios for API calls, via the configured axiosInstance
- Prefer async/await for asynchronous code
- Import order: React, MUI, other external libraries, internal components
- Exception handling with try/catch blocks with console.error for logging
- State management via React hooks (useState, useEffect)
- React Router v6 for routing with component-based routes

## Pre-Deployment Checklist

### Critical Issues to Address

1. **Environment Variables**
   - Update API URL in frontend/build-production.sh and docker-compose.yml
   - Replace example.com domains with actual domain in nginx-kanakku.conf
   - Replace placeholder Google credentials in backend/.env.production with actual values
   - Update mail configuration with actual SMTP credentials in backend/.env.production

2. **Security**
   - Remove the placeholder JWT and SECRET keys in .env.production and replace with newly generated strong keys
   - Remove exposed Google Client Secret in .env.production (should be replaced with actual secret before deployment)
   - Update SSL certificate paths in nginx configuration to point to actual certificates

3. **Database Configuration**
   - Change SQLite database to PostgreSQL for production in backend/.env.production if not using Docker
   - If using Docker, ensure PostgreSQL volume is properly configured for persistence

4. **Frontend Configuration**
   - Ensure axiosInstance.js is properly configured for production API URLs
   - Add .env file with REACT_APP_API_URL to frontend for local production builds

### Commands to Run Before Deployment

```bash
# Generate strong secret keys (store these securely)
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For JWT_SECRET_KEY

# Verify database migrations
cd backend
source venv/bin/activate
flask db upgrade

# Run frontend tests
cd frontend
npm run test:ci

# Build frontend for production 
REACT_APP_API_URL=https://your-actual-domain.com/api ./build-production.sh

# Configure Nginx
# 1. Update nginx-kanakku.conf with actual domain names
# 2. Update SSL certificate paths
```