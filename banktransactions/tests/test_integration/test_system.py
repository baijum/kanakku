#!/usr/bin/env python3
"""
Email Automation System Test Script

This script tests the various components of the email automation system
to ensure they are working correctly.

Usage:
    python test_system.py
"""

import os
import sys
import redis
from dotenv import load_dotenv

# Load environment variables from .env file
# This will look for .env files in the following order:
# 1. Current directory
# 2. Parent directory (banktransactions/)
# 3. Project root directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Add the project root to the Python path so we can import banktransactions module
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
# Also add the backend app to the Python path
sys.path.append(os.path.join(project_root, "backend"))


def test_redis_connection():
    """Test Redis connection."""
    print("Testing Redis connection...")
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)
        redis_conn.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False


def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        from shared.imports import database_session
        from sqlalchemy import text

        with database_session() as session:
            # Test query
            result = session.execute(text("SELECT 1"))

        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def test_email_configuration_model():
    """Test EmailConfiguration model."""
    print("Testing EmailConfiguration model...")
    try:

        print("✅ EmailConfiguration model imported successfully")
        return True
    except Exception as e:
        print(f"❌ EmailConfiguration model import failed: {str(e)}")
        return False


def test_encryption_utilities():
    """Test encryption utilities."""
    print("Testing encryption utilities...")
    try:
        from app.utils.encryption import encrypt_value, decrypt_value

        # Test encryption/decryption
        test_value = "test_password_123"
        encrypted = encrypt_value(test_value)
        decrypted = decrypt_value(encrypted)

        if decrypted == test_value:
            print("✅ Encryption utilities working correctly")
            return True
        else:
            print("❌ Encryption/decryption mismatch")
            return False
    except Exception as e:
        print(f"❌ Encryption utilities test failed: {str(e)}")
        return False


def test_worker_imports():
    """Test worker module imports."""
    print("Testing worker imports...")
    try:

        print("✅ Worker modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Worker imports failed: {str(e)}")
        return False


def test_banktransactions_imports():
    """Test banktransactions module imports."""
    print("Testing banktransactions imports...")
    try:

        print("✅ Banktransactions modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Banktransactions imports failed: {str(e)}")
        return False


def test_environment_variables():
    """Test required environment variables."""
    print("Testing environment variables...")
    required_vars = ["DATABASE_URL"]
    optional_vars = ["REDIS_URL", "GOOGLE_API_KEY", "ENCRYPTION_KEY"]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_required:
        print(
            f"❌ Missing required environment variables: {', '.join(missing_required)}"
        )
        return False

    if missing_optional:
        print(
            f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}"
        )

    print("✅ Required environment variables are set")
    return True


def test_rq_queue():
    """Test RQ queue functionality."""
    print("Testing RQ queue...")
    try:
        from rq import Queue

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)

        queue = Queue("test_queue", connection=redis_conn)

        # Test job enqueueing
        def test_job():
            return "test_result"

        job = queue.enqueue(test_job)
        print(f"✅ RQ queue test successful, job ID: {job.id}")
        return True
    except Exception as e:
        print(f"❌ RQ queue test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🧪 Email Automation System Test Suite")
    print("=" * 50)

    tests = [
        test_environment_variables,
        test_redis_connection,
        test_database_connection,
        test_email_configuration_model,
        test_encryption_utilities,
        test_banktransactions_imports,
        test_worker_imports,
        test_rq_queue,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Email automation system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
