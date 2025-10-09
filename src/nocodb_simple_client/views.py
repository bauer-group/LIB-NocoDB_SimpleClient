"""View management system for NocoDB tables.

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
    from .meta_client import NocoDBMetaClient


class NocoDBViews:
    """Manager for NocoDB table views.

    Provides methods to manage different view types including Grid, Gallery,
    Form, Kanban, and Calendar views.
    """

    VIEW_TYPES = {
        "grid": "Grid",
        "gallery": "Gallery",
        "form": "Form",
        "kanban": "Kanban",
        "calendar": "Calendar",
    }

    def __init__(self, meta_client: "NocoDBMetaClient") -> None:
        """Initialize the views manager.

        Args:
            meta_client: NocoDBMetaClient instance (inherits from NocoDBClient)
        """
        self.meta_client = meta_client

    def get_views(self, table_id: str) -> list[dict[str, Any]]:
        """Get all views for a table.

        Args:
            table_id: ID of the table

        Returns:
            List of view dictionaries

        Raises:
            NocoDBException: For API errors
        """
        return self.meta_client.list_views(table_id)

    def get_view(self, table_id: str, view_id: str) -> dict[str, Any]:
        """Get a specific view by ID.

        Args:
            table_id: ID of the table
            view_id: ID of the view

        Returns:
            View dictionary

        Raises:
            NocoDBException: For API errors
            ViewNotFoundException: If the view is not found
        """
        return self.meta_client.get_view(view_id)

    def create_view(
        self, table_id: str, title: str, view_type: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a new view.

        Args:
            table_id: ID of the table
            title: Title of the view
            view_type: Type of view (grid, gallery, form, kanban, calendar)
            options: Additional view options

        Returns:
            Created view dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If view_type is invalid
        """
        if view_type.lower() not in self.VIEW_TYPES:
            raise ValueError(
                f"Invalid view type: {view_type}. "
                f"Supported types: {list(self.VIEW_TYPES.keys())}"
            )

        data = {"title": title, "type": self.VIEW_TYPES[view_type.lower()], "table_id": table_id}

        if options:
            data.update(options)

        response = self.meta_client.create_view(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from view creation")

    def update_view(
        self,
        table_id: str,
        view_id: str,
        title: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing view.

        Args:
            table_id: ID of the table
            view_id: ID of the view to update
            title: New title for the view
            options: Updated view options

        Returns:
            Updated view dictionary

        Raises:
            NocoDBException: For API errors
            ViewNotFoundException: If the view is not found
        """
        data = {}

        if title:
            data["title"] = title

        if options:
            data.update(options)

        if not data:
            raise ValueError("At least title or options must be provided")

        response = self.meta_client.update_view(view_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from view update")

    def delete_view(self, table_id: str, view_id: str) -> bool:
        """Delete a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view to delete

        Returns:
            True if deletion was successful

        Raises:
            NocoDBException: For API errors
            ViewNotFoundException: If the view is not found
        """
        response = self.meta_client.delete_view(view_id)
        return response is not None

    def get_view_columns(self, table_id: str, view_id: str) -> list[dict[str, Any]]:
        """Get columns configuration for a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view

        Returns:
            List of column configuration dictionaries

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/columns"
        response = self.meta_client._get(endpoint)
        columns_list = response.get("list", [])
        return columns_list if isinstance(columns_list, list) else []

    def update_view_column(
        self, table_id: str, view_id: str, column_id: str, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Update column configuration in a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            column_id: ID of the column
            options: Column configuration options (show, order, width, etc.)

        Returns:
            Updated column configuration

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/columns/{column_id}"
        response = self.meta_client._patch(endpoint, data=options)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from view column update")

    def get_view_filters(self, table_id: str, view_id: str) -> list[dict[str, Any]]:
        """Get filters for a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view

        Returns:
            List of filter dictionaries

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/filters"
        response = self.meta_client._get(endpoint)
        filters_list = response.get("list", [])
        return filters_list if isinstance(filters_list, list) else []

    def create_view_filter(
        self,
        table_id: str,
        view_id: str,
        column_id: str,
        comparison_op: str,
        value: Any = None,
        logical_op: str = "and",
    ) -> dict[str, Any]:
        """Create a filter for a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            column_id: ID of the column to filter
            comparison_op: Comparison operator (eq, gt, like, etc.)
            value: Filter value
            logical_op: Logical operator (and, or)

        Returns:
            Created filter dictionary

        Raises:
            NocoDBException: For API errors
        """
        data = {"fk_column_id": column_id, "comparison_op": comparison_op, "logical_op": logical_op}

        if value is not None:
            data["value"] = value

        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/filters"
        response = self.meta_client._post(endpoint, data=data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from filter creation")

    def update_view_filter(
        self,
        table_id: str,
        view_id: str,
        filter_id: str,
        comparison_op: str | None = None,
        value: Any = None,
        logical_op: str | None = None,
    ) -> dict[str, Any]:
        """Update a view filter.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            filter_id: ID of the filter to update
            comparison_op: New comparison operator
            value: New filter value
            logical_op: New logical operator

        Returns:
            Updated filter dictionary

        Raises:
            NocoDBException: For API errors
        """
        data = {}

        if comparison_op:
            data["comparison_op"] = comparison_op
        if value is not None:
            data["value"] = value
        if logical_op:
            data["logical_op"] = logical_op

        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/filters/{filter_id}"
        response = self.meta_client._patch(endpoint, data=data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from filter update")

    def delete_view_filter(self, table_id: str, view_id: str, filter_id: str) -> bool:
        """Delete a view filter.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            filter_id: ID of the filter to delete

        Returns:
            True if deletion was successful

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/filters/{filter_id}"
        response = self.meta_client._delete(endpoint)
        return response is not None

    def get_view_sorts(self, table_id: str, view_id: str) -> list[dict[str, Any]]:
        """Get sort configuration for a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view

        Returns:
            List of sort dictionaries

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/sorts"
        response = self.meta_client._get(endpoint)
        sorts_list = response.get("list", [])
        return sorts_list if isinstance(sorts_list, list) else []

    def create_view_sort(
        self, table_id: str, view_id: str, column_id: str, direction: str = "asc"
    ) -> dict[str, Any]:
        """Create a sort for a view.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            column_id: ID of the column to sort by
            direction: Sort direction (asc or desc)

        Returns:
            Created sort dictionary

        Raises:
            NocoDBException: For API errors
        """
        if direction.lower() not in ["asc", "desc"]:
            raise ValueError("Direction must be 'asc' or 'desc'")

        data = {"fk_column_id": column_id, "direction": direction.lower()}

        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/sorts"
        response = self.meta_client._post(endpoint, data=data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from sort creation")

    def update_view_sort(
        self, table_id: str, view_id: str, sort_id: str, direction: str
    ) -> dict[str, Any]:
        """Update a view sort.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_id: ID of the sort to update
            direction: New sort direction (asc or desc)

        Returns:
            Updated sort dictionary

        Raises:
            NocoDBException: For API errors
        """
        if direction.lower() not in ["asc", "desc"]:
            raise ValueError("Direction must be 'asc' or 'desc'")

        data = {"direction": direction.lower()}

        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/sorts/{sort_id}"
        response = self.meta_client._patch(endpoint, data=data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from sort update")

    def delete_view_sort(self, table_id: str, view_id: str, sort_id: str) -> bool:
        """Delete a view sort.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_id: ID of the sort to delete

        Returns:
            True if deletion was successful

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/sorts/{sort_id}"
        response = self.meta_client._delete(endpoint)
        return response is not None

    def get_view_data(
        self,
        table_id: str,
        view_id: str,
        fields: list[str] | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get data from a view with its filters and sorts applied.

        Args:
            table_id: ID of the table
            view_id: ID of the view
            fields: List of fields to retrieve
            limit: Maximum number of records to retrieve
            offset: Number of records to skip

        Returns:
            List of record dictionaries with view filters/sorts applied

        Raises:
            NocoDBException: For API errors
        """
        params: dict[str, str | int] = {"limit": limit, "offset": offset}

        if fields:
            params["fields"] = ",".join(fields)

        endpoint = f"api/v2/tables/{table_id}/views/{view_id}/records"
        response = self.meta_client._get(endpoint, params=params)
        view_list = response.get("list", [])
        return view_list if isinstance(view_list, list) else []

    def duplicate_view(self, table_id: str, view_id: str, new_title: str) -> dict[str, Any]:
        """Duplicate an existing view with a new title.

        Args:
            table_id: ID of the table
            view_id: ID of the view to duplicate
            new_title: Title for the duplicated view

        Returns:
            Created view dictionary

        Raises:
            NocoDBException: For API errors
        """
        # Get the original view
        original_view = self.get_view(table_id, view_id)

        # Create new view with same type and options
        new_view = self.create_view(
            table_id=table_id,
            title=new_title,
            view_type=original_view.get("type", "grid").lower(),
            options=original_view.get("meta", {}),
        )

        new_view_id = new_view["id"]

        # Copy filters
        filters = self.get_view_filters(table_id, view_id)
        for filter_config in filters:
            self.create_view_filter(
                table_id=table_id,
                view_id=new_view_id,
                column_id=filter_config["fk_column_id"],
                comparison_op=filter_config["comparison_op"],
                value=filter_config.get("value"),
                logical_op=filter_config.get("logical_op", "and"),
            )

        # Copy sorts
        sorts = self.get_view_sorts(table_id, view_id)
        for sort_config in sorts:
            self.create_view_sort(
                table_id=table_id,
                view_id=new_view_id,
                column_id=sort_config["fk_column_id"],
                direction=sort_config["direction"],
            )

        return new_view


class TableViews:
    """Helper class for managing views on a specific table.

    This is a convenience wrapper that automatically includes table_id
    in all view operations.
    """

    def __init__(self, views_manager: NocoDBViews, table_id: str) -> None:
        """Initialize table-specific views manager.

        Args:
            views_manager: NocoDBViews instance
            table_id: ID of the table
        """
        self._views = views_manager
        self._table_id = table_id

    def get_views(self) -> list[dict[str, Any]]:
        """Get all views for this table."""
        return self._views.get_views(self._table_id)

    def get_view(self, view_id: str) -> dict[str, Any]:
        """Get a specific view by ID."""
        return self._views.get_view(self._table_id, view_id)

    def create_view(
        self, title: str, view_type: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a new view for this table."""
        return self._views.create_view(self._table_id, title, view_type, options)

    def update_view(
        self, view_id: str, title: str | None = None, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Update an existing view."""
        return self._views.update_view(self._table_id, view_id, title, options)

    def delete_view(self, view_id: str) -> bool:
        """Delete a view."""
        return self._views.delete_view(self._table_id, view_id)

    def get_view_data(
        self, view_id: str, fields: list[str] | None = None, limit: int = 25, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get data from a view."""
        return self._views.get_view_data(self._table_id, view_id, fields, limit, offset)

    def duplicate_view(self, view_id: str, new_title: str) -> dict[str, Any]:
        """Duplicate an existing view."""
        return self._views.duplicate_view(self._table_id, view_id, new_title)
