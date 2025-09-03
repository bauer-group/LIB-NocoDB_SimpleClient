"""Tests for NocoDB Views management based on actual implementation."""

from unittest.mock import Mock
import pytest

from nocodb_simple_client.views import NocoDBViews
from nocodb_simple_client.meta_client import NocoDBMetaClient


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
        meta_client.get_view.assert_called_once_with("view_123")

    def test_create_view_valid_type(self, views, meta_client):
        """Test create_view with valid view type."""
        expected_view = {"id": "new_view_123", "title": "New Grid View", "type": "Grid"}
        meta_client.create_view.return_value = expected_view

        result = views.create_view("table_123", "New Grid View", "grid")

        assert result == expected_view
        # Verify the call with expected data structure
        call_args = meta_client.create_view.call_args
        assert call_args[0][0] == "table_123"  # table_id
        data = call_args[0][1]  # view data
        assert data["title"] == "New Grid View"
        assert data["type"] == "Grid"
        assert data["table_id"] == "table_123"

    def test_create_view_invalid_type(self, views, meta_client):
        """Test create_view with invalid view type."""
        with pytest.raises(ValueError, match="Invalid view type: invalid"):
            views.create_view("table_123", "Invalid View", "invalid")

    def test_create_view_with_options(self, views, meta_client):
        """Test create_view with additional options."""
        expected_view = {"id": "new_view_123", "title": "New View"}
        meta_client.create_view.return_value = expected_view
        options = {"show_system_fields": False, "cover_image_idx": 0}

        result = views.create_view("table_123", "New Gallery View", "gallery", options)

        assert result == expected_view
        call_args = meta_client.create_view.call_args
        data = call_args[0][1]
        assert data["show_system_fields"] is False
        assert data["cover_image_idx"] == 0

    def test_update_view_with_title(self, views, meta_client):
        """Test update_view with new title."""
        expected_view = {"id": "view_123", "title": "Updated View"}
        meta_client.update_view.return_value = expected_view

        result = views.update_view("table_123", "view_123", title="Updated View")

        assert result == expected_view
        meta_client.update_view.assert_called_once_with("view_123", {"title": "Updated View"})

    def test_update_view_with_options(self, views, meta_client):
        """Test update_view with options."""
        expected_view = {"id": "view_123", "show_system_fields": True}
        meta_client.update_view.return_value = expected_view
        options = {"show_system_fields": True}

        result = views.update_view("table_123", "view_123", options=options)

        assert result == expected_view
        meta_client.update_view.assert_called_once_with("view_123", {"show_system_fields": True})

    def test_update_view_no_parameters(self, views, meta_client):
        """Test update_view with no parameters raises error."""
        with pytest.raises(ValueError, match="At least title or options must be provided"):
            views.update_view("table_123", "view_123")

    def test_delete_view(self, views, meta_client):
        """Test delete_view method."""
        meta_client.delete_view.return_value = {"success": True}

        result = views.delete_view("table_123", "view_123")

        assert result is True
        meta_client.delete_view.assert_called_once_with("view_123")

    def test_delete_view_returns_none(self, views, meta_client):
        """Test delete_view when meta client returns None."""
        meta_client.delete_view.return_value = None

        result = views.delete_view("table_123", "view_123")

        assert result is False

    def test_get_view_columns(self, views, meta_client):
        """Test get_view_columns method."""
        expected_columns = [
            {"id": "col_1", "title": "Name", "show": True},
            {"id": "col_2", "title": "Email", "show": False}
        ]
        expected_response = {"list": expected_columns}
        meta_client._get.return_value = expected_response

        result = views.get_view_columns("table_123", "view_123")

        assert result == expected_columns
        meta_client._get.assert_called_once_with("api/v2/tables/table_123/views/view_123/columns")


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

    def test_view_type_case_insensitive(self):
        """Test that view type matching is case insensitive."""
        views = NocoDBViews(Mock())
        meta_client = Mock()
        meta_client.create_view.return_value = {"id": "test"}
        views.meta_client = meta_client

        # Test uppercase
        views.create_view("table_123", "Test View", "GRID")
        call_args = meta_client.create_view.call_args
        assert call_args[0][1]["type"] == "Grid"

        # Reset mock
        meta_client.reset_mock()

        # Test mixed case
        views.create_view("table_123", "Test View", "GalLery")
        call_args = meta_client.create_view.call_args
        assert call_args[0][1]["type"] == "Gallery"


class TestViewValidation:
    """Test view validation and error handling."""

    @pytest.fixture
    def views(self):
        """Create views instance."""
        return NocoDBViews(Mock())

    def test_create_view_validates_response_type(self, views):
        """Test that create_view validates response type."""
        views.meta_client.create_view.return_value = "invalid_response"

        with pytest.raises(ValueError, match="Expected dict response from view creation"):
            views.create_view("table_123", "Test View", "grid")

    def test_update_view_validates_response_type(self, views):
        """Test that update_view validates response type."""
        views.meta_client.update_view.return_value = "invalid_response"

        with pytest.raises(ValueError, match="Expected dict response from view update"):
            views.update_view("table_123", "view_123", title="Updated")

    def test_view_type_validation_comprehensive(self, views):
        """Test comprehensive view type validation."""
        invalid_types = ["invalid", "list", "chart", "", None]

        for invalid_type in invalid_types:
            if invalid_type is not None:
                with pytest.raises(ValueError):
                    views.create_view("table_123", "Test View", invalid_type)


class TestViewOperations:
    """Test comprehensive view operations."""

    @pytest.fixture
    def views(self):
        """Create views instance with mock."""
        return NocoDBViews(Mock())

    def test_view_workflow_complete(self, views):
        """Test complete view workflow: create, update, get, delete."""
        # Mock responses for each operation
        create_response = {"id": "view_123", "title": "Test View", "type": "Grid"}
        update_response = {"id": "view_123", "title": "Updated View", "type": "Grid"}
        get_response = {"id": "view_123", "title": "Updated View", "type": "Grid"}

        views.meta_client.create_view.return_value = create_response
        views.meta_client.update_view.return_value = update_response
        views.meta_client.get_view.return_value = get_response
        views.meta_client.delete_view.return_value = {"success": True}

        # Create view
        created = views.create_view("table_123", "Test View", "grid")
        assert created["title"] == "Test View"

        # Update view
        updated = views.update_view("table_123", "view_123", title="Updated View")
        assert updated["title"] == "Updated View"

        # Get view
        retrieved = views.get_view("table_123", "view_123")
        assert retrieved["title"] == "Updated View"

        # Delete view
        deleted = views.delete_view("table_123", "view_123")
        assert deleted is True

        # Verify all calls were made
        views.meta_client.create_view.assert_called_once()
        views.meta_client.update_view.assert_called_once()
        views.meta_client.get_view.assert_called_once()
        views.meta_client.delete_view.assert_called_once()
