"""
Backend package for Kanakku

This package provides the Flask web application and API for the Kanakku
personal finance management system.
"""

import os
import sys
from pathlib import Path


def setup_backend_paths():
    """
    Set up Python paths for backend imports.
    This ensures that 'app' imports work correctly when the backend
    module is imported from outside the backend directory.
    """
    # Get the backend directory (where this __init__.py is located)
    backend_dir = Path(__file__).parent.absolute()
    
    # Add backend directory to Python path so 'app' imports work
    backend_str = str(backend_dir)
    if backend_str not in sys.path:
        sys.path.insert(0, backend_str)


# Automatically set up paths when this module is imported
setup_backend_paths()

# Version information
__version__ = "1.0.0"
__author__ = "Kanakku Team"
