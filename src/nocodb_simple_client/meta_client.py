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

        Supports both API v2 and v3.

        Returns:
            List of workspace metadata dictionaries

        Raises:
            NocoDBException: For API errors

        Example:
            >>> workspaces = meta_client.list_workspaces()
            >>> for workspace in workspaces:
            ...     print(workspace['id'], workspace['title'])
        """
        # Workspace endpoints are same for v2 and v3
        endpoint = f"api/{self.api_version}/meta/workspaces"
        response = self._get(endpoint)
        workspace_list = response.get("list", [])
        return workspace_list if isinstance(workspace_list, list) else []

    def get_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Get detailed information about a specific workspace.

        Supports both API v2 and v3.

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
        endpoint = f"api/{self.api_version}/meta/workspaces/{workspace_id}"
        result = self._get(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    def create_workspace(self, workspace_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new workspace.

        Supports both API v2 and v3.

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
        endpoint = f"api/{self.api_version}/meta/workspaces"
        result = self._post(endpoint, data=workspace_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_workspace(self, workspace_id: str, workspace_data: dict[str, Any]) -> dict[str, Any]:
        """Update workspace metadata.

        Supports both API v2 and v3.

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
        endpoint = f"api/{self.api_version}/meta/workspaces/{workspace_id}"
        result = self._patch(endpoint, data=workspace_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Delete a workspace.

        Warning: This will delete all bases and data within the workspace.

        Supports both API v2 and v3.

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
        endpoint = f"api/{self.api_version}/meta/workspaces/{workspace_id}"
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # BASE OPERATIONS (Meta API)
    # ========================================================================

    def list_bases(self) -> list[dict[str, Any]]:
        """List all bases.

        Supports both API v2 and v3.

        Returns:
            List of base metadata dictionaries

        Raises:
            NocoDBException: For API errors

        Example:
            >>> bases = meta_client.list_bases()
            >>> for base in bases:
            ...     print(base['id'], base['title'])
        """
        endpoint = self._path_builder.bases_list()
        response = self._get(endpoint)
        base_list = response.get("list", [])
        return base_list if isinstance(base_list, list) else []

    def get_base(self, base_id: str) -> dict[str, Any]:
        """Get detailed information about a specific base.

        Supports both API v2 and v3.

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
        endpoint = self._path_builder.base_get(base_id)
        result = self._get(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    def create_base(self, workspace_id: str, base_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new base in a workspace.

        Supports both API v2 and v3.

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
        endpoint = f"api/{self.api_version}/meta/workspaces/{workspace_id}/bases"
        result = self._post(endpoint, data=base_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_base(self, base_id: str, base_data: dict[str, Any]) -> dict[str, Any]:
        """Update base metadata.

        Supports both API v2 and v3.

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
        endpoint = self._path_builder.base_get(base_id)
        result = self._patch(endpoint, data=base_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_base(self, base_id: str) -> dict[str, Any]:
        """Delete a base.

        Warning: This will delete all tables and data within the base.

        Supports both API v2 and v3.

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
        endpoint = self._path_builder.base_get(base_id)
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # TABLE STRUCTURE OPERATIONS (Meta API)
    # ========================================================================

    def list_tables(self, base_id: str) -> list[dict[str, Any]]:
        """List all tables in a base.

        Supports both API v2 and v3.

        Args:
            base_id: The base ID

        Returns:
            List of table metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If base_id is invalid
        """
        endpoint = self._path_builder.tables_list_meta(base_id)
        response = self._get(endpoint)
        table_list = response.get("list", [])
        return table_list if isinstance(table_list, list) else []

    def get_table_info(self, table_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Get table metadata information.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Table metadata dictionary containing schema, columns, relationships

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.table_get_meta(table_id, resolved_base_id)
        result = self._get(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    def create_table(self, base_id: str, table_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new table in a base.

        Supports both API v2 and v3.

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
        endpoint = self._path_builder.tables_list_meta(base_id)
        result = self._post(endpoint, data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_table(
        self, table_id: str, table_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Update table metadata (title, description, etc.).

        Supports both API v2 and v3.

        Args:
            table_id: The table ID to update
            table_data: Updated table data
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Updated table metadata

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.table_get_meta(table_id, resolved_base_id)
        result = self._patch(endpoint, data=table_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_table(self, table_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Delete a table and all its data.

        WARNING: This operation cannot be undone. All data in the table will be lost.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.table_get_meta(table_id, resolved_base_id)
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # COLUMN OPERATIONS (Meta API)
    # ========================================================================

    def list_columns(self, table_id: str, base_id: str | None = None) -> list[dict[str, Any]]:
        """List all columns in a table.

        Supports both API v2 and v3. Note: In v3, columns are called 'fields'.

        Args:
            table_id: The table ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of column metadata including types, constraints, relationships

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.columns_create(table_id, resolved_base_id)
        response = self._get(endpoint)
        column_list = response.get("list", [])
        return column_list if isinstance(column_list, list) else []

    def create_column(
        self, table_id: str, column_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Create a new column in a table.

        Supports both API v2 and v3. Note: In v3, columns are called 'fields'.

        Args:
            table_id: The table ID where column will be created
            column_data: Column definition (title, type, constraints, etc.)
            base_id: Base ID (required for v3, optional for v2)

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
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.columns_create(table_id, resolved_base_id)
        result = self._post(endpoint, data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_column(
        self, column_id: str, column_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Update an existing column's properties.

        Supports both API v2 and v3. Note: In v3, columns are called 'fields'.

        Args:
            column_id: The column ID to update
            column_data: Updated column data (title, constraints, etc.)
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Updated column metadata

        Raises:
            NocoDBException: For API errors
            ValidationException: If column_data is invalid
        """
        # Resolve base_id for v3 (column_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 column operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.column_get(column_id, resolved_base_id)
        result = self._patch(endpoint, data=column_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_column(self, column_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Delete a column from a table.

        WARNING: This will permanently delete the column and all its data.

        Supports both API v2 and v3. Note: In v3, columns are called 'fields'.

        Args:
            column_id: The column ID to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (column_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 column operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.column_get(column_id, resolved_base_id)
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # VIEW OPERATIONS (Meta API)
    # ========================================================================

    def list_views(self, table_id: str, base_id: str | None = None) -> list[dict[str, Any]]:
        """List all views for a table.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of view metadata (grid, gallery, form, kanban, calendar views)

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.views_list(table_id, resolved_base_id)
        response = self._get(endpoint)
        view_list = response.get("list", [])
        return view_list if isinstance(view_list, list) else []

    def get_view(self, view_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Get detailed view metadata.

        Supports both API v2 and v3.

        Args:
            view_id: The view ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            View metadata including filters, sorts, column configuration

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (view_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 view operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.view_get(view_id, resolved_base_id)
        return self._get(endpoint)

    def create_view(
        self, table_id: str, view_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Create a new view for a table.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID where view will be created
            view_data: View configuration (title, type, filters, sorts)
            base_id: Base ID (required for v3, optional for v2)

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
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.views_list(table_id, resolved_base_id)
        result = self._post(endpoint, data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_view(
        self, view_id: str, view_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Update view properties (title, filters, sorts, etc.).

        Supports both API v2 and v3.

        Args:
            view_id: The view ID to update
            view_data: Updated view configuration
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Updated view metadata

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (view_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 view operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.view_get(view_id, resolved_base_id)
        result = self._patch(endpoint, data=view_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_view(self, view_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Delete a view.

        Supports both API v2 and v3.

        Args:
            view_id: The view ID to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (view_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 view operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.view_get(view_id, resolved_base_id)
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    # ========================================================================
    # WEBHOOK OPERATIONS (Meta API)
    # ========================================================================

    def list_webhooks(self, table_id: str, base_id: str | None = None) -> list[dict[str, Any]]:
        """List all webhooks configured for a table.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            List of webhook configurations

        Raises:
            NocoDBException: For API errors
            TableNotFoundException: If table is not found
        """
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.webhooks_list(table_id, resolved_base_id)
        response = self._get(endpoint)
        webhook_list = response.get("list", [])
        return webhook_list if isinstance(webhook_list, list) else []

    def get_webhook(self, hook_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Get webhook configuration details.

        Supports both API v2 and v3.

        Args:
            hook_id: The webhook ID
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Webhook configuration including URL, events, conditions

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (hook_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 webhook operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.webhook_get(hook_id, resolved_base_id)
        return self._get(endpoint)

    def create_webhook(
        self, table_id: str, webhook_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Create a new webhook for table events.

        Supports both API v2 and v3.

        Args:
            table_id: The table ID where webhook will be created
            webhook_data: Webhook configuration (URL, events, conditions)
            base_id: Base ID (required for v3, optional for v2)

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
        # Resolve base_id for v3
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            resolved_base_id = self._resolve_base_id(table_id, base_id)

        endpoint = self._path_builder.webhooks_list(table_id, resolved_base_id)
        result = self._post(endpoint, data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def update_webhook(
        self, hook_id: str, webhook_data: dict[str, Any], base_id: str | None = None
    ) -> dict[str, Any]:
        """Update webhook configuration.

        Supports both API v2 and v3.

        Args:
            hook_id: The webhook ID to update
            webhook_data: Updated webhook configuration
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Updated webhook configuration

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (hook_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 webhook operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.webhook_get(hook_id, resolved_base_id)
        result = self._patch(endpoint, data=webhook_data)
        return result if isinstance(result, dict) else {"data": result}

    def delete_webhook(self, hook_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Delete a webhook.

        Supports both API v2 and v3.

        Args:
            hook_id: The webhook ID to delete
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Deletion confirmation response

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (hook_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 webhook operations")
            resolved_base_id = base_id or self.base_id

        endpoint = self._path_builder.webhook_get(hook_id, resolved_base_id)
        result = self._delete(endpoint)
        return result if isinstance(result, dict) else {"data": result}

    def test_webhook(self, hook_id: str, base_id: str | None = None) -> dict[str, Any]:
        """Test a webhook by triggering it manually.

        Supports both API v2 and v3.

        Args:
            hook_id: The webhook ID to test
            base_id: Base ID (required for v3, optional for v2)

        Returns:
            Test execution results including HTTP response details

        Raises:
            NocoDBException: For API errors
        """
        # Resolve base_id for v3 (hook_id doesn't directly resolve, so base_id must be provided)
        from .api_version import APIVersion

        resolved_base_id = None
        if self.api_version == APIVersion.V3:
            if not base_id and not self.base_id:
                raise ValueError("base_id is required for API v3 webhook operations")
            resolved_base_id = base_id or self.base_id

        # Build endpoint for webhook test
        endpoint = self._path_builder.webhook_get(hook_id, resolved_base_id) + "/test"
        result = self._post(endpoint, data={})
        return result if isinstance(result, dict) else {"data": result}
