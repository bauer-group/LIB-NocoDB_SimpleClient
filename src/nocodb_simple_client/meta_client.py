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

from typing import Any

from .client import NocoDBClient
from .config import NocoDBConfig


class NocoDBMetaClient(NocoDBClient):
    """Meta API client for NocoDB structure and configuration operations.

    This client extends NocoDBClient to provide Meta API operations for managing
    database structure like tables, views, columns, webhooks, and other metadata
    operations following the official NocoDB Meta API specification in
    docs/nocodb-openapi-meta.json.

    Inherits all HTTP functionality from NocoDBClient while providing specialized
    Meta API methods. This eliminates code duplication and ensures consistent
    HTTP handling, authentication, and error management.

    The Meta API handles:
    - Table structure operations (create, update, delete tables)
    - Column management (add, modify, delete columns)
    - View operations (create, configure views)
    - Webhook automation (setup, test webhooks)
    - Database schema operations

    Args:
        config: NocoDBConfig instance with connection settings, or None to create from kwargs
        **kwargs: Alternative way to pass config parameters (base_url, api_token, etc.)

    Example:
        >>> # Direct initialization
        >>> meta_client = NocoDBMetaClient(
        ...     base_url="https://app.nocodb.com",
        ...     api_token="your-api-token"
        ... )
        >>> tables = meta_client.list_tables(base_id="base123")
        >>>
        >>> # Or using config object
        >>> config = NocoDBConfig(base_url="...", api_token="...")
        >>> meta_client = NocoDBMetaClient(config)
        >>> columns = meta_client.list_columns(table_id="table456")
        >>>
        >>> # Can also use inherited data operations
        >>> records = meta_client.get_records("table_id")  # From NocoDBClient
        >>> new_table = meta_client.create_table("base_id", {...})  # Meta API
    """

    def __init__(self, config: NocoDBConfig | None = None, **kwargs: Any) -> None:
        """Initialize the Meta API client.

        Args:
            config: NocoDBConfig instance or None to create from kwargs
            **kwargs: Alternative way to pass config parameters
        """
        super().__init__(config=config, **kwargs)

    # ========================================================================
    # WORKSPACE OPERATIONS (Meta API)
    # ========================================================================

    def list_workspaces(self) -> list[dict[str, Any]]:
        """List all workspaces accessible to the authenticated user.

        Returns:
            List of workspace metadata dictionaries

        Raises:
            NocoDBException: For API errors

        Example:
            >>> workspaces = meta_client.list_workspaces()
            >>> for workspace in workspaces:
            ...     print(workspace['id'], workspace['title'])
        """
        response = self._get("api/v2/meta/workspaces")
        workspace_list = response.get("list", [])
        return workspace_list if isinstance(workspace_list, list) else []

    def get_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Get detailed information about a specific workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            Workspace metadata dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If workspace_id is invalid

        Example:
            >>> workspace = meta_client.get_workspace("ws_abc123")
            >>> print(workspace['title'], workspace['created_at'])
        """
        result = self._get(f"api/v2/meta/workspaces/{workspace_id}")
        return result if isinstance(result, dict) else {"data": result}

    def create_workspace(self, workspace_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new workspace.

        Args:
            workspace_data: Workspace creation data (title, description, etc.)

        Returns:
            Created workspace metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If workspace_data is invalid

        Example:
            >>> workspace_data = {
            ...     "title": "My Workspace",
            ...     "description": "Team workspace"
            ... }
            >>> workspace = meta_client.create_workspace(workspace_data)
        """
        result = self._post("api/v2/meta/workspaces", data=workspace_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_workspace(self, workspace_id: str, workspace_data: dict[str, Any]) -> dict[str, Any]:
        """Update workspace metadata.

        Args:
            workspace_id: The workspace ID to update
            workspace_data: Updated workspace data

        Returns:
            Updated workspace metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If workspace_id or workspace_data is invalid

        Example:
            >>> updated = meta_client.update_workspace(
            ...     "ws_abc123",
            ...     {"title": "Updated Workspace Name"}
            ... )
        """
        result = self._patch(f"api/v2/meta/workspaces/{workspace_id}", data=workspace_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Delete a workspace.

        Warning: This will delete all bases and data within the workspace.

        Args:
            workspace_id: The workspace ID to delete

        Returns:
            Deletion confirmation

        Raises:
            NocoDBException: For API errors
            ValidationException: If workspace_id is invalid

        Example:
            >>> result = meta_client.delete_workspace("ws_abc123")
        """
        result = self._delete(f"api/v2/meta/workspaces/{workspace_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # BASE OPERATIONS (Meta API)
    # ========================================================================

    def list_bases(self) -> list[dict[str, Any]]:
        """List all bases.

        Returns:
            List of base metadata dictionaries

        Raises:
            NocoDBException: For API errors

        Example:
            >>> bases = meta_client.list_bases()
            >>> for base in bases:
            ...     print(base['id'], base['title'])
        """
        response = self._get("api/v2/meta/bases/")
        base_list = response.get("list", [])
        return base_list if isinstance(base_list, list) else []

    def get_base(self, base_id: str) -> dict[str, Any]:
        """Get detailed information about a specific base.

        Args:
            base_id: The base ID

        Returns:
            Base metadata dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If base_id is invalid

        Example:
            >>> base = meta_client.get_base("p_abc123")
            >>> print(base['title'], base['status'])
        """
        result = self._get(f"api/v2/meta/bases/{base_id}")
        return result if isinstance(result, dict) else {"data": result}

    def create_base(self, workspace_id: str, base_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new base in a workspace.

        Args:
            workspace_id: The workspace ID where base will be created
            base_data: Base creation data (title, description, etc.)

        Returns:
            Created base metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If workspace_id or base_data is invalid

        Example:
            >>> base_data = {
            ...     "title": "My Project",
            ...     "description": "Project database"
            ... }
            >>> base = meta_client.create_base("ws_abc123", base_data)
        """
        result = self._post(f"api/v2/meta/workspaces/{workspace_id}/bases", data=base_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_base(self, base_id: str, base_data: dict[str, Any]) -> dict[str, Any]:
        """Update base metadata.

        Args:
            base_id: The base ID to update
            base_data: Updated base data

        Returns:
            Updated base metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If base_id or base_data is invalid

        Example:
            >>> updated = meta_client.update_base(
            ...     "p_abc123",
            ...     {"title": "Updated Project Name"}
            ... )
        """
        result = self._patch(f"api/v2/meta/bases/{base_id}", data=base_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_base(self, base_id: str) -> dict[str, Any]:
        """Delete a base.

        Warning: This will delete all tables and data within the base.

        Args:
            base_id: The base ID to delete

        Returns:
            Deletion confirmation

        Raises:
            NocoDBException: For API errors
            ValidationException: If base_id is invalid

        Example:
            >>> result = meta_client.delete_base("p_abc123")
        """
        result = self._delete(f"api/v2/meta/bases/{base_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # TABLE STRUCTURE OPERATIONS (Meta API)
    # ========================================================================

    def list_tables(self, base_id: str) -> list[dict[str, Any]]:
        """List all tables in a base.

        Args:
            base_id: The base ID

        Returns:
            List of table metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If base_id is invalid
        """
        response = self._get(f"api/v2/meta/bases/{base_id}/tables")
        table_list = response.get("list", [])
        return table_list if isinstance(table_list, list) else []

    def get_table_info(self, table_id: str) -> dict[str, Any]:
        """Get table metadata information.

        Args:
            table_id: The table ID

        Returns:
            Table metadata dictionary containing schema, columns, relationships

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        result = self._get(f"api/v2/meta/tables/{table_id}")
        return result if isinstance(result, dict) else {"data": result}

    def create_table(self, base_id: str, table_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new table in a base.

        Args:
            base_id: The base ID where table will be created
            table_data: Table creation data (title, columns, etc.)

        Returns:
            Created table metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If table_data is invalid

        Example:
            >>> table_data = {
            ...     "title": "Users",
            ...     "columns": [
            ...         {"title": "Name", "uidt": "SingleLineText"},
            ...         {"title": "Email", "uidt": "Email"}
            ...     ]
            ... }
            >>> table = meta_client.create_table("base123", table_data)
        """
        result = self._post(f"api/v2/meta/bases/{base_id}/tables", data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_table(self, table_id: str, table_data: dict[str, Any]) -> dict[str, Any]:
        """Update table metadata (title, description, etc.).

        Args:
            table_id: The table ID to update
            table_data: Updated table data

        Returns:
            Updated table metadata

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        result = self._patch(f"api/v2/meta/tables/{table_id}", data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_table(self, table_id: str) -> dict[str, Any]:
        """Delete a table and all its data.

        WARNING: This operation cannot be undone. All data in the table will be lost.

        Args:
            table_id: The table ID to delete

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        result = self._delete(f"api/v2/meta/tables/{table_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # COLUMN OPERATIONS (Meta API)
    # ========================================================================

    def list_columns(self, table_id: str) -> list[dict[str, Any]]:
        """List all columns in a table.

        Args:
            table_id: The table ID

        Returns:
            List of column metadata including types, constraints, relationships

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        response = self._get(f"api/v2/meta/tables/{table_id}/columns")
        column_list = response.get("list", [])
        return column_list if isinstance(column_list, list) else []

    def create_column(self, table_id: str, column_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new column in a table.

        Args:
            table_id: The table ID where column will be created
            column_data: Column definition (title, type, constraints, etc.)

        Returns:
            Created column metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If column_data is invalid

        Example:
            >>> column_data = {
            ...     "title": "Age",
            ...     "uidt": "Number",
            ...     "dtxp": "3",  # precision
            ...     "dtxs": "0"   # scale
            ... }
            >>> column = meta_client.create_column("table123", column_data)
        """
        result = self._post(f"api/v2/meta/tables/{table_id}/columns", data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_column(self, column_id: str, column_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing column's properties.

        Args:
            column_id: The column ID to update
            column_data: Updated column data (title, constraints, etc.)

        Returns:
            Updated column metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If column_data is invalid
        """
        result = self._patch(f"api/v2/meta/columns/{column_id}", data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_column(self, column_id: str) -> dict[str, Any]:
        """Delete a column from a table.

        WARNING: This will permanently delete the column and all its data.

        Args:
            column_id: The column ID to delete

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        result = self._delete(f"api/v2/meta/columns/{column_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # VIEW OPERATIONS (Meta API)
    # ========================================================================

    def list_views(self, table_id: str) -> list[dict[str, Any]]:
        """List all views for a table.

        Args:
            table_id: The table ID

        Returns:
            List of view metadata (grid, gallery, form, kanban, calendar views)

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        response = self._get(f"api/v2/meta/tables/{table_id}/views")
        view_list = response.get("list", [])
        return view_list if isinstance(view_list, list) else []

    def get_view(self, view_id: str) -> dict[str, Any]:
        """Get detailed view metadata.

        Args:
            view_id: The view ID

        Returns:
            View metadata including filters, sorts, column configuration

        Raises:
            NocoDBException: For API errors
        """
        return self._get(f"api/v2/meta/views/{view_id}")

    def create_view(self, table_id: str, view_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new view for a table.

        Args:
            table_id: The table ID where view will be created
            view_data: View configuration (title, type, filters, sorts)

        Returns:
            Created view metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If view_data is invalid

        Example:
            >>> view_data = {
            ...     "title": "Active Users",
            ...     "type": "Grid",
            ...     "show_system_fields": False
            ... }
            >>> view = meta_client.create_view("table123", view_data)
        """
        result = self._post(f"api/v2/meta/tables/{table_id}/views", data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_view(self, view_id: str, view_data: dict[str, Any]) -> dict[str, Any]:
        """Update view properties (title, filters, sorts, etc.).

        Args:
            view_id: The view ID to update
            view_data: Updated view configuration

        Returns:
            Updated view metadata

        Raises:
            NocoDBException: For API errors
        """
        result = self._patch(f"api/v2/meta/views/{view_id}", data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_view(self, view_id: str) -> dict[str, Any]:
        """Delete a view.

        Args:
            view_id: The view ID to delete

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        result = self._delete(f"api/v2/meta/views/{view_id}")
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # WEBHOOK OPERATIONS (Meta API)
    # ========================================================================

    def list_webhooks(self, table_id: str) -> list[dict[str, Any]]:
        """List all webhooks configured for a table.

        Args:
            table_id: The table ID

        Returns:
            List of webhook configurations

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        response = self._get(f"api/v2/meta/tables/{table_id}/hooks")
        webhook_list = response.get("list", [])
        return webhook_list if isinstance(webhook_list, list) else []

    def get_webhook(self, hook_id: str) -> dict[str, Any]:
        """Get webhook configuration details.

        Args:
            hook_id: The webhook ID

        Returns:
            Webhook configuration including URL, events, conditions

        Raises:
            NocoDBException: For API errors
        """
        return self._get(f"api/v2/meta/hooks/{hook_id}")

    def create_webhook(self, table_id: str, webhook_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new webhook for table events.

        Args:
            table_id: The table ID where webhook will be created
            webhook_data: Webhook configuration (URL, events, conditions)

        Returns:
            Created webhook configuration

        Raises:
            NocoDBException: For API errors
            ValidationException: If webhook_data is invalid

        Example:
            >>> webhook_data = {
            ...     "title": "Slack Notification",
            ...     "event": "after",
            ...     "operation": "insert",
            ...     "notification": {
            ...         "type": "URL",
            ...         "payload": {
            ...             "method": "POST",
            ...             "url": "https://hooks.slack.com/...",
            ...             "body": "New record: {{title}}"
            ...         }
            ...     },
            ...     "active": True
            ... }
            >>> webhook = meta_client.create_webhook("table123", webhook_data)
        """
        result = self._post(f"api/v2/meta/tables/{table_id}/hooks", data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_webhook(self, hook_id: str, webhook_data: dict[str, Any]) -> dict[str, Any]:
        """Update webhook configuration.

        Args:
            hook_id: The webhook ID to update
            webhook_data: Updated webhook configuration

        Returns:
            Updated webhook configuration

        Raises:
            NocoDBException: For API errors
        """
        result = self._patch(f"api/v2/meta/hooks/{hook_id}", data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_webhook(self, hook_id: str) -> dict[str, Any]:
        """Delete a webhook.

        Args:
            hook_id: The webhook ID to delete

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        result = self._delete(f"api/v2/meta/hooks/{hook_id}")
        return result if isinstance(result, dict) else {"data": result}

    def test_webhook(self, hook_id: str) -> dict[str, Any]:
        """Test a webhook by triggering it manually.

        Args:
            hook_id: The webhook ID to test

        Returns:
            Test execution results including HTTP response details

        Raises:
            NocoDBException: For API errors
        """
        result = self._post(f"api/v2/meta/hooks/{hook_id}/test", data={})
        return result if isinstance(result, dict) else {"data": result}
