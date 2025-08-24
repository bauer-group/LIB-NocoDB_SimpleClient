"""Async NocoDB REST API client implementation.

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

import asyncio
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import aiohttp

try:
    import aiofiles
    import aiohttp

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    aiohttp = None
    aiofiles = None  # type: ignore[assignment]

if ASYNC_AVAILABLE:
    from .config import NocoDBConfig
    from .exceptions import (
        AuthenticationException,
        AuthorizationException,
        ConnectionTimeoutException,
        NetworkException,
        NocoDBException,
        RateLimitException,
        RecordNotFoundException,
        ServerErrorException,
        TableNotFoundException,
        ValidationException,
    )
    from .validation import (
        validate_field_names,
        validate_limit,
        validate_record_data,
        validate_record_id,
        validate_sort_clause,
        validate_table_id,
        validate_where_clause,
    )

    class AsyncNocoDBClient:
        """Async client for interacting with the NocoDB REST API.

        This client provides async methods to perform CRUD operations, file operations,
        and other interactions with NocoDB tables through the REST API.

        Args:
            config: NocoDBConfig instance with connection settings

        Example:
            >>> config = NocoDBConfig(
            ...     base_url="https://app.nocodb.com",
            ...     api_token="your-api-token"
            ... )
            >>> async with AsyncNocoDBClient(config) as client:
            ...     records = await client.get_records("table_id", limit=10)
        """

        def __init__(self, config: NocoDBConfig):
            self.config = config
            self.logger = logging.getLogger(__name__)
            self._session: aiohttp.ClientSession | None = None

            # Validate configuration
            self.config.validate()

            # Setup logging
            self.config.setup_logging()

        async def __aenter__(self) -> "AsyncNocoDBClient":
            """Async context manager entry."""
            await self._create_session()
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            """Async context manager exit."""
            await self.close()

        async def _create_session(self) -> None:
            """Create aiohttp session with proper configuration."""
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "xc-token": self.config.api_token,
                "User-Agent": self.config.user_agent,
            }

            if self.config.access_protection_auth:
                headers[self.config.access_protection_header] = self.config.access_protection_auth

            headers.update(self.config.extra_headers)

            # Configure timeout
            timeout = aiohttp.ClientTimeout(
                total=self.config.timeout,
                connect=self.config.timeout / 3,
                sock_read=self.config.timeout / 2,
            )

            # Configure connector
            connector = aiohttp.TCPConnector(
                limit=self.config.pool_maxsize,
                limit_per_host=self.config.pool_connections,
                ttl_dns_cache=300,
                use_dns_cache=True,
                verify_ssl=self.config.verify_ssl,
            )

            self._session = aiohttp.ClientSession(
                headers=headers, timeout=timeout, connector=connector, raise_for_status=False
            )

        async def close(self) -> None:
            """Close the session."""
            if self._session:
                await self._session.close()
                self._session = None

        async def _request(
            self,
            method: str,
            endpoint: str,
            params: dict[str, Any] | None = None,
            data: dict[str, Any] | None = None,
            json_data: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Make an async HTTP request."""
            if not self._session:
                await self._create_session()

            if self._session is None:
                raise RuntimeError("Failed to create session")

            url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            self.logger.debug(f"{method} {url}")

            try:
                async with self._session.request(
                    method=method, url=url, params=params, data=data, json=json_data
                ) as response:
                    await self._check_for_error(response)

                    if response.content_type == "application/json":
                        result = await response.json()
                        return result if isinstance(result, dict) else {"data": result}
                    else:
                        text = await response.text()
                        try:
                            import json

                            parsed = json.loads(text)
                            return parsed if isinstance(parsed, dict) else {"data": parsed}
                        except json.JSONDecodeError:
                            return {"data": text}

            except aiohttp.ClientError as e:
                self.logger.error(f"Network error: {e}")
                raise NetworkException(f"Network error: {e}", original_error=e) from e
            except TimeoutError as e:
                self.logger.error(f"Request timeout: {e}")
                raise ConnectionTimeoutException(
                    f"Request timeout after {self.config.timeout}s",
                    timeout_seconds=self.config.timeout,
                ) from e

        async def _check_for_error(self, response: "aiohttp.ClientResponse") -> None:
            """Check HTTP response for errors and raise appropriate exceptions."""
            if response.status < 400:
                return

            try:
                error_info = await response.json()
            except Exception:
                error_info = {"error": f"HTTP_{response.status}", "message": await response.text()}

            error_code = error_info.get("error", f"HTTP_{response.status}")
            message = error_info.get("message", f"HTTP {response.status}")

            # Map specific error types
            if response.status == 401:
                raise AuthenticationException(message)
            elif response.status == 403:
                raise AuthorizationException(message)
            elif response.status == 404:
                if "record" in message.lower():
                    raise RecordNotFoundException(message)
                elif "table" in message.lower():
                    raise TableNotFoundException(message)
                else:
                    raise NocoDBException(error_code, message, response.status, error_info)
            elif response.status == 408:
                raise ConnectionTimeoutException(message)
            elif response.status == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitException(
                    message, retry_after=int(retry_after) if retry_after else None
                )
            elif response.status >= 500:
                raise ServerErrorException(message, response.status)
            else:
                raise NocoDBException(error_code, message, response.status, error_info)

        async def get_records(
            self,
            table_id: str,
            sort: str | None = None,
            where: str | None = None,
            fields: list[str] | None = None,
            limit: int = 25,
        ) -> list[dict[str, Any]]:
            """Get multiple records from a table asynchronously.

            Args:
                table_id: The ID of the table
                sort: Sort criteria (e.g., "Id", "-CreatedAt")
                where: Filter condition (e.g., "(Name,eq,John)")
                fields: List of fields to retrieve
                limit: Maximum number of records to retrieve

            Returns:
                List of record dictionaries
            """
            table_id = validate_table_id(table_id)
            if where:
                where = validate_where_clause(where)
            if sort:
                sort = validate_sort_clause(sort)
            if fields:
                fields = validate_field_names(fields)
            limit = validate_limit(limit)

            records = []
            offset = 0
            remaining_limit = limit

            while remaining_limit > 0:
                batch_limit = min(remaining_limit, 100)  # NocoDB max limit per request
                params = {"sort": sort, "where": where, "limit": batch_limit, "offset": offset}
                if fields:
                    params["fields"] = ",".join(fields)

                # Remove None values from params
                params = {k: v for k, v in params.items() if v is not None}

                response = await self._request(
                    "GET", f"api/v2/tables/{table_id}/records", params=params
                )

                batch_records = response.get("list", [])
                records.extend(batch_records)

                page_info = response.get("pageInfo", {})
                offset += len(batch_records)
                remaining_limit -= len(batch_records)

                if page_info.get("isLastPage", True) or not batch_records:
                    break

            return records[:limit]

        async def get_record(
            self,
            table_id: str,
            record_id: int | str,
            fields: list[str] | None = None,
        ) -> dict[str, Any]:
            """Get a single record by ID asynchronously.

            Args:
                table_id: The ID of the table
                record_id: The ID of the record
                fields: List of fields to retrieve

            Returns:
                Record dictionary
            """
            table_id = validate_table_id(table_id)
            record_id = validate_record_id(record_id)
            if fields:
                fields = validate_field_names(fields)

            params = {}
            if fields:
                params["fields"] = ",".join(fields)

            return await self._request(
                "GET", f"api/v2/tables/{table_id}/records/{record_id}", params=params
            )

        async def insert_record(self, table_id: str, record: dict[str, Any]) -> int | str:
            """Insert a new record into a table asynchronously.

            Args:
                table_id: The ID of the table
                record: Dictionary containing the record data

            Returns:
                The ID of the inserted record
            """
            table_id = validate_table_id(table_id)
            record = validate_record_data(record)

            response = await self._request(
                "POST", f"api/v2/tables/{table_id}/records", json_data=record
            )
            record_id = response.get("Id")
            return record_id if record_id is not None else ""

        async def update_record(
            self,
            table_id: str,
            record: dict[str, Any],
            record_id: int | str | None = None,
        ) -> int | str:
            """Update an existing record asynchronously.

            Args:
                table_id: The ID of the table
                record: Dictionary containing the updated record data
                record_id: The ID of the record to update (optional if included in record)

            Returns:
                The ID of the updated record
            """
            table_id = validate_table_id(table_id)
            record = validate_record_data(record)

            if record_id is not None:
                record_id = validate_record_id(record_id)
                record["Id"] = record_id

            response = await self._request(
                "PATCH", f"api/v2/tables/{table_id}/records", json_data=record
            )
            record_id = response.get("Id")
            return record_id if record_id is not None else ""

        async def delete_record(self, table_id: str, record_id: int | str) -> int | str:
            """Delete a record from a table asynchronously.

            Args:
                table_id: The ID of the table
                record_id: The ID of the record to delete

            Returns:
                The ID of the deleted record
            """
            table_id = validate_table_id(table_id)
            record_id = validate_record_id(record_id)

            response = await self._request(
                "DELETE", f"api/v2/tables/{table_id}/records", json_data={"Id": record_id}
            )
            deleted_id = response.get("Id")
            return deleted_id if deleted_id is not None else ""

        async def count_records(self, table_id: str, where: str | None = None) -> int:
            """Count records in a table asynchronously.

            Args:
                table_id: The ID of the table
                where: Filter condition (e.g., "(Name,eq,John)")

            Returns:
                Number of records matching the criteria
            """
            table_id = validate_table_id(table_id)
            if where:
                where = validate_where_clause(where)

            params = {}
            if where:
                params["where"] = where

            response = await self._request(
                "GET", f"api/v2/tables/{table_id}/records/count", params=params
            )
            count = response.get("count", 0)
            return int(count) if isinstance(count, int | str) else 0

        async def bulk_insert_records(
            self, table_id: str, records: list[dict[str, Any]]
        ) -> list[int | str]:
            """Insert multiple records in parallel.

            Args:
                table_id: The ID of the table
                records: List of record dictionaries

            Returns:
                List of inserted record IDs
            """
            table_id = validate_table_id(table_id)

            # Validate all records first
            validated_records = [validate_record_data(record) for record in records]

            # Create tasks for parallel execution
            tasks = [self.insert_record(table_id, record) for record in validated_records]

            # Execute in parallel with concurrency limit
            semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

            async def limited_insert(task: Any) -> Any:
                async with semaphore:
                    return await task

            results = await asyncio.gather(*[limited_insert(task) for task in tasks])
            return results

        async def bulk_update_records(
            self, table_id: str, records: list[dict[str, Any]]
        ) -> list[int | str]:
            """Update multiple records in parallel.

            Args:
                table_id: The ID of the table
                records: List of record dictionaries (must include 'Id')

            Returns:
                List of updated record IDs
            """
            table_id = validate_table_id(table_id)

            # Validate all records and ensure they have IDs
            validated_records = []
            for record in records:
                validated_record = validate_record_data(record)
                if "Id" not in validated_record:
                    raise ValidationException(
                        "Record must include 'Id' for bulk update", field_name="Id"
                    )
                validated_records.append(validated_record)

            # Create tasks for parallel execution
            tasks = [self.update_record(table_id, record) for record in validated_records]

            # Execute in parallel with concurrency limit
            semaphore = asyncio.Semaphore(10)

            async def limited_update(task: Any) -> Any:
                async with semaphore:
                    return await task

            results = await asyncio.gather(*[limited_update(task) for task in tasks])
            return results

    class AsyncNocoDBTable:
        """Async wrapper class for performing operations on a specific NocoDB table.

        This class provides a convenient interface for working with a single table
        by wrapping the AsyncNocoDBClient methods and automatically passing the table ID.

        Args:
            client: An instance of AsyncNocoDBClient
            table_id: The ID of the table to operate on

        Example:
            >>> async with AsyncNocoDBClient(config) as client:
            ...     table = AsyncNocoDBTable(client, "table_id")
            ...     records = await table.get_records(limit=10)
        """

        def __init__(self, client: AsyncNocoDBClient, table_id: str):
            self.client = client
            self.table_id = validate_table_id(table_id)

        async def get_records(
            self,
            sort: str | None = None,
            where: str | None = None,
            fields: list[str] | None = None,
            limit: int = 25,
        ) -> list[dict[str, Any]]:
            """Get multiple records from the table."""
            return await self.client.get_records(self.table_id, sort, where, fields, limit)

        async def get_record(
            self,
            record_id: int | str,
            fields: list[str] | None = None,
        ) -> dict[str, Any]:
            """Get a single record by ID."""
            return await self.client.get_record(self.table_id, record_id, fields)

        async def insert_record(self, record: dict[str, Any]) -> int | str:
            """Insert a new record into the table."""
            return await self.client.insert_record(self.table_id, record)

        async def update_record(
            self,
            record: dict[str, Any],
            record_id: int | str | None = None,
        ) -> int | str:
            """Update an existing record."""
            return await self.client.update_record(self.table_id, record, record_id)

        async def delete_record(self, record_id: int | str) -> int | str:
            """Delete a record from the table."""
            return await self.client.delete_record(self.table_id, record_id)

        async def count_records(self, where: str | None = None) -> int:
            """Count records in the table."""
            return await self.client.count_records(self.table_id, where)

        async def bulk_insert_records(self, records: list[dict[str, Any]]) -> list[int | str]:
            """Insert multiple records in parallel."""
            return await self.client.bulk_insert_records(self.table_id, records)

        async def bulk_update_records(self, records: list[dict[str, Any]]) -> list[int | str]:
            """Update multiple records in parallel."""
            return await self.client.bulk_update_records(self.table_id, records)

else:
    # Fallback classes when async dependencies are not available
    class AsyncNocoDBClient:  # type: ignore[no-redef]
        """Fallback class when async dependencies are not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "Async support requires additional dependencies. "
                "Install with: pip install 'nocodb-simple-client[async]'"
            )

    class AsyncNocoDBTable:  # type: ignore[no-redef]
        """Fallback class when async dependencies are not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "Async support requires additional dependencies. "
                "Install with: pip install 'nocodb-simple-client[async]'"
            )
