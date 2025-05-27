#!/usr/bin/env python3
"""
Database migration checker for Kanakku deployment.

This script checks if database tables exist and handles migration stamping
to avoid conflicts during deployment.
"""

import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["FLASK_ENV"] = "production"
os.environ["FLASK_SKIP_DB_CREATE"] = "1"


def check_tables_exist():
    """Check if database tables exist."""
    try:
        from app import create_app
        from app.extensions import db

        app = create_app("production")

        with app.app_context():
            # Try to query the user table to see if schema exists
            from sqlalchemy import text

            with db.engine.connect() as connection:
                result = connection.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables WHERE table_name = 'user'"
                    )
                )
                exists = result.fetchone() is not None
                return exists

    except Exception as e:
        logging.error(f"Error checking tables: {e}")
        return False


def main():
    """Main function to check migration status."""
    if check_tables_exist():
        print("TABLES_EXIST")
        sys.exit(0)
    else:
        print("TABLES_NOT_EXIST")
        sys.exit(1)


if __name__ == "__main__":
    main()
