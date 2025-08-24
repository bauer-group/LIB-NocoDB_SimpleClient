"""
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
"""NocoDB REST API client implementation."""

import mimetypes
from pathlib import Path
from typing import Any, Optional, Union

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .exceptions import NocoDBException, RecordNotFoundException


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

    Attributes:
        headers (Dict[str, str]): HTTP headers used for requests

    Example:
        >>> # Default usage
        >>> client = NocoDBClient(
        ...     base_url="https://app.nocodb.com",
        ...     db_auth_token="your-api-token"
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
        base_url: str,
        db_auth_token: str,
        access_protection_auth: Optional[str] = None,
        access_protection_header: str = "X-BAUERGROUP-Auth",
        max_redirects: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "xc-token": db_auth_token,
        }

        if access_protection_auth:
            self.headers[access_protection_header] = access_protection_auth

        self._request_timeout = timeout
        self._session = requests.Session()

        if max_redirects is not None:
            self._session.max_redirects = max_redirects

    def _get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.get(
            url, headers=self.headers, params=params, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()

    def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.post(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()

    def _patch(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a PATCH request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.patch(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()

    def _put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a PUT request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.put(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()

    def _delete(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a DELETE request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.delete(
            url, headers=self.headers, json=data, timeout=self._request_timeout
        )
        self._check_for_error(response)
        return response.json()

    def _check_for_error(self, response: requests.Response) -> None:
        """Check HTTP response for errors and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                error_info = response.json()
                if "error" in error_info and "message" in error_info:
                    if error_info["error"] == "RECORD_NOT_FOUND":
                        raise RecordNotFoundException(error_info["error"], error_info["message"])
                    else:
                        raise NocoDBException(error_info["error"], error_info["message"])
            except ValueError:
                pass
            response.raise_for_status()

    def get_records(
        self,
        table_id: str,
        sort: Optional[str] = None,
        where: Optional[str] = None,
        fields: Optional[list[str]] = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get multiple records from a table.

        Args:
            table_id: The ID of the table
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

            response = self._get(f"api/v2/tables/{table_id}/records", params=params)

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
        record_id: Union[int, str],
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Get a single record by ID.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            fields: List of fields to retrieve

        Returns:
            Record dictionary

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        return self._get(f"api/v2/tables/{table_id}/records/{record_id}", params=params)

    def insert_record(self, table_id: str, record: dict[str, Any]) -> Union[int, str]:
        """Insert a new record into a table.

        Args:
            table_id: The ID of the table
            record: Dictionary containing the record data

        Returns:
            The ID of the inserted record

        Raises:
            NocoDBException: For API errors
        """
        response = self._post(f"api/v2/tables/{table_id}/records", data=record)
        return response.get("Id")

    def update_record(
        self,
        table_id: str,
        record: dict[str, Any],
        record_id: Optional[Union[int, str]] = None,
    ) -> Union[int, str]:
        """Update an existing record.

        Args:
            table_id: The ID of the table
            record: Dictionary containing the updated record data
            record_id: The ID of the record to update (optional if included in record)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        if record_id is not None:
            record["Id"] = record_id

        response = self._patch(f"api/v2/tables/{table_id}/records", data=record)
        return response.get("Id")

    def delete_record(self, table_id: str, record_id: Union[int, str]) -> Union[int, str]:
        """Delete a record from a table.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record to delete

        Returns:
            The ID of the deleted record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        response = self._delete(f"api/v2/tables/{table_id}/records", data={"Id": record_id})
        return response.get("Id")

    def count_records(self, table_id: str, where: Optional[str] = None) -> int:
        """Count records in a table.

        Args:
            table_id: The ID of the table
            where: Filter condition (e.g., "(Name,eq,John)")

        Returns:
            Number of records matching the criteria

        Raises:
            NocoDBException: For API errors
        """
        params = {}
        if where:
            params["where"] = where

        response = self._get(f"api/v2/tables/{table_id}/records/count", params=params)
        return response.get("count", 0)

    def _multipart_post(
        self,
        endpoint: str,
        files: dict[str, Any],
        fields: Optional[dict[str, Any]] = None,
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
        return response.json()

    def _upload_file(self, table_id: str, file_path: Union[str, Path]) -> dict[str, Any]:
        """Upload a file to NocoDB storage.

        Args:
            table_id: The ID of the table
            file_path: Path to the file to upload

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

        with file_path.open("rb") as f:
            files = {"file": (filename, f, mime_type)}
            path = f"files/{table_id}"
            return self._multipart_post("api/v2/storage/upload", files, fields={"path": path})

    def attach_file_to_record(
        self,
        table_id: str,
        record_id: Union[int, str],
        field_name: str,
        file_path: Union[str, Path],
    ) -> Union[int, str]:
        """Attach a file to a record.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path to the file to attach

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        upload_response = self._upload_file(table_id, file_path)
        record = {field_name: upload_response}
        return self.update_record(table_id, record, record_id)

    def attach_files_to_record(
        self,
        table_id: str,
        record_id: Union[int, str],
        field_name: str,
        file_paths: list[Union[str, Path]],
    ) -> Union[int, str]:
        """Attach multiple files to a record without overwriting existing files.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_paths: List of file paths to attach

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        existing_record = self.get_record(table_id, record_id, fields=[field_name])
        existing_files = existing_record.get(field_name, []) or []

        for file_path in file_paths:
            upload_response = self._upload_file(table_id, file_path)
            existing_files.append(upload_response[0])

        record_update = {field_name: existing_files}
        return self.update_record(table_id, record_update, record_id)

    def delete_file_from_record(
        self,
        table_id: str,
        record_id: Union[int, str],
        field_name: str,
    ) -> Union[int, str]:
        """Delete all files from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        record = {field_name: "[]"}
        return self.update_record(table_id, record, record_id)

    def download_file_from_record(
        self,
        table_id: str,
        record_id: Union[int, str],
        field_name: str,
        file_path: Union[str, Path],
    ) -> None:
        """Download the first file from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path where the file should be saved

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        record = self.get_record(table_id, record_id, fields=[field_name])

        if field_name not in record or not record[field_name]:
            raise NocoDBException("FILE_NOT_FOUND", "No file found in the specified field.")

        file_info = record[field_name][0]  # Get first file
        signed_path = file_info["signedPath"]
        download_url = f"{self._base_url}/{signed_path}"

        response = self._session.get(
            download_url, headers=self.headers, timeout=self._request_timeout, stream=True
        )

        if response.status_code != 200:
            raise NocoDBException(
                "DOWNLOAD_ERROR",
                f"Failed to download file. HTTP status code: {response.status_code}",
            )

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def download_files_from_record(
        self,
        table_id: str,
        record_id: Union[int, str],
        field_name: str,
        directory: Union[str, Path],
    ) -> None:
        """Download all files from a record field.

        Args:
            table_id: The ID of the table
            record_id: The ID of the record
            field_name: The name of the attachment field
            directory: Directory where files should be saved

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        record = self.get_record(table_id, record_id, fields=[field_name])

        if field_name not in record or not record[field_name]:
            raise NocoDBException("FILE_NOT_FOUND", "No files found in the specified field.")

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        for file_info in record[field_name]:
            signed_path = file_info["signedPath"]
            file_title = file_info["title"]
            download_url = f"{self._base_url}/{signed_path}"

            response = self._session.get(
                download_url, headers=self.headers, timeout=self._request_timeout, stream=True
            )

            if response.status_code != 200:
                raise NocoDBException(
                    "DOWNLOAD_ERROR",
                    f"Failed to download file {file_title}. HTTP status code: {response.status_code}",
                )

            file_path = directory / file_title
            with file_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()

    def __enter__(self):
        """Support for context manager usage."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager usage."""
        self.close()
