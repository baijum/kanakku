#!/usr/bin/env python3
"""
Check email configurations in the database
"""

import os
import sys
from pathlib import Path

# Set up project paths
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from shared.imports import setup_project_paths, database_session, EmailConfiguration

setup_project_paths()


def check_configs():
    try:
        with database_session() as session:
            configs = session.query(EmailConfiguration).all()
            print(f"Total email configurations: {len(configs)}")
            for config in configs:
                print(
                    f"User {config.user_id}: enabled={config.is_enabled}, email={config.email_address}, last_check={config.last_check_time}"
                )
    except Exception as e:
        print(f"Error checking configurations: {e}")


if __name__ == "__main__":
    check_configs()
