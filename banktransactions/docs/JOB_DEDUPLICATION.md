# Email Automation Job Deduplication

## Overview

This document describes the implementation of job deduplication for the email automation system to prevent multiple jobs from being queued for the same user simultaneously.

## Problem Statement

Previously, the email automation system could queue multiple jobs for the same user, leading to:

1. **Resource waste** - Multiple workers processing the same user's emails
2. **Race conditions** - Concurrent updates to `last_check_time` and email processing
3. **IMAP connection issues** - Multiple simultaneous connections to the same email account
4. **Duplicate transaction processing** - Risk of processing the same emails multiple times

## Implemented Solutions

### 1. Job Deduplication (`job_utils.py`)

Created a comprehensive utility module with functions to check job status:

- `generate_job_id(user_id, timestamp)` - Creates consistent job IDs
- `is_user_job_running(redis_conn, user_id)` - Checks for running jobs
- `is_user_job_scheduled(redis_conn, user_id)` - Checks for scheduled jobs  
- `is_user_job_queued(redis_conn, user_id)` - Checks for queued jobs
- `has_user_job_pending(redis_conn, user_id)` - Checks all job states
- `get_user_job_status(redis_conn, user_id)` - Returns comprehensive status

### 2. Consistent Job IDs

**Before:**
```python
# Scheduler used timestamp-based IDs
job_id=f"email_process_{config.user_id}_{next_run.timestamp()}"

# Manual trigger used random IDs
job = queue.enqueue(process_user_emails_standalone, user_id, job_timeout="10m")
```

**After:**
```python
# Both use the same ID generation function
job_id = generate_job_id(user_id, timestamp)
job = queue.enqueue(
    process_user_emails_standalone, 
    user_id, 
    job_id=job_id,
    job_timeout="10m"
)
```

### 3. Scheduler Deduplication

**Updated `EmailScheduler._schedule_user_job()`:**

```python
def _schedule_user_job(self, config: EmailConfiguration):
    try:
        # Check if user already has a pending job
        if has_user_job_pending(self.redis_conn, config.user_id):
            job_status = get_user_job_status(self.redis_conn, config.user_id)
            logger.info(f"Skipping job scheduling for user {config.user_id} - job already pending: {job_status}")
            return

        # Calculate next run time
        next_run = self._calculate_next_run(config)
        if not next_run:
            return

        # Generate consistent job ID
        job_id = generate_job_id(config.user_id, next_run)

        # Schedule the job
        self.scheduler.enqueue_at(
            next_run,
            process_user_emails_standalone,
            config.user_id,
            job_id=job_id,
            queue_name="email_processing",
        )

        logger.info(f"Scheduled job {job_id} for user {config.user_id}")
    except Exception as e:
        logger.error(f"Error scheduling job for user {config.user_id}: {str(e)}")
```

### 4. Manual Trigger Deduplication

**Updated `trigger_email_processing()` endpoint:**

```python
# Check if user already has a pending job
if has_user_job_pending(redis_conn, user_id):
    job_status = get_user_job_status(redis_conn, user_id)
    return (
        jsonify({
            "success": False,
            "error": "Email processing job already pending for this user",
            "job_status": job_status,
        }),
        409,  # Conflict status code
    )

# Generate consistent job ID
job_id = generate_job_id(user_id)

# Enqueue with explicit job ID
job = queue.enqueue(
    process_user_emails_standalone, 
    user_id, 
    job_id=job_id,
    job_timeout="10m"
)
```

### 5. Frontend Handling

**Updated `handleTriggerProcessing()` in React component:**

```javascript
catch (err) {
  if (err.response?.status === 409) {
    // Conflict - job already pending
    const jobStatus = err.response.data.job_status;
    let statusMessage = 'An email processing job is already pending for your account.';
    
    if (jobStatus) {
      const statusParts = [];
      if (jobStatus.has_running_job) statusParts.push('running');
      if (jobStatus.has_scheduled_job) statusParts.push('scheduled');
      if (jobStatus.has_queued_job) statusParts.push('queued');
      
      if (statusParts.length > 0) {
        statusMessage += ` Status: ${statusParts.join(', ')}.`;
      }
    }
    
    setError(statusMessage);
  } else {
    setError(err.response?.data?.error || 'Failed to trigger email processing');
  }
}
```

## Job States Checked

The deduplication system checks for jobs in three states:

1. **Running** - Jobs currently being processed by workers
2. **Scheduled** - Jobs scheduled for future execution
3. **Queued** - Jobs waiting in the queue to be picked up by workers

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd banktransactions/email_automation
python test_scheduler_deduplication.py
```

### Integration Tests

Test with real Redis:

```bash
cd banktransactions/email_automation
python test_deduplication.py
```

### Manual Testing

1. **Test Scheduler Deduplication:**
   ```bash
   # Start scheduler
   python run_scheduler.py --interval 60
   
   # Check logs for "Skipping job scheduling" messages
   tail -f ../logs/scheduler.log
   ```

2. **Test Manual Trigger Deduplication:**
   - Go to Email Automation settings in the UI
   - Click "TRIGGER PROCESSING" multiple times quickly
   - Should see conflict message after first click

## Benefits

### Before Implementation
- ❌ Multiple jobs could be queued for same user
- ❌ Resource waste and race conditions
- ❌ Inconsistent job IDs between scheduler and manual triggers
- ❌ No user feedback about existing jobs

### After Implementation
- ✅ Only one job per user at any time
- ✅ Consistent job ID generation
- ✅ Comprehensive job status checking
- ✅ Clear user feedback about job conflicts
- ✅ Reduced resource usage and improved reliability

## Monitoring

### Log Messages

**Scheduler skipping duplicate:**
```
INFO - Skipping job scheduling for user 123 - job already pending: {'user_id': 123, 'has_running_job': True, ...}
```

**Successful scheduling:**
```
INFO - Scheduled job email_process_123_1234567890 for user 123 (user@example.com) at 2024-01-01 12:00:00
```

**Manual trigger conflict:**
```
409 Conflict - Email processing job already pending for this user
```

### Redis Queue Inspection

Check job status using the debug tools:

```bash
cd hack
python debug_redis_queue.py --status
```

## Error Handling

The implementation includes robust error handling:

1. **Redis connection failures** - Functions return `False` and log errors
2. **Job fetch failures** - Individual job errors don't stop the entire check
3. **Scheduler errors** - Caught and logged, don't crash the scheduler
4. **API errors** - Return appropriate HTTP status codes

## Future Enhancements

1. **Job Priority** - Allow high-priority manual triggers to cancel scheduled jobs
2. **Job Queuing** - Queue manual triggers to run after current job completes
3. **User Notifications** - Notify users when their scheduled jobs complete
4. **Metrics** - Track job deduplication statistics
5. **Admin Interface** - Allow admins to view and manage all user jobs

## Files Modified

1. **`banktransactions/email_automation/workers/job_utils.py`** - New utility module
2. **`banktransactions/email_automation/workers/scheduler.py`** - Added deduplication logic
3. **`backend/app/email_automation.py`** - Updated manual trigger endpoint
4. **`frontend/src/components/Auth/EmailAutomation.jsx`** - Handle conflict responses
5. **Test files** - Comprehensive test coverage

## Backward Compatibility

The implementation is fully backward compatible:

- Existing jobs continue to work normally
- No database schema changes required
- No breaking changes to the API
- Graceful degradation if Redis is unavailable 