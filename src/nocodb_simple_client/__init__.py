"""A simple and powerful NocoDB REST API client for Python.

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

# Async support (optional)
from typing import TYPE_CHECKING

from .api_version import APIVersion, PathBuilder, QueryParamAdapter
from .base_resolver import BaseIdResolver
from .cache import CacheManager
from .client import NocoDBClient
from .columns import NocoDBColumns, TableColumns
from .exceptions import AuthenticationError  # noqa: F401 (alias for compatibility)
from .exceptions import FileOperationError  # noqa: F401
from .exceptions import NocoDBError  # noqa: F401
from .exceptions import QueryBuilderError  # noqa: F401
from .exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConnectionTimeoutException,
    FileUploadException,
    InvalidResponseException,
    NetworkException,
    NocoDBException,
    RateLimitException,
    RecordNotFoundException,
    ServerErrorException,
    TableNotFoundException,
    ValidationException,
)
from .file_operations import FileManager, TableFileManager
from .filter_builder import FilterBuilder, SortBuilder, create_filter, create_sort
from .links import NocoDBLinks, TableLinks
from .meta_client import NocoDBMetaClient
from .pagination import PaginatedResult, PaginationHandler

# New components
from .query_builder import QueryBuilder
from .table import NocoDBTable
from .views import NocoDBViews, TableViews
from .webhooks import NocoDBWebhooks, TableWebhooks

if TYPE_CHECKING:
    from .async_client import AsyncNocoDBClient, AsyncNocoDBTable
else:
    try:
        from .async_client import AsyncNocoDBClient, AsyncNocoDBTable

        ASYNC_AVAILABLE = True
    except ImportError:
        ASYNC_AVAILABLE = False

        # Create fallbacks that are safe to use
        class AsyncNocoDBClient:  # type: ignore[misc]
            def __init__(self, *args, **kwargs):  # type: ignore[misc]
                raise ImportError("Async support not available. Install aiohttp and aiofiles.")

        class AsyncNocoDBTable:  # type: ignore[misc]
            def __init__(self, *args, **kwargs):  # type: ignore[misc]
                raise ImportError("Async support not available. Install aiohttp and aiofiles.")


__version__ = "1.3.0"
__author__ = "BAUER GROUP (Karl Bauer)"
__email__ = "karl.bauer@bauer-group.com"

__all__ = [
    # Core classes
    "NocoDBClient",
    "NocoDBTable",
    "NocoDBMetaClient",
    # API Version support
    "APIVersion",
    "PathBuilder",
    "QueryParamAdapter",
    "BaseIdResolver",
    # Exceptions
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
    # Query building
    "QueryBuilder",
    "FilterBuilder",
    "SortBuilder",
    "create_filter",
    "create_sort",
    # Pagination
    "PaginationHandler",
    "PaginatedResult",
    # Links and relationships
    "NocoDBLinks",
    "TableLinks",
    # Views management
    "NocoDBViews",
    "TableViews",
    # Webhooks and automation
    "NocoDBWebhooks",
    "TableWebhooks",
    # Column/field management
    "NocoDBColumns",
    "TableColumns",
    # File operations
    "FileManager",
    "TableFileManager",
    # Caching
    "CacheManager",
    "NocoDBCache",
    "InMemoryCache",
    # Async support (if available)
    "AsyncNocoDBClient",
    "AsyncNocoDBTable",
    "ASYNC_AVAILABLE",
]
