# Debug Logging Management

The Kanakku Admin Server now supports dynamic debug logging management for troubleshooting production issues. This feature allows you to temporarily enable detailed debug logging without modifying configuration files manually.

## Overview

Debug logging can be enabled/disabled for the following Kanakku services:
- `kanakku` - Main web application
- `kanakku-worker` - Email processing worker
- `kanakku-scheduler` - Email scheduling service

When enabled, debug logging provides:
- Detailed function entry/exit logs
- SQL query logging (optional)
- Request/response debugging
- Enhanced error context

## Usage

### Check Current Debug Status

```bash
# Via admin server tools
check_debug_status
```

This will show whether debug logging is currently enabled and display the current configuration.

### Enable Debug Logging

```bash
# Enable debug logging for all Kanakku services
toggle_debug_logging --enable true

# Enable debug logging for specific services only
toggle_debug_logging --enable true --services kanakku,kanakku-worker

# Enable with custom timeout (useful for slower systems)
toggle_debug_logging --enable true --timeout 180
```

### Disable Debug Logging

```bash
# Disable debug logging for all services
toggle_debug_logging --enable false

# Disable for specific services
toggle_debug_logging --enable false --services kanakku
```

## How It Works

### Environment Configuration

The system uses a `/opt/kanakku/debug.env` file to control debug settings:

```bash
# Contents of debug.env when enabled
LOG_LEVEL=DEBUG
FLASK_DEBUG=1
SQL_ECHO=false
```

### Service Integration

All Kanakku systemd services are configured to read from:
1. `/opt/kanakku/.env` - Main configuration
2. `/opt/kanakku/debug.env` - Debug overrides (optional)

When debug logging is enabled:
1. The `debug.env` file is created with debug settings
2. Systemd daemon is reloaded
3. Affected services are restarted to pick up new environment
4. Service status is verified

### Logging Levels

The system supports these log levels (via `LOG_LEVEL` environment variable):
- `DEBUG` - Most verbose, includes function calls and detailed context
- `INFO` - Standard operational messages (default)
- `WARNING` - Warning conditions
- `ERROR` - Error conditions only
- `CRITICAL` - Critical errors only

## Security Considerations

### Safe Operations
- Only authorized debug operations are allowed
- File operations are restricted to `/opt/kanakku/debug.env`
- Service operations are limited to Kanakku services only
- All operations are logged and audited

### Automatic Cleanup
- Debug logging should be disabled after troubleshooting
- The `debug.env` file is automatically removed when disabled
- Services restart with normal logging levels

### Monitoring
- Debug mode status is visible via `check_debug_status`
- All debug operations are logged in admin server logs
- Service restart operations are tracked

## Troubleshooting

### Common Issues

#### 1. Service Restart Failures
```bash
# Check service status
get_service_status --service kanakku

# Check system logs
read_log --log_key systemd_kanakku --lines 50
```

#### 2. Debug Settings Not Applied
```bash
# Verify debug.env file exists and has correct content
execute_command "cat /opt/kanakku/debug.env"

# Check if services are reading environment files
execute_command "systemctl show kanakku | grep Environment"
```

#### 3. Permission Issues
```bash
# Check file permissions
execute_command "ls -la /opt/kanakku/debug.env"

# Verify service user permissions
execute_command "sudo -u kanakku test -w /opt/kanakku/"
```

### Recovery Procedures

If debug logging gets stuck in an inconsistent state:

1. **Manual Cleanup**:
   ```bash
   # Remove debug.env file
   execute_command "rm -f /opt/kanakku/debug.env"
   
   # Restart all services
   restart_all_kanakku_services
   ```

2. **Verify Normal Operation**:
   ```bash
   # Check all services are running
   get_service_status
   
   # Verify debug is disabled
   check_debug_status
   ```

## Best Practices

### When to Use Debug Logging

✅ **Appropriate Use Cases:**
- Investigating specific error conditions
- Troubleshooting API request/response issues
- Debugging authentication problems
- Analyzing database query performance

❌ **Avoid Debug Logging For:**
- Normal production monitoring
- Long-term logging (performance impact)
- High-traffic periods (log volume)
- When disk space is limited

### Operational Guidelines

1. **Enable Temporarily**: Only enable debug logging for the duration needed to investigate an issue

2. **Monitor Resources**: Debug logging increases:
   - Log file sizes
   - Disk I/O
   - CPU usage (minimal)

3. **Coordinate with Team**: Inform team members when debug logging is enabled in production

4. **Document Findings**: Record what was discovered during debug sessions

### Performance Impact

- **Log Volume**: Debug logging can increase log volume by 5-10x
- **Disk Space**: Monitor `/opt/kanakku/logs/` directory
- **Performance**: Minimal impact on application performance
- **Memory**: Slight increase in memory usage for log buffers

## Examples

### Typical Troubleshooting Session

```bash
# 1. Check current status
check_debug_status

# 2. Enable debug logging
toggle_debug_logging --enable true

# 3. Reproduce the issue (external action)

# 4. Check logs for detailed information
read_log --log_key kanakku_app --lines 200
search_logs --query "ERROR" --log_keys kanakku_app,kanakku_error

# 5. Disable debug logging when done
toggle_debug_logging --enable false

# 6. Verify normal operation
check_debug_status
get_service_status
```

### Service-Specific Debugging

```bash
# Debug only the main application
toggle_debug_logging --enable true --services kanakku

# Debug only email processing
toggle_debug_logging --enable true --services kanakku-worker,kanakku-scheduler
```

## Integration with Monitoring

The debug logging feature integrates with existing monitoring:

- **Admin Server Logs**: All debug operations are logged
- **Service Logs**: Enhanced detail when debug is enabled
- **System Monitoring**: Service restart events are tracked
- **Health Checks**: Normal health check endpoints continue to work

For more information, see:
- [Admin Server README](README.md)
- [Service Management Guide](SERVICE_MANAGEMENT.md)
- [Security Documentation](SECURITY.md) 