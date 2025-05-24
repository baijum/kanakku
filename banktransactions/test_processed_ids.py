#!/usr/bin/env python3

import pytest
import tempfile
import os
import sys
import logging
from unittest.mock import patch, mock_open

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from banktransactions.processed_ids import (
        load_processed_gmail_msgids,
        save_processed_gmail_msgids,
        PROCESSED_GMAIL_MSGIDS_FILE
    )
except ImportError:
    # Fallback to relative import if running from within the directory
    from processed_ids import (
        load_processed_gmail_msgids,
        save_processed_gmail_msgids,
        PROCESSED_GMAIL_MSGIDS_FILE
    )


class TestProcessedIds:
    """Test cases for the processed_ids module functions."""

    def test_load_processed_gmail_msgids_success(self):
        """Test successful loading of processed Gmail message IDs."""
        # Create a temporary file with test data
        test_msgids = ["123456789", "987654321", "555666777"]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for msgid in test_msgids:
                f.write(f"{msgid}\n")
            temp_file_path = f.name
        
        try:
            result = load_processed_gmail_msgids(temp_file_path)
            
            assert isinstance(result, set)
            assert len(result) == 3
            assert "123456789" in result
            assert "987654321" in result
            assert "555666777" in result
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_processed_gmail_msgids_file_not_found(self, caplog):
        """Test behavior when the processed IDs file doesn't exist."""
        non_existent_path = "/path/that/does/not/exist.txt"
        
        with caplog.at_level(logging.INFO):
            result = load_processed_gmail_msgids(non_existent_path)
        
        assert isinstance(result, set)
        assert len(result) == 0
        assert f"Processed Gmail Message IDs file ({non_existent_path}) not found" in caplog.text

    def test_load_processed_gmail_msgids_with_invalid_lines(self):
        """Test loading file with invalid (non-digit) lines."""
        test_content = """123456789
invalid_line
987654321
another_invalid
555666777
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            result = load_processed_gmail_msgids(temp_file_path)
            
            # Should only include valid digit lines
            assert isinstance(result, set)
            assert len(result) == 3
            assert "123456789" in result
            assert "987654321" in result
            assert "555666777" in result
            assert "invalid_line" not in result
            assert "another_invalid" not in result
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_processed_gmail_msgids_empty_file(self):
        """Test loading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("")  # Empty file
            temp_file_path = f.name
        
        try:
            result = load_processed_gmail_msgids(temp_file_path)
            
            assert isinstance(result, set)
            assert len(result) == 0
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_processed_gmail_msgids_with_whitespace(self):
        """Test loading file with whitespace and empty lines."""
        test_content = """
123456789

987654321
   
555666777
   
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            result = load_processed_gmail_msgids(temp_file_path)
            
            assert isinstance(result, set)
            assert len(result) == 3
            assert "123456789" in result
            assert "987654321" in result
            assert "555666777" in result
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_load_processed_gmail_msgids_permission_error(self, mock_file, caplog):
        """Test behavior when file cannot be opened due to permissions."""
        test_path = "/some/test/path.txt"
        
        with caplog.at_level(logging.ERROR):
            result = load_processed_gmail_msgids(test_path)
        
        assert isinstance(result, set)
        assert len(result) == 0
        assert f"Error loading processed Gmail Message IDs from {test_path}" in caplog.text

    def test_save_processed_gmail_msgids_success(self, caplog):
        """Test successful saving of processed Gmail message IDs."""
        test_msgids = {"123456789", "987654321", "555666777"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file_path = f.name
        
        try:
            with caplog.at_level(logging.INFO):
                save_processed_gmail_msgids(test_msgids, temp_file_path)
            
            # Verify the file was created and contains correct data
            with open(temp_file_path, 'r') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            assert len(lines) == 3
            
            # Should be sorted
            assert lines == sorted(list(test_msgids))
            
            assert f"Saved {len(test_msgids)} processed Gmail Message IDs to {temp_file_path}" in caplog.text
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_save_processed_gmail_msgids_empty_set(self, caplog):
        """Test saving an empty set of message IDs."""
        test_msgids = set()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file_path = f.name
        
        try:
            with caplog.at_level(logging.INFO):
                save_processed_gmail_msgids(test_msgids, temp_file_path)
            
            # Verify the file was created and is empty
            with open(temp_file_path, 'r') as f:
                content = f.read()
            
            assert content == ""
            assert f"Saved 0 processed Gmail Message IDs to {temp_file_path}" in caplog.text
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_processed_gmail_msgids_permission_error(self, mock_file, caplog):
        """Test behavior when file cannot be written due to permissions."""
        test_msgids = {"123456789", "987654321"}
        test_path = "/some/test/path.txt"
        
        with caplog.at_level(logging.ERROR):
            save_processed_gmail_msgids(test_msgids, test_path)
        
        assert f"Error saving processed Gmail Message IDs to {test_path}" in caplog.text

    def test_save_and_load_roundtrip(self):
        """Test that saving and loading message IDs works correctly together."""
        original_msgids = {"123456789", "987654321", "555666777", "111222333"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file_path = f.name
        
        try:
            # Save the message IDs
            save_processed_gmail_msgids(original_msgids, temp_file_path)
            
            # Load them back
            loaded_msgids = load_processed_gmail_msgids(temp_file_path)
            
            # Should be identical
            assert loaded_msgids == original_msgids
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_default_file_path_constants(self):
        """Test that the default file path constant is correctly defined."""
        assert PROCESSED_GMAIL_MSGIDS_FILE == "processed_gmail_msgids.txt"

    def test_load_processed_gmail_msgids_large_numbers(self):
        """Test loading very large Gmail message ID numbers."""
        # Gmail message IDs can be very large integers
        large_msgids = ["1234567890123456789", "9876543210987654321", "5555666677778888999"]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for msgid in large_msgids:
                f.write(f"{msgid}\n")
            temp_file_path = f.name
        
        try:
            result = load_processed_gmail_msgids(temp_file_path)
            
            assert isinstance(result, set)
            assert len(result) == 3
            for msgid in large_msgids:
                assert msgid in result
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_save_processed_gmail_msgids_sorting(self):
        """Test that saved message IDs are properly sorted."""
        # Use unsorted input
        test_msgids = {"999", "111", "555", "333", "777"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file_path = f.name
        
        try:
            save_processed_gmail_msgids(test_msgids, temp_file_path)
            
            # Read the file and check order
            with open(temp_file_path, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
            
            # Should be sorted as strings
            expected_order = ["111", "333", "555", "777", "999"]
            assert lines == expected_order
            
        finally:
            # Clean up
            os.unlink(temp_file_path) 