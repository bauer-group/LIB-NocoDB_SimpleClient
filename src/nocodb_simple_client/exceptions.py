"""Custom exceptions for NocoDB Simple Client.

MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any


class NocoDBException(Exception):
    """Base exception for NocoDB operations.

    Args:
        error (str): The error code
        message (str): The error message
        status_code (int, optional): HTTP status code
        response_data (dict, optional): Raw response data
    """

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error = error
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        status_info = f" (HTTP {self.status_code})" if self.status_code else ""
        return f"{self.error}: {self.message}{status_info}"


class RecordNotFoundException(NocoDBException):
    """Exception raised when a record is not found."""

    def __init__(self, message: str = "Record not found", record_id: str | None = None):
        super().__init__("RECORD_NOT_FOUND", message, status_code=404)
        self.record_id = record_id


class ValidationException(NocoDBException):
    """Exception raised when input validation fails."""

    def __init__(self, message: str, field_name: str | None = None):
        super().__init__("VALIDATION_ERROR", message, status_code=400)
        self.field_name = field_name


class AuthenticationException(NocoDBException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__("AUTHENTICATION_ERROR", message, status_code=401)


class AuthorizationException(NocoDBException):
    """Exception raised when authorization fails."""

    def __init__(self, message: str = "Access denied"):
        super().__init__("AUTHORIZATION_ERROR", message, status_code=403)


class ConnectionTimeoutException(NocoDBException):
    """Exception raised when connection timeout occurs."""

    def __init__(self, message: str = "Connection timeout", timeout_seconds: float | None = None):
        super().__init__("CONNECTION_TIMEOUT", message, status_code=408)
        self.timeout_seconds = timeout_seconds


class RateLimitException(NocoDBException):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__("RATE_LIMIT_EXCEEDED", message, status_code=429)
        self.retry_after = retry_after


class ServerErrorException(NocoDBException):
    """Exception raised when server encounters an error."""

    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__("SERVER_ERROR", message, status_code=status_code)


class NetworkException(NocoDBException):
    """Exception raised when network-related errors occur."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__("NETWORK_ERROR", message)
        self.original_error = original_error


class TableNotFoundException(NocoDBException):
    """Exception raised when a table is not found."""

    def __init__(self, message: str = "Table not found", table_id: str | None = None):
        super().__init__("TABLE_NOT_FOUND", message, status_code=404)
        self.table_id = table_id


class FileUploadException(NocoDBException):
    """Exception raised when file upload fails."""

    def __init__(self, message: str, filename: str | None = None):
        super().__init__("FILE_UPLOAD_ERROR", message)
        self.filename = filename


class InvalidResponseException(NocoDBException):
    """Exception raised when API response is invalid or unexpected."""

    def __init__(
        self,
        message: str = "Invalid response format",
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__("INVALID_RESPONSE", message, response_data=response_data)
