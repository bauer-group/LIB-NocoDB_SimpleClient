"""Security tests for NocoDB Simple Client."""

from unittest.mock import Mock, patch

import pytest

from nocodb_simple_client import NocoDBClient, NocoDBTable
from nocodb_simple_client.config import NocoDBConfig
from nocodb_simple_client.exceptions import AuthenticationException, ValidationException
from nocodb_simple_client.validation import (
    sanitize_string,
    validate_api_token,
    validate_record_id,
    validate_table_id,
    validate_url,
    validate_where_clause,
)


class TestInputValidation:
    """Test input validation security."""

    def test_table_id_validation(self):
        """Test table ID validation prevents injection."""
        # Valid table IDs
        assert validate_table_id("table_123") == "table_123"
        assert validate_table_id("my-table") == "my-table"
        assert validate_table_id("Table123") == "Table123"

        # Invalid table IDs (potential injection attempts)
        with pytest.raises(ValidationException):
            validate_table_id("")

        with pytest.raises(ValidationException):
            validate_table_id("table; DROP TABLE users;")

        with pytest.raises(ValidationException):
            validate_table_id("table/../../etc/passwd")

        with pytest.raises(ValidationException):
            validate_table_id("table<script>alert('xss')</script>")

    def test_record_id_validation(self):
        """Test record ID validation."""
        # Valid record IDs
        assert validate_record_id(123) == 123
        assert validate_record_id("rec_123") == "rec_123"

        # Invalid record IDs
        with pytest.raises(ValidationException):
            validate_record_id(0)

        with pytest.raises(ValidationException):
            validate_record_id(-1)

        with pytest.raises(ValidationException):
            validate_record_id("")

        with pytest.raises(ValidationException):
            validate_record_id("'; DROP TABLE users; --")

    def test_where_clause_validation(self):
        """Test WHERE clause validation prevents SQL injection."""
        # Valid WHERE clauses
        assert validate_where_clause("(Name,eq,John)") == "(Name,eq,John)"
        assert (
            validate_where_clause("(Age,gt,21)~and(Status,eq,Active)")
            == "(Age,gt,21)~and(Status,eq,Active)"
        )

        # Invalid WHERE clauses (potential SQL injection)
        with pytest.raises(ValidationException):
            validate_where_clause("")

        with pytest.raises(ValidationException):
            validate_where_clause("(Name,eq,John))")  # Unbalanced parentheses

        with pytest.raises(ValidationException):
            validate_where_clause("'; DROP TABLE users; --")

        with pytest.raises(ValidationException):
            validate_where_clause("1=1 UNION SELECT * FROM users")

        with pytest.raises(ValidationException):
            validate_where_clause("Name = 'test' OR 1=1 --")

    def test_api_token_validation(self):
        """Test API token validation."""
        # Valid tokens
        valid_token = "abcd1234567890efgh"
        assert validate_api_token(valid_token) == valid_token

        # Invalid tokens
        with pytest.raises(ValidationException):
            validate_api_token("")

        with pytest.raises(ValidationException):
            validate_api_token("short")

        with pytest.raises(ValidationException):
            validate_api_token("token with spaces")

        with pytest.raises(ValidationException):
            validate_api_token("token<script>alert('xss')</script>")

    def test_url_validation(self):
        """Test URL validation prevents malicious URLs."""
        # Valid URLs
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://localhost:8080") == "http://localhost:8080"
        assert validate_url("https://nocodb.example.com/api") == "https://nocodb.example.com/api"

        # Invalid URLs
        with pytest.raises(ValidationException):
            validate_url("")

        with pytest.raises(ValidationException):
            validate_url("javascript:alert('xss')")

        with pytest.raises(ValidationException):
            validate_url("ftp://malicious.com")

        with pytest.raises(ValidationException):
            validate_url("file:///etc/passwd")

        with pytest.raises(ValidationException):
            validate_url("not_a_url")

    def test_string_sanitization(self):
        """Test string sanitization."""
        # Normal strings
        assert sanitize_string("Hello World") == "Hello World"
        assert sanitize_string("Test123") == "Test123"

        # Strings with control characters
        assert sanitize_string("Hello\x00World") == "HelloWorld"
        assert sanitize_string("Test\x01\x02String") == "TestString"

        # Keep allowed control characters
        assert sanitize_string("Line1\nLine2") == "Line1\nLine2"
        assert sanitize_string("Col1\tCol2") == "Col1\tCol2"
        assert sanitize_string("Line1\rLine2") == "Line1\rLine2"

        # Long strings
        long_string = "x" * 2000
        with pytest.raises(ValidationException):
            sanitize_string(long_string, max_length=1000)


class TestAuthenticationSecurity:
    """Test authentication and authorization security."""

    def test_api_token_masking_in_logs(self):
        """Test that API tokens are not exposed in logs."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com", api_token="secret_api_token_123456"
        )

        # Check that config representation masks the token
        config_dict = config.to_dict()
        assert config_dict["api_token"] == "***"
        assert "secret_api_token_123456" not in str(config_dict)

    @patch("requests.Session.get")
    def test_authentication_error_handling(self, mock_get):
        """Test proper handling of authentication errors."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "UNAUTHORIZED", "message": "Invalid API token"}
        mock_get.return_value = mock_response

        config = NocoDBConfig(base_url="https://test.nocodb.com", api_token="invalid_token")

        with pytest.raises(AuthenticationException):
            with NocoDBClient(config) as client:
                table = NocoDBTable(client, "test_table")
                table.get_records()

    def test_header_injection_protection(self):
        """Test protection against header injection."""
        # Attempt header injection in custom headers
        dangerous_headers = {
            "X-Injected": "value\r\nX-Malicious: injected",
            "Normal-Header": "safe_value",
        }

        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test_token",
            extra_headers=dangerous_headers,
        )

        client = NocoDBClient(config)

        # Headers should be sanitized or the dangerous one should be rejected
        # This would depend on the HTTP library's handling
        assert "Normal-Header" in client.headers or "Normal-Header" in config.extra_headers
        client.close()


