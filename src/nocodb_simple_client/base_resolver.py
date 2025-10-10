"""Base ID resolution and caching for NocoDB API v3.

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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import NocoDBClient


class BaseIdResolver:
    """Resolver for mapping table IDs to base IDs in v3 API.

    In NocoDB API v3, all endpoints require a baseId in the path.
    This resolver caches the mapping between table IDs and base IDs
    to avoid repeated API calls.

    Example:
        >>> resolver = BaseIdResolver(client)
        >>> base_id = resolver.get_base_id("table_abc123")
        >>> # Subsequent calls use cached value
        >>> base_id = resolver.get_base_id("table_abc123")  # No API call
    """

    def __init__(self, client: "NocoDBClient"):
        """Initialize the base ID resolver.

        Args:
            client: The NocoDB client instance
        """
        self._client = client
        self._cache: dict[str, str] = {}  # table_id -> base_id
        self._enabled = True

    def get_base_id(self, table_id: str, force_refresh: bool = False) -> str:
        """Get the base ID for a given table ID.

        Args:
            table_id: The table ID to resolve
            force_refresh: Force a cache refresh even if value exists

        Returns:
            The base ID for the table

        Raises:
            TableNotFoundException: If the table doesn't exist
            NocoDBException: If the API call fails
        """
        # Check cache first
        if not force_refresh and table_id in self._cache:
            return self._cache[table_id]

        # Fetch table metadata to get base_id
        # This uses the v2 endpoint which doesn't require base_id
        table_info = self._client._get(f"api/v2/meta/tables/{table_id}")

        base_id: str
        if not table_info or "base_id" not in table_info:
            # Try alternative response structure
            if "source_id" in table_info:
                # In some NocoDB versions, it's called source_id
                base_id = str(table_info["source_id"])
            elif "project_id" in table_info:
                # Or project_id in older versions
                base_id = str(table_info["project_id"])
            else:
                # If we can't find it, try to extract from fk_model_id or similar
                # As a fallback, we might need to list all bases and find the table
                base_id = self._find_base_id_from_list(table_id)
        else:
            base_id = str(table_info["base_id"])

        # Cache the result
        self._cache[table_id] = base_id
        return base_id

    def _find_base_id_from_list(self, table_id: str) -> str:
        """Fallback method to find base_id by listing tables in all bases.

        Args:
            table_id: The table ID to find

        Returns:
            The base ID containing this table

        Raises:
            TableNotFoundException: If table not found in any base
        """
        from .exceptions import TableNotFoundException

        # This is a more expensive operation, should rarely be needed
        # We'd need to implement listing bases first
        # For now, raise an error with helpful message
        raise TableNotFoundException(
            f"Could not resolve base_id for table {table_id}. "
            "Please provide base_id explicitly when using API v3."
        )

    def set_base_id(self, table_id: str, base_id: str) -> None:
        """Manually set a base ID mapping.

        Useful when you already know the base_id and want to avoid API calls.

        Args:
            table_id: The table ID
            base_id: The base ID
        """
        self._cache[table_id] = base_id

    def clear_cache(self, table_id: str | None = None) -> None:
        """Clear the cache.

        Args:
            table_id: If provided, clear only this table's cache.
                     If None, clear all cache.
        """
        if table_id:
            self._cache.pop(table_id, None)
        else:
            self._cache.clear()

    def get_cache_size(self) -> int:
        """Get the number of cached mappings.

        Returns:
            Number of table_id -> base_id mappings in cache
        """
        return len(self._cache)

    def disable(self) -> None:
        """Disable the resolver (will raise errors when base_id needed)."""
        self._enabled = False

    def enable(self) -> None:
        """Enable the resolver."""
        self._enabled = True

    def is_enabled(self) -> bool:
        """Check if resolver is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled
