#!/usr/bin/env python3
"""
Job wrapper for email automation tasks.
This module provides a simple interface that SpawnWorker can reliably import.
"""

import os
import sys

def setup_python_path():
    """Set up Python path for the spawned process."""
    # Get the absolute path to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    backend_path = os.path.join(project_root, "backend")
    banktransactions_path = os.path.join(project_root, "banktransactions")
    
    # Add to Python path if not already there
    paths_to_add = [project_root, backend_path, banktransactions_path]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Also ensure the current working directory is the project root
    if os.getcwd() != project_root:
        os.chdir(project_root)

# Set up the path immediately when this module is imported
setup_python_path()

# Now we can safely import the actual function
try:
    from banktransactions.automation.email_processor import process_user_emails_standalone as _process_emails
except ImportError as e:
    print(f"Failed to import email processor: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Looking for: banktransactions.email_automation.workers.email_processor")
    
    # Try to find the file manually
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_file = os.path.join(current_dir, "workers", "email_processor.py")
    print(f"Expected file location: {expected_file}")
    print(f"File exists: {os.path.exists(expected_file)}")
    
    # List the contents of the workers directory
    workers_dir = os.path.join(current_dir, "workers")
    if os.path.exists(workers_dir):
        print(f"Contents of workers directory: {os.listdir(workers_dir)}")
    else:
        print(f"Workers directory does not exist: {workers_dir}")
    
    raise

def process_user_emails_standalone(user_id: int):
    """
    Wrapper function for email processing that can be reliably imported by SpawnWorker.
    
    Args:
        user_id (int): The user ID to process emails for
        
    Returns:
        dict: Result of email processing
    """
    return _process_emails(user_id) 