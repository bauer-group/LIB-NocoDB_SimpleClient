"""Links and relations management for NocoDB.

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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import NocoDBClient


class NocoDBLinks:
    """Manager for NocoDB table relationships and linked records.

    Provides methods to manage relationships between records in different tables,
    including linking, unlinking, and querying linked records.
    """

    def __init__(self, client: "NocoDBClient") -> None:
        """Initialize the links manager.

        Args:
            client: NocoDBClient instance
        """
        self.client = client

    def get_linked_records(
        self,
        table_id: str,
        record_id: int | str,
        link_field_id: str,
        fields: list[str] | None = None,
        sort: str | None = None,
        where: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get records linked to a specific record through a link field.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to get linked records for
            link_field_id: ID of the link field (relationship field)
            fields: List of fields to retrieve from linked records
            sort: Sort criteria for linked records
            where: Filter conditions for linked records
            limit: Maximum number of linked records to retrieve
            offset: Number of records to skip

        Returns:
            List of linked record dictionaries with pageInfo

        Raises:
            NocoDBException: For API errors
            RecordNotFoundException: If the source record is not found
        """
        params: dict[str, str | int] = {"limit": limit, "offset": offset}

        if fields:
            params["fields"] = ",".join(fields)
        if sort:
            params["sort"] = sort
        if where:
            params["where"] = where

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        endpoint = f"api/v2/tables/{table_id}/links/{link_field_id}/records/{record_id}"
        response = self.client._get(endpoint, params=params)

        linked_list = response.get("list", [])
        return linked_list if isinstance(linked_list, list) else []

    def count_linked_records(
        self,
        table_id: str,
        record_id: int | str,
        link_field_id: str,
        where: str | None = None,
    ) -> int:
        """Count linked records for a specific record.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to count linked records for
            link_field_id: ID of the link field
            where: Filter conditions for linked records

        Returns:
            Number of linked records

        Raises:
            NocoDBException: For API errors
        """
        params = {}
        if where:
            params["where"] = where

        endpoint = f"api/v2/tables/{table_id}/links/{link_field_id}/records/{record_id}/count"
        response = self.client._get(endpoint, params=params)

        count = response.get("count", 0)
        return count if isinstance(count, int) else 0

    def link_records(
        self,
        table_id: str,
        record_id: int | str,
        link_field_id: str,
        linked_record_ids: list[int | str],
    ) -> bool:
        """Link records to a specific record.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to link to
            link_field_id: ID of the link field
            linked_record_ids: List of record IDs to link

        Returns:
            True if linking was successful

        Raises:
            NocoDBException: For API errors
            ValidationException: If linked_record_ids is invalid
        """
        if not linked_record_ids:
            return True

        if not isinstance(linked_record_ids, list):
            raise ValueError("linked_record_ids must be a list")

        # Convert to expected format
        data = [{"Id": record_id} for record_id in linked_record_ids]

        endpoint = f"api/v2/tables/{table_id}/links/{link_field_id}/records/{record_id}"
        response = self.client._post(endpoint, data=data)

        return response is not None

    def unlink_records(
        self,
        table_id: str,
        record_id: int | str,
        link_field_id: str,
        linked_record_ids: list[int | str],
    ) -> bool:
        """Unlink records from a specific record.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to unlink from
            link_field_id: ID of the link field
            linked_record_ids: List of record IDs to unlink

        Returns:
            True if unlinking was successful

        Raises:
            NocoDBException: For API errors
            ValidationException: If linked_record_ids is invalid
        """
        if not linked_record_ids:
            return True

        if not isinstance(linked_record_ids, list):
            raise ValueError("linked_record_ids must be a list")

        # Convert to expected format
        data = [{"Id": record_id} for record_id in linked_record_ids]

        endpoint = f"api/v2/tables/{table_id}/links/{link_field_id}/records/{record_id}"
        response = self.client._delete(endpoint, data=data)

        return response is not None

    def unlink_all_records(self, table_id: str, record_id: int | str, link_field_id: str) -> bool:
        """Unlink all records from a specific record.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to unlink all from
            link_field_id: ID of the link field

        Returns:
            True if unlinking was successful

        Raises:
            NocoDBException: For API errors
        """
        # First get all linked records
        linked_records = self.get_linked_records(
            table_id, record_id, link_field_id, fields=["Id"], limit=1000  # Get a large batch
        )

        if not linked_records:
            return True

        # Extract IDs and unlink
        linked_ids = [record["Id"] for record in linked_records if "Id" in record]

        if linked_ids:
            return self.unlink_records(table_id, record_id, link_field_id, linked_ids)

        return True

    def replace_links(
        self,
        table_id: str,
        record_id: int | str,
        link_field_id: str,
        new_linked_record_ids: list[int | str],
    ) -> bool:
        """Replace all existing links with new ones.

        Args:
            table_id: ID of the source table
            record_id: ID of the record to update links for
            link_field_id: ID of the link field
            new_linked_record_ids: List of new record IDs to link

        Returns:
            True if replacement was successful

        Raises:
            NocoDBException: For API errors
        """
        # First unlink all existing records
        self.unlink_all_records(table_id, record_id, link_field_id)

        # Then link the new records
        if new_linked_record_ids:
            return self.link_records(table_id, record_id, link_field_id, new_linked_record_ids)

        return True

    def get_link_field_info(self, table_id: str, link_field_id: str) -> dict[str, Any]:
        """Get information about a link field.

        Args:
            table_id: ID of the table containing the link field
            link_field_id: ID of the link field

        Returns:
            Dictionary with link field information

        Raises:
            NocoDBException: For API errors
        """
        # This would require access to table schema/columns endpoint
        # For now, we'll implement a basic version
        endpoint = f"api/v2/tables/{table_id}/columns/{link_field_id}"
        try:
            return self.client._get(endpoint)
        except Exception:
            # Fallback - return basic structure
            return {"id": link_field_id, "table_id": table_id, "type": "Link"}

    def bulk_link_records(self, operations: list[dict[str, Any]]) -> list[bool]:
        """Perform multiple link operations in batch.

        Args:
            operations: List of link operation dictionaries, each containing:
                - table_id: Source table ID
                - record_id: Source record ID
                - link_field_id: Link field ID
                - linked_record_ids: List of record IDs to link
                - action: 'link' or 'unlink'

        Returns:
            List of boolean results for each operation

        Raises:
            NocoDBException: For API errors
            ValidationException: If operations format is invalid
        """
        results = []

        for operation in operations:
            try:
                table_id = operation["table_id"]
                record_id = operation["record_id"]
                link_field_id = operation["link_field_id"]
                linked_record_ids = operation["linked_record_ids"]
                action = operation.get("action", "link")

                if action == "link":
                    result = self.link_records(
                        table_id, record_id, link_field_id, linked_record_ids
                    )
                elif action == "unlink":
                    result = self.unlink_records(
                        table_id, record_id, link_field_id, linked_record_ids
                    )
                else:
                    raise ValueError(f"Invalid action: {action}. Must be 'link' or 'unlink'")

                results.append(result)

            except Exception:
                # Log error and continue with next operation
                results.append(False)

        return results

    def get_relationship_summary(self, table_id: str, record_id: int | str) -> dict[str, int]:
        """Get a summary of all relationships for a record.

        Args:
            table_id: ID of the table
            record_id: ID of the record

        Returns:
            Dictionary mapping link field names to count of linked records

        Note:
            This is a convenience method that would require knowledge of
            all link fields in the table. Implementation would need to
            query table schema first.
        """
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Get table schema to identify link fields
        # 2. For each link field, count linked records
        # 3. Return summary dictionary

        return {
            # Example: 'Users': 5, 'Orders': 12
        }


