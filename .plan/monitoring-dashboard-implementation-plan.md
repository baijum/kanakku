# Kanakku Monitoring Dashboard Implementation Plan

## Overview

This plan outlines the implementation of a web-based monitoring dashboard for Kanakku that extends the existing Admin MCP Server infrastructure. The dashboard will provide real-time monitoring of services, system metrics, and logs through a simple web interface deployed on the same production server.

## Project Goals

### Primary Objectives
- **Extend Existing Infrastructure**: Leverage the current Admin MCP Server capabilities
- **Simple Web Interface**: Provide visual monitoring for non-technical team members
- **Real-time Monitoring**: Display live service status, system metrics, and logs
- **Minimal Resource Impact**: Use existing server resources efficiently
- **Security First**: Maintain the same security standards as existing services

### Success Criteria
- Dashboard accessible via `monitor.example.com`
- Real-time service status for all Kanakku services
- System metrics visualization (CPU, memory, disk, uptime)
- Live log viewing capability
- Authentication and secure access
- Deployment completed within existing infrastructure

## Technical Architecture

### Current Infrastructure Analysis
```
Existing Setup:
- Main App: 127.0.0.1:8000 (Gunicorn)
- Frontend: Nginx serving React app
- API: api.example.com → proxy to :8000
- Admin MCP: SSH-based monitoring via Cursor
- Services: kanakku, kanakku-worker, kanakku-scheduler, nginx, postgresql, redis
```

### Proposed Architecture
```
Enhanced Setup:
- Main App: 127.0.0.1:8000 (existing)
- Frontend: Nginx serving React app (existing)
- API: api.example.com → proxy to :8000 (existing)
- Admin MCP: SSH-based monitoring (existing)
- NEW: Monitor Dashboard: 127.0.0.1:5001 → monitor.example.com
```

### Technology Stack
- **Backend**: Flask (lightweight web framework)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla or minimal framework)
- **Real-time Updates**: Server-Sent Events (SSE) or WebSockets
- **Authentication**: HTTP Basic Auth or integration with existing auth
- **Deployment**: Gunicorn + systemd service
- **Proxy**: Nginx reverse proxy

## Implementation Phases

### Phase 1: Core Dashboard Infrastructure (Week 1)

#### 1.1 Project Setup
**Deliverables:**
- Directory structure in `/opt/kanakku/adminserver/`
- Basic Flask application
- Development environment setup

**Tasks:**
- [ ] Create `web_dashboard.py` Flask application
- [ ] Set up templates and static directories
- [ ] Create basic HTML template structure
- [ ] Install Flask dependencies in existing venv
- [ ] Create development configuration

**Files to Create:**
```
adminserver/
├── web_dashboard.py           # Main Flask application
├── templates/
│   ├── base.html             # Base template
│   ├── dashboard.html        # Main dashboard
│   └── components/           # Reusable components
├── static/
│   ├── css/
│   │   └── dashboard.css     # Dashboard styling
│   ├── js/
│   │   └── dashboard.js      # Dashboard functionality
│   └── img/                  # Images and icons
└── config/
    └── dashboard_config.py   # Configuration settings
```

#### 1.2 Basic Service Monitoring
**Deliverables:**
- Service status API endpoint
- Real-time service status display
- Basic dashboard layout

**API Endpoints:**
- `GET /` - Dashboard home page
- `GET /api/services/status` - Service status JSON
- `GET /api/health` - Dashboard health check

**Tasks:**
- [ ] Implement service status checking using existing admin_server functions
- [ ] Create service status grid UI component
- [ ] Add real-time updates with JavaScript
- [ ] Style service status indicators

### Phase 2: System Metrics Integration (Week 2)

#### 2.1 System Metrics Collection
**Deliverables:**
- System metrics API endpoints
- Metrics visualization components
- Historical data collection (basic)

**API Endpoints:**
- `GET /api/system/metrics` - Current system metrics
- `GET /api/system/uptime` - System uptime information
- `GET /api/system/processes` - Process information

**Metrics to Display:**
- CPU usage and load average
- Memory usage (RAM and swap)
- Disk usage and I/O
- Network statistics
- System uptime
- Process count

