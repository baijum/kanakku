# Production Deployment Checklist for Kanakku

This document provides a checklist to ensure Kanakku is properly deployed to production.

## Pre-Deployment

- [ ] All tests pass (backend and frontend)
- [ ] Linting passes with no errors
- [ ] Security audit completed
- [ ] Production environment variables set correctly
- [ ] Database backups in place (if upgrading an existing deployment)
- [ ] SSL certificates obtained and configured

## Backend Deployment

- [ ] Update `.env.production` with appropriate values:
  - [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
  - [ ] Configure database URL for production database
  - [ ] Set correct MAIL configuration values
  - [ ] Set correct Google OAuth credentials
  - [ ] Set proper API URL for frontend
  - [ ] Ensure FLASK_ENV is set to 'production'
  - [ ] Ensure FLASK_DEBUG is set to 0
- [ ] Run the deployment script:
  ```bash
  cd backend
  ./deploy-production.sh
  ```
- [ ] Configure a WSGI server (Gunicorn):
  ```bash
  gunicorn 'app:create_app()' --bind 0.0.0.0:8000
  ```
- [ ] Set up process monitoring (systemd, supervisor, etc.)
- [ ] Configure Nginx or another reverse proxy
- [ ] Set up proper log rotation

## Frontend Deployment

- [ ] Ensure environment variables are set correctly
  - [ ] REACT_APP_API_URL points to the correct production API endpoint
- [ ] Build the frontend:
  ```bash
  cd frontend
  ./build-production.sh
  ```
- [ ] Deploy the built files to the web server
- [ ] Configure web server (Nginx, Apache) to serve static files
- [ ] Set up proper caching headers
- [ ] Configure proper SSL termination

## Database

- [ ] Run database migrations
- [ ] Verify data integrity
- [ ] Set up automated backups
- [ ] Configure appropriate database user permissions
- [ ] Set up monitoring

## Security Checks

- [ ] Ensure all sensitive environment variables are properly set
- [ ] Verify SSL/TLS configuration
- [ ] Check for exposed API endpoints
- [ ] Ensure JWT secrets are strong and unique
- [ ] Check CORS settings are correctly configured
- [ ] Verify proper authentication is enforced on all protected routes
- [ ] Ensure error logging doesn't expose sensitive information

## Monitoring and Maintenance

- [ ] Set up application monitoring (Prometheus, Grafana, etc.)
- [ ] Configure server monitoring
- [ ] Set up alerting for critical errors
- [ ] Document backup and recovery procedures
- [ ] Establish regular update schedule

## Post-Deployment Verification

- [ ] Test authentication flow in production
- [ ] Test transaction creation and retrieval
- [ ] Verify report generation
- [ ] Test all major application features
- [ ] Monitor error logs for unexpected issues

## Notes for Specific Deployment Environments

### Cloud Provider Deployment

If deploying to a cloud provider:
- [ ] Configure scaling rules
- [ ] Set up load balancing if needed
- [ ] Configure proper network security groups
- [ ] Set up cloud-specific monitoring 