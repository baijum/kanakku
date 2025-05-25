#!/usr/bin/env python3
"""
Check email configurations in the database
"""

import os
import sys

sys.path.append("../../backend")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import EmailConfiguration


def check_configs():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    configs = session.query(EmailConfiguration).all()
    print(f"Total email configurations: {len(configs)}")
    for config in configs:
        print(
            f"User {config.user_id}: enabled={config.is_enabled}, email={config.email_address}, last_check={config.last_check_time}"
        )
    session.close()


if __name__ == "__main__":
    check_configs()