**Tasks:**
- [ ] Implement metrics collection using existing remote command execution
- [ ] Create metrics parsing functions
- [ ] Design metrics dashboard layout
- [ ] Add real-time metrics updates
- [ ] Implement basic alerting for high resource usage

#### 2.2 Performance Visualization
**Deliverables:**
- Simple charts for metrics visualization
- Alert indicators for threshold breaches
- Responsive design for mobile access

**Tasks:**
- [ ] Integrate lightweight charting library (Chart.js or similar)
- [ ] Create CPU, memory, and disk usage charts
- [ ] Implement alert thresholds and visual indicators
- [ ] Add responsive CSS for mobile devices

### Phase 3: Log Management Interface (Week 3)

#### 3.1 Log Viewer Implementation
**Deliverables:**
- Log viewing interface
- Log search functionality
- Real-time log streaming

**API Endpoints:**
- `GET /api/logs/<log_key>` - Get recent log entries
- `GET /api/logs/<log_key>/search` - Search logs
- `GET /api/logs/stream/<log_key>` - Real-time log streaming

**Tasks:**
- [ ] Implement log reading using existing admin_server functions
- [ ] Create log viewer UI component
- [ ] Add log filtering and search capabilities
- [ ] Implement real-time log streaming
- [ ] Add log level highlighting and formatting

#### 3.2 Advanced Log Features
**Deliverables:**
- Log download functionality
- Log rotation status
- Error log aggregation

**Tasks:**
- [ ] Add log download endpoints
- [ ] Implement error log aggregation across services
- [ ] Create log rotation status monitoring
- [ ] Add log file size monitoring

### Phase 4: Security and Authentication (Week 4)

#### 4.1 Authentication Implementation
**Deliverables:**
- Secure authentication system
- User session management
- Access control

**Security Features:**
- HTTP Basic Authentication (initial)
- Session management
- CSRF protection
- Rate limiting

**Tasks:**
- [ ] Implement HTTP Basic Auth with nginx
- [ ] Create user management (if needed)
- [ ] Add CSRF protection to forms
- [ ] Implement rate limiting for API endpoints
- [ ] Add security headers

#### 4.2 Production Security Hardening
**Deliverables:**
- SSL/TLS configuration
- Security headers
- Access logging
- Intrusion detection integration

**Tasks:**
- [ ] Configure SSL certificates for monitor.example.com
- [ ] Implement security headers
- [ ] Add comprehensive access logging
- [ ] Integrate with existing fail2ban configuration

### Phase 5: Deployment and Production Setup (Week 5)

#### 5.1 Production Deployment
**Deliverables:**
- Systemd service configuration
- Nginx reverse proxy setup
- Production environment configuration

**Files to Create:**
- `kanakku-monitor.service` - Systemd service file
- Updated `nginx-kanakku.conf` - Nginx configuration
- Production environment variables

**Tasks:**
- [ ] Create systemd service file
- [ ] Update nginx configuration
- [ ] Configure DNS for monitor.example.com
- [ ] Set up SSL certificates
- [ ] Configure production environment variables

#### 5.2 Monitoring and Maintenance
**Deliverables:**
- Health check endpoints
- Monitoring integration
- Backup procedures
- Documentation

**Tasks:**
- [ ] Implement dashboard health checks
- [ ] Add monitoring to existing admin MCP server
- [ ] Create backup procedures for dashboard configuration
- [ ] Write operational documentation

## Detailed Implementation Specifications

### Flask Application Structure

```python
# web_dashboard.py - Main application structure
from flask import Flask, render_template, jsonify, request
import asyncio
from admin_server import (
    execute_remote_command,
    read_log_file,
    KANAKKU_SERVICES,
    LOG_PATHS
)

app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('DASHBOARD_SECRET_KEY'),
    WTF_CSRF_ENABLED=True,
    RATELIMIT_STORAGE_URL='redis://localhost:6379'
)

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/services/status')
def get_services_status():
    # Implementation using existing admin_server functions
    pass

@app.route('/api/system/metrics')
def get_system_metrics():
    # Implementation for system metrics
    pass

@app.route('/api/logs/<log_key>')
def get_logs(log_key):
    # Implementation for log retrieval
    pass
```