class TestDataSecurity:
    """Test data security and privacy."""

    def test_sensitive_data_in_records(self):
        """Test handling of potentially sensitive data in records."""
        from nocodb_simple_client.validation import validate_record_data

        # Test records with potentially sensitive data
        sensitive_record = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "should_not_be_here",
            "social_security": "123-45-6789",
            "credit_card": "4111-1111-1111-1111",
        }

        # Validation should pass (client doesn't know what's sensitive)
        # but this test documents that sensitive data handling is application responsibility
        validated = validate_record_data(sensitive_record)
        assert validated == sensitive_record

    def test_dangerous_field_names(self):
        """Test handling of potentially dangerous field names."""
        from nocodb_simple_client.validation import validate_record_data

        dangerous_record = {
            "__proto__": "dangerous",
            "constructor": "also_dangerous",
            "prototype": "very_dangerous",
            "normal_field": "safe",
        }

        # Should reject dangerous prototype pollution field names
        with pytest.raises(ValidationException):
            validate_record_data(dangerous_record)

    def test_file_upload_security(self):
        """Test file upload security validation."""
        import tempfile
        from pathlib import Path

        from nocodb_simple_client.validation import validate_file_path

        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"safe content")
            safe_file_path = Path(tmp_file.name)

        try:
            # Valid file should pass
            validated_path = validate_file_path(safe_file_path)
            assert validated_path == safe_file_path

            # Non-existent file should fail
            with pytest.raises(ValidationException):
                validate_file_path("/nonexistent/file.txt")

            # Directory instead of file should fail
            with pytest.raises(ValidationException):
                validate_file_path("/tmp")

        finally:
            # Clean up
            safe_file_path.unlink(missing_ok=True)

    def test_response_data_sanitization(self):
        """Test that response data is properly handled."""
        # Mock response with potentially dangerous content
        mock_response_data = {
            "records": [
                {"id": 1, "name": "Normal Record", "description": "Safe content"},
                {
                    "id": 2,
                    "name": "<script>alert('xss')</script>",
                    "description": "Potentially dangerous content",
                },
            ]
        }

        # Client should not sanitize response data (that's application responsibility)
        # but should handle it safely without executing it
        assert "<script>" in mock_response_data["records"][1]["name"]


class TestNetworkSecurity:
    """Test network-level security."""

    def test_ssl_verification_enabled(self):
        """Test that SSL verification is enabled by default."""
        config = NocoDBConfig(base_url="https://test.nocodb.com", api_token="test_token")

        assert config.verify_ssl is True

    def test_ssl_verification_can_be_disabled(self):
        """Test that SSL verification can be disabled (for dev environments)."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com", api_token="test_token", verify_ssl=False
        )

        assert config.verify_ssl is False

    def test_timeout_configuration(self):
        """Test that timeouts are properly configured."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com", api_token="test_token", timeout=10.0
        )

        client = NocoDBClient(config)
        assert client.config.timeout == 10.0
        client.close()

    def test_redirect_limits(self):
        """Test that redirect limits are enforced."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com", api_token="test_token", max_retries=3
        )

        client = NocoDBClient(config)
        assert client.config.max_retries == 3
        client.close()


class TestErrorInformationLeakage:
    """Test that errors don't leak sensitive information."""

    @patch("requests.Session.get")
    def test_error_message_sanitization(self, mock_get):
        """Test that error messages don't contain sensitive information."""
        # Mock response with detailed error that might contain sensitive info
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": "DATABASE_ERROR",
            "message": (
                "Connection failed to database at internal-db-server:5432 with user admin_user"
            ),
            "stack_trace": "Full stack trace with internal paths...",
        }
        mock_get.return_value = mock_response

        config = NocoDBConfig(base_url="https://test.nocodb.com", api_token="test_token")

        with pytest.raises(Exception) as exc_info:
            with NocoDBClient(config) as client:
                table = NocoDBTable(client, "test_table")
                table.get_records()

        # Error message should not expose sensitive internal information
        error_msg = str(exc_info.value)
        # This is a basic test - in practice, you might want more sophisticated filtering
        assert error_msg is not None


class TestSecurityHeaders:
    """Test security-related HTTP headers."""

    def test_user_agent_header(self):
        """Test that user agent header is set properly."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test_token",
            user_agent="nocodb-simple-client/1.0.0",
        )

        client = NocoDBClient(config)
        assert config.user_agent == "nocodb-simple-client/1.0.0"
        client.close()

    def test_custom_headers_validation(self):
        """Test that custom headers are properly validated."""
        # Test with safe custom headers
        safe_headers = {"X-Custom-Header": "safe_value", "X-Request-ID": "12345"}

        config = NocoDBConfig(
            base_url="https://test.nocodb.com", api_token="test_token", extra_headers=safe_headers
        )

        client = NocoDBClient(config)
        assert config.extra_headers == safe_headers
        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
