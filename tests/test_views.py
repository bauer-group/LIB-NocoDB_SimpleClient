"""Tests for view management functionality."""

from unittest.mock import Mock

import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.views import NocoDBViews, TableViews


class TestNocoDBViews:
    """Test NocoDBViews class functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def views_manager(self, mock_client):
        """Create a views manager instance for testing."""
        return NocoDBViews(mock_client)

    def test_get_views_success(self, mock_client, views_manager):
        """Test successful retrieval of views."""
        # Arrange
        table_id = "table1"
        expected_views = [
            {"id": "view1", "title": "Grid View", "type": "Grid"},
            {"id": "view2", "title": "Gallery View", "type": "Gallery"},
        ]

        mock_client._get.return_value = {"list": expected_views}

        # Act
        result = views_manager.get_views(table_id)

        # Assert
        assert result == expected_views
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/views")

    def test_get_view_success(self, mock_client, views_manager):
        """Test successful retrieval of a single view."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        expected_view = {
            "id": "view1",
            "title": "My Grid View",
            "type": "Grid",
            "meta": {"columns": []},
        }

        mock_client._get.return_value = expected_view

        # Act
        result = views_manager.get_view(table_id, view_id)

        # Assert
        assert result == expected_view
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/views/{view_id}")

    def test_create_view_success(self, mock_client, views_manager):
        """Test successful view creation."""
        # Arrange
        table_id = "table1"
        title = "New Grid View"
        view_type = "grid"
        options = {"show_system_fields": False}

        expected_view = {"id": "new_view_id", "title": title, "type": "Grid", "table_id": table_id}

        mock_client._post.return_value = expected_view

        # Act
        result = views_manager.create_view(table_id, title, view_type, options)

        # Assert
        assert result == expected_view
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/views" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == title
        assert data["type"] == "Grid"
        assert data["table_id"] == table_id
        assert data["show_system_fields"] is False

    def test_create_view_invalid_type(self, mock_client, views_manager):
        """Test creating view with invalid type raises ValueError."""
        # Arrange
        table_id = "table1"
        title = "New View"
        invalid_view_type = "invalid_type"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid view type"):
            views_manager.create_view(table_id, title, invalid_view_type)

    def test_update_view_success(self, mock_client, views_manager):
        """Test successful view update."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        new_title = "Updated View Title"
        options = {"show_pagination": True}

        expected_view = {"id": view_id, "title": new_title, "show_pagination": True}

        mock_client._patch.return_value = expected_view

        # Act
        result = views_manager.update_view(table_id, view_id, title=new_title, options=options)

        # Assert
        assert result == expected_view
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == new_title
        assert data["show_pagination"] is True

    def test_update_view_no_changes(self, mock_client, views_manager):
        """Test updating view with no changes raises ValueError."""
        # Arrange
        table_id = "table1"
        view_id = "view1"

        # Act & Assert
        with pytest.raises(ValueError, match="At least title or options must be provided"):
            views_manager.update_view(table_id, view_id)

    def test_delete_view_success(self, mock_client, views_manager):
        """Test successful view deletion."""
        # Arrange
        table_id = "table1"
        view_id = "view1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = views_manager.delete_view(table_id, view_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(f"api/v2/tables/{table_id}/views/{view_id}")

    def test_get_view_columns_success(self, mock_client, views_manager):
        """Test getting view columns configuration."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        expected_columns = [
            {"id": "col1", "title": "Name", "show": True, "order": 1},
            {"id": "col2", "title": "Email", "show": True, "order": 2},
        ]

        mock_client._get.return_value = {"list": expected_columns}

        # Act
        result = views_manager.get_view_columns(table_id, view_id)

        # Assert
        assert result == expected_columns
        mock_client._get.assert_called_once_with(
            f"api/v2/tables/{table_id}/views/{view_id}/columns"
        )

    def test_update_view_column_success(self, mock_client, views_manager):
        """Test updating view column configuration."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        column_id = "col1"
        options = {"show": False, "width": 200}

        expected_column = {"id": column_id, "show": False, "width": 200}

        mock_client._patch.return_value = expected_column

        # Act
        result = views_manager.update_view_column(table_id, view_id, column_id, options)

        # Assert
        assert result == expected_column
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/columns/{column_id}" in call_args[0][0]
        assert call_args[1]["data"] == options

    def test_get_view_filters_success(self, mock_client, views_manager):
        """Test getting view filters."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        expected_filters = [
            {"id": "filter1", "fk_column_id": "col1", "comparison_op": "eq", "value": "Active"}
        ]

        mock_client._get.return_value = {"list": expected_filters}

        # Act
        result = views_manager.get_view_filters(table_id, view_id)

        # Assert
        assert result == expected_filters
        mock_client._get.assert_called_once_with(
            f"api/v2/tables/{table_id}/views/{view_id}/filters"
        )

    def test_create_view_filter_success(self, mock_client, views_manager):
        """Test creating a view filter."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        column_id = "col1"
        comparison_op = "eq"
        value = "Active"
        logical_op = "and"

        expected_filter = {
            "id": "new_filter_id",
            "fk_column_id": column_id,
            "comparison_op": comparison_op,
            "value": value,
            "logical_op": logical_op,
        }

        mock_client._post.return_value = expected_filter

        # Act
        result = views_manager.create_view_filter(
            table_id, view_id, column_id, comparison_op, value, logical_op
        )

        # Assert
        assert result == expected_filter
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/filters" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["fk_column_id"] == column_id
        assert data["comparison_op"] == comparison_op
        assert data["value"] == value
        assert data["logical_op"] == logical_op

    def test_update_view_filter_success(self, mock_client, views_manager):
        """Test updating a view filter."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        filter_id = "filter1"
        new_value = "Inactive"
        new_op = "neq"

        expected_filter = {"id": filter_id, "comparison_op": new_op, "value": new_value}

        mock_client._patch.return_value = expected_filter

        # Act
        result = views_manager.update_view_filter(
            table_id, view_id, filter_id, comparison_op=new_op, value=new_value
        )

        # Assert
        assert result == expected_filter
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/filters/{filter_id}" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["comparison_op"] == new_op
        assert data["value"] == new_value

    def test_delete_view_filter_success(self, mock_client, views_manager):
        """Test deleting a view filter."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        filter_id = "filter1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = views_manager.delete_view_filter(table_id, view_id, filter_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(
            f"api/v2/tables/{table_id}/views/{view_id}/filters/{filter_id}"
        )

    def test_get_view_sorts_success(self, mock_client, views_manager):
        """Test getting view sorts."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        expected_sorts = [{"id": "sort1", "fk_column_id": "col1", "direction": "asc"}]

        mock_client._get.return_value = {"list": expected_sorts}

        # Act
        result = views_manager.get_view_sorts(table_id, view_id)

        # Assert
        assert result == expected_sorts
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/views/{view_id}/sorts")

    def test_create_view_sort_success(self, mock_client, views_manager):
        """Test creating a view sort."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        column_id = "col1"
        direction = "desc"

        expected_sort = {"id": "new_sort_id", "fk_column_id": column_id, "direction": direction}

        mock_client._post.return_value = expected_sort

        # Act
        result = views_manager.create_view_sort(table_id, view_id, column_id, direction)

        # Assert
        assert result == expected_sort
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/sorts" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["fk_column_id"] == column_id
        assert data["direction"] == direction

    def test_create_view_sort_invalid_direction(self, mock_client, views_manager):
        """Test creating sort with invalid direction."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        column_id = "col1"
        invalid_direction = "invalid"

        # Act & Assert
        with pytest.raises(ValueError, match="Direction must be 'asc' or 'desc'"):
            views_manager.create_view_sort(table_id, view_id, column_id, invalid_direction)

    def test_update_view_sort_success(self, mock_client, views_manager):
        """Test updating a view sort."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        sort_id = "sort1"
        new_direction = "desc"

        expected_sort = {"id": sort_id, "direction": new_direction}

        mock_client._patch.return_value = expected_sort

        # Act
        result = views_manager.update_view_sort(table_id, view_id, sort_id, new_direction)

        # Assert
        assert result == expected_sort
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/sorts/{sort_id}" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["direction"] == new_direction

    def test_delete_view_sort_success(self, mock_client, views_manager):
        """Test deleting a view sort."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        sort_id = "sort1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = views_manager.delete_view_sort(table_id, view_id, sort_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(
            f"api/v2/tables/{table_id}/views/{view_id}/sorts/{sort_id}"
        )

    def test_get_view_data_success(self, mock_client, views_manager):
        """Test getting data from a view."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        fields = ["Name", "Email"]
        limit = 50
        offset = 10

        expected_records = [
            {"Id": "rec1", "Name": "John", "Email": "john@example.com"},
            {"Id": "rec2", "Name": "Jane", "Email": "jane@example.com"},
        ]

        mock_client._get.return_value = {"list": expected_records}

        # Act
        result = views_manager.get_view_data(table_id, view_id, fields, limit, offset)

        # Assert
        assert result == expected_records
        mock_client._get.assert_called_once()
        call_args = mock_client._get.call_args
        assert f"api/v2/tables/{table_id}/views/{view_id}/records" in call_args[0][0]

        params = call_args[1]["params"]
        assert params["fields"] == "Name,Email"
        assert params["limit"] == limit
        assert params["offset"] == offset

    def test_duplicate_view_success(self, mock_client, views_manager):
        """Test duplicating a view."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        new_title = "Duplicated View"

        # Mock the original view
        original_view = {
            "id": view_id,
            "title": "Original View",
            "type": "Grid",
            "meta": {"show_system_fields": False},
        }

        # Mock the new view
        new_view = {"id": "new_view_id", "title": new_title, "type": "Grid"}

        # Mock responses
        mock_client._get.side_effect = [
            original_view,  # get_view call
            {"list": []},  # get_view_filters call
            {"list": []},  # get_view_sorts call
        ]
        mock_client._post.return_value = new_view

        # Act
        result = views_manager.duplicate_view(table_id, view_id, new_title)

        # Assert
        assert result == new_view
        assert mock_client._get.call_count == 3  # get_view, get_filters, get_sorts
        mock_client._post.assert_called_once()  # create_view

    def test_duplicate_view_with_filters_and_sorts(self, mock_client, views_manager):
        """Test duplicating a view that has filters and sorts."""
        # Arrange
        table_id = "table1"
        view_id = "view1"
        new_title = "Duplicated View"

        original_view = {"id": view_id, "title": "Original View", "type": "Grid", "meta": {}}

        filters = [
            {"fk_column_id": "col1", "comparison_op": "eq", "value": "Active", "logical_op": "and"}
        ]

        sorts = [{"fk_column_id": "col2", "direction": "desc"}]

        new_view = {"id": "new_view_id", "title": new_title}

        # Mock responses
        mock_client._get.side_effect = [
            original_view,  # get_view
            {"list": filters},  # get_view_filters
            {"list": sorts},  # get_view_sorts
        ]
        mock_client._post.side_effect = [
            new_view,  # create_view
            {"id": "filter_id"},  # create_view_filter
            {"id": "sort_id"},  # create_view_sort
        ]

        # Act
        result = views_manager.duplicate_view(table_id, view_id, new_title)

        # Assert
        assert result == new_view
        assert mock_client._post.call_count == 3  # create_view, create_filter, create_sort


class TestTableViews:
    """Test TableViews helper class."""

    @pytest.fixture
    def mock_views_manager(self):
        """Create a mock views manager."""
        return Mock(spec=NocoDBViews)

    @pytest.fixture
    def table_views(self, mock_views_manager):
        """Create a table views instance."""
        return TableViews(mock_views_manager, "test_table_id")

    def test_get_views_delegates(self, mock_views_manager, table_views):
        """Test that get_views delegates to views manager."""
        # Arrange
        expected_views = [{"id": "view1", "title": "Test View"}]
        mock_views_manager.get_views.return_value = expected_views

        # Act
        result = table_views.get_views()

        # Assert
        assert result == expected_views
        mock_views_manager.get_views.assert_called_once_with("test_table_id")

    def test_get_view_delegates(self, mock_views_manager, table_views):
        """Test that get_view delegates to views manager."""
        # Arrange
        view_id = "view1"
        expected_view = {"id": view_id, "title": "Test View"}
        mock_views_manager.get_view.return_value = expected_view

        # Act
        result = table_views.get_view(view_id)

        # Assert
        assert result == expected_view
        mock_views_manager.get_view.assert_called_once_with("test_table_id", view_id)

    def test_create_view_delegates(self, mock_views_manager, table_views):
        """Test that create_view delegates to views manager."""
        # Arrange
        title = "New View"
        view_type = "grid"
        options = {"show_system_fields": False}
        expected_view = {"id": "new_view", "title": title}

        mock_views_manager.create_view.return_value = expected_view

        # Act
        result = table_views.create_view(title, view_type, options)

        # Assert
        assert result == expected_view
        mock_views_manager.create_view.assert_called_once_with(
            "test_table_id", title, view_type, options
        )

    def test_update_view_delegates(self, mock_views_manager, table_views):
        """Test that update_view delegates to views manager."""
        # Arrange
        view_id = "view1"
        title = "Updated View"
        options = {"show_pagination": True}
        expected_view = {"id": view_id, "title": title}

        mock_views_manager.update_view.return_value = expected_view

        # Act
        result = table_views.update_view(view_id, title, options)

        # Assert
        assert result == expected_view
        mock_views_manager.update_view.assert_called_once_with(
            "test_table_id", view_id, title, options
        )

    def test_delete_view_delegates(self, mock_views_manager, table_views):
        """Test that delete_view delegates to views manager."""
        # Arrange
        view_id = "view1"
        mock_views_manager.delete_view.return_value = True

        # Act
        result = table_views.delete_view(view_id)

        # Assert
        assert result is True
        mock_views_manager.delete_view.assert_called_once_with("test_table_id", view_id)

    def test_get_view_data_delegates(self, mock_views_manager, table_views):
        """Test that get_view_data delegates to views manager."""
        # Arrange
        view_id = "view1"
        fields = ["Name", "Email"]
        limit = 100
        offset = 0
        expected_records = [{"Id": "rec1", "Name": "Test"}]

        mock_views_manager.get_view_data.return_value = expected_records

        # Act
        result = table_views.get_view_data(view_id, fields, limit, offset)

        # Assert
        assert result == expected_records
        mock_views_manager.get_view_data.assert_called_once_with(
            "test_table_id", view_id, fields, limit, offset
        )

    def test_duplicate_view_delegates(self, mock_views_manager, table_views):
        """Test that duplicate_view delegates to views manager."""
        # Arrange
        view_id = "view1"
        new_title = "Duplicated View"
        expected_view = {"id": "new_view", "title": new_title}

        mock_views_manager.duplicate_view.return_value = expected_view

        # Act
        result = table_views.duplicate_view(view_id, new_title)

        # Assert
        assert result == expected_view
        mock_views_manager.duplicate_view.assert_called_once_with(
            "test_table_id", view_id, new_title
        )


class TestViewsIntegration:
    """Integration tests for views functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with realistic responses."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def views_manager(self, mock_client):
        """Create views manager with mock client."""
        return NocoDBViews(mock_client)

    def test_complete_view_management_workflow(self, mock_client, views_manager):
        """Test a complete workflow of view management operations."""
        # Arrange
        table_id = "users_table"

        # Mock responses for the workflow
        new_view = {"id": "new_view_id", "title": "Active Users View", "type": "Grid"}

        filter_response = {
            "id": "filter_id",
            "fk_column_id": "status_col",
            "comparison_op": "eq",
            "value": "Active",
        }

        sort_response = {"id": "sort_id", "fk_column_id": "name_col", "direction": "asc"}

        view_data = [
            {"Id": "user1", "Name": "Alice", "Status": "Active"},
            {"Id": "user2", "Name": "Bob", "Status": "Active"},
        ]

        mock_client._post.side_effect = [new_view, filter_response, sort_response]
        mock_client._get.return_value = {"list": view_data}

        # Act - Complete workflow
        # 1. Create a new view
        created_view = views_manager.create_view(table_id, "Active Users View", "grid")

        # 2. Add a filter to show only active users
        created_filter = views_manager.create_view_filter(
            table_id, created_view["id"], "status_col", "eq", "Active"
        )

        # 3. Add sorting by name
        created_sort = views_manager.create_view_sort(
            table_id, created_view["id"], "name_col", "asc"
        )

        # 4. Get data from the configured view
        view_records = views_manager.get_view_data(table_id, created_view["id"])

        # Assert
        assert created_view["title"] == "Active Users View"
        assert created_filter["comparison_op"] == "eq"
        assert created_filter["value"] == "Active"
        assert created_sort["direction"] == "asc"
        assert len(view_records) == 2
        assert all(record["Status"] == "Active" for record in view_records)


if __name__ == "__main__":
    pytest.main([__file__])
