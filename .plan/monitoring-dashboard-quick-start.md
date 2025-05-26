# Kanakku Monitoring Dashboard - Quick Start Guide

## Overview

This guide provides the essential steps to quickly implement a basic monitoring dashboard for Kanakku. This is a simplified version of the full implementation plan for rapid deployment.

## Prerequisites

- Kanakku production server with existing Admin MCP Server
- SSH access to production server
- Basic familiarity with Flask and systemd

## Quick Implementation (1-2 Hours)

### Step 1: Create Basic Flask Dashboard (30 minutes)

Create the main dashboard file:

```bash
# On production server
cd /opt/kanakku/adminserver
```

Create `web_dashboard.py`:

```python
#!/usr/bin/env python3
"""
Kanakku Quick Monitoring Dashboard
A minimal Flask web interface for monitoring Kanakku services
"""

import asyncio
import os
from datetime import datetime
from flask import Flask, render_template, jsonify

# Import from existing admin server
from admin_server import (
    execute_remote_command,
    read_log_file,
    KANAKKU_SERVICES,
    LOG_PATHS
)

app = Flask(__name__)
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'dev-key-change-in-production')

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'kanakku-monitor'
    })

@app.route('/api/services/status')
def services_status():
    """Get status of all Kanakku services"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    services = {}
    
    try:
        for service in KANAKKU_SERVICES:
            stdout, stderr, returncode = loop.run_until_complete(
                execute_remote_command(f"systemctl is-active {service}")
            )
            
            services[service] = {
                'name': service,
                'active': returncode == 0,
                'status': stdout.strip(),
                'last_checked': datetime.now().isoformat()
            }
    except Exception as e:
        app.logger.error(f"Error checking services: {e}")
    finally:
        loop.close()
    
    return jsonify(services)

@app.route('/api/system/basic')
def system_basic():
    """Get basic system information"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    info = {}
    
    try:
        # Uptime
        stdout, _, _ = loop.run_until_complete(
            execute_remote_command("uptime")
        )
        info['uptime'] = stdout.strip()
        
        # Memory
        stdout, _, _ = loop.run_until_complete(
            execute_remote_command("free -h | head -2")
        )
        info['memory'] = stdout.strip()
        
        # Disk
        stdout, _, _ = loop.run_until_complete(
            execute_remote_command("df -h / | tail -1")
        )
        info['disk'] = stdout.strip()
        
        # Load
        stdout, _, _ = loop.run_until_complete(
            execute_remote_command("cat /proc/loadavg")
        )
        info['load'] = stdout.strip()
        
    except Exception as e:
        app.logger.error(f"Error getting system info: {e}")
    finally:
        loop.close()
    
    return jsonify(info)

@app.route('/api/logs/<log_key>')
def get_logs(log_key):
    """Get recent log entries"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        logs = loop.run_until_complete(read_log_file(log_key, lines=50))
        return jsonify({
            'log_key': log_key,
            'logs': logs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Error reading logs: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
```

### Step 2: Create Templates Directory (15 minutes)

```bash
mkdir -p templates static/css static/js
```

