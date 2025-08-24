"""Custom exceptions for NocoDB Simple Client."""

from typing import Optional, Dict, Any


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
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
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
    
    def __init__(self, message: str = "Record not found", record_id: Optional[str] = None):
        super().__init__("RECORD_NOT_FOUND", message, status_code=404)
        self.record_id = record_id


class ValidationException(NocoDBException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None):
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
    
    def __init__(self, message: str = "Connection timeout", timeout_seconds: Optional[float] = None):
        super().__init__("CONNECTION_TIMEOUT", message, status_code=408)
        self.timeout_seconds = timeout_seconds


class RateLimitException(NocoDBException):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__("RATE_LIMIT_EXCEEDED", message, status_code=429)
        self.retry_after = retry_after


class ServerErrorException(NocoDBException):
    """Exception raised when server encounters an error."""
    
    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__("SERVER_ERROR", message, status_code=status_code)


class NetworkException(NocoDBException):
    """Exception raised when network-related errors occur."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("NETWORK_ERROR", message)
        self.original_error = original_error


class TableNotFoundException(NocoDBException):
    """Exception raised when a table is not found."""
    
    def __init__(self, message: str = "Table not found", table_id: Optional[str] = None):
        super().__init__("TABLE_NOT_FOUND", message, status_code=404)
        self.table_id = table_id


class FileUploadException(NocoDBException):
    """Exception raised when file upload fails."""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        super().__init__("FILE_UPLOAD_ERROR", message)
        self.filename = filename


class InvalidResponseException(NocoDBException):
    """Exception raised when API response is invalid or unexpected."""
    
    def __init__(self, message: str = "Invalid response format", response_data: Optional[Dict[str, Any]] = None):
        super().__init__("INVALID_RESPONSE", message, response_data=response_data)