### Frontend Architecture

```html
<!-- dashboard.html - Main dashboard template -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kanakku Monitoring Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
</head>
<body>
    <header class="dashboard-header">
        <h1>Kanakku Monitoring Dashboard</h1>
        <div class="status-summary"></div>
    </header>
    
    <main class="dashboard-main">
        <section class="services-section">
            <h2>Service Status</h2>
            <div class="services-grid" id="services-grid">
                <!-- Service cards populated by JavaScript -->
            </div>
        </section>
        
        <section class="metrics-section">
            <h2>System Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card" id="cpu-metrics"></div>
                <div class="metric-card" id="memory-metrics"></div>
                <div class="metric-card" id="disk-metrics"></div>
                <div class="metric-card" id="uptime-metrics"></div>
            </div>
        </section>
        
        <section class="logs-section">
            <h2>Recent Logs</h2>
            <div class="log-viewer">
                <select id="log-selector">
                    <option value="kanakku_app">Application Logs</option>
                    <option value="kanakku_error">Error Logs</option>
                    <option value="nginx_access">Nginx Access</option>
                    <option value="nginx_error">Nginx Error</option>
                </select>
                <div class="log-content" id="log-content"></div>
            </div>
        </section>
    </main>
    
    <script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
</body>
</html>
```

### Nginx Configuration

```nginx
# Addition to nginx-kanakku.conf
server {
    listen 443 ssl http2;
    server_name monitor.example.com;

    # SSL configuration (reuse existing certificates)
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # SSL settings (same as existing)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Authentication
    auth_basic "Kanakku Monitoring";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=monitor:10m rate=10r/m;
    limit_req zone=monitor burst=20 nodelay;

    # Proxy to monitoring dashboard
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for real-time updates
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files caching
    location /static/ {
        expires 1d;
        add_header Cache-Control "public, no-transform";
    }
}
```

### Systemd Service Configuration

```ini
# kanakku-monitor.service
[Unit]
Description=Kanakku Monitoring Dashboard
After=network.target kanakku.service redis.service
Wants=kanakku.service

[Service]
Type=notify
User=kanakku
Group=kanakku
WorkingDirectory=/opt/kanakku/adminserver
Environment="PATH=/opt/kanakku/backend/venv/bin"
Environment="PYTHONPATH=/opt/kanakku:/opt/kanakku/backend:/opt/kanakku/adminserver"
EnvironmentFile=-/opt/kanakku/.env
EnvironmentFile=-/opt/kanakku/debug.env
ExecStart=/opt/kanakku/backend/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5001 --timeout 60 'web_dashboard:app'
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

# Security enhancements
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/kanakku/logs /var/log/kanakku
NoNewPrivileges=true
PrivateDevices=true
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Resource limits
LimitNOFILE=65536
MemoryMax=256M

[Install]
WantedBy=multi-user.target
```

## Security Considerations

### Authentication and Authorization
- **HTTP Basic Authentication**: Initial implementation using nginx auth_basic
- **Session Management**: Flask session handling with secure cookies
- **CSRF Protection**: Flask-WTF CSRF tokens for form submissions
- **Rate Limiting**: nginx rate limiting to prevent abuse

### Network Security
- **HTTPS Only**: All traffic encrypted with existing SSL certificates
- **Firewall Rules**: Restrict access to monitoring port (5001) to localhost only
- **Access Control**: Limit dashboard access to authorized personnel only

### Data Security
- **No Sensitive Data Storage**: Dashboard doesn't store sensitive information
- **Secure Communication**: All server communication via existing SSH infrastructure
- **Audit Logging**: Log all dashboard access and actions

## Resource Requirements

### Server Resources
- **Additional Memory**: ~100-200MB for dashboard process
- **CPU Usage**: Minimal (only during active monitoring)
- **Disk Space**: ~50MB for dashboard code and assets
- **Network**: Uses existing SSH connections, minimal additional bandwidth

### Dependencies
- **Python Packages**: Flask, Gunicorn (likely already installed)
- **System Requirements**: None (uses existing infrastructure)
- **External Services**: None (self-contained)

## Testing Strategy

