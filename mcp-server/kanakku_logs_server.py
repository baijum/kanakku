#!/usr/bin/env python3
"""
Kanakku Logs MCP Server

A Model Context Protocol server that provides access to Kanakku production logs
for debugging purposes. This server allows Cursor to read various log files
from the production server including application logs, system logs, and Nginx logs.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kanakku-logs-server")

# Server configuration
server = Server("kanakku-logs-server")

# Log file paths based on the deployment configuration
LOG_PATHS = {
    # Application logs
    "kanakku_app": "/opt/kanakku/logs/kanakku.log",
    "kanakku_error": "/opt/kanakku/logs/error.log",
    "kanakku_worker": "/opt/kanakku/logs/worker.log",
    "kanakku_scheduler": "/opt/kanakku/logs/scheduler.log",
    # System service logs (accessed via journalctl)
    "systemd_kanakku": "journalctl -u kanakku",
    "systemd_kanakku_worker": "journalctl -u kanakku-worker",
    "systemd_kanakku_scheduler": "journalctl -u kanakku-scheduler",
    "systemd_nginx": "journalctl -u nginx",
    "systemd_postgresql": "journalctl -u postgresql",
    "systemd_redis": "journalctl -u redis-server",
    # Nginx logs
    "nginx_access": "/var/log/nginx/access.log",
    "nginx_error": "/var/log/nginx/error.log",
    "nginx_kanakku_access": "/var/log/nginx/kanakku_access.log",
    "nginx_kanakku_error": "/var/log/nginx/kanakku_error.log",
    # System logs
    "syslog": "/var/log/syslog",
    "auth": "/var/log/auth.log",
    "fail2ban": "/var/log/fail2ban.log",
    # Health check logs
    "health_check": "/var/log/kanakku/health-check.log",
    # Deployment logs
    "deployment": "/opt/kanakku/logs/deployment.log",
}

# SSH configuration for remote server access
SSH_CONFIG = {
    "host": os.getenv("KANAKKU_DEPLOY_HOST"),
    "user": os.getenv("KANAKKU_DEPLOY_USER", "root"),
    "key_path": os.getenv("KANAKKU_SSH_KEY_PATH", "~/.ssh/kanakku_deploy"),
    "port": int(os.getenv("KANAKKU_SSH_PORT", "22")),
}


def validate_ssh_config() -> bool:
    """Validate SSH configuration for remote access."""
    if not SSH_CONFIG["host"]:
        logger.error("KANAKKU_DEPLOY_HOST environment variable not set")
        return False

    key_path = Path(SSH_CONFIG["key_path"]).expanduser()
    if not key_path.exists():
        logger.error(f"SSH key not found at {key_path}")
        return False

    return True


async def execute_remote_command(
    command: str, timeout: int = 30
) -> tuple[str, str, int]:
    """Execute a command on the remote server via SSH."""
    if not validate_ssh_config():
        return "", "SSH configuration invalid", 1

    ssh_command = [
        "ssh",
        "-i",
        str(Path(SSH_CONFIG["key_path"]).expanduser()),
        "-p",
        str(SSH_CONFIG["port"]),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=10",
        f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}",
        command,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *ssh_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            process.returncode or 0,
        )
    except asyncio.TimeoutError:
        return "", f"Command timed out after {timeout} seconds", 1
    except Exception as e:
        return "", f"SSH command failed: {str(e)}", 1


async def read_log_file(log_key: str, lines: int = 100, follow: bool = False) -> str:
    """Read log file content from the remote server."""
    if log_key not in LOG_PATHS:
        return f"Unknown log file: {log_key}"

    log_path = LOG_PATHS[log_key]

    # Handle systemd journal logs
    if log_path.startswith("journalctl"):
        command = f"{log_path} --no-pager -n {lines}"
        if follow:
            command += " --since '1 hour ago'"
    else:
        # Handle regular log files
        command = f"tail -n {lines} {log_path}"
        if follow:
            command = f"tail -f -n {lines} {log_path}"

    stdout, stderr, returncode = await execute_remote_command(command)

    if returncode != 0:
        return f"Error reading log {log_key}: {stderr}"

    return stdout


async def search_logs(
    query: str, log_keys: List[str], since: Optional[str] = None
) -> Dict[str, str]:
    """Search for a pattern across multiple log files."""
    results = {}

    for log_key in log_keys:
        if log_key not in LOG_PATHS:
            results[log_key] = f"Unknown log file: {log_key}"
            continue

        log_path = LOG_PATHS[log_key]

        if log_path.startswith("journalctl"):
            command = f"{log_path} --no-pager --grep '{query}'"
            if since:
                command += f" --since '{since}'"
        else:
            command = f"grep -n '{query}' {log_path}"
            if since:
                # For file logs, use find with modification time
                command = (
                    f"find {log_path} -newermt '{since}' -exec grep -n '{query}' {{}} +"
                )

        stdout, stderr, returncode = await execute_remote_command(command)

        if returncode != 0 and "No entries" not in stderr:
            results[log_key] = f"Error searching {log_key}: {stderr}"
        else:
            results[log_key] = stdout if stdout else "No matches found"

    return results


# Security configuration for arbitrary command execution
ALLOWED_COMMANDS = {
    # System information commands
    "uptime",
    "whoami",
    "id",
    "uname",
    "hostname",
    "date",
    # Resource monitoring
    "free",
    "df",
    "du",
    "top",
    "htop",
    "iotop",
    "vmstat",
    "iostat",
    # Process management (read-only)
    "ps",
    "pgrep",
    "pstree",
    "jobs",
    # Network information
    "netstat",
    "ss",
    "lsof",
    "nslookup",
    "dig",
    "ping",
    "traceroute",
    # File system (read-only)
    "ls",
    "find",
    "locate",
    "which",
    "whereis",
    "file",
    "stat",
    # Text processing
    "cat",
    "head",
    "tail",
    "grep",
    "awk",
    "sed",
    "sort",
    "uniq",
    "wc",
    # System services
    "systemctl",
    "service",
    "journalctl",
    # Package management (query only)
    "dpkg",
    "apt",
    "yum",
    "rpm",
    # Log analysis
    "zcat",
    "zgrep",
    "less",
    "more",
}

DANGEROUS_PATTERNS = [
    # Destructive operations
    r"\brm\b",
    r"\bmv\b",
    r"\bcp\b.*>",
    r"\bdd\b",
    # System modification
    r"\bchmod\b",
    r"\bchown\b",
    r"\bmount\b",
    r"\bumount\b",
    # Process control
    r"\bkill\b",
    r"\bkillall\b",
    r"\bpkill\b",
    # Network operations
    r"\bwget\b",
    r"\bcurl\b.*-X\s*(POST|PUT|DELETE)",
    r"\bscp\b",
    r"\brsync\b",
    # Package installation
    r"\bapt\s+install\b",
    r"\byum\s+install\b",
    r"\bpip\s+install\b",
    # File editing
    r"\bvi\b",
    r"\bvim\b",
    r"\bnano\b",
    r"\bemacs\b",
    # Redirection that could overwrite files
    r">\s*[^|]",
    r">>",
    r"\btee\b",
    # Command chaining that could be dangerous
    r"&&",
    r"\|\|",
    r";",
    # Privilege escalation
    r"\bsudo\b",
    r"\bsu\b",
    # System control
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bhalt\b",
    r"\bpoweroff\b",
]


def is_command_safe(command: str) -> tuple[bool, str]:
    """
    Check if a command is safe to execute.

    Returns:
        tuple: (is_safe, reason)
    """
    import re

    # Basic safety checks
    command = command.strip()

    if not command:
        return False, "Empty command"

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Command contains dangerous pattern: {pattern}"

    # Extract the base command (first word)
    base_command = command.split()[0].split("/")[-1]  # Handle full paths

    # Check if base command is in allowed list
    if base_command not in ALLOWED_COMMANDS:
        return False, f"Command '{base_command}' is not in the allowed list"

    # Additional specific checks
    if base_command == "find":
        # Allow find but not with -exec that could be dangerous
        if "-exec" in command and not re.search(
            r"-exec\s+(cat|head|tail|grep|ls)\b", command
        ):
            return (
                False,
                "find -exec only allowed with safe commands (cat, head, tail, grep, ls)",
            )

    if base_command in ["systemctl", "service"]:
        # Only allow status, is-active, is-enabled, list-units
        if not re.search(r"\b(status|is-active|is-enabled|list-units|show)\b", command):
            return False, "systemctl/service only allowed for status queries"

    if base_command in ["apt", "yum", "rpm", "dpkg"]:
        # Only allow query operations
        if not re.search(r"\b(list|search|show|query|info|-l|-q)\b", command):
            return False, "Package managers only allowed for query operations"

    # Check command length (prevent extremely long commands)
    if len(command) > 500:
        return False, "Command too long (max 500 characters)"

    return True, "Command is safe"


async def execute_safe_command(
    command: str, timeout: int = 30
) -> tuple[str, str, int, str]:
    """
    Execute a command after safety validation.

    Returns:
        tuple: (stdout, stderr, returncode, safety_note)
    """
    # Validate command safety
    is_safe, reason = is_command_safe(command)

    if not is_safe:
        return "", f"Command blocked: {reason}", 1, f"🚫 BLOCKED: {reason}"

    # Add safety measures to the command
    safe_command = f"timeout 30 {command}"

    # Execute the command
    stdout, stderr, returncode = await execute_remote_command(safe_command, timeout)

    safety_note = "✅ Command executed safely"
    if returncode != 0:
        safety_note += f" (exit code: {returncode})"

    return stdout, stderr, returncode, safety_note


# Service management configuration
KANAKKU_SERVICES = [
    "kanakku",
    "kanakku-worker",
    "kanakku-scheduler",
    "nginx",
    "postgresql",
    "redis-server",
]

ALLOWED_SERVICE_OPERATIONS = [
    "start",
    "stop",
    "restart",
    "reload",
    "daemon-reload",
    "status",
    "is-active",
    "is-enabled",
]


async def execute_service_operation(
    operation: str, service: Optional[str] = None, timeout: int = 60
) -> tuple[str, str, int, str]:
    """
    Execute a service management operation safely.

    Args:
        operation: The systemctl operation (start, stop, restart, reload, etc.)
        service: The service name (optional for daemon-reload)
        timeout: Command timeout in seconds

    Returns:
        tuple: (stdout, stderr, returncode, safety_note)
    """
    # Validate operation
    if operation not in ALLOWED_SERVICE_OPERATIONS:
        return (
            "",
            f"Operation '{operation}' not allowed",
            1,
            "🚫 BLOCKED: Invalid operation",
        )

    # Special case for daemon-reload
    if operation == "daemon-reload":
        command = "systemctl daemon-reload"
        safety_note = "🔄 DAEMON-RELOAD: Reloading systemd configuration"
    else:
        # Validate service name
        if not service:
            return (
                "",
                "Service name required for this operation",
                1,
                "🚫 BLOCKED: Missing service name",
            )

        if service not in KANAKKU_SERVICES:
            return (
                "",
                f"Service '{service}' not in allowed list",
                1,
                "🚫 BLOCKED: Service not allowed",
            )

        command = f"systemctl {operation} {service}"
        safety_note = f"🔧 SERVICE: {operation.upper()} {service}"

    # Execute the command
    stdout, stderr, returncode = await execute_remote_command(command, timeout)

    if returncode != 0:
        safety_note += f" (FAILED - exit code: {returncode})"
    else:
        safety_note += " (SUCCESS)"

    return stdout, stderr, returncode, safety_note


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for log access."""
    return [
        types.Tool(
            name="read_log",
            description="Read content from a specific log file",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_key": {
                        "type": "string",
                        "description": f"Log file identifier. Available: {', '.join(LOG_PATHS.keys())}",
                        "enum": list(LOG_PATHS.keys()),
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to read (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 10000,
                    },
                },
                "required": ["log_key"],
            },
        ),
        types.Tool(
            name="search_logs",
            description="Search for a pattern across multiple log files",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search pattern or regex",
                    },
                    "log_keys": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(LOG_PATHS.keys())},
                        "description": "List of log files to search",
                    },
                    "since": {
                        "type": "string",
                        "description": "Time filter (e.g., '1 hour ago', '2023-12-01', 'yesterday')",
                        "default": None,
                    },
                },
                "required": ["query", "log_keys"],
            },
        ),
        types.Tool(
            name="get_service_status",
            description="Get status of Kanakku services",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name (optional, gets all if not specified)",
                        "enum": [
                            "kanakku",
                            "kanakku-worker",
                            "kanakku-scheduler",
                            "nginx",
                            "postgresql",
                            "redis-server",
                        ],
                    }
                },
            },
        ),
        types.Tool(
            name="get_system_info",
            description="Get system information and resource usage",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="tail_log",
            description="Follow a log file in real-time (returns recent entries)",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_key": {
                        "type": "string",
                        "description": f"Log file identifier. Available: {', '.join(LOG_PATHS.keys())}",
                        "enum": list(LOG_PATHS.keys()),
                    },
                    "duration": {
                        "type": "string",
                        "description": "Time period to show (e.g., '1 hour ago', '30 minutes ago')",
                        "default": "1 hour ago",
                    },
                },
                "required": ["log_key"],
            },
        ),
        types.Tool(
            name="execute_command",
            description="Execute a safe system command for debugging (RESTRICTED: only read-only commands allowed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute. Only safe, read-only commands are allowed (e.g., 'free -h', 'df -h', 'ps aux', 'netstat -tlnp'). Destructive operations are blocked.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 30, max: 60)",
                        "default": 30,
                        "minimum": 1,
                        "maximum": 60,
                    },
                },
                "required": ["command"],
            },
        ),
        types.Tool(
            name="manage_service",
            description="Manage Kanakku services (start, stop, restart, reload, daemon-reload)",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Service operation to perform",
                        "enum": [
                            "start",
                            "stop",
                            "restart",
                            "reload",
                            "daemon-reload",
                            "status",
                            "is-active",
                            "is-enabled",
                        ],
                    },
                    "service": {
                        "type": "string",
                        "description": "Service name (not required for daemon-reload)",
                        "enum": [
                            "kanakku",
                            "kanakku-worker",
                            "kanakku-scheduler",
                            "nginx",
                            "postgresql",
                            "redis-server",
                        ],
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 60, max: 120)",
                        "default": 60,
                        "minimum": 10,
                        "maximum": 120,
                    },
                },
                "required": ["operation"],
            },
        ),
        types.Tool(
            name="restart_all_kanakku_services",
            description="Restart all Kanakku application services (kanakku, kanakku-worker, kanakku-scheduler) in the correct order",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_nginx": {
                        "type": "boolean",
                        "description": "Whether to also restart nginx (default: false)",
                        "default": False,
                    },
                    "daemon_reload": {
                        "type": "boolean",
                        "description": "Whether to run daemon-reload first (default: true)",
                        "default": True,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls for log operations."""

    if name == "read_log":
        log_key = arguments["log_key"]
        lines = arguments.get("lines", 100)

        content = await read_log_file(log_key, lines)

        return [
            types.TextContent(
                type="text",
                text=f"=== {log_key.upper()} LOG ({lines} lines) ===\n\n{content}",
            )
        ]

    elif name == "search_logs":
        query = arguments["query"]
        log_keys = arguments["log_keys"]
        since = arguments.get("since")

        results = await search_logs(query, log_keys, since)

        output = f"=== SEARCH RESULTS FOR: {query} ===\n\n"
        for log_key, result in results.items():
            output += f"--- {log_key.upper()} ---\n{result}\n\n"

        return [types.TextContent(type="text", text=output)]

    elif name == "get_service_status":
        service = arguments.get("service")

        if service:
            command = f"systemctl status {service} --no-pager"
        else:
            services = [
                "kanakku",
                "kanakku-worker",
                "kanakku-scheduler",
                "nginx",
                "postgresql",
                "redis-server",
            ]
            command = f"systemctl status {' '.join(services)} --no-pager"

        stdout, stderr, returncode = await execute_remote_command(command)

        output = f"=== SERVICE STATUS ===\n\n{stdout}"
        if stderr:
            output += f"\nErrors:\n{stderr}"

        return [types.TextContent(type="text", text=output)]

    elif name == "get_system_info":
        commands = [
            "uptime",
            "df -h",
            "free -h",
            "ps aux --sort=-%cpu | head -10",
            "netstat -tlnp | grep -E ':(80|443|8000|5432|6379)'",
        ]

        output = "=== SYSTEM INFORMATION ===\n\n"

        for cmd in commands:
            stdout, stderr, returncode = await execute_remote_command(cmd)
            output += f"--- {cmd.upper()} ---\n{stdout}\n"
            if stderr:
                output += f"Errors: {stderr}\n"
            output += "\n"

        return [types.TextContent(type="text", text=output)]

    elif name == "tail_log":
        log_key = arguments["log_key"]
        duration = arguments.get("duration", "1 hour ago")

        log_path = LOG_PATHS[log_key]

        if log_path.startswith("journalctl"):
            command = f"{log_path} --no-pager --since '{duration}'"
        else:
            # For file logs, show recent entries
            command = f"find {log_path} -newermt '{duration}' -exec tail -100 {{}} +"

        stdout, stderr, returncode = await execute_remote_command(command)

        if returncode != 0:
            content = f"Error tailing log {log_key}: {stderr}"
        else:
            content = (
                stdout if stdout else f"No recent entries in {log_key} since {duration}"
            )

        return [
            types.TextContent(
                type="text",
                text=f"=== {log_key.upper()} LOG (since {duration}) ===\n\n{content}",
            )
        ]

    elif name == "execute_command":
        command = arguments["command"]
        timeout = arguments.get("timeout", 30)

        # Validate timeout
        timeout = max(1, min(60, timeout))

        # Execute the command safely
        stdout, stderr, returncode, safety_note = await execute_safe_command(
            command, timeout
        )

        # Format output
        output = "=== COMMAND EXECUTION ===\n"
        output += f"Command: {command}\n"
        output += f"Safety Check: {safety_note}\n"
        output += f"Exit Code: {returncode}\n\n"

        if stdout:
            output += f"--- STDOUT ---\n{stdout}\n"

        if stderr:
            output += f"--- STDERR ---\n{stderr}\n"

        if not stdout and not stderr and returncode == 0:
            output += "Command executed successfully with no output.\n"

        return [types.TextContent(type="text", text=output)]

    elif name == "manage_service":
        operation = arguments["operation"]
        service = arguments.get("service")
        timeout = arguments.get("timeout", 60)

        # Validate timeout
        timeout = max(10, min(120, timeout))

        # Execute the service operation
        stdout, stderr, returncode, safety_note = await execute_service_operation(
            operation, service, timeout
        )

        # Format output
        output = "=== SERVICE MANAGEMENT ===\n"
        output += f"Operation: {operation}\n"
        if service:
            output += f"Service: {service}\n"
        output += f"Safety Check: {safety_note}\n"
        output += f"Exit Code: {returncode}\n\n"

        if stdout:
            output += f"--- STDOUT ---\n{stdout}\n"

        if stderr:
            output += f"--- STDERR ---\n{stderr}\n"

        if not stdout and not stderr and returncode == 0:
            output += "Operation completed successfully with no output.\n"

        return [types.TextContent(type="text", text=output)]

    elif name == "restart_all_kanakku_services":
        include_nginx = arguments.get("include_nginx", False)
        daemon_reload = arguments.get("daemon_reload", True)

        output = "=== RESTART ALL KANAKKU SERVICES ===\n\n"

        # Step 1: Daemon reload if requested
        if daemon_reload:
            output += "Step 1: Reloading systemd daemon...\n"
            stdout, stderr, returncode, safety_note = await execute_service_operation(
                "daemon-reload", timeout=60
            )
            output += f"Result: {safety_note}\n"
            if stderr:
                output += f"Errors: {stderr}\n"
            output += "\n"

        # Step 2: Stop services in reverse order
        services_to_restart = ["kanakku", "kanakku-worker", "kanakku-scheduler"]
        if include_nginx:
            services_to_restart.append("nginx")

        output += "Step 2: Stopping services...\n"
        for service in reversed(services_to_restart):
            stdout, stderr, returncode, safety_note = await execute_service_operation(
                "stop", service, timeout=60
            )
            output += f"  {service}: {safety_note}\n"
            if stderr and "not loaded" not in stderr.lower():
                output += f"    Errors: {stderr}\n"

        output += "\n"

        # Step 3: Start services in correct order
        output += "Step 3: Starting services...\n"
        for service in services_to_restart:
            stdout, stderr, returncode, safety_note = await execute_service_operation(
                "start", service, timeout=60
            )
            output += f"  {service}: {safety_note}\n"
            if stderr:
                output += f"    Errors: {stderr}\n"

        output += "\n"

        # Step 4: Check final status
        output += "Step 4: Final service status...\n"
        for service in services_to_restart:
            stdout, stderr, returncode, safety_note = await execute_service_operation(
                "is-active", service, timeout=30
            )
            status = stdout.strip() if stdout else "unknown"
            output += f"  {service}: {status}\n"

        return [types.TextContent(type="text", text=output)]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available log resources."""
    resources = []

    for log_key, log_path in LOG_PATHS.items():
        resources.append(
            types.Resource(
                uri=f"kanakku://logs/{log_key}",
                name=f"Kanakku {log_key.replace('_', ' ').title()} Log",
                description=f"Access to {log_path}",
                mimeType="text/plain",
            )
        )

    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific log resource."""
    if not uri.startswith("kanakku://logs/"):
        raise ValueError(f"Unknown resource: {uri}")

    log_key = uri.replace("kanakku://logs/", "")

    if log_key not in LOG_PATHS:
        raise ValueError(f"Unknown log: {log_key}")

    content = await read_log_file(log_key, lines=500)
    return content


async def main():
    """Main entry point for the MCP server."""
    # Validate configuration
    if not validate_ssh_config():
        logger.error("Invalid SSH configuration. Please set environment variables:")
        logger.error("- KANAKKU_DEPLOY_HOST: Production server hostname/IP")
        logger.error("- KANAKKU_DEPLOY_USER: SSH user (default: root)")
        logger.error(
            "- KANAKKU_SSH_KEY_PATH: Path to SSH private key (default: ~/.ssh/kanakku_deploy)"
        )
        logger.error("- KANAKKU_SSH_PORT: SSH port (default: 22)")
        sys.exit(1)

    # Test connection
    logger.info(f"Testing connection to {SSH_CONFIG['host']}...")
    stdout, stderr, returncode = await execute_remote_command(
        "echo 'Connection test successful'"
    )

    if returncode != 0:
        logger.error(f"Failed to connect to server: {stderr}")
        sys.exit(1)

    logger.info("Connection successful. Starting MCP server...")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kanakku-logs-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