class TableLinks:
    """Helper class for managing links on a specific table.

    This is a convenience wrapper that automatically includes table_id
    in all link operations.
    """

    def __init__(self, links_manager: NocoDBLinks, table_id: str) -> None:
        """Initialize table-specific links manager.

        Args:
            links_manager: NocoDBLinks instance
            table_id: ID of the table
        """
        self._links = links_manager
        self._table_id = table_id

    def get_linked_records(
        self, record_id: int | str, link_field_id: str, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Get linked records for this table."""
        return self._links.get_linked_records(self._table_id, record_id, link_field_id, **kwargs)

    def count_linked_records(
        self, record_id: int | str, link_field_id: str, where: str | None = None
    ) -> int:
        """Count linked records for this table."""
        return self._links.count_linked_records(self._table_id, record_id, link_field_id, where)

    def link_records(
        self,
        record_id: int | str,
        link_field_id: str,
        linked_record_ids: list[int | str],
    ) -> bool:
        """Link records for this table."""
        return self._links.link_records(self._table_id, record_id, link_field_id, linked_record_ids)

    def unlink_records(
        self,
        record_id: int | str,
        link_field_id: str,
        linked_record_ids: list[int | str],
    ) -> bool:
        """Unlink records for this table."""
        return self._links.unlink_records(
            self._table_id, record_id, link_field_id, linked_record_ids
        )

    def unlink_all_records(self, record_id: int | str, link_field_id: str) -> bool:
        """Unlink all records for this table."""
        return self._links.unlink_all_records(self._table_id, record_id, link_field_id)

    def replace_links(
        self,
        record_id: int | str,
        link_field_id: str,
        new_linked_record_ids: list[int | str],
    ) -> bool:
        """Replace all links for this table."""
        return self._links.replace_links(
            self._table_id, record_id, link_field_id, new_linked_record_ids
        )
