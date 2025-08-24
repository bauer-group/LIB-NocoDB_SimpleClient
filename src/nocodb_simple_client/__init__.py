"""A simple and powerful NocoDB REST API client for Python."""

from .client import NocoDBClient
from .table import NocoDBTable
from .exceptions import (
    NocoDBException,
    RecordNotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConnectionTimeoutException,
    RateLimitException,
    ServerErrorException,
    NetworkException,
    TableNotFoundException,
    FileUploadException,
    InvalidResponseException,
)

__version__ = "0.4.0"
__author__ = "BAUER GROUP (Karl Bauer)"
__email__ = "karl.bauer@bauer-group.com"

__all__ = [
    "NocoDBClient",
    "NocoDBTable", 
    "NocoDBException",
    "RecordNotFoundException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ConnectionTimeoutException",
    "RateLimitException",
    "ServerErrorException",
    "NetworkException",
    "TableNotFoundException",
    "FileUploadException",
    "InvalidResponseException",
]