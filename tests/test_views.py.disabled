"""Tests for NocoDB Views management based on actual implementation."""

from unittest.mock import Mock, patch
import pytest

from nocodb_simple_client.views import NocoDBViews, TableViews
from nocodb_simple_client.meta_client import NocoDBMetaClient
from nocodb_simple_client.table import NocoDBTable
from nocodb_simple_client.exceptions import NocoDBException, ValidationException


class TestNocoDBViews:
    """Test NocoDBViews functionality."""

    @pytest.fixture
    def meta_client(self):
        """Create mock meta client."""
        return Mock(spec=NocoDBMetaClient)

    @pytest.fixture
    def views(self, meta_client):
        """Create views instance."""
        return NocoDBViews(meta_client)

    def test_views_initialization(self, meta_client):
        """Test views initialization."""
        views = NocoDBViews(meta_client)

        assert views.meta_client == meta_client
        assert hasattr(views, 'VIEW_TYPES')
        assert "grid" in views.VIEW_TYPES
        assert "gallery" in views.VIEW_TYPES

    def test_get_views(self, views, meta_client):
        """Test get_views method."""
        expected_views = [
            {"id": "view_1", "title": "Grid View", "type": "Grid"},
            {"id": "view_2", "title": "Gallery View", "type": "Gallery"}
        ]
        meta_client.list_views.return_value = expected_views

        result = views.get_views("table_123")

        assert result == expected_views
        meta_client.list_views.assert_called_once_with("table_123")

    def test_get_view(self, views, meta_client):
        """Test get_view method."""
        expected_view = {"id": "view_123", "title": "Test View", "type": "Grid"}
        meta_client.get_view.return_value = expected_view

        result = views.get_view("table_123", "view_123")

        assert result == expected_view
        meta_client.get_view.assert_called_once_with("table_123", "view_123")

    def test_create_view(self, views, meta_client):
        """Test create_view method."""
        view_data = {
            "title": "New View",
            "type": "Grid",
            "show_system_fields": False
        }
        expected_view = {"id": "new_view_123", **view_data}
        meta_client.create_view.return_value = expected_view

        result = views.create_view("table_123", **view_data)

        assert result == expected_view
        meta_client.create_view.assert_called_once_with("table_123", **view_data)

    def test_update_view(self, views, meta_client):
        """Test update_view method."""
        update_data = {"title": "Updated View"}
        expected_view = {"id": "view_123", "title": "Updated View"}
        meta_client.update_view.return_value = expected_view

        result = views.update_view("table_123", "view_123", **update_data)

        assert result == expected_view
        meta_client.update_view.assert_called_once_with("table_123", "view_123", **update_data)

    def test_delete_view(self, views, meta_client):
        """Test delete_view method."""
        meta_client.delete_view.return_value = True

        result = views.delete_view("table_123", "view_123")

        assert result is True
        meta_client.delete_view.assert_called_once_with("table_123", "view_123")

    def test_get_view_columns(self, views, meta_client):
        """Test get_view_columns method."""
        expected_columns = [
            {"id": "col_1", "title": "Name", "show": True},
            {"id": "col_2", "title": "Email", "show": False}
        ]
        meta_client.get_view_columns.return_value = expected_columns

        result = views.get_view_columns("table_123", "view_123")

        assert result == expected_columns
        meta_client.get_view_columns.assert_called_once_with("table_123", "view_123")

    def test_update_view_column(self, views, meta_client):
        """Test update_view_column method."""
        column_data = {"show": False, "width": 200}
        expected_column = {"id": "col_123", **column_data}
        meta_client.update_view_column.return_value = expected_column

        result = views.update_view_column("table_123", "view_123", "col_123", **column_data)

        assert result == expected_column
        meta_client.update_view_column.assert_called_once_with("table_123", "view_123", "col_123", **column_data)

    def test_get_view_filters(self, views, meta_client):
        """Test get_view_filters method."""
        expected_filters = [
            {"id": "filter_1", "column_id": "col_1", "comparison_op": "eq", "value": "test"}
        ]
        meta_client.get_view_filters.return_value = expected_filters

        result = views.get_view_filters("table_123", "view_123")

        assert result == expected_filters
        meta_client.get_view_filters.assert_called_once_with("table_123", "view_123")

    def test_create_view_filter(self, views, meta_client):
        """Test create_view_filter method."""
        filter_data = {
            "column_id": "col_123",
            "comparison_op": "eq",
            "value": "active"
        }
        expected_filter = {"id": "filter_123", **filter_data}
        meta_client.create_view_filter.return_value = expected_filter

        result = views.create_view_filter("table_123", "view_123", **filter_data)

        assert result == expected_filter
        meta_client.create_view_filter.assert_called_once_with("table_123", "view_123", **filter_data)

    def test_update_view_filter(self, views, meta_client):
        """Test update_view_filter method."""
        filter_data = {"value": "updated_value"}
        expected_filter = {"id": "filter_123", **filter_data}
        meta_client.update_view_filter.return_value = expected_filter

        result = views.update_view_filter("table_123", "view_123", "filter_123", **filter_data)

        assert result == expected_filter
        meta_client.update_view_filter.assert_called_once_with("table_123", "view_123", "filter_123", **filter_data)

    def test_delete_view_filter(self, views, meta_client):
        """Test delete_view_filter method."""
        meta_client.delete_view_filter.return_value = True

        result = views.delete_view_filter("table_123", "view_123", "filter_123")

        assert result is True
        meta_client.delete_view_filter.assert_called_once_with("table_123", "view_123", "filter_123")

    def test_get_view_sorts(self, views, meta_client):
        """Test get_view_sorts method."""
        expected_sorts = [
            {"id": "sort_1", "column_id": "col_1", "direction": "asc"}
        ]
        meta_client.get_view_sorts.return_value = expected_sorts

        result = views.get_view_sorts("table_123", "view_123")

        assert result == expected_sorts
        meta_client.get_view_sorts.assert_called_once_with("table_123", "view_123")

    def test_create_view_sort(self, views, meta_client):
        """Test create_view_sort method."""
        sort_data = {
            "column_id": "col_123",
            "direction": "desc"
        }
        expected_sort = {"id": "sort_123", **sort_data}
        meta_client.create_view_sort.return_value = expected_sort

        result = views.create_view_sort("table_123", "view_123", **sort_data)

        assert result == expected_sort
        meta_client.create_view_sort.assert_called_once_with("table_123", "view_123", **sort_data)

    def test_update_view_sort(self, views, meta_client):
        """Test update_view_sort method."""
        sort_data = {"direction": "asc"}
        expected_sort = {"id": "sort_123", **sort_data}
        meta_client.update_view_sort.return_value = expected_sort

        result = views.update_view_sort("table_123", "view_123", "sort_123", **sort_data)

        assert result == expected_sort
        meta_client.update_view_sort.assert_called_once_with("table_123", "view_123", "sort_123", **sort_data)

    def test_delete_view_sort(self, views, meta_client):
        """Test delete_view_sort method."""
        meta_client.delete_view_sort.return_value = True

        result = views.delete_view_sort("table_123", "view_123", "sort_123")

        assert result is True
        meta_client.delete_view_sort.assert_called_once_with("table_123", "view_123", "sort_123")

    def test_get_view_data(self, views, meta_client):
        """Test get_view_data method."""
        expected_data = {
            "list": [{"Id": "1", "Name": "Record 1"}],
            "pageInfo": {"totalRows": 1}
        }
        meta_client.get_view_records.return_value = expected_data

        result = views.get_view_data("table_123", "view_123", limit=10)

        assert result == expected_data
        meta_client.get_view_records.assert_called_once_with("table_123", "view_123", limit=10)

    def test_duplicate_view(self, views, meta_client):
        """Test duplicate_view method."""
        expected_view = {"id": "duplicated_view_123", "title": "Copy of Original"}
        meta_client.duplicate_view.return_value = expected_view

        result = views.duplicate_view("table_123", "view_123", "Copy of Original")

        assert result == expected_view
        meta_client.duplicate_view.assert_called_once_with("table_123", "view_123", "Copy of Original")


