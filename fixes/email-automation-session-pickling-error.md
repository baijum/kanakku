# Email Automation Session Pickling Error

## Problem Description

When clicking on 'TRIGGER PROCESSING' in the Email Automation settings under Profile Settings, the system was showing this error:

```
Failed to queue email processing job: Can't pickle <class 'sqlalchemy.orm.session.Session'>: it's not the same object as sqlalchemy.orm.session.Session
```

## Root Cause Analysis

The issue was in the `trigger_email_processing` function in `backend/app/email_automation.py`. The code was attempting to:

1. Create a SQLAlchemy database session in the web application process
2. Pass this session to the `EmailProcessor` constructor
3. Enqueue the `EmailProcessor` instance method to Redis Queue (RQ)

However, RQ uses Python's `pickle` module to serialize job arguments for storage in Redis. SQLAlchemy session objects cannot be pickled because they contain database connections, locks, and other non-serializable state.

### Problematic Code

```python
# This was the problematic approach
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db_session = Session()

job = queue.enqueue(
    EmailProcessor(db_session).process_user_emails, user_id, job_timeout="10m"
)
```

## Solution Implemented

Created a standalone function `process_user_emails_standalone` that:

1. Creates its own database session within the worker process
2. Can be safely pickled by RQ since it doesn't contain any session state
3. Properly manages the database session lifecycle (creation and cleanup)

### New Approach

```python
def process_user_emails_standalone(user_id: int) -> Dict:
    """
    Standalone function to process emails for a user.
    This creates its own database session and can be safely pickled by RQ.
    """
    db_session = None
    try:
        # Create database session within the worker
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create EmailProcessor instance with the new session
        processor = EmailProcessor(db_session)
        
        # Process emails
        result = processor.process_user_emails(user_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_user_emails_standalone: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        if db_session:
            db_session.close()
```

### Updated Queue Usage

```python
# Import the standalone function
from banktransactions.email_automation.workers.email_processor import (
    process_user_emails_standalone,
)

# Enqueue using the standalone function
job = queue.enqueue(
    process_user_emails_standalone, user_id, job_timeout="10m"
)
```

## Files Modified

1. **`banktransactions/email_automation/workers/email_processor.py`**
   - Added `process_user_emails_standalone` function
   - Added necessary imports for SQLAlchemy session creation

2. **`backend/app/email_automation.py`**
   - Updated `trigger_email_processing` function to use the standalone function
   - Removed session creation code from the web application process

3. **`banktransactions/email_automation/workers/scheduler.py`**
   - Updated to use the standalone function for scheduled jobs
   - Changed import from `EmailProcessor` to `process_user_emails_standalone`

4. **`banktransactions/email_automation/run_worker.py`**
   - Removed unused `EmailProcessor` import

## Key Lessons Learned

1. **RQ Serialization**: RQ requires all job arguments to be picklable. Database sessions, file handles, and other stateful objects cannot be passed directly.

2. **Session Management**: Database sessions should be created within the worker process, not passed from the web application process.

3. **Separation of Concerns**: The web application should only be responsible for queuing jobs, while workers should handle their own resource management.

4. **Error Handling**: Always ensure proper cleanup of resources (like database sessions) in worker functions using try/finally blocks.

## Testing

After implementing this fix:

1. The 'TRIGGER PROCESSING' button in Email Automation settings should work without errors
2. Jobs should be successfully queued to Redis
3. Workers should be able to process the jobs and create their own database sessions
4. No pickling errors should occur

## Prevention

To prevent similar issues in the future:

1. Always consider serializability when designing RQ job functions
2. Keep job functions stateless and self-contained
3. Create resources (database sessions, file handles) within the worker process
4. Use standalone functions rather than class methods for RQ jobs when possible

## Update (Post-Fix)

**Note**: The legacy `EmailProcessor` class referenced in this document has been subsequently removed from the codebase. The system now uses only the `process_user_emails_standalone` function, which was the solution implemented to fix this pickling issue. 