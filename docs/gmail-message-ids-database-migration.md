# Gmail Message IDs Database Migration

## Overview

This document describes the architectural change from file-based storage to database-based storage for Gmail Message IDs in the kanakku application.

## Background

Previously, the application stored processed Gmail Message IDs in a text file (`processed_gmail_msgids.txt`) to avoid reprocessing the same emails. This approach had several limitations:

1. **No user isolation**: All users shared the same file
2. **Concurrency issues**: Multiple processes could conflict when accessing the file
3. **Scalability problems**: File-based storage doesn't scale well
4. **Data integrity**: Risk of file corruption or loss

## New Architecture

### Database Table

A new table `processed_gmail_messages` has been created with the following structure:

```sql
CREATE TABLE processed_gmail_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user(id),
    gmail_message_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP,
    created_at TIMESTAMP,
    CONSTRAINT uq_user_gmail_message UNIQUE (user_id, gmail_message_id)
);
```

### Key Features

1. **User isolation**: Each user has their own processed message IDs
2. **Data integrity**: Database constraints prevent duplicates
3. **Audit trail**: Timestamps track when messages were processed
4. **Scalability**: Database storage scales better than files

### Database Model

```python
class ProcessedGmailMessage(db.Model):
    __tablename__ = "processed_gmail_messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    gmail_message_id = Column(String(255), nullable=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="processed_gmail_messages", lazy=True)
    
    __table_args__ = (
        UniqueConstraint("user_id", "gmail_message_id", name="uq_user_gmail_message"),
    )
```

## Service Layer

### New Gmail Message Service

A new service module `app/services/gmail_message_service.py` provides database operations:

- `load_processed_gmail_msgids(user_id)`: Load processed IDs for a user
- `save_processed_gmail_msgid(user_id, msgid)`: Save a single ID for a user (recommended)
- `save_processed_gmail_msgids(user_id, msgids)`: Save multiple IDs for a user (bulk operation)
- `is_gmail_message_processed(user_id, msgid)`: Check if an ID is processed
- `get_processed_message_count(user_id)`: Get count of processed messages
- `clear_processed_gmail_msgids(user_id)`: Clear all processed IDs for a user

### Backward Compatibility

A new module `banktransactions/processed_ids_db.py` provides the same interface as the original `processed_ids.py` but uses database storage. It includes fallback to file-based storage if the database is unavailable.

## Migration Process

### Database Migration

1. Created migration file: `b97344b3383f_add_processed_gmail_messages_table.py`
2. Applied migration: `flask db upgrade`

### Code Changes

1. **New Model**: Added `ProcessedGmailMessage` to `backend/app/models.py`
2. **New Service**: Created `backend/app/services/gmail_message_service.py`
3. **Database Adapter**: Created `banktransactions/processed_ids_db.py`
4. **Updated Email Processor**: Modified `banktransactions/email_automation/workers/email_processor.py` to use database approach

### Updated Components

- `banktransactions/email_automation/workers/email_processor.py`: Now uses database-based storage with user context and individual message ID saves
- `banktransactions/processed_ids_db.py`: New database adapter with fallback support
- `banktransactions/imap_client.py`: Enhanced to support callback functions for individual message ID saves

## Usage

### Callback-Based Approach (Recommended)

The new architecture uses a callback-based approach where Gmail Message IDs are saved to the database individually as they are processed, rather than in bulk at the end. This provides better error handling and immediate persistence.

```python
from banktransactions.imap_client import get_bank_emails
from banktransactions.processed_ids_db import load_processed_gmail_msgids, save_processed_gmail_msgid

# Create a callback function to save individual message IDs
def save_msgid_to_db(gmail_message_id):
    try:
        result = save_processed_gmail_msgid(gmail_message_id, user_id=user_id)
        return result
    except Exception as e:
        logging.error(f"Error saving Gmail Message ID {gmail_message_id}: {e}")
        return False

# Load existing processed IDs
processed_msgids = load_processed_gmail_msgids(user_id=user_id)

# Process emails with callback
updated_msgids, newly_processed_count = get_bank_emails(
    username=email_address,
    password=password,
    bank_email_list=bank_emails,
    processed_gmail_msgids=processed_msgids,
    save_msgid_callback=save_msgid_to_db
)
```

### For Email Processing Workers

```python
from banktransactions.processed_ids_db import load_processed_gmail_msgids, save_processed_gmail_msgid

# Load processed IDs for a specific user
processed_msgids = load_processed_gmail_msgids(user_id=user_id)

# Save individual IDs as they are processed (recommended approach)
save_processed_gmail_msgid(gmail_message_id, user_id=user_id)
```

### For Backend Services

```python
from app.services.gmail_message_service import (
    load_processed_gmail_msgids,
    save_processed_gmail_msgid,
    is_gmail_message_processed
)

# Within Flask app context
with app.app_context():
    # Load processed IDs
    msgids = load_processed_gmail_msgids(user_id)
    
    # Check if processed
    is_processed = is_gmail_message_processed(user_id, gmail_message_id)
    
    # Save single ID
    save_processed_gmail_msgid(user_id, gmail_message_id)
```

## Benefits

1. **User Isolation**: Each user's processed messages are separate
2. **Data Integrity**: Database constraints prevent duplicates and ensure consistency
3. **Scalability**: Database storage scales better than file-based storage
4. **Audit Trail**: Timestamps provide processing history
5. **Concurrency**: Database handles concurrent access properly
6. **Backup/Recovery**: Processed IDs are included in database backups
7. **Immediate Persistence**: Individual message IDs are saved immediately as processed
8. **Better Error Handling**: Failed saves don't affect other message processing
9. **Real-time Tracking**: Processing status is updated in real-time

## Backward Compatibility

The original file-based approach is still supported as a fallback. The `processed_ids_db.py` module will automatically fall back to file-based storage if:

1. The database is unavailable
2. No user_id is provided
3. The Flask app context is not available

## Testing

The new service has been tested with:

1. Loading empty processed message sets
2. Saving single and multiple message IDs
3. Checking processed status
4. Handling duplicate message IDs
5. Getting message counts
6. Clearing processed messages

All tests pass successfully, confirming the database operations work correctly.

## Future Considerations

1. **Data Migration**: Consider migrating existing file-based data to the database
2. **Cleanup**: Remove old file-based storage after confirming database approach works
3. **Monitoring**: Add monitoring for database performance and storage usage
4. **Archiving**: Consider archiving old processed message records periodically 