"""
Automation modules for email processing and scheduling.

This package contains the automation system for:
- Background email processing workers
- Job scheduling and management
- Email processing workflows
- Job utilities and helpers
"""

# Export main functions for easy access
from .email_processor import process_user_emails_standalone
from .job_utils import generate_job_id, has_user_job_pending, get_user_job_status
from .job_wrapper import process_user_emails_standalone as process_emails_wrapper

# Import EmailScheduler conditionally since it depends on Flask models
try:
    from .scheduler import EmailScheduler
    _scheduler_available = True
except ImportError:
    EmailScheduler = None
    _scheduler_available = False

__all__ = [
    'process_user_emails_standalone',
    'generate_job_id',
    'has_user_job_pending', 
    'get_user_job_status',
    'process_emails_wrapper'
]

# Add EmailScheduler to __all__ if available
if _scheduler_available:
    __all__.append('EmailScheduler')
