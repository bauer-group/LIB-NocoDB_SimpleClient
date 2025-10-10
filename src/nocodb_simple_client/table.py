"""NocoDB table wrapper for simplified operations.

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

from pathlib import Path
from typing import Any

from .client import NocoDBClient
from .query_builder import QueryBuilder


class NocoDBTable:
    """A wrapper class for performing operations on a specific NocoDB table.

    This class provides a convenient interface for working with a single table
    by wrapping the NocoDBClient methods and automatically passing the table ID.

    Args:
        client: An instance of NocoDBClient
        table_id: The ID of the table to operate on

    Attributes:
        client: The NocoDB client instance
        table_id: The table ID this instance operates on

    Example:
        >>> client = NocoDBClient(base_url="...", db_auth_token="...")
        >>> table = NocoDBTable(client, table_id="table123")
        >>> records = table.get_records(limit=10)
    """

    def __init__(self, client: NocoDBClient, table_id: str) -> None:
        self.client = client
        self.table_id = table_id

    def get_records(
        self,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        limit: int = 25,
        base_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get multiple records from the table.

        Args:
            sort: Sort criteria (e.g., "Id", "-CreatedAt")
            where: Filter condition (e.g., "(Name,eq,John)")
            fields: List of fields to retrieve
            limit: Maximum number of records to retrieve
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of record dictionaries

        Raises:
            RecordNotFoundException: If no records match the criteria
            NocoDBException: For other API errors
        """
        return self.client.get_records(
            self.table_id, base_id=base_id, sort=sort, where=where, fields=fields, limit=limit
        )

    def get_record(
        self,
        record_id: int | str,
        fields: list[str] | None = None,
        base_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a single record by ID.

        Args:
            record_id: The ID of the record
            fields: List of fields to retrieve
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Record dictionary

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.get_record(self.table_id, record_id, base_id=base_id, fields=fields)

    def insert_record(
        self,
        record: dict[str, Any],
        base_id: str | None = None,
    ) -> int | str:
        """Insert a new record into the table.

        Args:
            record: Dictionary containing the record data
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the inserted record

        Raises:
            NocoDBException: For API errors
        """
        return self.client.insert_record(self.table_id, record, base_id=base_id)

    def update_record(
        self,
        record: dict[str, Any],
        record_id: int | str | None = None,
        base_id: str | None = None,
    ) -> int | str:
        """Update an existing record.

        Args:
            record: Dictionary containing the updated record data
            record_id: The ID of the record to update (optional if included in record)
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.update_record(self.table_id, record, record_id, base_id=base_id)

    def delete_record(
        self,
        record_id: int | str,
        base_id: str | None = None,
    ) -> int | str:
        """Delete a record from the table.

        Args:
            record_id: The ID of the record to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            The ID of the deleted record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.delete_record(self.table_id, record_id, base_id=base_id)

    def count_records(
        self,
        where: str | None = None,
        base_id: str | None = None,
    ) -> int:
        """Count records in the table.

        Args:
            where: Filter condition (e.g., "(Name,eq,John)")
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Number of records matching the criteria

        Raises:
            NocoDBException: For API errors
        """
        return self.client.count_records(self.table_id, where, base_id=base_id)

    def bulk_insert_records(
        self,
        records: list[dict[str, Any]],
        base_id: str | None = None,
    ) -> list[int | str]:
        """Insert multiple records at once for better performance.

        Args:
            records: List of record dictionaries to insert
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of inserted record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If records data is invalid
        """
        return self.client.bulk_insert_records(self.table_id, records, base_id=base_id)

    def bulk_update_records(
        self,
        records: list[dict[str, Any]],
        base_id: str | None = None,
    ) -> list[int | str]:
        """Update multiple records at once for better performance.

        Args:
            records: List of record dictionaries to update (must include Id field)
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of updated record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If records data is invalid
        """
        return self.client.bulk_update_records(self.table_id, records, base_id=base_id)

    def bulk_delete_records(
        self,
        record_ids: list[int | str],
        base_id: str | None = None,
    ) -> list[int | str]:
        """Delete multiple records at once for better performance.

        Args:
            record_ids: List of record IDs to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of deleted record IDs

        Raises:
            NocoDBException: For API errors
            ValidationException: If record_ids is invalid
        """
        return self.client.bulk_delete_records(self.table_id, record_ids, base_id=base_id)

    def query(self) -> QueryBuilder:
        """Create a new QueryBuilder for this table.

        Returns:
            QueryBuilder instance for building complex queries

        Example:
            >>> records = (table.query()
            ...     .select('Name', 'Email', 'Status')
            ...     .where('Status', 'eq', 'Active')
            ...     .order_by('CreatedAt', 'desc')
            ...     .limit(50)
            ...     .execute())
        """
        return QueryBuilder(self)

    def attach_file_to_record(
        self,
        record_id: int | str,
        field_name: str,
        file_path: str | Path,
    ) -> int | str:
        """Attach a file to a record.

        Args:
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path to the file to attach

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.attach_file_to_record(self.table_id, record_id, field_name, file_path)

    def attach_files_to_record(
        self,
        record_id: int | str,
        field_name: str,
        file_paths: list[str | Path],
    ) -> int | str:
        """Attach multiple files to a record without overwriting existing files.

        Args:
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_paths: List of file paths to attach

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.attach_files_to_record(self.table_id, record_id, field_name, file_paths)

    def delete_file_from_record(
        self,
        record_id: int | str,
        field_name: str,
    ) -> int | str:
        """Delete all files from a record field.

        Args:
            record_id: The ID of the record
            field_name: The name of the attachment field

        Returns:
            The ID of the updated record

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: For other API errors
        """
        return self.client.delete_file_from_record(self.table_id, record_id, field_name)

    def download_file_from_record(
        self,
        record_id: int | str,
        field_name: str,
        file_path: str | Path,
    ) -> None:
        """Download the first file from a record field.

        Args:
            record_id: The ID of the record
            field_name: The name of the attachment field
            file_path: Path where the file should be saved

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        return self.client.download_file_from_record(
            self.table_id, record_id, field_name, file_path
        )

    def download_files_from_record(
        self,
        record_id: int | str,
        field_name: str,
        directory: str | Path,
    ) -> None:
        """Download all files from a record field.

        Args:
            record_id: The ID of the record
            field_name: The name of the attachment field
            directory: Directory where files should be saved

        Raises:
            RecordNotFoundException: If the record is not found
            NocoDBException: If no files are found or download fails
        """
        return self.client.download_files_from_record(
            self.table_id, record_id, field_name, directory
        )
