"""NocoDB Meta API client for structure and configuration operations.

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


class NocoDBMetaClient:
    """Meta API client for NocoDB structure and configuration operations.

    This client handles operations on database structure like tables, views,
    columns, webhooks, and other metadata operations following the official
    NocoDB Meta API specification in docs/nocodb-openapi-meta.json.

    Separate from NocoDBClient which handles data operations (CRUD on records).
    This client reuses the NocoDBClient for HTTP operations to avoid code duplication.

    Args:
        client: NocoDBClient instance to use for HTTP operations

    Example:
        >>> client = NocoDBClient(
        ...     base_url="https://app.nocodb.com",
        ...     api_token="your-api-token"
        ... )
        >>> meta_client = NocoDBMetaClient(client)
        >>> tables = meta_client.list_tables(base_id="base123")
    """

    def __init__(self, client: "NocoDBClient") -> None:
        """Initialize the Meta API client.

        Args:
            client: NocoDBClient instance to use for HTTP operations
        """
        self.client = client

    # ========================================================================
    # TABLE STRUCTURE OPERATIONS (Meta API)
    # ========================================================================

    def list_tables(self, base_id: str) -> list[dict[str, Any]]:
        """List all tables in a base.

        Args:
            base_id: The base ID

        Returns:
            List of table metadata
        """
        response = self.client._get(f"api/v2/meta/bases/{base_id}/tables")
        table_list = response.get("list", [])
        return table_list if isinstance(table_list, list) else []

    def get_table_info(self, table_id: str) -> dict[str, Any]:
        """Get table metadata information.

        Args:
            table_id: The table ID

        Returns:
            Table metadata
        """
        result = self.client._get(f"api/v2/meta/tables/{table_id}")
        return result if isinstance(result, dict) else {"data": result}

    def create_table(self, base_id: str, table_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new table.

        Args:
            base_id: The base ID
            table_data: Table creation data

        Returns:
            Created table metadata
        """
        result = self.client._post(f"api/v2/meta/bases/{base_id}/tables", data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_table(self, table_id: str, table_data: dict[str, Any]) -> dict[str, Any]:
        """Update table metadata.

        Args:
            table_id: The table ID
            table_data: Updated table data

        Returns:
            Updated table metadata
        """
        result = self.client._patch(f"api/v2/meta/tables/{table_id}", data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_table(self, table_id: str) -> dict[str, Any]:
        """Delete a table.

        Args:
            table_id: The table ID

        Returns:
            Deletion response
        """
        result = self.client._delete(f"api/v2/meta/tables/{table_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # COLUMN OPERATIONS (Meta API)
    # ========================================================================

    def list_columns(self, table_id: str) -> list[dict[str, Any]]:
        """List all columns in a table.

        Args:
            table_id: The table ID

        Returns:
            List of column metadata
        """
        response = self.client._get(f"api/v2/meta/tables/{table_id}/columns")
        column_list = response.get("list", [])
        return column_list if isinstance(column_list, list) else []

    def create_column(self, table_id: str, column_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new column.

        Args:
            table_id: The table ID
            column_data: Column creation data

        Returns:
            Created column metadata
        """
        result = self.client._post(f"api/v2/meta/tables/{table_id}/columns", data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_column(self, column_id: str, column_data: dict[str, Any]) -> dict[str, Any]:
        """Update a column.

        Args:
            column_id: The column ID
            column_data: Updated column data

        Returns:
            Updated column metadata
        """
        result = self.client._patch(f"api/v2/meta/columns/{column_id}", data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_column(self, column_id: str) -> dict[str, Any]:
        """Delete a column.

        Args:
            column_id: The column ID

        Returns:
            Deletion response
        """
        result = self.client._delete(f"api/v2/meta/columns/{column_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # VIEW OPERATIONS (Meta API)
    # ========================================================================

    def list_views(self, table_id: str) -> list[dict[str, Any]]:
        """List all views for a table.

        Args:
            table_id: The table ID

        Returns:
            List of view metadata
        """
        response = self.client._get(f"api/v2/meta/tables/{table_id}/views")
        view_list = response.get("list", [])
        return view_list if isinstance(view_list, list) else []

    def get_view(self, view_id: str) -> dict[str, Any]:
        """Get view metadata.

        Args:
            view_id: The view ID

        Returns:
            View metadata
        """
        return self.client._get(f"api/v2/meta/views/{view_id}")

    def create_view(self, table_id: str, view_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new view.

        Args:
            table_id: The table ID
            view_data: View creation data

        Returns:
            Created view metadata
        """
        result = self.client._post(f"api/v2/meta/tables/{table_id}/views", data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_view(self, view_id: str, view_data: dict[str, Any]) -> dict[str, Any]:
        """Update a view.

        Args:
            view_id: The view ID
            view_data: Updated view data

        Returns:
            Updated view metadata
        """
        result = self.client._patch(f"api/v2/meta/views/{view_id}", data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_view(self, view_id: str) -> dict[str, Any]:
        """Delete a view.

        Args:
            view_id: The view ID

        Returns:
            Deletion response
        """
        result = self.client._delete(f"api/v2/meta/views/{view_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # WEBHOOK OPERATIONS (Meta API)
    # ========================================================================

    def list_webhooks(self, table_id: str) -> list[dict[str, Any]]:
        """List all webhooks for a table.

        Args:
            table_id: The table ID

        Returns:
            List of webhook metadata
        """
        response = self.client._get(f"api/v2/meta/tables/{table_id}/hooks")
        webhook_list = response.get("list", [])
        return webhook_list if isinstance(webhook_list, list) else []

    def get_webhook(self, hook_id: str) -> dict[str, Any]:
        """Get webhook metadata.

        Args:
            hook_id: The webhook ID

        Returns:
            Webhook metadata
        """
        return self.client._get(f"api/v2/meta/hooks/{hook_id}")

    def create_webhook(self, table_id: str, webhook_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new webhook.

        Args:
            table_id: The table ID
            webhook_data: Webhook creation data

        Returns:
            Created webhook metadata
        """
        result = self.client._post(f"api/v2/meta/tables/{table_id}/hooks", data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_webhook(self, hook_id: str, webhook_data: dict[str, Any]) -> dict[str, Any]:
        """Update a webhook.

        Args:
            hook_id: The webhook ID
            webhook_data: Updated webhook data

        Returns:
            Updated webhook metadata
        """
        result = self.client._patch(f"api/v2/meta/hooks/{hook_id}", data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_webhook(self, hook_id: str) -> dict[str, Any]:
        """Delete a webhook.

        Args:
            hook_id: The webhook ID

        Returns:
            Deletion response
        """
        result = self.client._delete(f"api/v2/meta/hooks/{hook_id}")
        return result if isinstance(result, dict) else {"data": result}

    def test_webhook(self, hook_id: str) -> dict[str, Any]:
        """Test a webhook.

        Args:
            hook_id: The webhook ID

        Returns:
            Test response
        """
        result = self.client._post(f"api/v2/meta/hooks/{hook_id}/test", data={})
        return result if isinstance(result, dict) else {"data": result}
