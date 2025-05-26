#!/usr/bin/env python3
"""
User management utility for Kanakku Monitoring Dashboard

This script helps create and manage htpasswd files for dashboard authentication.
"""

import argparse
import getpass
import os
import sys
from pathlib import Path

from auth import add_user_to_htpasswd, create_htpasswd_file
from config.dashboard_config import get_config


def create_user(htpasswd_file: str, username: str, password: str = None) -> bool:
    """Create or update a user in the htpasswd file."""
    if not password:
        password = getpass.getpass(f"Enter password for user '{username}': ")
        confirm_password = getpass.getpass("Confirm password: ")

        if password != confirm_password:
            print("Error: Passwords do not match!")
            return False

    if not password:
        print("Error: Password cannot be empty!")
        return False

    success = add_user_to_htpasswd(htpasswd_file, username, password)

    if success:
        print(
            f"✅ User '{username}' {'updated' if os.path.exists(htpasswd_file) else 'created'} successfully!"
        )
        print(f"📁 htpasswd file: {htpasswd_file}")
        return True
    else:
        print(f"❌ Failed to create/update user '{username}'")
        return False


def list_users(htpasswd_file: str) -> bool:
    """List all users in the htpasswd file."""
    if not os.path.exists(htpasswd_file):
        print(f"❌ htpasswd file not found: {htpasswd_file}")
        return False

    try:
        from passlib.apache import HtpasswdFile

        htpasswd = HtpasswdFile(htpasswd_file)
        users = list(htpasswd.users())

        if users:
            print(f"📋 Users in {htpasswd_file}:")
            for user in sorted(users):
                print(f"  • {user}")
        else:
            print(f"📋 No users found in {htpasswd_file}")

        return True

    except Exception as e:
        print(f"❌ Error reading htpasswd file: {e}")
        return False


def delete_user(htpasswd_file: str, username: str) -> bool:
    """Delete a user from the htpasswd file."""
    if not os.path.exists(htpasswd_file):
        print(f"❌ htpasswd file not found: {htpasswd_file}")
        return False

    try:
        from passlib.apache import HtpasswdFile

        htpasswd = HtpasswdFile(htpasswd_file)

        if username not in htpasswd:
            print(f"❌ User '{username}' not found in htpasswd file")
            return False

        htpasswd.delete(username)
        htpasswd.save()

        print(f"✅ User '{username}' deleted successfully!")
        return True

    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False


def check_file_permissions(htpasswd_file: str) -> None:
    """Check and display file permissions."""
    if os.path.exists(htpasswd_file):
        stat_info = os.stat(htpasswd_file)
        permissions = oct(stat_info.st_mode)[-3:]

        print(f"📁 File: {htpasswd_file}")
        print(f"🔒 Permissions: {permissions}")

        # Recommend secure permissions
        if permissions != "600":
            print("⚠️  Recommended permissions: 600 (read/write for owner only)")
            print(f"   Run: chmod 600 {htpasswd_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manage users for Kanakku Monitoring Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install dependencies first (from project root)
  pip install -e ".[dev]"

  # Create a new user (will prompt for password)
  python manage_users.py create admin

  # Create a user with password (not recommended for production)
  python manage_users.py create admin --password mypassword

  # List all users
  python manage_users.py list

  # Delete a user
  python manage_users.py delete olduser

  # Check file permissions
  python manage_users.py check

  # Use custom htpasswd file location
  python manage_users.py --file /custom/path/dashboard.htpasswd create admin
        """,
    )

    parser.add_argument(
        "--file", help="Path to htpasswd file (default: from config)", default=None
    )

    parser.add_argument(
        "--env",
        help="Environment (development, production, testing)",
        default="development",
        choices=["development", "production", "testing"],
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create user command
    create_parser = subparsers.add_parser("create", help="Create or update a user")
    create_parser.add_argument("username", help="Username to create/update")
    create_parser.add_argument(
        "--password", help="Password (will prompt if not provided)"
    )

    # List users command
    subparsers.add_parser("list", help="List all users")

    # Delete user command
    delete_parser = subparsers.add_parser("delete", help="Delete a user")
    delete_parser.add_argument("username", help="Username to delete")

    # Check permissions command
    subparsers.add_parser("check", help="Check file permissions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Set environment for config
    os.environ["FLASK_ENV"] = args.env

    # Get htpasswd file path
    if args.file:
        htpasswd_file = args.file
    else:
        config = get_config()
        htpasswd_file = config.HTPASSWD_FILE

    print(f"🔧 Environment: {args.env}")
    print(f"📁 htpasswd file: {htpasswd_file}")
    print()

    # Execute command
    if args.command == "create":
        success = create_user(htpasswd_file, args.username, args.password)
        if success:
            check_file_permissions(htpasswd_file)
        return 0 if success else 1

    elif args.command == "list":
        success = list_users(htpasswd_file)
        return 0 if success else 1

    elif args.command == "delete":
        success = delete_user(htpasswd_file, args.username)
        return 0 if success else 1

    elif args.command == "check":
        check_file_permissions(htpasswd_file)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
