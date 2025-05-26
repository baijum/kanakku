# Kanakku Admin MCP Server

A Model Context Protocol (MCP) server that provides administrative access to Kanakku production systems from Cursor IDE. This enables efficient debugging of production issues, log monitoring, and system administration without manually SSH-ing into the server.

## Features

- **Real-time Log Access**: Read application, system, and Nginx logs directly from Cursor
- **Log Search**: Search across multiple log files with time filtering
- **Service Monitoring**: Check status of all Kanakku services
- **System Information**: Get server resource usage and performance metrics
- **Safe Command Execution**: Execute read-only system commands with security restrictions
- **Secure SSH Connection**: Uses SSH key authentication for secure remote access

## Available Log Sources

### Application Logs
- `kanakku_app` - Main Flask application logs (`/opt/kanakku/logs/kanakku.log`)
- `kanakku_error` - Application error logs (`/opt/kanakku/logs/error.log`)
- `kanakku_worker` - Email automation worker logs (`/opt/kanakku/logs/worker.log`)
- `kanakku_scheduler` - Email scheduler logs (`/opt/kanakku/logs/scheduler.log`)

### System Service Logs (via journalctl)
- `systemd_kanakku` - Kanakku service logs
- `systemd_kanakku_worker` - Worker service logs
- `systemd_kanakku_scheduler` - Scheduler service logs
- `systemd_nginx` - Nginx service logs
- `systemd_postgresql` - PostgreSQL service logs
- `systemd_redis` - Redis service logs

### Nginx Logs
- `nginx_access` - General Nginx access logs (`/var/log/nginx/access.log`)
- `nginx_error` - General Nginx error logs (`/var/log/nginx/error.log`)
- `nginx_kanakku_access` - Kanakku-specific access logs
- `nginx_kanakku_error` - Kanakku-specific error logs

### System Logs
- `syslog` - System messages (`/var/log/syslog`)
- `auth` - Authentication logs (`/var/log/auth.log`)
- `fail2ban` - Fail2ban security logs (`/var/log/fail2ban.log`)

### Monitoring Logs
- `health_check` - Application health check logs (`/var/log/kanakku/health-check.log`)
- `deployment` - Deployment logs (`/opt/kanakku/logs/deployment.log`)

## Installation

### Prerequisites

- Python 3.8 or higher
- SSH access to your Kanakku production server
- SSH key for authentication

### Quick Setup

1. **Clone or download the MCP server files**:
   ```bash
   # If part of Kanakku repository
   cd adminserver
   
   # Or download files individually
   mkdir kanakku-admin-server && cd kanakku-admin-server
   # Download the files from the repository
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit with your server details
   nano .env
   ```

### Manual Installation

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up SSH access** (see SSH Configuration section below)

## Configuration

### Environment Variables

Set these environment variables in your shell or `.env` file:

```bash
# Required: Your production server details
export KANAKKU_DEPLOY_HOST="your-production-server-ip"
export KANAKKU_DEPLOY_USER="root"  # or your SSH user
export KANAKKU_SSH_KEY_PATH="~/.ssh/kanakku_deploy"
export KANAKKU_SSH_PORT="22"
```

### SSH Configuration

1. **Generate SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/kanakku_deploy
   ```

2. **Copy public key to server**:
   ```bash
   ssh-copy-id -i ~/.ssh/kanakku_deploy.pub user@your-server
   ```

3. **Test SSH connection**:
   ```bash
   ssh -i ~/.ssh/kanakku_deploy user@your-server "echo 'Connection successful'"
   ```

### Cursor Integration

1. **Open Cursor Settings** (Cmd/Ctrl + ,)

2. **Search for "MCP"** or "Model Context Protocol"

3. **Add the server configuration**:
   ```json
   {
     "mcpServers": {
       "kanakku-admin": {
         "command": "python",
                   "args": ["/path/to/adminserver/admin_server.py"],
         "env": {
           "KANAKKU_DEPLOY_HOST": "your-production-server-ip",
           "KANAKKU_DEPLOY_USER": "root",
           "KANAKKU_SSH_KEY_PATH": "~/.ssh/kanakku_deploy",
           "KANAKKU_SSH_PORT": "22"
         }
       }
     }
   }
   ```

4. **Restart Cursor** to load the MCP server

## Usage

Once configured, you can use the following tools directly in Cursor:

### Reading Logs

Ask Cursor to read specific logs:
```
"Show me the last 100 lines of the Kanakku application log"
"Read the Nginx error log"
"Get the latest entries from the worker service log"
```

### Searching Logs

Search across multiple log files:
```
"Search for 'error' in all application logs from the last hour"
"Find any mentions of '500' in Nginx logs since yesterday"
"Look for authentication failures in system logs"
```

### Service Monitoring

Check service status:
```
"What's the status of all Kanakku services?"
"Is the Nginx service running?"
"Show me system resource usage"
```

### Real-time Monitoring

Get recent log entries:
```
"Show me recent entries from the application log"
"Tail the Nginx access log for the last 30 minutes"
"What happened in the last hour according to system logs?"
```

### Command Execution

Execute safe system commands for debugging:
```
"Run 'free -h' to check memory usage"
"Execute 'df -h' to see disk space"
"Run 'ps aux | grep kanakku' to see running processes"
"Execute 'netstat -tlnp' to check listening ports"
```

## Available Tools

### `read_log`
Read content from a specific log file.

**Parameters:**
- `log_key` (required): Log file identifier
- `lines` (optional): Number of lines to read (default: 100, max: 10000)

### `search_logs`
Search for patterns across multiple log files.

**Parameters:**
- `query` (required): Search pattern or regex
- `log_keys` (required): Array of log file identifiers to search
- `since` (optional): Time filter (e.g., "1 hour ago", "yesterday")

### `get_service_status`
Get status of Kanakku services.

**Parameters:**
- `service` (optional): Specific service name, or all services if not specified

### `get_system_info`
Get system information and resource usage.

**Parameters:** None

### `tail_log`
Follow a log file and show recent entries.

**Parameters:**
- `log_key` (required): Log file identifier
- `duration` (optional): Time period to show (default: "1 hour ago")

### `execute_command`
Execute a safe system command for debugging purposes.

**Parameters:**
- `command` (required): Command to execute (must be in allowed list)
- `timeout` (optional): Command timeout in seconds (default: 30, max: 60)

**Security Features:**
- Only allows pre-approved, read-only commands
- Blocks destructive operations (rm, mv, chmod, etc.)
- Prevents privilege escalation (sudo, su)
- Blocks file modification and network operations
- Command length limited to 500 characters
- Automatic timeout protection

## Troubleshooting

### Connection Issues

1. **SSH Connection Failed**:
   ```bash
   # Test SSH manually
   ssh -i ~/.ssh/kanakku_deploy -v user@your-server
   
   # Check SSH key permissions
   chmod 600 ~/.ssh/kanakku_deploy
   
   # Verify server is accessible
   ping your-server
   ```

2. **Permission Denied**:
   - Ensure SSH key is added to server's `authorized_keys`
   - Check that the SSH user has appropriate permissions
   - Verify firewall settings allow SSH connections

3. **Log File Access Issues**:
   - Ensure SSH user has read permissions for log files
   - Some logs may require sudo access (configure sudoers if needed)

### MCP Server Issues

1. **Server Won't Start**:
   ```bash
   # Check Python version
   python3 --version
   
   # Verify dependencies
   pip list | grep mcp
   
   # Test server manually
