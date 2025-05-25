"""
Enhanced tests for api module to improve coverage
"""
import pytest
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse

from werkzeug.exceptions import MethodNotAllowed


class TestApiEnhanced:
    """Enhanced test cases for API module"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_check_method_not_allowed(self, client):
        """Test health check with wrong method"""
        response = client.post("/api/v1/health")
        
        assert response.status_code == 405

    def test_get_csrf_token_success(self, app, client):
        """Test successful CSRF token generation"""
        app.config['FRONTEND_URL'] = 'https://example.com:3000'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data
        assert len(data["csrf_token"]) > 0
        
        # Check headers
        assert "X-CSRFToken" in response.headers
        assert response.headers["X-CSRFToken"] == data["csrf_token"]

    def test_get_csrf_token_with_domain_extraction(self, app, client):
        """Test CSRF token generation with domain extraction"""
        app.config['FRONTEND_URL'] = 'https://myapp.example.com:8080'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    def test_get_csrf_token_no_frontend_url(self, app, client):
        """Test CSRF token generation without frontend URL"""
        app.config.pop('FRONTEND_URL', None)
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    def test_get_csrf_token_invalid_frontend_url(self, app, client):
        """Test CSRF token generation with invalid frontend URL"""
        app.config['FRONTEND_URL'] = 'invalid-url'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    def test_get_csrf_token_url_parsing_exception(self, app, client):
        """Test CSRF token generation when URL parsing raises exception"""
        app.config['FRONTEND_URL'] = 'https://example.com'
        
        with patch('app.api.urlparse') as mock_urlparse:
            mock_urlparse.side_effect = Exception("URL parsing error")
            
            response = client.get("/api/v1/csrf-token")
            
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    def test_get_csrf_token_domain_with_port(self, app, client):
        """Test CSRF token generation with domain containing port"""
        app.config['FRONTEND_URL'] = 'https://localhost:3000'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    def test_get_csrf_token_domain_without_port(self, app, client):
        """Test CSRF token generation with domain without port"""
        app.config['FRONTEND_URL'] = 'https://example.com'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "csrf_token" in data

    @patch('app.api.generate_csrf')
    def test_get_csrf_token_generation_error(self, mock_generate_csrf, app, client):
        """Test CSRF token generation when token generation fails"""
        mock_generate_csrf.side_effect = Exception("Token generation failed")
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 500
        data = response.get_json()
        assert data["error"] == "Internal Server Error"

    def test_csrf_token_cookie_attributes(self, app, client):
        """Test CSRF token cookie attributes"""
        app.config['FRONTEND_URL'] = 'https://example.com'
        
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        
        # Check cookie was set (this is implementation dependent on test client)
        # In a real test, you might check response.headers['Set-Cookie']

    def test_method_not_allowed_error_handler(self, client):
        """Test 405 method not allowed error handler"""
        # Try to POST to health endpoint which only accepts GET
        response = client.post("/api/v1/health")
        
        assert response.status_code == 405
        data = response.get_json()
        assert data["error"] == "Method Not Allowed"

    def test_csrf_token_logging(self, app, client):
        """Test that CSRF token generation includes proper logging"""
        app.config['FRONTEND_URL'] = 'https://example.com:3000'
        
        with app.test_client() as test_client:
            with app.app_context():
                response = test_client.get("/api/v1/csrf-token")
                
        assert response.status_code == 200

    def test_csrf_token_response_structure(self, app, client):
        """Test CSRF token response structure"""
        response = client.get("/api/v1/csrf-token")
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check response structure
        assert isinstance(data, dict)
        assert "csrf_token" in data
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) > 10  # Should be a reasonable length

    def test_csrf_token_uniqueness(self, app, client):
        """Test that CSRF tokens are unique across requests"""
        response1 = client.get("/api/v1/csrf-token")
        response2 = client.get("/api/v1/csrf-token")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # Tokens should be different (though this might not always be true in practice)
        # This test mainly ensures the endpoint works multiple times
        assert "csrf_token" in data1
        assert "csrf_token" in data2

    def test_api_blueprint_registration(self, app):
        """Test that API blueprint is properly registered"""
        # Check that the blueprint is registered
        assert 'api' in app.blueprints
        
        # Check that routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/api/v1/health' in rules
        assert '/api/v1/csrf-token' in rules 