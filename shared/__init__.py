"""
Shared utilities package for Kanakku project.

This package provides common functionality that can be used by both
the backend Flask application and the banktransactions processing modules.
"""

import os
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BACKEND_PATH = PROJECT_ROOT / "backend"
BANKTRANSACTIONS_PATH = PROJECT_ROOT / "banktransactions"

def setup_project_paths():
    """
    Set up Python paths for cross-module imports.
    This should be called once at the beginning of any module that needs
    to import from other parts of the project.
    """
    paths_to_add = [
        str(PROJECT_ROOT),
        str(BACKEND_PATH),
        str(BANKTRANSACTIONS_PATH),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

# Automatically set up paths when this module is imported
setup_project_paths()

# Version information
__version__ = "1.0.0"
__author__ = "Kanakku Team" 