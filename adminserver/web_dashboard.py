#!/usr/bin/env python3
"""
Kanakku Monitoring Dashboard

A web-based monitoring dashboard that extends the existing Admin MCP Server
infrastructure to provide real-time monitoring of services, system metrics,
and logs through a simple web interface.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

# Import existing admin server functions
from admin_server import (
    KANAKKU_SERVICES,
    LOG_PATHS,
    execute_remote_command,
    execute_safe_command,
    read_log_file,
    search_logs,
)

# Import configuration
from config.dashboard_config import get_config
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Create Flask application
app = Flask(__name__)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Configure logging
logging.basicConfig(
    level=getattr(logging, app.config["LOG_LEVEL"]), format=app.config["LOG_FORMAT"]
)
logger = logging.getLogger("kanakku-monitor-dashboard")

# Enable CORS if configured
if app.config.get("CORS_ORIGINS"):
    CORS(app, origins=app.config["CORS_ORIGINS"])
else:
    # Enable CORS for development with default settings
    if app.config.get("DEBUG"):
        CORS(app)


def run_async(coro):
    """Helper function to run async functions in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


@app.route("/")
def dashboard():
    """Main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/health")
def health_check():
    """Dashboard health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "kanakku-monitor-dashboard",
        }
    )


@app.route("/api/services/status")
def get_services_status():
    """Get status of all Kanakku services."""
    try:
        services_status = {}

        for service in KANAKKU_SERVICES:
            # Check service status using systemctl
            command = f"systemctl is-active {service}"
            stdout, stderr, returncode, _ = run_async(execute_safe_command(command))

            status = (
                "active"
                if returncode == 0 and stdout.strip() == "active"
                else "inactive"
            )

            # Get additional service info
            info_command = f"systemctl show {service} --property=LoadState,ActiveState,SubState,MainPID"
            info_stdout, _, info_returncode, _ = run_async(
                execute_safe_command(info_command)
            )

            service_info = {
                "status": status,
                "active": status == "active",
                "last_checked": datetime.utcnow().isoformat(),
            }

            if info_returncode == 0:
                # Parse systemctl show output
                for line in info_stdout.strip().split("\n"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        service_info[key.lower()] = value

            services_status[service] = service_info

        return jsonify(
            {
                "services": services_status,
                "timestamp": datetime.utcnow().isoformat(),
                "total_services": len(KANAKKU_SERVICES),
                "active_services": sum(
                    1 for s in services_status.values() if s["active"]
                ),
            }
        )

    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/system/metrics")
def get_system_metrics():
    """Get current system metrics."""
    try:
        metrics = {}

        # CPU usage and load average
        cpu_command = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        cpu_stdout, _, cpu_returncode, _ = run_async(execute_safe_command(cpu_command))
        if cpu_returncode == 0:
            try:
                metrics["cpu_usage"] = float(cpu_stdout.strip())
            except ValueError:
                metrics["cpu_usage"] = 0.0

        # Load average
        load_command = (
            "uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ','"
        )
        load_stdout, _, load_returncode, _ = run_async(
            execute_safe_command(load_command)
        )
        if load_returncode == 0:
            try:
                metrics["load_average"] = float(load_stdout.strip())
            except ValueError:
                metrics["load_average"] = 0.0

        # Memory usage
        mem_command = (
            "free -m | awk 'NR==2{printf \"%.1f %.1f %.1f\", $3*100/$2, $2, $3}'"
        )
        mem_stdout, _, mem_returncode, _ = run_async(execute_safe_command(mem_command))
        if mem_returncode == 0:
            try:
                mem_parts = mem_stdout.strip().split()
                metrics["memory"] = {
                    "usage_percent": float(mem_parts[0]),
                    "total_mb": float(mem_parts[1]),
                    "used_mb": float(mem_parts[2]),
                }
            except (ValueError, IndexError):
                metrics["memory"] = {
                    "usage_percent": 0.0,
                    "total_mb": 0.0,
                    "used_mb": 0.0,
                }

        # Disk usage
        disk_command = "df -h / | awk 'NR==2 {print $5}' | tr -d '%'"
        disk_stdout, _, disk_returncode, _ = run_async(
            execute_safe_command(disk_command)
        )
        if disk_returncode == 0:
            try:
                metrics["disk_usage"] = float(disk_stdout.strip())
            except ValueError:
                metrics["disk_usage"] = 0.0

        # System uptime
        uptime_command = "uptime -p"
        uptime_stdout, _, uptime_returncode, _ = run_async(
            execute_safe_command(uptime_command)
        )
        if uptime_returncode == 0:
            metrics["uptime"] = uptime_stdout.strip()
        else:
            metrics["uptime"] = "Unknown"

        # Process count
        proc_command = "ps aux | wc -l"
        proc_stdout, _, proc_returncode, _ = run_async(
            execute_safe_command(proc_command)
        )
        if proc_returncode == 0:
            try:
                metrics["process_count"] = (
                    int(proc_stdout.strip()) - 1
                )  # Subtract header line
            except ValueError:
                metrics["process_count"] = 0

        metrics["timestamp"] = datetime.utcnow().isoformat()

        return jsonify(metrics)

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/system/uptime")
def get_system_uptime():
    """Get detailed system uptime information."""
    try:
        # Get detailed uptime info
        uptime_command = "uptime"
        uptime_stdout, _, uptime_returncode, _ = run_async(
            execute_safe_command(uptime_command)
        )

        # Get boot time
        boot_command = "who -b | awk '{print $3, $4}'"
        boot_stdout, _, boot_returncode, _ = run_async(
            execute_safe_command(boot_command)
        )

        uptime_info = {"timestamp": datetime.utcnow().isoformat()}

        if uptime_returncode == 0:
            uptime_info["uptime_raw"] = uptime_stdout.strip()

        if boot_returncode == 0:
            uptime_info["boot_time"] = boot_stdout.strip()

        return jsonify(uptime_info)

    except Exception as e:
        logger.error(f"Error getting uptime info: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs/<log_key>")
def get_logs(log_key):
    """Get recent log entries for a specific log."""
    try:
        lines = request.args.get("lines", 100, type=int)
        lines = min(lines, 1000)  # Limit to 1000 lines max

        if log_key not in LOG_PATHS:
            return jsonify({"error": f"Unknown log file: {log_key}"}), 400

        log_content = run_async(read_log_file(log_key, lines=lines))

        return jsonify(
            {
                "log_key": log_key,
                "content": log_content,
                "lines_requested": lines,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error reading log {log_key}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs/<log_key>/search")
def search_log(log_key):
    """Search for a pattern in a specific log."""
    try:
        query = request.args.get("q", "")
        since = request.args.get("since", None)

        if not query:
            return jsonify({"error": 'Query parameter "q" is required'}), 400

        if log_key not in LOG_PATHS:
            return jsonify({"error": f"Unknown log file: {log_key}"}), 400

        results = run_async(search_logs(query, [log_key], since=since))

        return jsonify(
            {
                "log_key": log_key,
                "query": query,
                "since": since,
                "results": results.get(log_key, ""),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error searching log {log_key}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs/available")
def get_available_logs():
    """Get list of available log files."""
    return jsonify(
        {
            "logs": list(LOG_PATHS.keys()),
            "log_paths": LOG_PATHS,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


if __name__ == "__main__":
    # Development server
    app.run(host="127.0.0.1", port=5001, debug=True)
