import os
import logging
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from email_automation.workers.scheduler import EmailScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)

        # Initialize database connection
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()

        # Initialize scheduler
        scheduler = EmailScheduler(redis_conn, db_session)

        # Schedule jobs
        logger.info("Starting email scheduler...")
        scheduler.schedule_jobs()
        logger.info("Email scheduler started successfully")

    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise


if __name__ == "__main__":
    main()