Create `templates/dashboard.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kanakku Monitor</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .status { padding: 4px 12px; border-radius: 4px; color: white; font-size: 12px; }
        .active { background: #27ae60; }
        .inactive { background: #e74c3c; }
        .logs { font-family: monospace; background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto; }
        .refresh { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .last-update { color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Kanakku Monitoring Dashboard</h1>
        <p>Real-time monitoring for Kanakku services</p>
        <button class="refresh" onclick="refreshAll()">Refresh All</button>
        <span class="last-update" id="last-update"></span>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Service Status</h2>
            <div id="services-list">Loading...</div>
        </div>

        <div class="card">
            <h2>System Information</h2>
            <div id="system-info">Loading...</div>
        </div>

        <div class="card">
            <h2>Recent Application Logs</h2>
            <div id="app-logs" class="logs">Loading...</div>
        </div>

        <div class="card">
            <h2>Recent Error Logs</h2>
            <div id="error-logs" class="logs">Loading...</div>
        </div>
    </div>

    <script>
        async function fetchServices() {
            try {
                const response = await fetch('/api/services/status');
                const services = await response.json();
                
                const html = Object.values(services).map(service => `
                    <div class="service">
                        <span>${service.name}</span>
                        <span class="status ${service.active ? 'active' : 'inactive'}">
                            ${service.active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                `).join('');
                
                document.getElementById('services-list').innerHTML = html;
            } catch (error) {
                document.getElementById('services-list').innerHTML = 'Error loading services';
            }
        }

        async function fetchSystemInfo() {
            try {
                const response = await fetch('/api/system/basic');
                const info = await response.json();
                
                const html = `
                    <p><strong>Uptime:</strong> ${info.uptime || 'N/A'}</p>
                    <p><strong>Load:</strong> ${info.load || 'N/A'}</p>
                    <p><strong>Memory:</strong><br><pre>${info.memory || 'N/A'}</pre></p>
                    <p><strong>Disk:</strong><br><pre>${info.disk || 'N/A'}</pre></p>
                `;
                
                document.getElementById('system-info').innerHTML = html;
            } catch (error) {
                document.getElementById('system-info').innerHTML = 'Error loading system info';
            }
        }

        async function fetchLogs(logKey, elementId) {
            try {
                const response = await fetch(`/api/logs/${logKey}`);
                const data = await response.json();
                
                const logs = data.logs || 'No logs available';
                document.getElementById(elementId).textContent = logs;
            } catch (error) {
                document.getElementById(elementId).textContent = 'Error loading logs';
            }
        }

        function refreshAll() {
            fetchServices();
            fetchSystemInfo();
            fetchLogs('kanakku_app', 'app-logs');
            fetchLogs('kanakku_error', 'error-logs');
            document.getElementById('last-update').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }

        // Initial load
        refreshAll();

        // Auto-refresh every 30 seconds
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>
```

### Step 3: Create Systemd Service (10 minutes)

Create `kanakku-monitor.service`:

```ini
[Unit]
Description=Kanakku Monitoring Dashboard
After=network.target kanakku.service
Wants=kanakku.service

[Service]
Type=simple
User=kanakku
Group=kanakku
WorkingDirectory=/opt/kanakku/adminserver
Environment="PATH=/opt/kanakku/backend/venv/bin"
Environment="PYTHONPATH=/opt/kanakku:/opt/kanakku/backend:/opt/kanakku/adminserver"
EnvironmentFile=-/opt/kanakku/.env
ExecStart=/opt/kanakku/backend/venv/bin/python web_dashboard.py
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

# Basic security
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Install and start the service:

```bash
sudo cp kanakku-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kanakku-monitor
sudo systemctl start kanakku-monitor
sudo systemctl status kanakku-monitor
```

### Step 4: Configure Nginx (15 minutes)

Add to your `nginx-kanakku.conf`:

```nginx
# Quick monitoring dashboard (add this server block)
server {
    listen 8080;
    server_name _;

    # Basic auth (optional for quick setup)
    # auth_basic "Kanakku Monitor";
    # auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test and reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Test the Dashboard (10 minutes)

1. **Check service status:**
   ```bash
   sudo systemctl status kanakku-monitor
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u kanakku-monitor -f
   ```

3. **Access dashboard:**
   - Open browser to `http://your-server-ip:8080`
   - You should see the monitoring dashboard

4. **Test API endpoints:**
   ```bash
   curl http://localhost:5001/api/health
   curl http://localhost:5001/api/services/status
   ```

## Quick Security Setup (Optional - 10 minutes)

### Add Basic Authentication

```bash
# Install apache2-utils if not already installed
sudo apt-get install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Uncomment auth_basic lines in nginx config
sudo nano /etc/nginx/sites-available/kanakku
# Uncomment the auth_basic lines

# Reload nginx
sudo systemctl reload nginx
```

## Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   sudo journalctl -u kanakku-monitor -n 50
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R kanakku:kanakku /opt/kanakku/adminserver
   ```

3. **Python import errors:**
   ```bash
   # Check Python path
   cd /opt/kanakku/adminserver
   /opt/kanakku/backend/venv/bin/python -c "import admin_server; print('OK')"
   ```

4. **Nginx errors:**
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

### Verification Commands

```bash
# Check all services
sudo systemctl status kanakku kanakku-worker kanakku-scheduler kanakku-monitor

# Check ports
sudo netstat -tlnp | grep -E ':(5001|8080)'

# Test dashboard locally
curl -s http://localhost:5001/api/health | jq .
```

## Next Steps

Once the basic dashboard is working:

1. **Add HTTPS:** Configure SSL certificates for production
2. **Enhance Security:** Implement proper authentication
3. **Add Features:** Implement the full plan features
4. **Monitor Performance:** Track dashboard resource usage
5. **Backup Configuration:** Include dashboard in backup procedures

## Production Considerations

- **Change default secret key** in production
- **Set up proper SSL/TLS** for external access
- **Implement rate limiting** to prevent abuse
- **Monitor dashboard performance** and resource usage
- **Set up log rotation** for dashboard logs

This quick start gets you a functional monitoring dashboard in under 2 hours. For production use, follow the full implementation plan for enhanced security, features, and reliability. 