# MCP Server Linux Service Deployment

## Problem
The MCP (Model Context Protocol) server was created as a standalone Python application but needed to be integrated into the production deployment pipeline as a proper Linux systemd service for reliable operation and automatic startup.

## Solution Implemented

### 1. Created Systemd Service File
**File**: `kanakku-mcp-server.service`

- Configured as a systemd service following the same pattern as other Kanakku services
- Runs as the `kanakku` user for security
- Includes comprehensive security hardening (PrivateTmp, ProtectSystem, etc.)
- Configured with automatic restart on failure
- Limited memory usage to 256M
- Allows network access for SSH connections to access logs

### 2. Updated GitHub Actions Deployment Pipeline
**File**: `.github/workflows/deploy.yml`

Added MCP server to all deployment stages:
- **Build Phase**: Include mcp-server directory in deployment archive
- **Deploy Phase**: Copy MCP server files and set up virtual environment
- **Configure Phase**: Install and enable kanakku-mcp-server systemd service
- **Start Phase**: Start MCP server service and verify status
- **Health Check**: Include MCP server in service status checks
- **Rollback**: Include MCP server in backup/restore procedures

### 3. Created MCP Server Deployment Script
**File**: `mcp-server/deploy-production.sh`

- Sets up Python virtual environment
- Installs dependencies from requirements.txt
- Creates logs directory
- Provides environment configuration template
- Runs connection tests to verify setup
- Provides clear instructions for systemd service setup

### 4. Created Management Helper Script
**File**: `scripts/mcp-server-helper.sh`

Provides convenient commands for MCP server management:
- `status` - Show service status
- `start/stop/restart` - Service control
- `logs` - View service logs in follow mode
- `test` - Run connection tests
- `deploy` - Deploy/update MCP server

### 5. Updated Deployment Documentation
**File**: `docs/deployment.md`

Added comprehensive documentation for:
- MCP server architecture overview
- SSH key configuration for log access
- Environment variable setup
- Service management commands
- Troubleshooting procedures
- Helper script usage

### 6. Updated Linting Pipeline
**File**: `lint.sh`

- Added MCP server directory to linting checks
- Ensures code quality standards are maintained
- Includes both Ruff and Black formatting checks

## Key Features

### Security
- Runs as dedicated `kanakku` user (not root)
- Comprehensive systemd security hardening
- SSH key-based authentication for log access
- Limited resource usage and network access

### Reliability
- Automatic service restart on failure
- Integrated with deployment pipeline
- Backup and rollback procedures
- Health monitoring and status checks

### Maintainability
- Follows existing service patterns
- Comprehensive documentation
- Helper scripts for common operations
- Integrated with existing deployment tools

## Deployment Process

1. **Automatic Deployment**: MCP server is automatically deployed with the main application via GitHub Actions
2. **Service Management**: Use systemctl commands or the helper script for service control
3. **Monitoring**: Service logs are available via journalctl and the helper script
4. **Updates**: MCP server is updated automatically with application deployments

## Testing

The implementation includes:
- Connection testing via `test-connection.py`
- Service status verification in deployment pipeline
- Health checks in GitHub Actions
- Manual testing capabilities via helper script

## Benefits

1. **Production Ready**: MCP server now runs as a proper system service
2. **Automated Deployment**: Fully integrated with CI/CD pipeline
3. **Reliable Operation**: Automatic restart and monitoring
4. **Easy Management**: Helper scripts and clear documentation
5. **Security Hardened**: Follows security best practices
6. **Maintainable**: Consistent with other Kanakku services

This implementation ensures the MCP server is production-ready and can be reliably deployed and managed alongside the main Kanakku application. 