### Development Testing
- **Unit Tests**: Test individual dashboard functions
- **Integration Tests**: Test with existing admin_server functions
- **Browser Testing**: Cross-browser compatibility testing
- **Mobile Testing**: Responsive design testing

### Production Testing
- **Load Testing**: Verify dashboard performance under load
- **Security Testing**: Penetration testing and vulnerability assessment
- **Failover Testing**: Test dashboard behavior during service outages
- **Backup Testing**: Verify backup and restore procedures

## Deployment Checklist

### Pre-Deployment
- [ ] Code review completed
- [ ] Security review completed
- [ ] Testing completed (unit, integration, security)
- [ ] Documentation updated
- [ ] Backup procedures verified

### Deployment Steps
1. [ ] Deploy dashboard code to `/opt/kanakku/adminserver/`
2. [ ] Install dependencies in existing virtual environment
3. [ ] Create systemd service file
4. [ ] Update nginx configuration
5. [ ] Configure DNS for monitor.example.com
6. [ ] Set up SSL certificates (if needed)
7. [ ] Create HTTP auth credentials
8. [ ] Start and enable monitoring service
9. [ ] Verify dashboard accessibility
10. [ ] Update monitoring documentation

### Post-Deployment
- [ ] Monitor dashboard performance
- [ ] Verify all features working correctly
- [ ] Update team documentation
- [ ] Schedule regular maintenance tasks

## Maintenance and Operations

### Regular Maintenance
- **Daily**: Check dashboard accessibility and basic functionality
- **Weekly**: Review dashboard logs for errors or security issues
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and update authentication credentials

### Monitoring the Monitor
- **Health Checks**: Implement dashboard health check endpoints
- **Log Monitoring**: Monitor dashboard logs for errors
- **Performance Monitoring**: Track dashboard response times
- **Security Monitoring**: Monitor for unauthorized access attempts

### Backup and Recovery
- **Configuration Backup**: Backup dashboard configuration files
- **Code Backup**: Dashboard code included in existing backup procedures
- **Recovery Procedures**: Document dashboard recovery procedures
- **Testing**: Regular testing of backup and recovery procedures

## Future Enhancements

### Phase 6: Advanced Features (Future)
- **Historical Data**: Store and display historical metrics
- **Advanced Alerting**: Email/SMS notifications for critical issues
- **Custom Dashboards**: User-configurable dashboard layouts
- **API Integration**: Integration with external monitoring tools
- **Mobile App**: Native mobile application for monitoring

### Potential Integrations
- **Slack/Discord**: Notifications to team chat channels
- **Email Alerts**: Critical issue notifications via email
- **SMS Alerts**: Emergency notifications via SMS
- **Webhook Support**: Integration with external systems

## Success Metrics

### Technical Metrics
- **Uptime**: Dashboard availability > 99.5%
- **Response Time**: Page load time < 2 seconds
- **Resource Usage**: Memory usage < 200MB
- **Error Rate**: Error rate < 1%

### User Metrics
- **Adoption**: Team members actively using dashboard
- **Feedback**: Positive feedback from team members
- **Efficiency**: Reduced time to identify and resolve issues
- **Accessibility**: Dashboard accessible from various devices

## Risk Assessment and Mitigation

### Technical Risks
- **Performance Impact**: Monitor server resources and optimize as needed
- **Security Vulnerabilities**: Regular security updates and monitoring
- **Service Dependencies**: Ensure dashboard doesn't affect main services
- **Data Accuracy**: Verify monitoring data accuracy

### Operational Risks
- **Team Training**: Ensure team members know how to use dashboard
- **Documentation**: Maintain up-to-date documentation
- **Backup Procedures**: Ensure dashboard included in backup procedures
- **Recovery Planning**: Plan for dashboard recovery scenarios

## Conclusion

This implementation plan provides a comprehensive roadmap for creating a monitoring dashboard that extends the existing Kanakku Admin MCP Server infrastructure. The phased approach ensures manageable development cycles while maintaining system stability and security.

The dashboard will provide significant value by:
- Making monitoring accessible to all team members
- Providing real-time visibility into system health
- Reducing time to identify and resolve issues
- Leveraging existing infrastructure investments

The plan prioritizes security, performance, and maintainability while keeping the implementation simple and focused on core monitoring needs. 