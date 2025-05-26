# Service Management Features

The Kanakku Admin MCP Server includes comprehensive service management capabilities for safely managing Kanakku production services.

## New Tools Added

### 1. `manage_service`
Manage individual Kanakku services with fine-grained control.

**Parameters:**
- `operation` (required): Service operation to perform
  - `start` - Start a service
  - `stop` - Stop a service  
  - `restart` - Restart a service
  - `reload` - Reload service configuration
  - `daemon-reload` - Reload systemd daemon configuration
  - `status` - Get service status
  - `is-active` - Check if service is active
  - `is-enabled` - Check if service is enabled
- `service` (optional): Service name (not required for daemon-reload)
  - `kanakku` - Main application service
  - `kanakku-worker` - Background worker service
  - `kanakku-scheduler` - Scheduled task service
  - `kanakku-monitor` - Monitoring dashboard service
  - `nginx` - Web server
  - `postgresql` - Database service
  - `redis-server` - Cache/session store
- `timeout` (optional): Command timeout in seconds (default: 60, max: 120)

**Examples:**
```json
// Restart the main Kanakku service
{
  "operation": "restart",
  "service": "kanakku"
}

// Reload systemd daemon configuration
{
  "operation": "daemon-reload"
}

// Check if worker service is active
{
  "operation": "is-active", 
  "service": "kanakku-worker"
}

// Check monitoring dashboard status
{
  "operation": "status",
  "service": "kanakku-monitor"
}
```

### 2. `restart_all_kanakku_services`
Restart all Kanakku application services in the correct order with optional nginx restart.

**Parameters:**
- `include_nginx` (optional): Whether to also restart nginx (default: false)
- `daemon_reload` (optional): Whether to run daemon-reload first (default: true)

**Process:**
1. **Daemon Reload** (if enabled): Reloads systemd configuration
2. **Stop Services**: Stops services in reverse order (kanakku → kanakku-worker → kanakku-scheduler → kanakku-monitor → nginx)
3. **Start Services**: Starts services in correct order (kanakku-scheduler → kanakku-worker → kanakku → kanakku-monitor → nginx)
4. **Status Check**: Verifies all services are active

**Examples:**
```json
// Restart all Kanakku services only
{
  "include_nginx": false,
  "daemon_reload": true
}

// Restart everything including nginx
{
  "include_nginx": true,
  "daemon_reload": true
}
```

## Security Features

### Allowed Services
Only predefined Kanakku-related services are allowed:
- `kanakku` - Main application
- `kanakku-worker` - Background worker
- `kanakku-scheduler` - Scheduled tasks
- `kanakku-monitor` - Monitoring dashboard
- `nginx` - Web server
- `postgresql` - Database
- `redis-server` - Cache/session store

### Allowed Operations
Service operations are restricted to safe management commands:
- `start`, `stop`, `restart`, `reload` - Service lifecycle
- `daemon-reload` - Systemd configuration reload
- `status`, `is-active`, `is-enabled` - Status queries

### Safety Checks
- **Operation Validation**: Only allowed operations are permitted
- **Service Validation**: Only whitelisted services can be managed
- **Timeout Protection**: Commands have configurable timeouts (10-120 seconds)
- **Error Handling**: Comprehensive error reporting and safety notes
- **Audit Trail**: All operations are logged with safety status

## Usage Examples

### Common Deployment Workflow
1. **Deploy new code** (outside MCP server)
2. **Reload systemd configuration**:
   ```json
   {"operation": "daemon-reload"}
   ```
3. **Restart all services**:
   ```json
   {"include_nginx": false, "daemon_reload": false}
   ```
4. **Verify services are running**:
   ```json
   {"operation": "status", "service": "kanakku"}
   ```

### Monitoring Dashboard Management
1. **Check monitoring dashboard status**:
   ```json
   {"operation": "status", "service": "kanakku-monitor"}
   ```
2. **Restart monitoring dashboard**:
   ```json
   {"operation": "restart", "service": "kanakku-monitor"}
   ```
