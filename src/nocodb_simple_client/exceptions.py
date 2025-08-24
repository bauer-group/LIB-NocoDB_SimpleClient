"""Custom exceptions for NocoDB Simple Client."""


class NocoDBException(Exception):
    """Base exception for NocoDB operations.
    
    Args:
        error (str): The error code
        message (str): The error message
    """
    
    def __init__(self, error: str, message: str):
        super().__init__(message)
        self.error = error
        self.message = message

    def __str__(self) -> str:
        return f"{self.error}: {self.message}"


class RecordNotFoundException(NocoDBException):
    """Exception raised when a record is not found."""
    pass