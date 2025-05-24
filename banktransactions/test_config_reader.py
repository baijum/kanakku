#!/usr/bin/env python3

import pytest
import tempfile
import os
import sys
from unittest.mock import patch, mock_open

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from banktransactions.config_reader import load_config
except ImportError:
    # Fallback to relative import if running from within the directory
    from config_reader import load_config


class TestLoadConfig:
    """Test cases for the load_config function."""

    def test_load_config_success(self):
        """Test successful loading of a valid TOML file."""
        # Create a temporary TOML file
        toml_content = """
[bank-account-map]
XX1648 = "Assets:Bank:Axis"
XX0907 = "Liabilities:CC:Axis"

[expense-account-map]
"BAKE HOUSE" = ["Expenses:Food:Restaurant", "Restaurant at Kattangal"]
"Jio Prepaid" = ["Expenses:Mobile:Baiju Jio", "FIXME"]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(toml_content)
            temp_file_path = f.name
        
        try:
            result = load_config(temp_file_path)
            
            # Verify the structure
            assert result is not None
            assert "bank-account-map" in result
            assert "expense-account-map" in result
            
            # Verify specific values
            assert result["bank-account-map"]["XX1648"] == "Assets:Bank:Axis"
            assert result["bank-account-map"]["XX0907"] == "Liabilities:CC:Axis"
            assert result["expense-account-map"]["BAKE HOUSE"] == ["Expenses:Food:Restaurant", "Restaurant at Kattangal"]
            assert result["expense-account-map"]["Jio Prepaid"] == ["Expenses:Mobile:Baiju Jio", "FIXME"]
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_config_file_not_found(self, capsys):
        """Test behavior when the config file doesn't exist."""
        non_existent_path = "/path/that/does/not/exist.toml"
        
        result = load_config(non_existent_path)
        
        assert result is None
        
        # Check that error message was printed
        captured = capsys.readouterr()
        assert f"Error: File not found at {non_existent_path}" in captured.out

    def test_load_config_invalid_toml(self, capsys):
        """Test behavior with invalid TOML content."""
        invalid_toml_content = """
[bank-account-map
XX1648 = "Assets:Bank:Axis"  # Missing closing bracket
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(invalid_toml_content)
            temp_file_path = f.name
        
        try:
            result = load_config(temp_file_path)
            
            assert result is None
            
            # Check that error message was printed
            captured = capsys.readouterr()
            assert f"Error decoding TOML file {temp_file_path}" in captured.out
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_config_empty_file(self):
        """Test behavior with an empty TOML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("")  # Empty file
            temp_file_path = f.name
        
        try:
            result = load_config(temp_file_path)
            
            # Empty TOML file should return empty dict
            assert result == {}
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_load_config_permission_error(self, mock_file, capsys):
        """Test behavior when file cannot be opened due to permissions."""
        test_path = "/some/test/path.toml"
        
        # Mock os.path.exists to return True
        with patch("os.path.exists", return_value=True):
            result = load_config(test_path)
        
        assert result is None
        
        # Check that error message was printed
        captured = capsys.readouterr()
        assert f"An unexpected error occurred while reading {test_path}" in captured.out

    def test_load_config_with_complex_structure(self):
        """Test loading a more complex TOML structure."""
        complex_toml_content = """
[database]
host = "localhost"
port = 5432
name = "testdb"

[api]
endpoint = "http://localhost:5000"
timeout = 30

[features]
enable_logging = true
debug_mode = false
max_retries = 3

[nested.section]
value1 = "test"
value2 = 42
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(complex_toml_content)
            temp_file_path = f.name
        
        try:
            result = load_config(temp_file_path)
            
            assert result is not None
            assert result["database"]["host"] == "localhost"
            assert result["database"]["port"] == 5432
            assert result["api"]["endpoint"] == "http://localhost:5000"
            assert result["features"]["enable_logging"] is True
            assert result["features"]["debug_mode"] is False
            assert result["nested"]["section"]["value1"] == "test"
            assert result["nested"]["section"]["value2"] == 42
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_load_config_with_unicode_content(self):
        """Test loading TOML file with Unicode characters."""
        unicode_toml_content = """
[messages]
greeting = "Hello, 世界!"
emoji = "🚀 Test"
special_chars = "Café résumé naïve"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False, encoding='utf-8') as f:
            f.write(unicode_toml_content)
            temp_file_path = f.name
        
        try:
            result = load_config(temp_file_path)
            
            assert result is not None
            assert result["messages"]["greeting"] == "Hello, 世界!"
            assert result["messages"]["emoji"] == "🚀 Test"
            assert result["messages"]["special_chars"] == "Café résumé naïve"
            
        finally:
            # Clean up
            os.unlink(temp_file_path) 