class TestTableViews:
    """Test TableViews functionality."""

    @pytest.fixture
    def mock_table(self):
        """Create mock table."""
        table = Mock(spec=NocoDBTable)
        table.table_id = "test_table_123"
        return table

    @pytest.fixture
    def table_views(self, mock_table):
        """Create table views instance."""
        return TableViews(mock_table)

    def test_table_views_initialization(self, mock_table):
        """Test table views initialization."""
        table_views = TableViews(mock_table)

        assert table_views.table == mock_table
        assert table_views.table_id == "test_table_123"

    def test_get_views_table_delegation(self, table_views, mock_table):
        """Test get_views delegation to table's client."""
        expected_views = [{"id": "view_1", "title": "Grid View"}]

        # Mock the client's views property
        mock_views = Mock()
        mock_views.get_views.return_value = expected_views
        mock_table.client.views = mock_views

        result = table_views.get_views()

        assert result == expected_views
        mock_views.get_views.assert_called_once_with("test_table_123")

    def test_get_view_table_delegation(self, table_views, mock_table):
        """Test get_view delegation to table's client."""
        expected_view = {"id": "view_123", "title": "Test View"}

        mock_views = Mock()
        mock_views.get_view.return_value = expected_view
        mock_table.client.views = mock_views

        result = table_views.get_view("view_123")

        assert result == expected_view
        mock_views.get_view.assert_called_once_with("test_table_123", "view_123")

    def test_create_view_table_delegation(self, table_views, mock_table):
        """Test create_view delegation to table's client."""
        view_data = {"title": "New View", "type": "Grid"}
        expected_view = {"id": "new_view_123", **view_data}

        mock_views = Mock()
        mock_views.create_view.return_value = expected_view
        mock_table.client.views = mock_views

        result = table_views.create_view(**view_data)

        assert result == expected_view
        mock_views.create_view.assert_called_once_with("test_table_123", **view_data)

    def test_update_view_table_delegation(self, table_views, mock_table):
        """Test update_view delegation to table's client."""
        update_data = {"title": "Updated View"}
        expected_view = {"id": "view_123", **update_data}

        mock_views = Mock()
        mock_views.update_view.return_value = expected_view
        mock_table.client.views = mock_views

        result = table_views.update_view("view_123", **update_data)

        assert result == expected_view
        mock_views.update_view.assert_called_once_with("test_table_123", "view_123", **update_data)

    def test_delete_view_table_delegation(self, table_views, mock_table):
        """Test delete_view delegation to table's client."""
        mock_views = Mock()
        mock_views.delete_view.return_value = True
        mock_table.client.views = mock_views

        result = table_views.delete_view("view_123")

        assert result is True
        mock_views.delete_view.assert_called_once_with("test_table_123", "view_123")

    def test_get_view_data_table_delegation(self, table_views, mock_table):
        """Test get_view_data delegation to table's client."""
        expected_data = {"list": [{"Id": "1"}], "pageInfo": {"totalRows": 1}}

        mock_views = Mock()
        mock_views.get_view_data.return_value = expected_data
        mock_table.client.views = mock_views

        result = table_views.get_view_data("view_123", limit=5)

        assert result == expected_data
        mock_views.get_view_data.assert_called_once_with("test_table_123", "view_123", limit=5)

    def test_duplicate_view_table_delegation(self, table_views, mock_table):
        """Test duplicate_view delegation to table's client."""
        expected_view = {"id": "duplicated_view_123", "title": "Copy"}

        mock_views = Mock()
        mock_views.duplicate_view.return_value = expected_view
        mock_table.client.views = mock_views

        result = table_views.duplicate_view("view_123", "Copy")

        assert result == expected_view
        mock_views.duplicate_view.assert_called_once_with("test_table_123", "view_123", "Copy")