source venv/bin/activate
python admin_server.py
   ```

2. **Cursor Can't Connect**:
   - Restart Cursor after configuration changes
   - Check Cursor's MCP settings are correct
   - Verify file paths in configuration are absolute

### Log Access Issues

1. **Empty Log Results**:
   - Check if log files exist on the server
   - Verify log file paths in the server configuration
   - Ensure services are actually writing to logs

2. **Permission Errors**:
   - Some logs may require elevated permissions
   - Consider adding SSH user to appropriate groups (e.g., `adm` for system logs)

## Security Considerations

### SSH Security
- **SSH Key Security**: Keep your SSH private key secure and use strong passphrases
- **Network Security**: Ensure SSH is properly configured with key-based authentication
- **Access Control**: Limit SSH user permissions to only what's necessary for log access

### Command Execution Security
- **Whitelist Approach**: Only pre-approved commands are allowed
- **Read-Only Operations**: Destructive commands are blocked by design
- **Pattern Matching**: Advanced regex patterns detect and block dangerous operations
- **Timeout Protection**: All commands have automatic timeout limits
- **No Privilege Escalation**: sudo, su, and similar commands are blocked

### Allowed Commands
The following command categories are permitted:
- **System Info**: uptime, whoami, id, uname, hostname, date
- **Resource Monitoring**: free, df, du, top, htop, vmstat, iostat
- **Process Info**: ps, pgrep, pstree (read-only)
- **Network Info**: netstat, ss, lsof, nslookup, dig, ping
- **File System**: ls, find, locate, which, stat (read-only)
- **Text Processing**: cat, head, tail, grep, awk, sed, sort, uniq, wc
- **Service Status**: systemctl status, journalctl (query only)
- **Package Info**: dpkg, apt, yum, rpm (query only)

### Blocked Operations
- File modification (rm, mv, cp with redirection, chmod, chown)
- Process control (kill, killall, pkill)
- System control (reboot, shutdown, halt)
- Network operations (wget, curl POST/PUT/DELETE, scp)
- Package installation (apt install, yum install, pip install)
- File editing (vi, vim, nano, emacs)
- Privilege escalation (sudo, su)
- Command chaining (&&, ||, ;)
- File redirection (>, >>, tee)

### Data Sensitivity
- **Log Sensitivity**: Be aware that logs may contain sensitive information
- **Command Output**: Review command outputs for sensitive data before sharing

## Development

### Testing the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export KANAKKU_DEPLOY_HOST="your-server"

# Run server in test mode
python admin_server.py
```

### Adding New Log Sources

To add new log sources, edit the `LOG_PATHS` dictionary in `admin_server.py`:

```python
LOG_PATHS = {
    # ... existing logs ...
    "new_log_name": "/path/to/new/log/file",
    "new_service_log": "journalctl -u new-service",
}
```

### Customizing Commands

Modify the command generation logic in the `read_log_file` and `search_logs` functions to customize how logs are accessed.

## Support

For issues related to:
- **MCP Server**: Check the troubleshooting section above
- **Kanakku Application**: Refer to the main Kanakku documentation
- **Deployment Issues**: See the deployment guide in `docs/deployment.md`

## License

This MCP server is part of the Kanakku project and follows the same license terms. 