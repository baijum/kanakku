# Quick Start Guide - Kanakku Admin MCP Server

Get up and running with the Kanakku Admin MCP Server in 5 minutes.

## Prerequisites

- Python 3.8+
- SSH access to your Kanakku production server
- SSH key for authentication

## 1. Setup

```bash
# Navigate to the MCP server directory
cd mcp-server

# Run the automated setup
./setup.sh
```

## 2. Configure Environment

```bash
# Set your production server details
export KANAKKU_DEPLOY_HOST="your-production-server-ip"
export KANAKKU_DEPLOY_USER="root"  # or your SSH user
export KANAKKU_SSH_KEY_PATH="~/.ssh/kanakku_deploy"
export KANAKKU_SSH_PORT="22"
```

## 3. Test Connection

```bash
# Test the connection and log access
python test-connection.py
```

## 4. Configure Cursor

Add this to your Cursor settings (Cmd/Ctrl + , → search "MCP"):

```json
{
  "mcpServers": {
    "kanakku-admin": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server/admin_server.py"],
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

**Important**: Use the absolute path to the script file.

## 5. Restart Cursor

Restart Cursor to load the MCP server.

## 6. Start Debugging!

You can now ask Cursor things like:

- "Show me the last 100 lines of the Kanakku application log"
- "Search for 'error' in all logs from the last hour"
- "What's the status of all Kanakku services?"
- "Show me recent Nginx access logs"
- "Run 'free -h' to check memory usage"
- "Execute 'df -h' to see disk space"

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH manually
ssh -i ~/.ssh/kanakku_deploy root@your-server

# Check key permissions
chmod 600 ~/.ssh/kanakku_deploy
```

### MCP Server Not Working

1. Check absolute paths in Cursor configuration
2. Restart Cursor after configuration changes
3. Verify environment variables are set correctly

### Log Access Issues

- Ensure SSH user has read permissions for log files
- Some logs may require sudo access

## Available Log Types

- **Application**: `kanakku_app`, `kanakku_error`, `kanakku_worker`, `kanakku_scheduler`
- **System Services**: `systemd_kanakku`, `systemd_nginx`, `systemd_postgresql`, `systemd_redis`
- **Nginx**: `nginx_access`, `nginx_error`, `nginx_kanakku_access`, `nginx_kanakku_error`
- **System**: `syslog`, `auth`, `fail2ban`
- **Monitoring**: `health_check`, `deployment`

## Example Usage in Cursor

```
"Read the last 50 lines from kanakku_app log"
"Search for '500 error' in nginx_access and nginx_error logs since yesterday"
"Show me the status of the kanakku service"
"What system resources are being used?"
"Run 'ps aux | grep kanakku' to see running processes"
"Execute 'netstat -tlnp' to check listening ports"
```

For detailed documentation, see [README.md](README.md). 