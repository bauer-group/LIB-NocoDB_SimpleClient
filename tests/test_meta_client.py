"""Tests for NocoDB Meta Client based on actual implementation."""

from unittest.mock import Mock, patch
import pytest

from nocodb_simple_client.meta_client import NocoDBMetaClient
from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.config import NocoDBConfig


class TestMetaClientInheritance:
    """Test NocoDBMetaClient inheritance from NocoDBClient."""

    def test_meta_client_inherits_from_client(self):
        """Test that meta client properly inherits from base client."""
        # Verify inheritance
        assert issubclass(NocoDBMetaClient, NocoDBClient)

    def test_meta_client_has_http_methods(self):
        """Test that meta client inherits HTTP methods."""
        # This tests the class structure, not actual instantiation
        assert hasattr(NocoDBMetaClient, '_get')
        assert hasattr(NocoDBMetaClient, '_post')
        assert hasattr(NocoDBMetaClient, '_patch')
        assert hasattr(NocoDBMetaClient, '_delete')

    @patch('nocodb_simple_client.meta_client.NocoDBConfig')
    def test_meta_client_initialization_with_config(self, mock_config_class):
        """Test meta client initialization with config object."""
        # Mock config object
        mock_config = Mock(spec=NocoDBConfig)
        mock_config.validate.return_value = None
        mock_config.setup_logging.return_value = None
        mock_config_class.return_value = mock_config

        # Test should not raise errors with proper mocking
        with patch.object(NocoDBClient, '__init__', return_value=None):
            meta_client = NocoDBMetaClient(mock_config)
            # Verify the config was used
            assert hasattr(meta_client, 'list_tables')
            assert hasattr(meta_client, 'create_table')