class TestViewTypes:
    """Test view type constants and utilities."""

    def test_view_types_constant(self):
        """Test VIEW_TYPES constant."""
        views = NocoDBViews(Mock())

        assert views.VIEW_TYPES["grid"] == "Grid"
        assert views.VIEW_TYPES["gallery"] == "Gallery"
        assert views.VIEW_TYPES["form"] == "Form"
        assert views.VIEW_TYPES["kanban"] == "Kanban"
        assert views.VIEW_TYPES["calendar"] == "Calendar"

    def test_all_view_types_covered(self):
        """Test that all view types are defined."""
        views = NocoDBViews(Mock())
        expected_types = ["grid", "gallery", "form", "kanban", "calendar"]

        for view_type in expected_types:
            assert view_type in views.VIEW_TYPES


class TestViewFiltersAndSorts:
    """Test view filter and sort specific functionality."""

    @pytest.fixture
    def views(self):
        """Create views instance for filter/sort tests."""
        return NocoDBViews(Mock(spec=NocoDBMetaClient))

    def test_filter_operations(self, views):
        """Test that filter operations are available."""
        assert hasattr(views, 'get_view_filters')
        assert hasattr(views, 'create_view_filter')
        assert hasattr(views, 'update_view_filter')
        assert hasattr(views, 'delete_view_filter')

    def test_sort_operations(self, views):
        """Test that sort operations are available."""
        assert hasattr(views, 'get_view_sorts')
        assert hasattr(views, 'create_view_sort')
        assert hasattr(views, 'update_view_sort')
        assert hasattr(views, 'delete_view_sort')

    def test_column_operations(self, views):
        """Test that column operations are available."""
        assert hasattr(views, 'get_view_columns')
        assert hasattr(views, 'update_view_column')
