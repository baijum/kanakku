# Kanakku Email Automation - Deployment Documentation

This directory contains comprehensive deployment guides for the Kanakku email automation system. Choose the deployment method that best fits your infrastructure and requirements.

## Available Deployment Guides

### 1. [Linux Deployment Guide](linux-deployment-guide.md)
**Recommended for production environments**

A comprehensive manual deployment guide for Linux servers that provides:
- Complete control over the deployment environment
- Detailed security hardening steps
- Production-ready systemd service configurations
- Nginx reverse proxy setup with SSL
- Comprehensive monitoring and logging setup
- Database and Redis optimization
- Backup and recovery procedures

**Best for**: Production environments, organizations requiring full control over the deployment stack, environments with specific compliance requirements.

### 2. [Docker Deployment Guide](docker-deployment.md)
**Recommended for containerized environments**

A Docker-based deployment using Docker Compose that provides:
- Consistent deployment across environments
- Easy scaling and management
- Isolated service containers
- Simplified dependency management
- Quick setup and deployment
- Container orchestration with health checks

**Best for**: Development teams familiar with Docker, cloud-native deployments, environments requiring easy scaling, CI/CD pipelines.

### 3. [Deployment Checklist](deployment-checklist.md)
**Essential for all deployments**

A comprehensive checklist covering:
- Pre-deployment planning and requirements
- Step-by-step deployment verification
- Security hardening validation
- Performance optimization checks
- Post-deployment monitoring
- Rollback procedures

**Use this**: Regardless of your chosen deployment method to ensure nothing is missed.

## Quick Start Guide

### For Production Linux Deployment
1. Review the [Deployment Checklist](deployment-checklist.md)
2. Follow the [Linux Deployment Guide](linux-deployment-guide.md)
3. Use the checklist to verify each step

### For Docker Deployment
1. Review the [Deployment Checklist](deployment-checklist.md) (Docker-specific sections)
2. Follow the [Docker Deployment Guide](docker-deployment.md)
3. Verify deployment using the checklist

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or equivalent Linux distribution
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: Stable internet connection

### Recommended for Production
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed connection with low latency

## Key Components

The Kanakku email automation system consists of:

1. **Flask Backend API** - Main application server
2. **Email Automation Scheduler** - Schedules email processing jobs
3. **Email Automation Worker** - Processes emails and extracts transactions
4. **PostgreSQL Database** - Stores application data
5. **Redis Queue** - Manages background job processing
6. **Nginx** - Reverse proxy and static file server (Linux deployment)

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Flask         │    │   PostgreSQL    │
│   (Reverse      │────│   Backend       │────│   Database      │
│   Proxy)        │    │   API           │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis         │    │   Email         │
                       │   Queue         │────│   Automation    │
                       │                 │    │   Services      │
                       └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   Scheduler     │
                                              │   +             │
                                              │   Worker(s)     │
                                              └─────────────────┘
```

## Security Considerations

Both deployment methods include:
- SSL/TLS encryption with strong cipher suites
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Firewall configuration
- Secure secret management
- Database security hardening
- Regular security updates

## Monitoring and Maintenance

### Health Monitoring
- Service health checks
- Database connectivity monitoring
- Redis connectivity monitoring
- Queue processing monitoring
- Resource usage monitoring

### Logging
- Structured application logging
- Log rotation and retention
- Centralized log collection (optional)
- Security event logging

### Backup Strategy
- Automated daily database backups
- Application data backups
- Backup encryption and off-site storage
- Regular backup restoration testing

## Troubleshooting

Common issues and solutions are covered in each deployment guide:

1. **Service startup issues** - Check logs and dependencies
2. **Database connection problems** - Verify credentials and connectivity
3. **Redis connection issues** - Check Redis service status
4. **Email processing failures** - Verify queue status and worker logs
5. **SSL certificate problems** - Check certificate validity and configuration

## Support and Maintenance

### Regular Maintenance Tasks
- **Daily**: Monitor service status and logs
- **Weekly**: Review system resources and performance
- **Monthly**: Apply security updates and review configurations
- **Quarterly**: Test backup and recovery procedures

### Performance Optimization
- Database query optimization
- Redis memory management
- Worker scaling based on load
- Nginx caching configuration
- System resource tuning

## Migration and Updates

### Updating the Application
1. Backup current deployment
2. Pull latest code changes
3. Update dependencies
4. Run database migrations
5. Restart services
6. Verify deployment

### Scaling Considerations
- Horizontal scaling of worker processes
- Database read replicas for high load
- Load balancing for multiple backend instances
- Redis clustering for high availability

## Getting Help

If you encounter issues during deployment:

1. **Check the troubleshooting sections** in the relevant deployment guide
2. **Review the logs** for error messages and stack traces
3. **Verify the checklist** to ensure all steps were completed
4. **Check system resources** (CPU, memory, disk space)
5. **Consult the project documentation** for additional context

## Contributing

To improve these deployment guides:
1. Test the procedures in your environment
2. Document any issues or improvements
3. Submit feedback or pull requests
4. Share your deployment experiences

---

**Note**: Always test deployments in a staging environment before deploying to production. These guides are based on the successful resolution of macOS-specific issues and extensive testing of the email automation system. 