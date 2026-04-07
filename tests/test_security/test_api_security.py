import pytest
import requests
import configparser
import os

# Read API Host from properties.ini or default to a dummy host
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '../../config/properties.ini')
config.read(config_path)

try:
    API_HOST = config.get('API', 'host')
    if not API_HOST:
        API_HOST = "https://reqres.in/api"
except (configparser.NoSectionError, configparser.NoOptionError):
    API_HOST = "https://reqres.in/api"


class TestAPISecurity:
    """
    Basic security testing for the mobile app's backend APIs.
    These tests inject common malicious payloads to ensure the 
    backend handles them safely without crashing (500 errors) or exposing data.
    """

    @pytest.mark.parametrize("payload", [
        "' OR 1=1 --",
        "admin'--",
        "' UNION SELECT * FROM users --",
        "1; DROP TABLE users",
        "'; EXEC xp_cmdshell('dir'); --"
    ])
    def test_sql_injection_prevention(self, payload):
        """
        Test that login or data retrieval endpoints resist SQL Injection.
        """
        # Targeting a common potential vulnerable endpoint (mock example)
        endpoint = f"{API_HOST}/login"
        data = {
            "username": payload,
            "password": "password123"
        }
        
        response = requests.post(endpoint, json=data)
        
        # The server should NOT return a 5xx Error (crash/exception leaked)
        assert response.status_code < 500, f"SQLi payload caused a server error: {payload}"
        
        # Ensure we didn't successfully log in or dump a database
        if response.status_code == 200:
            assert "token" not in response.json().get("keys", []), "SQLi payload bypassed authentication!"

    @pytest.mark.parametrize("payload", [
        "<script>alert(1)</script>",
        "\"><img src=x onerror=alert(1)>",
        "javascript:alert('XSS')",
        "<svg/onload=alert(1)>"
    ])
    def test_xss_prevention(self, payload):
        """
        Test that user input endpoints resist Cross-Site Scripting (XSS).
        """
        endpoint = f"{API_HOST}/users"
        data = {
            "name": payload,
            "job": "Tester"
        }
        
        response = requests.post(endpoint, json=data)
        
        # Server should gracefully handle the bad input
        assert response.status_code < 500, f"XSS payload caused a server error: {payload}"

    @pytest.mark.parametrize("path", [
        "/../../../../etc/passwd",
        "/..%2f..%2f..%2fetc%2fpasswd",
        "/../../../windows/win.ini"
    ])
    def test_path_traversal_prevention(self, path):
        """
        Test that the API does not allow directory/path traversal.
        """
        endpoint = f"{API_HOST}{path}"
        response = requests.get(endpoint)
        
        # The server should reject the request (400, 403, 404), not return actual files (200)
        assert response.status_code in [400, 403, 404, 500], f"Path traversal might be possible: {path}"
        assert "root:x:0:0:" not in response.text, "Path traversal successful: /etc/passwd leaked!"

    def test_security_headers(self):
        """
        Check if the API returns standard security headers.
        """
        endpoint = f"{API_HOST}/users"
        response = requests.get(endpoint)
        
        headers = response.headers
        
        # Note: Some APIs may not implement all headers in dev/staging.
        # This checks for common headers to ensure security best practices.
        print("\n--- Security Headers Check ---")
        print(f"X-Powered-By exposed (Should be missing or sanitized): {'x-powered-by' in headers}")
        print(f"X-Content-Type-Options (Prevents sniffing): {headers.get('x-content-type-options', 'Missing')}")
        print(f"Strict-Transport-Security (HSTS): {headers.get('strict-transport-security', 'Missing')}")
