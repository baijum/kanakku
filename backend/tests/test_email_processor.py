"""
Tests for email_processor module
"""
import pytest
from unittest.mock import patch, MagicMock

from app.email_processor import process_emails, analyze_email_with_gemini


class TestEmailProcessor:
    """Test cases for email processor functions"""

    @patch('app.email_processor.get_gemini_api_token')
    def test_process_emails_success(self, mock_get_token, app):
        """Test successful email processing with valid token"""
        mock_get_token.return_value = "test_token_123"
        
        with app.app_context():
            result = process_emails()
            
        assert result is True
        mock_get_token.assert_called_once()

    @patch('app.email_processor.get_gemini_api_token')
    def test_process_emails_no_token(self, mock_get_token, app):
        """Test email processing when no token is configured"""
        mock_get_token.return_value = None
        
        with app.app_context():
            result = process_emails()
            
        assert result is False
        mock_get_token.assert_called_once()

    @patch('app.email_processor.get_gemini_api_token')
    def test_process_emails_empty_token(self, mock_get_token, app):
        """Test email processing with empty token"""
        mock_get_token.return_value = ""
        
        with app.app_context():
            result = process_emails()
            
        assert result is False
        mock_get_token.assert_called_once()

    @patch('app.email_processor.get_gemini_api_token')
    def test_analyze_email_with_gemini_success(self, mock_get_token, app):
        """Test successful email analysis with valid token"""
        mock_get_token.return_value = "test_token_123"
        email_content = "Test email content"
        
        with app.app_context():
            result = analyze_email_with_gemini(email_content)
            
        assert result is not None
        assert result["status"] == "placeholder"
        assert "Email analysis will be implemented in a future ticket" in result["message"]
        mock_get_token.assert_called_once()

    @patch('app.email_processor.get_gemini_api_token')
    def test_analyze_email_with_gemini_no_token(self, mock_get_token, app):
        """Test email analysis when no token is configured"""
        mock_get_token.return_value = None
        email_content = "Test email content"
        
        with app.app_context():
            result = analyze_email_with_gemini(email_content)
            
        assert result is None
        mock_get_token.assert_called_once()

    @patch('app.email_processor.get_gemini_api_token')
    def test_analyze_email_with_gemini_empty_token(self, mock_get_token, app):
        """Test email analysis with empty token"""
        mock_get_token.return_value = ""
        email_content = "Test email content"
        
        with app.app_context():
            result = analyze_email_with_gemini(email_content)
            
        assert result is None
        mock_get_token.assert_called_once() 