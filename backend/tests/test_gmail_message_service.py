"""
Tests for gmail_message_service module
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import ProcessedGmailMessage
from app.services.gmail_message_service import (
    clear_processed_gmail_msgids,
    get_processed_message_count,
    is_gmail_message_processed,
    load_processed_gmail_msgids,
    save_processed_gmail_msgid,
    save_processed_gmail_msgids,
)


class TestGmailMessageService:
    """Test cases for Gmail message service functions"""

    def test_load_processed_gmail_msgids_empty(self, app, db_session, user):
        """Test loading processed message IDs when none exist"""
        with app.app_context():
            msgids = load_processed_gmail_msgids(user.id, db_session)

        assert msgids == set()

    def test_load_processed_gmail_msgids_with_data(self, app, db_session, user):
        """Test loading processed message IDs with existing data"""
        # Create test data
        msg1 = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_123",
            processed_at=datetime.now(timezone.utc),
        )
        msg2 = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_456",
            processed_at=datetime.now(timezone.utc),
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()

        with app.app_context():
            msgids = load_processed_gmail_msgids(user.id, db_session)

        assert msgids == {"msg_123", "msg_456"}

    def test_load_processed_gmail_msgids_database_error(self, app, user):
        """Test loading processed message IDs with database error"""
        with app.app_context():
            with patch("app.services.gmail_message_service.db.session") as mock_session:
                mock_session.query.side_effect = Exception("Database error")

                msgids = load_processed_gmail_msgids(user.id)

        assert msgids == set()

    def test_save_processed_gmail_msgid_success(self, app, db_session, user):
        """Test successfully saving a processed message ID"""
        with app.app_context():
            result = save_processed_gmail_msgid(user.id, "msg_789", db_session)

        assert result is True

        # Verify it was saved
        saved_msg = (
            db_session.query(ProcessedGmailMessage)
            .filter_by(user_id=user.id, gmail_message_id="msg_789")
            .first()
        )
        assert saved_msg is not None
        assert saved_msg.gmail_message_id == "msg_789"

    def test_save_processed_gmail_msgid_duplicate(self, app, db_session, user):
        """Test saving a duplicate message ID (should handle gracefully)"""
        # Create existing message
        existing_msg = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_duplicate",
            processed_at=datetime.now(timezone.utc),
        )
        db_session.add(existing_msg)
        db_session.commit()

        with app.app_context():
            result = save_processed_gmail_msgid(user.id, "msg_duplicate", db_session)

        assert result is True  # Should still return True for duplicates

    def test_save_processed_gmail_msgid_database_error(self, app, user):
        """Test saving message ID with database error"""
        with app.app_context():
            with patch("app.services.gmail_message_service.db.session") as mock_session:
                mock_session.add.side_effect = Exception("Database error")

                result = save_processed_gmail_msgid(user.id, "msg_error")

        assert result is False

    def test_save_processed_gmail_msgids_empty_set(self, app, db_session, user):
        """Test saving empty set of message IDs"""
        with app.app_context():
            result = save_processed_gmail_msgids(user.id, set(), db_session)

        assert result == 0

    def test_save_processed_gmail_msgids_new_messages(self, app, db_session, user):
        """Test saving multiple new message IDs"""
        msgids = {"msg_new1", "msg_new2", "msg_new3"}

        with app.app_context():
            result = save_processed_gmail_msgids(user.id, msgids, db_session)

        assert result == 3

        # Verify all were saved
        saved_count = (
            db_session.query(ProcessedGmailMessage).filter_by(user_id=user.id).count()
        )
        assert saved_count == 3

    def test_save_processed_gmail_msgids_mixed_new_existing(
        self, app, db_session, user
    ):
        """Test saving mix of new and existing message IDs"""
        # Create existing message
        existing_msg = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_existing",
            processed_at=datetime.now(timezone.utc),
        )
        db_session.add(existing_msg)
        db_session.commit()

        msgids = {"msg_existing", "msg_new1", "msg_new2"}

        with app.app_context():
            result = save_processed_gmail_msgids(user.id, msgids, db_session)

        assert result == 2  # Only 2 new messages saved

        # Verify total count
        saved_count = (
            db_session.query(ProcessedGmailMessage).filter_by(user_id=user.id).count()
        )
        assert saved_count == 3

    def test_save_processed_gmail_msgids_database_error(self, app, user):
        """Test saving message IDs with database error"""
        msgids = {"msg_error1", "msg_error2"}

        with app.app_context():
            with patch(
                "app.services.gmail_message_service.load_processed_gmail_msgids"
            ) as mock_load:
                mock_load.side_effect = Exception("Database error")

                result = save_processed_gmail_msgids(user.id, msgids)

        assert result == 0

    def test_is_gmail_message_processed_true(self, app, db_session, user):
        """Test checking if message is processed (exists)"""
        # Create existing message
        existing_msg = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_check",
            processed_at=datetime.now(timezone.utc),
        )
        db_session.add(existing_msg)
        db_session.commit()

        with app.app_context():
            result = is_gmail_message_processed(user.id, "msg_check", db_session)

        assert result is True

    def test_is_gmail_message_processed_false(self, app, db_session, user):
        """Test checking if message is processed (doesn't exist)"""
        with app.app_context():
            result = is_gmail_message_processed(user.id, "msg_nonexistent", db_session)

        assert result is False

    def test_is_gmail_message_processed_database_error(self, app, user):
        """Test checking message processed status with database error"""
        with app.app_context():
            with patch("app.services.gmail_message_service.db.session") as mock_session:
                mock_session.query.side_effect = Exception("Database error")

                result = is_gmail_message_processed(user.id, "msg_error")

        assert result is False

    def test_get_processed_message_count_zero(self, app, db_session, user):
        """Test getting count when no messages exist"""
        with app.app_context():
            count = get_processed_message_count(user.id, db_session)

        assert count == 0

    def test_get_processed_message_count_with_data(self, app, db_session, user):
        """Test getting count with existing messages"""
        # Create test messages
        for i in range(5):
            msg = ProcessedGmailMessage(
                user_id=user.id,
                gmail_message_id=f"msg_count_{i}",
                processed_at=datetime.now(timezone.utc),
            )
            db_session.add(msg)
        db_session.commit()

        with app.app_context():
            count = get_processed_message_count(user.id, db_session)

        assert count == 5

    def test_get_processed_message_count_database_error(self, app, user):
        """Test getting count with database error"""
        with app.app_context():
            with patch("app.services.gmail_message_service.db.session") as mock_session:
                mock_session.query.side_effect = Exception("Database error")

                count = get_processed_message_count(user.id)

        assert count == 0

    def test_clear_processed_gmail_msgids_success(self, app, db_session, user):
        """Test successfully clearing processed message IDs"""
        # Create test messages
        for i in range(3):
            msg = ProcessedGmailMessage(
                user_id=user.id,
                gmail_message_id=f"msg_clear_{i}",
                processed_at=datetime.now(timezone.utc),
            )
            db_session.add(msg)
        db_session.commit()

        with app.app_context():
            result = clear_processed_gmail_msgids(user.id, db_session)

        assert result is True

        # Verify messages were deleted
        remaining_count = (
            db_session.query(ProcessedGmailMessage).filter_by(user_id=user.id).count()
        )
        assert remaining_count == 0

    def test_clear_processed_gmail_msgids_database_error(self, app, user):
        """Test clearing message IDs with database error"""
        with app.app_context():
            with patch("app.services.gmail_message_service.db.session") as mock_session:
                mock_session.query.side_effect = Exception("Database error")

                result = clear_processed_gmail_msgids(user.id)

        assert result is False

    def user_isolation(self, app, db_session, user, user_2):
        """Test that users can only access their own processed messages"""
        # Create messages for both users
        msg1 = ProcessedGmailMessage(
            user_id=user.id,
            gmail_message_id="msg_user1",
            processed_at=datetime.now(timezone.utc),
        )
        msg2 = ProcessedGmailMessage(
            user_id=user_2.id,
            gmail_message_id="msg_user2",
            processed_at=datetime.now(timezone.utc),
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()

        with app.app_context():
            # User 1 should only see their message
            user1_msgids = load_processed_gmail_msgids(user.id, db_session)
            assert user1_msgids == {"msg_user1"}

            # User 2 should only see their message
            user2_msgids = load_processed_gmail_msgids(user_2.id, db_session)
            assert user2_msgids == {"msg_user2"}

            # User 1 should not see user 2's message as processed
            assert not is_gmail_message_processed(user.id, "msg_user2", db_session)
            assert not is_gmail_message_processed(user_2.id, "msg_user1", db_session)
