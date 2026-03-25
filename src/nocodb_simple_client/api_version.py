"""NocoDB API version support and adapters.

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

from enum import Enum
from typing import Any


class APIVersion(str, Enum):
    """NocoDB API version."""

    V2 = "v2"
    V3 = "v3"

    def __str__(self) -> str:
        return self.value


class ResponseAdapter:
    """Adapter for normalizing API responses between v2 and v3 formats.

    v2 returns flat records with 'Id' key and 'list' wrapper.
    v3 returns records with 'id' key, 'fields' wrapper, and 'records' wrapper.
    This adapter normalizes v3 responses to v2-compatible flat format.
    """

    @staticmethod
    def normalize_record(record: dict[str, Any], api_version: "APIVersion") -> dict[str, Any]:
        """Normalize a single record response to flat format.

        v2 format: {"Id": 1, "Name": "John", ...}
        v3 format: {"id": 1, "fields": {"Name": "John", ...}}

        Returns flat format with "Id" key for consistency.
        """
        if api_version == APIVersion.V2:
            return record

        # v3: extract fields and normalize id
        result: dict[str, Any] = {}
        if "id" in record:
            result["Id"] = record["id"]
        if "fields" in record:
            result.update(record["fields"])
        else:
            # Fallback: if no fields wrapper, copy all except 'id'
            for k, v in record.items():
                if k == "id":
                    result["Id"] = v
                elif k != "deleted":
                    result[k] = v
        return result

    @staticmethod
    def normalize_records_list(
        response: dict[str, Any], api_version: "APIVersion"
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Normalize a records list response.

        v2: {"list": [...], "pageInfo": {"isLastPage": true, ...}}
        v3: {"records": [...], "next": "...", "prev": null}

        Returns (records_list, page_info) where page_info uses v2-compatible format.
        """
        if api_version == APIVersion.V2:
            records = response.get("list", [])
            page_info = response.get("pageInfo", {})
            return records, page_info

        # v3: extract from "records" key
        raw_records = response.get("records", [])
        records = [ResponseAdapter.normalize_record(r, api_version) for r in raw_records]

        # Convert v3 pagination to v2-compatible pageInfo
        has_next = response.get("next") is not None
        page_info = {
            "isLastPage": not has_next,
            "next": response.get("next"),
            "prev": response.get("prev"),
        }

        return records, page_info

    @staticmethod
    def extract_record_id(response: dict[str, Any], api_version: "APIVersion") -> Any:
        """Extract record ID from a create/update/delete response.

        v2: {"Id": 123}
        v3: {"id": 123, "fields": {...}} or {"records": [{"id": 123, ...}]}
        """
        if api_version == APIVersion.V2:
            return response.get("Id")

        # v3: try direct id first
        if "id" in response:
            return response["id"]

        # v3: try records wrapper (bulk responses)
        records = response.get("records", [])
        if records and isinstance(records, list) and len(records) > 0:
            return records[0].get("id")

        # Fallback: try "Id" (in case of mixed format)
        return response.get("Id")

    @staticmethod
    def extract_record_ids(
        response: dict[str, Any] | list[dict[str, Any]], api_version: "APIVersion"
    ) -> list[Any]:
        """Extract multiple record IDs from bulk operation responses.

        v2: [{"Id": 1}, {"Id": 2}]
        v3: {"records": [{"id": 1, ...}, {"id": 2, ...}]}
        """
        if api_version == APIVersion.V2:
            if isinstance(response, list):
                return [
                    r.get("Id") for r in response if isinstance(r, dict) and r.get("Id") is not None
                ]
            elif isinstance(response, dict) and "Id" in response:
                return [response["Id"]]
            return []

        # v3: records wrapper
        if isinstance(response, dict):
            records = response.get("records", [])
            if records:
                return [
                    r.get("id") for r in records if isinstance(r, dict) and r.get("id") is not None
                ]
            # Fallback: direct id
            if "id" in response:
                return [response["id"]]
        elif isinstance(response, list):
            return [
                r.get("id") for r in response if isinstance(r, dict) and r.get("id") is not None
            ]

        return []