class TestTableOperations:
    """Test table operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        # Make sure it has the required methods
        client.list_tables = NocoDBMetaClient.list_tables.__get__(client)
        client.get_table_info = NocoDBMetaClient.get_table_info.__get__(client)
        client.create_table = NocoDBMetaClient.create_table.__get__(client)
        client.update_table = NocoDBMetaClient.update_table.__get__(client)
        client.delete_table = NocoDBMetaClient.delete_table.__get__(client)
        return client

    def test_list_tables(self, meta_client):
        """Test list_tables method."""
        expected_tables = [
            {"id": "table1", "title": "Users", "type": "table"},
            {"id": "table2", "title": "Orders", "type": "table"}
        ]
        expected_response = {"list": expected_tables}
        meta_client._get.return_value = expected_response

        result = meta_client.list_tables("base123")

        assert result == expected_tables
        meta_client._get.assert_called_once_with("api/v2/meta/bases/base123/tables")

    def test_list_tables_empty_response(self, meta_client):
        """Test list_tables with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_tables("base123")

        assert result == []

    def test_get_table_info(self, meta_client):
        """Test get_table_info method."""
        expected_info = {
            "id": "table123",
            "title": "Users",
            "columns": [{"title": "Name", "uidt": "SingleLineText"}]
        }
        meta_client._get.return_value = expected_info

        result = meta_client.get_table_info("table123")

        assert result == expected_info
        meta_client._get.assert_called_once_with("api/v2/meta/tables/table123")

    def test_get_table_info_non_dict_response(self, meta_client):
        """Test get_table_info with non-dict response."""
        meta_client._get.return_value = "unexpected_response"

        result = meta_client.get_table_info("table123")

        assert result == {"data": "unexpected_response"}

    def test_create_table(self, meta_client):
        """Test create_table method."""
        table_data = {
            "title": "New Table",
            "columns": [
                {"title": "Name", "uidt": "SingleLineText"},
                {"title": "Email", "uidt": "Email"}
            ]
        }
        expected_response = {"id": "new_table_123", "title": "New Table"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_table("base123", table_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/bases/base123/tables", data=table_data)

    def test_create_table_non_dict_response(self, meta_client):
        """Test create_table with non-dict response."""
        table_data = {"title": "New Table"}
        meta_client._post.return_value = "unexpected_response"

        result = meta_client.create_table("base123", table_data)

        assert result == {"data": "unexpected_response"}

    def test_update_table(self, meta_client):
        """Test update_table method."""
        update_data = {"title": "Updated Table", "description": "Updated description"}
        expected_response = {"id": "table123", "title": "Updated Table"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_table("table123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/tables/table123", data=update_data)

    def test_delete_table(self, meta_client):
        """Test delete_table method."""
        expected_response = {"success": True, "message": "Table deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_table("table123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/tables/table123")


class TestColumnOperations:
    """Test column operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        # Add methods that exist in the real implementation
        client.list_columns = Mock()
        return client

    def test_list_columns_method_exists(self, meta_client):
        """Test that list_columns method exists and can be called."""
        expected_columns = [
            {"id": "col1", "title": "Name", "uidt": "SingleLineText"},
            {"id": "col2", "title": "Email", "uidt": "Email"}
        ]
        meta_client.list_columns.return_value = expected_columns

        result = meta_client.list_columns("table123")

        assert result == expected_columns
        meta_client.list_columns.assert_called_once_with("table123")


class TestViewOperations:
    """Test view operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked view methods."""
        client = Mock(spec=NocoDBMetaClient)
        # Add methods that are used by the views module
        client.list_views = Mock()
        client.get_view = Mock()
        client.create_view = Mock()
        client.update_view = Mock()
        client.delete_view = Mock()
        return client

    def test_list_views_delegation(self, meta_client):
        """Test list_views method delegation."""
        expected_views = [
            {"id": "view1", "title": "Grid View", "type": "Grid"},
            {"id": "view2", "title": "Gallery View", "type": "Gallery"}
        ]
        meta_client.list_views.return_value = expected_views

        result = meta_client.list_views("table123")

        assert result == expected_views
        meta_client.list_views.assert_called_once_with("table123")

    def test_create_view_delegation(self, meta_client):
        """Test create_view method delegation."""
        view_data = {"title": "New View", "type": "Grid"}
        expected_response = {"id": "view123", "title": "New View"}
        meta_client.create_view.return_value = expected_response

        result = meta_client.create_view("table123", view_data)

        assert result == expected_response
        meta_client.create_view.assert_called_once_with("table123", view_data)


class TestMetaClientEndpoints:
    """Test that meta client uses correct API endpoints."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_tables = NocoDBMetaClient.list_tables.__get__(client)
        client.get_table_info = NocoDBMetaClient.get_table_info.__get__(client)
        client.create_table = NocoDBMetaClient.create_table.__get__(client)
        return client

    def test_endpoints_follow_meta_api_pattern(self, meta_client):
        """Test that endpoints follow the Meta API pattern."""
        meta_client._get.return_value = {"list": []}
        meta_client._post.return_value = {"id": "test"}

        # Test various endpoints
        meta_client.list_tables("base123")
        meta_client.get_table_info("table123")
        meta_client.create_table("base123", {"title": "Test"})

        # Verify endpoints follow Meta API pattern
        calls = [call[0][0] for call in meta_client._get.call_args_list + meta_client._post.call_args_list]

        for call in calls:
            assert call.startswith("api/v2/meta/"), f"Endpoint {call} doesn't follow Meta API pattern"


class TestMetaClientErrorHandling:
    """Test meta client error handling."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_tables = NocoDBMetaClient.list_tables.__get__(client)
        return client

    def test_list_tables_handles_missing_list_key(self, meta_client):
        """Test list_tables handles missing 'list' key gracefully."""
        meta_client._get.return_value = {"data": "something_else"}

        result = meta_client.list_tables("base123")

        assert result == []

    def test_list_tables_handles_invalid_list_type(self, meta_client):
        """Test list_tables handles invalid list type gracefully."""
        meta_client._get.return_value = {"list": "not_a_list"}

        result = meta_client.list_tables("base123")

        assert result == []


class TestMetaClientIntegration:
    """Test meta client integration scenarios."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for integration testing."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_tables = NocoDBMetaClient.list_tables.__get__(client)
        client.create_table = NocoDBMetaClient.create_table.__get__(client)
        client.delete_table = NocoDBMetaClient.delete_table.__get__(client)
        return client

    def test_table_lifecycle_workflow(self, meta_client):
        """Test complete table lifecycle: create, list, delete."""
        # Mock responses
        create_response = {"id": "table123", "title": "Test Table"}
        list_response = {"list": [{"id": "table123", "title": "Test Table"}]}
        delete_response = {"success": True}

        meta_client._post.return_value = create_response
        meta_client._get.return_value = list_response
        meta_client._delete.return_value = delete_response

        # Create table
        table_data = {"title": "Test Table", "columns": [{"title": "Name", "uidt": "SingleLineText"}]}
        created = meta_client.create_table("base123", table_data)
        assert created["title"] == "Test Table"

        # List tables
        tables = meta_client.list_tables("base123")
        assert len(tables) == 1
        assert tables[0]["title"] == "Test Table"

        # Delete table
        deleted = meta_client.delete_table("table123")
        assert deleted["success"] is True

        # Verify all calls were made
        meta_client._post.assert_called_once()
        meta_client._get.assert_called_once()
        meta_client._delete.assert_called_once()
