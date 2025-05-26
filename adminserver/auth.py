#!/usr/bin/env python3
"""
Authentication module for Kanakku Monitoring Dashboard

Provides htpasswd-based authentication functionality.
"""

import hashlib
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple

import bcrypt as bcrypt_lib

# Fix bcrypt compatibility issue with passlib
if not hasattr(bcrypt_lib, "__about__"):
    bcrypt_lib.__about__ = type(
        "about", (object,), {"__version__": bcrypt_lib.__version__}
    )

from flask import current_app, flash, redirect, request, session, url_for
from passlib.apache import HtpasswdFile

logger = logging.getLogger("kanakku-dashboard-auth")


class DashboardAuth:
    """Authentication handler for the monitoring dashboard."""

    def __init__(self, app=None):
        """Initialize the authentication handler."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the authentication with Flask app."""
        self.app = app

    def load_htpasswd_file(self) -> Optional[HtpasswdFile]:
        """Load and return the htpasswd file."""
        htpasswd_path = current_app.config.get("HTPASSWD_FILE")

        if not htpasswd_path:
            logger.error("HTPASSWD_FILE not configured")
            return None

        if not os.path.exists(htpasswd_path):
            logger.error(f"htpasswd file not found: {htpasswd_path}")
            return None

        try:
            return HtpasswdFile(htpasswd_path)
        except Exception as e:
            logger.error(f"Error loading htpasswd file {htpasswd_path}: {e}")
            return None

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password against htpasswd file."""
        try:
            htpasswd = self.load_htpasswd_file()
            if not htpasswd:
                return False

            # Check if user exists and verify password
            if username in htpasswd.users():
                return htpasswd.check_password(username, password)

            logger.warning(f"Authentication attempt for non-existent user: {username}")
            return False

        except Exception as e:
            logger.error(f"Error verifying credentials for {username}: {e}")
            return False

    def login_user(self, username: str) -> None:
        """Log in a user by setting session variables."""
        session["authenticated"] = True
        session["username"] = username
        session["login_time"] = datetime.utcnow().isoformat()
        session.permanent = True

        logger.info(
            f"User {username} logged in successfully from {request.remote_addr}"
        )

    def logout_user(self) -> None:
        """Log out the current user."""
        username = session.get("username", "unknown")
        session.clear()
        logger.info(f"User {username} logged out")

    def is_authenticated(self) -> bool:
        """Check if the current user is authenticated."""
        if not session.get("authenticated"):
            return False

        # Check session timeout
        login_time_str = session.get("login_time")
        if not login_time_str:
            return False

        try:
            login_time = datetime.fromisoformat(login_time_str)
            session_timeout = current_app.config.get("SESSION_TIMEOUT", 3600)

            if datetime.utcnow() > login_time + timedelta(seconds=session_timeout):
                logger.info(
                    f"Session expired for user {session.get('username', 'unknown')}"
                )
                self.logout_user()
                return False

        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing login time: {e}")
            self.logout_user()
            return False

        return True

    def get_current_user(self) -> Optional[str]:
        """Get the current authenticated username."""
        if self.is_authenticated():
            return session.get("username")
        return None


# Global auth instance
dashboard_auth = DashboardAuth()


def login_required(f):
    """Decorator to require authentication for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not dashboard_auth.is_authenticated():
            # Store the original URL to redirect after login
            session["next_url"] = request.url
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def create_htpasswd_file(filepath: str, username: str, password: str) -> bool:
    """
    Create a new htpasswd file with a single user.

    Args:
        filepath: Path where to create the htpasswd file
        username: Username to add
        password: Password for the user

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create htpasswd file
        htpasswd = HtpasswdFile(filepath, new=True)
        htpasswd.set_password(username, password)
        htpasswd.save()

        logger.info(f"Created htpasswd file: {filepath}")
        return True

    except Exception as e:
        logger.error(f"Error creating htpasswd file {filepath}: {e}")
        return False


def add_user_to_htpasswd(filepath: str, username: str, password: str) -> bool:
    """
    Add a user to an existing htpasswd file.

    Args:
        filepath: Path to the htpasswd file
        username: Username to add
        password: Password for the user

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(filepath):
            return create_htpasswd_file(filepath, username, password)

        htpasswd = HtpasswdFile(filepath)
        htpasswd.set_password(username, password)
        htpasswd.save()

        logger.info(f"Added/updated user {username} in htpasswd file: {filepath}")
        return True

    except Exception as e:
        logger.error(f"Error adding user to htpasswd file {filepath}: {e}")
        return False
