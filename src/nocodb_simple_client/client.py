"""NocoDB REST API client implementation.

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

import base64
import json
import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from .config import NocoDBConfig

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .api_version import APIVersion, PathBuilder, QueryParamAdapter, RequestAdapter, ResponseAdapter
from .base_resolver import BaseIdResolver
from .exceptions import NocoDBException, RecordNotFoundException, ValidationException


class NocoDBClient:
    """A client for interacting with the NocoDB REST API.

    This client provides methods to perform CRUD operations, file operations,
    and other interactions with NocoDB tables through the REST API.

    Args:
        base_url (str): The base URL of your NocoDB instance
        db_auth_token (str): The API token for authentication
        access_protection_auth (str, optional): Value for the access protection header
        access_protection_header (str, optional): Name of the access protection header
            (defaults to "X-BAUERGROUP-Auth")
        max_redirects (int, optional): Maximum number of redirects to follow
        timeout (int, optional): Request timeout in seconds
        api_version (str, optional): API version to use ("v2" or "v3", defaults to "v2")
        base_id (str, optional): Default base ID for v3 API operations

    Attributes:
        headers (Dict[str, str]): HTTP headers used for requests
        api_version (APIVersion): The API version being used
        base_id (str, optional): Default base ID for v3 operations

    Example:
        >>> # Default usage (v2 API)
        >>> client = NocoDBClient(
        ...     base_url="https://app.nocodb.com",
        ...     db_auth_token="your-api-token"
        ... )
        >>>
        >>> # Using v3 API with base_id
        >>> client = NocoDBClient(
        ...     base_url="https://app.nocodb.com",
        ...     db_auth_token="your-api-token",
        ...     api_version="v3",
        ...     base_id="base_abc123"
        ... )
        >>>
        >>> # With custom protection header
        >>> client = NocoDBClient(
        ...     base_url="https://app.nocodb.com",
        ...     db_auth_token="your-api-token",
        ...     access_protection_auth="your-auth-value",
        ...     access_protection_header="X-Custom-Auth"
        ... )
    """

    def __init__(
        self,
        base_url: Union[str, "NocoDBConfig", None] = None,
        db_auth_token: str | None = None,
        access_protection_auth: str | None = None,
        access_protection_header: str = "X-BAUERGROUP-Auth",
        max_redirects: int | None = None,
        timeout: int | None = None,
        config: "NocoDBConfig | None" = None,
        api_version: str = "v2",
        base_id: str | None = None,
    ) -> None:
        from .config import NocoDBConfig  # Import here to avoid circular import

        # Support both individual parameters and config object
        # Check if first parameter is a config object
        if isinstance(base_url, NocoDBConfig):
            config = base_url
            base_url = None

        if config is not None:
            # Config object provided - use its values
            self.config = config
            self._base_url = config.base_url.rstrip("/")
            auth_token = config.api_token
            access_protection_auth = getattr(
                config, "access_protection_auth", access_protection_auth
            )
            access_protection_header = getattr(
                config, "access_protection_header", access_protection_header
            )
            max_redirects = getattr(config, "max_redirects", max_redirects)
            timeout = getattr(config, "timeout", timeout)
        else:
            # Individual parameters provided
            if base_url is None or db_auth_token is None:
                raise TypeError(
                    "NocoDBClient.__init__() missing required arguments: 'base_url' and "
                    "'db_auth_token' (or provide config object)"
                )

            # Create a config object for compatibility
            self.config = NocoDBConfig(
                base_url=base_url,
                api_token=db_auth_token,
                timeout=timeout or 30,
                max_retries=max_redirects or 3,
            )

            self._base_url = base_url.rstrip("/")
            auth_token = db_auth_token

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "xc-token": auth_token,
        }

        if access_protection_auth:
            self.headers[access_protection_header] = access_protection_auth

        self._request_timeout = timeout
        self._session = requests.Session()

        if max_redirects is not None:
            self._session.max_redirects = max_redirects

        # API version support
        self.api_version = APIVersion(api_version)
        self.base_id = base_id
        self._path_builder = PathBuilder(self.api_version)
        self._param_adapter = QueryParamAdapter()
        self._response_adapter = ResponseAdapter()
        self._request_adapter = RequestAdapter()

        # Base ID resolver for v3 API (resolves table_id -> base_id)
        self._base_resolver = BaseIdResolver(self) if self.api_version == APIVersion.V3 else None

    def _resolve_base_id(self, table_id: str, base_id: str | None = None) -> str:
        """Resolve base_id for API v3 operations.

        Args:
            table_id: The table ID
            base_id: Optional base_id override

        Returns:
            The resolved base_id

        Raises:
            ValueError: If base_id cannot be resolved for v3 API
        """
        # If base_id provided explicitly, use it
        if base_id:
            return base_id

        # Use client's default base_id if set
        if self.base_id:
            return self.base_id

        # For v3, try to resolve from table_id
        if self.api_version == APIVersion.V3 and self._base_resolver:
            return self._base_resolver.get_base_id(table_id)

        # For v2, base_id is not required
        if self.api_version == APIVersion.V2:
            raise ValueError("base_id should not be required for API v2")

        raise ValueError(
            f"base_id is required for API v3. Please provide it in the client constructor "
            f"or as a parameter to the method call for table {table_id}"
        )

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.get(
            url, headers=self.headers, params=params, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _post(
        self, endpoint: str, data: dict[str, Any] | list[dict[str, Any]]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a POST request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.post(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _patch(
        self, endpoint: str, data: dict[str, Any] | list[dict[str, Any]]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a PATCH request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.patch(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a PUT request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.put(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _delete(
        self, endpoint: str, data: dict[str, Any] | list[dict[str, Any]] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a DELETE request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.delete(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _check_for_error(self, response: requests.Response) -> None:
        """Check HTTP response for errors and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                from .exceptions import (
                    AuthenticationException,
                    AuthorizationException,
                    RateLimitException,
                    ServerErrorException,
                    ValidationException,
                )

                error_info = response.json()
                message = error_info.get("message", f"HTTP {response.status_code} error")
                error_code = error_info.get("error", "UNKNOWN_ERROR")

                # Map HTTP status codes to appropriate exceptions
                if response.status_code == 401:
                    raise AuthenticationException(message)
                elif response.status_code == 403:
                    raise AuthorizationException(message)
                elif response.status_code == 404:
                    if error_code == "RECORD_NOT_FOUND":
                        raise RecordNotFoundException(message)
                    else:
                        raise NocoDBException(error_code, message, response.status_code, error_info)
                elif response.status_code == 400:
                    raise ValidationException(message)
                elif response.status_code == 429:
                    # NocoDB enforces ~5 req/s per user; surface Retry-After so
                    # callers can back off instead of getting a generic error.
                    raise RateLimitException(message, retry_after=self._parse_retry_after(response))
                elif response.status_code >= 500:
                    raise ServerErrorException(message, response.status_code)
                else:
                    raise NocoDBException(error_code, message, response.status_code, error_info)

            except ValueError as e:
                # If response is not JSON, create generic error
                from .exceptions import AuthenticationException as _AuthExc
                from .exceptions import AuthorizationException as _AuthzExc
                from .exceptions import RateLimitException as _RateExc

                if response.status_code == 401:
                    raise _AuthExc(f"Authentication failed (HTTP {response.status_code})") from e
                elif response.status_code == 403:
                    raise _AuthzExc(f"Access denied (HTTP {response.status_code})") from e
                elif response.status_code == 429:
                    raise _RateExc(
                        "Rate limit exceeded", retry_after=self._parse_retry_after(response)
                    ) from e
                else:
                    raise NocoDBException(
                        "HTTP_ERROR", f"HTTP {response.status_code} error", response.status_code
                    ) from e

    @staticmethod
    def _parse_retry_after(response: requests.Response) -> int | None:
        """Extract the Retry-After header (seconds) from a 429 response, if present."""
        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            return int(retry_after)
        return None

    def get_records(
        self,
        table_id: str,
        base_id: str | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get multiple records from a table.

        Args:
            table_id: The ID of the table
            base_id: Base ID (required for v3, optional for v2)
            sort: Sort criteria (e.g., "Id", "-CreatedAt")
            where: Filter condition (e.g., "(Name,eq,John)")
            fields: List of fields to retrieve
            limit: Maximum number of records to retrieve

        Returns:
            List of record dictionaries

        Raises:
            RecordNotFoundException: If no records match the criteria
            NocoDBException: For other API errors
        """
        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_list(table_id, resolved_base_id)

        records = []
        offset = 0
        remaining_limit = limit

        while remaining_limit > 0:
            batch_limit = min(remaining_limit, 100)  # NocoDB max limit per request
            params: dict[str, Any] = {
                "sort": sort,
                "where": where,
                "limit": batch_limit,
                "offset": offset,
            }
            if fields:
                params["fields"] = ",".join(fields)

            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}

            # Normalize the not-equal operator: current NocoDB rejects "ne" on
            # BOTH v2 and v3 ("ne is not supported" / "not a recognized
            # operator") and requires "neq" (verified live, releaseVersion
            # 2026.05.2). Applied for both versions so the documented "ne"
            # filter keeps working.
            if where:
                params["where"] = self._param_adapter.normalize_where_operators(where)

            # v3-only query differences (verified live):
            #  * pagination: offset/limit -> page/pageSize
            #  * sort: must be a JSON-encoded array of {field,direction}; the
            #    plain v2 string ("Name,-Age") is rejected with HTTP 422, and a
            #    raw Python list would be mangled by requests into repeated
            #    ?sort=field&sort=direction pairs.
            if self.api_version == APIVersion.V3:
                params = self._param_adapter.convert_pagination_to_v3(params)
                if sort:
                    params["sort"] = json.dumps(self._param_adapter.convert_sort_to_v3(sort))

            response = self._get(endpoint, params=params)

            batch_records, page_info = self._response_adapter.normalize_records_list(
                response, self.api_version
            )
            records.extend(batch_records)

            offset += len(batch_records)
            remaining_limit -= len(batch_records)

            if page_info.get("isLastPage", True) or not batch_records:
                break

        return records[:limit]

    def get_record(
        self,
        table_id: str,
        record_id: int | str,
        base_id: str | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get a single record by ID.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            base_id: Base ID (required for v3, optional for v2)
            fields: List of fields to retrieve

        Returns:
            Record dictionary

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_get(table_id, str(record_id), resolved_base_id)

        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        response = self._get(endpoint, params=params)
        return self._response_adapter.normalize_record(response, self.api_version)

    def insert_record(
        self, table_id: str, record: dict[str, Any], base_id: str | None = None
    ) -> int | str:
        """Insert a new record into a table.

        Args:
            table_id: The ID of the table
            record: Dictionary containing the record data
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the inserted record

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_create(table_id, resolved_base_id)

        # Format request for API version
        formatted_record = self._request_adapter.format_record(record, self.api_version)

        response = self._post(endpoint, data=formatted_record)
        if isinstance(response, dict):
            record_id = self._response_adapter.extract_record_id(response, self.api_version)
        else:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"Expected dict response from insert operation, got {type(response)}",
            )
        if record_id is None:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"No record ID returned from insert operation. Response: {response}",
            )
        return record_id  # type: ignore[no-any-return]

    def update_record(
        self,
        table_id: str,
        record: dict[str, Any],
        record_id: int | str | None = None,
        base_id: str | None = None,
    ) -> int | str:
        """Update an existing record.

        Args:
            table_id: The ID of the table
            record: Dictionary containing the updated record data
            record_id: The ID of the record to update (optional if included in record)
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        if record_id is not None:
            record["Id"] = record_id

        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_update(table_id, resolved_base_id)

        # Format request for API version
        formatted_record = self._request_adapter.format_record(record, self.api_version)

        response = self._patch(endpoint, data=formatted_record)
        if isinstance(response, dict):
            record_id = self._response_adapter.extract_record_id(response, self.api_version)
        else:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"Expected dict response from update operation, got {type(response)}",
            )
        if record_id is None:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"No record ID returned from update operation. Response: {response}",
            )
        return record_id  # type: ignore[no-any-return]

    def delete_record(
        self, table_id: str, record_id: int | str, base_id: str | None = None
    ) -> int | str:
        """Delete a record from a table.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the deleted record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_delete(table_id, resolved_base_id)

        # Format request for API version
        delete_data = self._request_adapter.format_delete(record_id, self.api_version)

        response = self._delete(endpoint, data=delete_data)
        if isinstance(response, dict):
            deleted_id = self._response_adapter.extract_record_id(response, self.api_version)
        else:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"Expected dict response from delete operation, got {type(response)}",
            )
        if deleted_id is None:
            raise NocoDBException(
                "INVALID_RESPONSE",
                f"No record ID returned from delete operation. Response: {response}",
            )
        return deleted_id  # type: ignore[no-any-return]

    def count_records(
        self, table_id: str, where: str | None = None, base_id: str | None = None
    ) -> int:
        """Count records in a table.

        Args:
            table_id: The ID of the table
            where: Filter condition (e.g., "(Name,eq,John)")
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Number of records matching the criteria

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_count(table_id, resolved_base_id)

        params = {}
        if where:
            # Current NocoDB requires "neq" (not "ne") on both v2 and v3
            # (verified live); normalize so the documented "ne" keeps working.
            params["where"] = self._param_adapter.normalize_where_operators(where)

        response = self._get(endpoint, params=params)
        count = response.get("count", 0)
        return int(count) if count is not None else 0

    def bulk_insert_records(
        self, table_id: str, records: list[dict[str, Any]], base_id: str | None = None
    ) -> list[int | str]:
        """Insert multiple records at once for better performance.

        Args:
            table_id: The ID of the table
            records: List of record dictionaries to insert
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of inserted record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If records data is invalid
        """
        if not records:
            return []

        if not isinstance(records, list):
            raise ValidationException("Records must be a list")

        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_create(table_id, resolved_base_id)

        # Format request for API version
        formatted_data = self._request_adapter.format_records(records, self.api_version)

        try:
            response = self._post(endpoint, data=formatted_data)

            # Extract record IDs using version-aware adapter
            record_ids = self._response_adapter.extract_record_ids(response, self.api_version)
            if record_ids:
                return record_ids

            raise NocoDBException("INVALID_RESPONSE", "Unexpected response format from bulk insert")

        except Exception as e:
            if isinstance(e, NocoDBException):
                raise
            raise NocoDBException("BULK_INSERT_ERROR", f"Bulk insert failed: {str(e)}") from e

    def bulk_update_records(
        self, table_id: str, records: list[dict[str, Any]], base_id: str | None = None
    ) -> list[int | str]:
        """Update multiple records at once for better performance.

        Args:
            table_id: The ID of the table
            records: List of record dictionaries to update (must include Id field)
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of updated record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If records data is invalid
        """
        if not records:
            return []

        if not isinstance(records, list):
            raise ValidationException("Records must be a list")

        # Validate that all records have ID field
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValidationException(f"Record at index {i} must be a dictionary")
            if "Id" not in record:
                raise ValidationException(f"Record at index {i} missing required 'Id' field")

        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_update(table_id, resolved_base_id)

        # Format request for API version
        formatted_data = self._request_adapter.format_records(records, self.api_version)

        try:
            response = self._patch(endpoint, data=formatted_data)

            # Extract record IDs using version-aware adapter
            record_ids = self._response_adapter.extract_record_ids(response, self.api_version)
            if record_ids:
                return record_ids

            raise NocoDBException("INVALID_RESPONSE", "Unexpected response format from bulk update")

        except Exception as e:
            if isinstance(e, NocoDBException):
                raise
            raise NocoDBException("BULK_UPDATE_ERROR", f"Bulk update failed: {str(e)}") from e

    def bulk_delete_records(
        self, table_id: str, record_ids: list[int | str], base_id: str | None = None
    ) -> list[int | str]:
        """Delete multiple records at once for better performance.

        Args:
            table_id: The ID of the table
            record_ids: List of record IDs to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of deleted record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If record_ids is invalid
        """
        if not record_ids:
            return []

        if not isinstance(record_ids, list):
            raise ValidationException("Record IDs must be a list")

        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build path using PathBuilder
        endpoint = self._path_builder.records_delete(table_id, resolved_base_id)

        # Format request for API version
        delete_data = self._request_adapter.format_bulk_delete(record_ids, self.api_version)

        try:
            response = self._delete(endpoint, data=delete_data)

            # Extract record IDs using version-aware adapter
            deleted_ids = self._response_adapter.extract_record_ids(response, self.api_version)
            if deleted_ids:
                return deleted_ids

            raise NocoDBException("INVALID_RESPONSE", "Unexpected response format from bulk delete")

        except Exception as e:
            if isinstance(e, NocoDBException):
                raise
            raise NocoDBException("BULK_DELETE_ERROR", f"Bulk delete failed: {str(e)}") from e

    def _multipart_post(
        self,
        endpoint: str,
        files: dict[str, Any],
        fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a multipart POST request for file uploads."""
        url = f"{self._base_url}/{endpoint}"
        form_data = MultipartEncoder(fields={**fields, **files} if fields else files)
        headers = self.headers.copy()
        headers["Content-Type"] = form_data.content_type
        response = self._session.post(
            url, headers=headers, data=form_data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()  # type: ignore[no-any-return]

    def _upload_file(self, table_id: str, file_path: str | Path) -> Any:
        """Upload a file to NocoDB storage (v2 storage endpoint).

        Returns attachment object(s) which the caller writes into a record's
        attachment field via a record update. This is the v2 mechanism; v3 uses
        a per-cell upload instead (see :meth:`_upload_file_to_cell`).

        Args:
            table_id: The ID of the table
            file_path: Path to the file to upload

        Returns:
            Upload response with file information (list of attachment objects)

        Raises:
            NocoDBException: For upload errors
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise NocoDBException("FILE_NOT_FOUND", f"File not found: {file_path}")

        filename = file_path.name
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"

        endpoint = self._path_builder.file_upload(table_id)

        with file_path.open("rb") as f:
            files = {"file": (filename, f, mime_type)}
            path = f"files/{table_id}"
            return self._multipart_post(endpoint, files, fields={"path": path})

    def _resolve_field_id(self, table_id: str, field_name: str) -> str:
        """Resolve an attachment field's id from its title/name.

        Needed for the v3 per-cell upload endpoint, which addresses the field by
        id rather than name. Uses the v2 table-meta endpoint, which is available
        regardless of the data API version in use.

        Raises:
            NocoDBException: If the field cannot be found.
        """
        info = self._get(f"api/v2/meta/tables/{table_id}")
        for col in info.get("columns", []):
            if field_name in (col.get("title"), col.get("column_name")):
                return str(col["id"])
        raise NocoDBException(
            "FIELD_NOT_FOUND", f"Field '{field_name}' not found in table {table_id}"
        )

    def _upload_file_to_cell(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        file_path: str | Path,
        base_id: str | None = None,
    ) -> Any:
        """Upload a file into a record's attachment cell (API v3).

        v3 has no usable storage-upload + record-PATCH flow (the PATCH silently
        drops the attachment, returning the field as ``[]``). The per-cell
        endpoint ``.../records/{recordId}/fields/{fieldId}/upload`` is the
        verified mechanism: it takes a single JSON object
        ``{"contentType", "filename", "file"}`` where ``file`` is the
        base64-encoded file content, appends the attachment to the cell, and
        returns the updated record. (Verified live against releaseVersion
        2026.05.2 — multipart bodies and list-wrapped descriptors are rejected
        with HTTP 400; content integrity on download confirmed.)

        Returns the upload response (the updated record).

        Raises:
            NocoDBException: For upload errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise NocoDBException("FILE_NOT_FOUND", f"File not found: {file_path}")

        resolved_base_id = self._resolve_base_id(table_id, base_id)
        field_id = self._resolve_field_id(table_id, field_name)

        filename = file_path.name
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"

        encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
        endpoint = self._path_builder.file_upload(
            table_id, resolved_base_id, str(record_id), field_id
        )
        return self._post(
            endpoint,
            data={"contentType": mime_type, "filename": filename, "file": encoded},
        )

    def attach_file_to_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        file_path: str | Path,
        base_id: str | None = None,
    ) -> int | str:
        """Attach a file to a record without overwriting existing files.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path to the file to attach
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.attach_files_to_record(table_id, record_id, field_name, [file_path], base_id)

    def attach_files_to_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        file_paths: list[str | Path],
        base_id: str | None = None,
    ) -> int | str:
        """Attach multiple files to a record without overwriting existing files.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_paths: List of file paths to attach
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        # v3: the per-cell upload endpoint appends directly to the attachment
        # field, so no read-modify-write is needed (and the v2 storage + PATCH
        # flow does not work on v3 — the PATCH silently drops the file).
        if self.api_version == APIVersion.V3:
            for file_path in file_paths:
                self._upload_file_to_cell(table_id, record_id, field_name, file_path, base_id)
            return record_id

        # v2: upload to storage, then append the returned objects to the field.
        existing_record = self.get_record(table_id, record_id, base_id=base_id, fields=[field_name])
        existing_files = existing_record.get(field_name, []) or []

        for file_path in file_paths:
            upload_response = self._upload_file(table_id, file_path)
            # NocoDB upload returns an array of file objects
            if isinstance(upload_response, list):
                existing_files.extend(upload_response)
            elif isinstance(upload_response, dict):
                existing_files.append(upload_response)
            else:
                raise NocoDBException("INVALID_RESPONSE", "Invalid upload response format")

        record_update = {field_name: existing_files}
        return self.update_record(table_id, record_update, record_id, base_id)

    def delete_file_from_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        base_id: str | None = None,
    ) -> int | str:
        """Delete all files from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        record = {field_name: "[]"}
        return self.update_record(table_id, record, record_id, base_id)

    def _resolve_attachment_url(self, file_info: dict[str, Any]) -> str:
        """Resolve a downloadable URL for an attachment across storage backends.

        NocoDB populates different keys depending on the storage adapter:

        * local storage -> ``signedPath`` (relative; prepend base_url) and ``path``
        * S3-type remote -> ``signedUrl`` (absolute) and ``url``

        Signed variants are preferred (they work with ``NC_SECURE_ATTACHMENTS``)
        but are short-lived (default 2h), so callers should download promptly.

        Raises:
            NocoDBException: If no usable path/url is present on the attachment.
        """
        if file_info.get("signedPath"):
            return f"{self._base_url}/{file_info['signedPath']}"
        if file_info.get("signedUrl"):
            return str(file_info["signedUrl"])
        if file_info.get("url"):
            return str(file_info["url"])
        if file_info.get("path"):
            return f"{self._base_url}/{file_info['path']}"
        title = file_info.get("title", "unknown")
        raise NocoDBException(
            "DOWNLOAD_ERROR",
            f"Attachment '{title}' has no downloadable path or url "
            "(expected one of signedPath, signedUrl, url, path)",
        )

    def _download_single_file(self, file_info: dict[str, Any], file_path: Path) -> None:
        """Helper method to download a single file.

        Args:
            file_info: File information dict from NocoDB (attachment object). Works
                with both local-storage (signedPath/path) and remote/S3
                (signedUrl/url) backends.
            file_path: Path where the file should be saved

        Raises:
            NocoDBException: If download fails
        """
        download_url = self._resolve_attachment_url(file_info)

        response = self._session.get(
            download_url, headers=self.headers, timeout=self._request_timeout, stream=True
        )

        if response.status_code != 200:
            file_title = file_info.get("title", "unknown")
            raise NocoDBException(
                "DOWNLOAD_ERROR",
                f"Failed to download file {file_title}. HTTP status code: {response.status_code}",
            )

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def download_file_from_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        file_path: str | Path,
        base_id: str | None = None,
    ) -> None:
        """Download the first file from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path where the file should be saved
            base_id: Base ID (required for v3, optional for v2)

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        record = self.get_record(table_id, record_id, base_id=base_id, fields=[field_name])

        if field_name not in record or not record[field_name]:
            raise NocoDBException("FILE_NOT_FOUND", "No file found in the specified field.")

        file_info = record[field_name][0]  # Get first file
        self._download_single_file(file_info, Path(file_path))

    def download_files_from_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        directory: str | Path,
        base_id: str | None = None,
    ) -> None:
        """Download all files from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            directory: Directory where files should be saved
            base_id: Base ID (required for v3, optional for v2)

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        record = self.get_record(table_id, record_id, base_id=base_id, fields=[field_name])

        if field_name not in record or not record[field_name]:
            raise NocoDBException("FILE_NOT_FOUND", "No files found in the specified field.")

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        for file_info in record[field_name]:
            file_title = file_info["title"]
            file_path = directory / file_title
            self._download_single_file(file_info, file_path)

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()

    def __enter__(self) -> "NocoDBClient":
        """Support for context manager usage."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support for context manager usage."""
        self.close()
