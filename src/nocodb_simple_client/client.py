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

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from .config import NocoDBConfig

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .api_version import APIVersion, PathBuilder, QueryParamAdapter
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
                elif response.status_code >= 500:
                    raise ServerErrorException(message, response.status_code)
                else:
                    raise NocoDBException(error_code, message, response.status_code, error_info)

            except ValueError as e:
                # If response is not JSON, create generic error
                if response.status_code == 401:
                    raise AuthenticationException(
                        f"Authentication failed (HTTP {response.status_code})"
                    ) from e
                elif response.status_code == 403:
                    raise AuthorizationException(
                        f"Access denied (HTTP {response.status_code})"
                    ) from e
                else:
                    raise NocoDBException(
                        "HTTP_ERROR", f"HTTP {response.status_code} error", response.status_code
                    ) from e

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

            # Convert query parameters for v3
            if self.api_version == APIVersion.V3:
                params = self._param_adapter.convert_pagination_to_v3(params)
                if sort:
                    params["sort"] = self._param_adapter.convert_sort_to_v3(sort)

            response = self._get(endpoint, params=params)

            batch_records = response.get("list", [])
            records.extend(batch_records)

            page_info = response.get("pageInfo", {})
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

        return self._get(endpoint, params=params)

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

        response = self._post(endpoint, data=record)
        # API v2 returns a single object: {"Id": 123}
        if isinstance(response, dict):
            record_id = response.get("Id")
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

        response = self._patch(endpoint, data=record)
        if isinstance(response, dict):
            record_id = response.get("Id")
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

        response = self._delete(endpoint, data={"Id": record_id})
        if isinstance(response, dict):
            deleted_id = response.get("Id")
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
            params["where"] = where

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

        # NocoDB v2 API supports bulk insert via array payload
        try:
            response = self._post(endpoint, data=records)

            # Response should be list of record IDs
            if isinstance(response, list):
                record_ids = []
                for record in response:
                    if isinstance(record, dict) and record.get("Id") is not None:
                        record_ids.append(record["Id"])
                return record_ids
            elif isinstance(response, dict) and "Id" in response:
                # Single record response (fallback)
                return [response["Id"]]
            else:
                raise NocoDBException(
                    "INVALID_RESPONSE", "Unexpected response format from bulk insert"
                )

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

        try:
            response = self._patch(endpoint, data=records)

            # Response should be list of record IDs
            if isinstance(response, list):
                record_ids = []
                for record in response:
                    if isinstance(record, dict) and record.get("Id") is not None:
                        record_ids.append(record["Id"])
                return record_ids
            elif isinstance(response, dict) and "Id" in response:
                # Single record response (fallback)
                return [response["Id"]]
            else:
                raise NocoDBException(
                    "INVALID_RESPONSE", "Unexpected response format from bulk update"
                )

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

        # Convert to list of dictionaries with Id field
        records_to_delete = [{"Id": record_id} for record_id in record_ids]

        try:
            response = self._delete(endpoint, data=records_to_delete)

            # Response should be list of record IDs
            if isinstance(response, list):
                record_ids = []
                for record in response:
                    if isinstance(record, dict) and record.get("Id") is not None:
                        record_ids.append(record["Id"])
                return record_ids
            elif isinstance(response, dict) and "Id" in response:
                # Single record response (fallback)
                return [response["Id"]]
            else:
                raise NocoDBException(
                    "INVALID_RESPONSE", "Unexpected response format from bulk delete"
                )

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

    def _upload_file(self, table_id: str, file_path: str | Path, base_id: str | None = None) -> Any:
        """Upload a file to NocoDB storage.

        Args:
            table_id: The ID of the table
            file_path: Path to the file to upload
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Upload response with file information

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

        # Resolve base_id for v3
        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        # Build upload endpoint
        endpoint = self._path_builder.file_upload(table_id, resolved_base_id)

        with file_path.open("rb") as f:
            files = {"file": (filename, f, mime_type)}
            path = f"files/{table_id}"
            return self._multipart_post(endpoint, files, fields={"path": path})

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
        existing_record = self.get_record(table_id, record_id, base_id=base_id, fields=[field_name])
        existing_files = existing_record.get(field_name, []) or []

        for file_path in file_paths:
            upload_response = self._upload_file(table_id, file_path, base_id)
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

    def _download_single_file(self, file_info: dict[str, Any], file_path: Path) -> None:
        """Helper method to download a single file.

        Args:
            file_info: File information dict from NocoDB (must contain 'signedPath')
            file_path: Path where the file should be saved

        Raises:
            NocoDBException: If download fails
        """
        signed_path = file_info["signedPath"]
        download_url = f"{self._base_url}/{signed_path}"

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