3. **Verify it's active**:
   ```json
   {"operation": "is-active", "service": "kanakku-monitor"}
   ```

### Troubleshooting Workflow
1. **Check service status**:
   ```json
   {"operation": "status", "service": "kanakku-worker"}
   ```
2. **Restart problematic service**:
   ```json
   {"operation": "restart", "service": "kanakku-worker"}
   ```
3. **Verify it's active**:
   ```json
   {"operation": "is-active", "service": "kanakku-worker"}
   ```

### Configuration Changes
1. **Reload systemd daemon** (after service file changes):
   ```json
   {"operation": "daemon-reload"}
   ```
2. **Reload service configuration** (for services that support it):
   ```json
   {"operation": "reload", "service": "nginx"}
   ```

## Output Format

All service management operations return structured output:

```
=== SERVICE MANAGEMENT ===
Operation: restart
Service: kanakku-monitor
Safety Check: 🔧 SERVICE: RESTART kanakku-monitor (SUCCESS)
Exit Code: 0

--- STDOUT ---
[Service output here]

--- STDERR ---
[Any errors here]
```

For the `restart_all_kanakku_services` tool, output includes step-by-step progress:

```
=== RESTART ALL KANAKKU SERVICES ===

Step 1: Reloading systemd daemon...
Result: 🔄 DAEMON-RELOAD: Reloading systemd configuration (SUCCESS)

Step 2: Stopping services...
  nginx: 🔧 SERVICE: STOP nginx (SUCCESS)
  kanakku: 🔧 SERVICE: STOP kanakku (SUCCESS)
  kanakku-worker: 🔧 SERVICE: STOP kanakku-worker (SUCCESS)
  kanakku-scheduler: 🔧 SERVICE: STOP kanakku-scheduler (SUCCESS)
  kanakku-monitor: 🔧 SERVICE: STOP kanakku-monitor (SUCCESS)

Step 3: Starting services...
  kanakku: 🔧 SERVICE: START kanakku (SUCCESS)
  kanakku-worker: 🔧 SERVICE: START kanakku-worker (SUCCESS)
  kanakku-scheduler: 🔧 SERVICE: START kanakku-scheduler (SUCCESS)
  kanakku-monitor: 🔧 SERVICE: START kanakku-monitor (SUCCESS)
  nginx: 🔧 SERVICE: START nginx (SUCCESS)

Step 4: Final service status...
  kanakku: active
  kanakku-worker: active
  kanakku-scheduler: active
  kanakku-monitor: active
  nginx: active
```

## Error Handling

The service management system includes comprehensive error handling:

- **Blocked Operations**: Invalid operations are blocked with clear error messages
- **Service Validation**: Unknown services are rejected
- **Timeout Protection**: Long-running commands are automatically terminated
- **Graceful Failures**: Failed operations are reported with exit codes and error details
- **Safety Notes**: All operations include safety status indicators

## Integration with Existing Tools

The new service management tools complement existing MCP server capabilities:

- Use `get_service_status` to check current status before making changes
- Use `read_log` and `search_logs` to investigate issues before restarting services
- Use `tail_log` to monitor service logs during restart operations
- Use `get_system_info` to check system resources before performing operations

## Monitoring Dashboard Integration

The kanakku-monitor service provides a web-based monitoring dashboard with:

- **Real-time Service Monitoring**: View status of all Kanakku services
- **System Metrics**: CPU, memory, disk usage visualization
- **Log Access**: Browse and search application and system logs
- **Service Management**: Start/stop/restart services through web interface

**Access Information:**
- Development: `http://127.0.0.1:5001`
- Production: `https://monitor.your-domain.com` (with nginx configuration)

**Log Sources Available:**
- Application logs: kanakku, worker, scheduler
- System service logs: All Kanakku services via journalctl
- Monitoring dashboard logs: `systemd_kanakku_monitor`

This provides a complete toolkit for managing Kanakku production services safely and effectively. 