class RequestAdapter:
    """Adapter for formatting API requests between v2 and v3 formats.

    v2 sends flat record data: {"Name": "John", "Email": "john@example.com"}
    v3 wraps field data: {"fields": {"Name": "John", "Email": "john@example.com"}}
    """

    @staticmethod
    def format_record(record: dict[str, Any], api_version: "APIVersion") -> dict[str, Any]:
        """Format a record for create/update requests.

        v2: {"Name": "John", "Email": "john@example.com"}
        v3: {"fields": {"Name": "John", "Email": "john@example.com"}}
        """
        if api_version == APIVersion.V2:
            return record

        # v3: wrap in fields, keeping Id/id separate
        fields = {}
        result: dict[str, Any] = {}
        for k, v in record.items():
            if k in ("Id", "id"):
                result["id"] = v
            else:
                fields[k] = v
        result["fields"] = fields
        return result

    @staticmethod
    def format_records(
        records: list[dict[str, Any]], api_version: "APIVersion"
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Format multiple records for bulk create/update requests.

        v2: [{"Name": "John"}, {"Name": "Jane"}]
        v3: {"records": [{"fields": {"Name": "John"}}, {"fields": {"Name": "Jane"}}]}
        """
        if api_version == APIVersion.V2:
            return records

        # v3: wrap in records array with fields
        return {"records": [RequestAdapter.format_record(r, api_version) for r in records]}

    @staticmethod
    def format_delete(record_id: int | str, api_version: "APIVersion") -> dict[str, Any]:
        """Format a delete request body.

        v2: {"Id": 123}
        v3: {"id": 123}
        """
        if api_version == APIVersion.V2:
            return {"Id": record_id}
        return {"id": record_id}

    @staticmethod
    def format_bulk_delete(
        record_ids: list[int | str], api_version: "APIVersion"
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Format bulk delete request body.

        v2: [{"Id": 1}, {"Id": 2}]
        v3: {"records": [{"id": 1}, {"id": 2}]}
        """
        if api_version == APIVersion.V2:
            return [{"Id": rid} for rid in record_ids]
        return {"records": [{"id": rid} for rid in record_ids]}


class QueryParamAdapter:
    """Adapter for converting query parameters between API versions."""

    @staticmethod
    def convert_pagination_to_v3(params: dict[str, Any]) -> dict[str, Any]:
        """Convert v2 offset/limit pagination to v3 page/pageSize.

        Args:
            params: Query parameters dict (may be modified in place)

        Returns:
            Modified parameters dict with v3 pagination

        Example:
            >>> params = {"offset": 50, "limit": 25}
            >>> QueryParamAdapter.convert_pagination_to_v3(params)
            {'page': 3, 'pageSize': 25}
        """
        result = params.copy()

        # Convert offset/limit to page/pageSize
        if "offset" in result or "limit" in result:
            offset = result.pop("offset", 0)
            limit = result.pop("limit", 25)

            # Calculate page number (1-indexed)
            page = (offset // limit) + 1 if limit > 0 else 1
            result["page"] = page
            result["pageSize"] = limit

        return result

    @staticmethod
    def convert_pagination_to_v2(params: dict[str, Any]) -> dict[str, Any]:
        """Convert v3 page/pageSize pagination to v2 offset/limit.

        Args:
            params: Query parameters dict (may be modified in place)

        Returns:
            Modified parameters dict with v2 pagination

        Example:
            >>> params = {"page": 3, "pageSize": 25}
            >>> QueryParamAdapter.convert_pagination_to_v2(params)
            {'offset': 50, 'limit': 25}
        """
        result = params.copy()

        # Convert page/pageSize to offset/limit
        if "page" in result or "pageSize" in result:
            page = result.pop("page", 1)
            page_size = result.pop("pageSize", 25)

            # Calculate offset (0-indexed)
            offset = (page - 1) * page_size if page > 0 else 0
            result["offset"] = offset
            result["limit"] = page_size

        return result

    @staticmethod
    def convert_sort_to_v3(sort_str: str | None) -> list[dict[str, str]] | None:
        """Convert v2 sort string to v3 JSON array format.

        Args:
            sort_str: v2 sort string (e.g., "field1,-field2")

        Returns:
            v3 sort array or None

        Example:
            >>> QueryParamAdapter.convert_sort_to_v3("name,-age")
            [{'field': 'name', 'direction': 'asc'}, {'field': 'age', 'direction': 'desc'}]
        """
        if not sort_str:
            return None

        sorts = []
        for field in sort_str.split(","):
            field = field.strip()
            if field.startswith("-"):
                sorts.append({"field": field[1:], "direction": "desc"})
            else:
                sorts.append({"field": field, "direction": "asc"})

        return sorts if sorts else None

    @staticmethod
    def convert_sort_to_v2(sort_list: list[dict[str, str]] | None) -> str | None:
        """Convert v3 sort JSON array to v2 string format.

        Args:
            sort_list: v3 sort array

        Returns:
            v2 sort string or None

        Example:
            >>> sort = [{'field': 'name', 'direction': 'asc'}, {'field': 'age', 'direction': 'desc'}]
            >>> QueryParamAdapter.convert_sort_to_v2(sort)
            'name,-age'
        """
        if not sort_list:
            return None

        fields = []
        for sort_item in sort_list:
            field = sort_item["field"]
            direction = sort_item.get("direction", "asc")
            if direction == "desc":
                fields.append(f"-{field}")
            else:
                fields.append(field)

        return ",".join(fields) if fields else None

    @staticmethod
    def convert_where_operators_to_v3(where: dict[str, Any] | None) -> dict[str, Any] | None:
        """Convert v2 where operators to v3 format.

        Changes 'ne' to 'neq' operator.

        Args:
            where: Where clause dict

        Returns:
            Modified where clause for v3
        """
        if not where:
            return where

        # Deep copy to avoid modifying original
        import json

        result: dict[str, Any] = json.loads(json.dumps(where))

        def replace_ne(obj: Any) -> None:
            if isinstance(obj, dict):
                # Replace 'ne' with 'neq'
                if "ne" in obj:
                    obj["neq"] = obj.pop("ne")
                # Recursively process nested dicts
                for value in obj.values():
                    replace_ne(value)
            elif isinstance(obj, list):
                for item in obj:
                    replace_ne(item)

        replace_ne(result)
        return result

    @staticmethod
    def convert_where_operators_to_v2(where: dict[str, Any] | None) -> dict[str, Any] | None:
        """Convert v3 where operators to v2 format.

        Changes 'neq' to 'ne' operator.

        Args:
            where: Where clause dict

        Returns:
            Modified where clause for v2
        """
        if not where:
            return where

        # Deep copy to avoid modifying original
        import json

        result: dict[str, Any] = json.loads(json.dumps(where))

        def replace_neq(obj: Any) -> None:
            if isinstance(obj, dict):
                # Replace 'neq' with 'ne'
                if "neq" in obj:
                    obj["ne"] = obj.pop("neq")
                # Recursively process nested dicts
                for value in obj.values():
                    replace_neq(value)
            elif isinstance(obj, list):
                for item in obj:
                    replace_neq(item)

        replace_neq(result)
        return result


class PathBuilder:
    """Builder for constructing API endpoint paths for different versions."""

    def __init__(self, api_version: APIVersion):
        """Initialize path builder.

        Args:
            api_version: The API version to use
        """
        self.api_version = api_version

    def records_list(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for listing records.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/tables/{table_id}/records"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/data/{base_id}/{table_id}/records"

    def records_get(self, table_id: str, record_id: str, base_id: str | None = None) -> str:
        """Build path for getting a single record.

        Args:
            table_id: Table ID
            record_id: Record ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/tables/{table_id}/records/{record_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/data/{base_id}/{table_id}/records/{record_id}"

    def records_create(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for creating records.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.records_list(table_id, base_id)

    def records_update(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for updating records.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.records_list(table_id, base_id)

    def records_delete(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for deleting records.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.records_list(table_id, base_id)

    def records_count(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for counting records.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/tables/{table_id}/records/count"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/data/{base_id}/{table_id}/count"

    def table_get(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for getting table metadata.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/tables/{table_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/tables/{table_id}"

    def tables_list(self, base_id: str) -> str:
        """Build path for listing tables.

        Args:
            base_id: Base ID

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/bases/{base_id}/tables"
        else:  # V3
            return f"api/v3/meta/bases/{base_id}/tables"

    def table_create(self, base_id: str) -> str:
        """Build path for creating a table.

        Args:
            base_id: Base ID

        Returns:
            API endpoint path
        """
        return self.tables_list(base_id)

    def table_update(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for updating a table.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.table_get(table_id, base_id)

    def table_delete(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for deleting a table.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.table_get(table_id, base_id)

    def links_list(
        self,
        table_id: str,
        link_field_id: str,
        record_id: str,
        base_id: str | None = None,
    ) -> str:
        """Build path for listing linked records.

        Args:
            table_id: Table ID
            link_field_id: Link field ID
            record_id: Record ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/tables/{table_id}/links/{link_field_id}/records/{record_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/data/{base_id}/{table_id}/links/{link_field_id}/{record_id}"

    def links_create(
        self,
        table_id: str,
        link_field_id: str,
        record_id: str,
        base_id: str | None = None,
    ) -> str:
        """Build path for creating links.

        Args:
            table_id: Table ID
            link_field_id: Link field ID
            record_id: Record ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.links_list(table_id, link_field_id, record_id, base_id)

    def links_delete(
        self,
        table_id: str,
        link_field_id: str,
        record_id: str,
        base_id: str | None = None,
    ) -> str:
        """Build path for deleting links.

        Args:
            table_id: Table ID
            link_field_id: Link field ID
            record_id: Record ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        return self.links_list(table_id, link_field_id, record_id, base_id)

    def file_upload(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for file upload.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return "api/v2/storage/upload"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/data/{base_id}/{table_id}/attachments"

    # ========================================================================
    # META API PATHS
    # ========================================================================

    def bases_list(self) -> str:
        """Build path for listing bases.

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return "api/v2/meta/bases"
        else:  # V3
            return "api/v3/meta/bases"

    def base_get(self, base_id: str) -> str:
        """Build path for getting base information.

        Args:
            base_id: Base ID

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/bases/{base_id}"
        else:  # V3
            return f"api/v3/meta/bases/{base_id}"

    def tables_list_meta(self, base_id: str) -> str:
        """Build path for listing tables (meta endpoint).

        Args:
            base_id: Base ID

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/bases/{base_id}/tables"
        else:  # V3
            return f"api/v3/meta/bases/{base_id}/tables"

    def table_get_meta(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for getting table metadata.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/tables/{table_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/tables/{table_id}"

    def column_get(self, column_id: str, base_id: str | None = None) -> str:
        """Build path for column/field operations.

        Args:
            column_id: Column/Field ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/columns/{column_id}"
        else:  # V3 - columns become fields
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/fields/{column_id}"

    def columns_create(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for creating columns/fields.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/tables/{table_id}/columns"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/tables/{table_id}/fields"

    def view_get(self, view_id: str, base_id: str | None = None) -> str:
        """Build path for view operations.

        Args:
            view_id: View ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/views/{view_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/views/{view_id}"

    def views_list(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for listing views.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/tables/{table_id}/views"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/tables/{table_id}/views"

    def webhook_get(self, webhook_id: str, base_id: str | None = None) -> str:
        """Build path for webhook operations.

        Args:
            webhook_id: Webhook ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/hooks/{webhook_id}"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/hooks/{webhook_id}"

    def webhooks_list(self, table_id: str, base_id: str | None = None) -> str:
        """Build path for listing webhooks.

        Args:
            table_id: Table ID
            base_id: Base ID (required for v3)

        Returns:
            API endpoint path
        """
        if self.api_version == APIVersion.V2:
            return f"api/v2/meta/tables/{table_id}/hooks"
        else:  # V3
            if not base_id:
                raise ValueError("base_id is required for API v3")
            return f"api/v3/meta/bases/{base_id}/tables/{table_id}/hooks"
