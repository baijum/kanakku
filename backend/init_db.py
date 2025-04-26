from dotenv import load_dotenv

from app import create_app, db


def init_db():
    load_dotenv()  # Load environment variables from .env file
    app = create_app()
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
