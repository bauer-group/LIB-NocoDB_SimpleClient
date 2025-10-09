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


class TestWorkspaceOperations:
    """Test workspace operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_workspaces = NocoDBMetaClient.list_workspaces.__get__(client)
        client.get_workspace = NocoDBMetaClient.get_workspace.__get__(client)
        client.create_workspace = NocoDBMetaClient.create_workspace.__get__(client)
        client.update_workspace = NocoDBMetaClient.update_workspace.__get__(client)
        client.delete_workspace = NocoDBMetaClient.delete_workspace.__get__(client)
        return client

    def test_list_workspaces(self, meta_client):
        """Test list_workspaces method."""
        expected_workspaces = [
            {"id": "ws1", "title": "Default Workspace"},
            {"id": "ws2", "title": "Team Workspace"}
        ]
        expected_response = {"list": expected_workspaces}
        meta_client._get.return_value = expected_response

        result = meta_client.list_workspaces()

        assert result == expected_workspaces
        meta_client._get.assert_called_once_with("api/v2/meta/workspaces")

    def test_list_workspaces_empty_response(self, meta_client):
        """Test list_workspaces with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_workspaces()

        assert result == []

    def test_get_workspace(self, meta_client):
        """Test get_workspace method."""
        expected_workspace = {
            "id": "ws123",
            "title": "My Workspace",
            "created_at": "2025-01-01"
        }
        meta_client._get.return_value = expected_workspace

        result = meta_client.get_workspace("ws123")

        assert result == expected_workspace
        meta_client._get.assert_called_once_with("api/v2/meta/workspaces/ws123")

    def test_create_workspace(self, meta_client):
        """Test create_workspace method."""
        workspace_data = {
            "title": "New Workspace",
            "description": "Team collaboration space"
        }
        expected_response = {"id": "ws_new", "title": "New Workspace"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_workspace(workspace_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/workspaces", data=workspace_data)

    def test_update_workspace(self, meta_client):
        """Test update_workspace method."""
        update_data = {"title": "Updated Workspace"}
        expected_response = {"id": "ws123", "title": "Updated Workspace"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_workspace("ws123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/workspaces/ws123", data=update_data)

    def test_delete_workspace(self, meta_client):
        """Test delete_workspace method."""
        expected_response = {"success": True, "message": "Workspace deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_workspace("ws123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/workspaces/ws123")


class TestBaseOperations:
    """Test base operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_bases = NocoDBMetaClient.list_bases.__get__(client)
        client.get_base = NocoDBMetaClient.get_base.__get__(client)
        client.create_base = NocoDBMetaClient.create_base.__get__(client)
        client.update_base = NocoDBMetaClient.update_base.__get__(client)
        client.delete_base = NocoDBMetaClient.delete_base.__get__(client)
        return client

    def test_list_bases(self, meta_client):
        """Test list_bases method."""
        expected_bases = [
            {"id": "base1", "title": "Project A", "status": "active"},
            {"id": "base2", "title": "Project B", "status": "active"}
        ]
        expected_response = {"list": expected_bases}
        meta_client._get.return_value = expected_response

        result = meta_client.list_bases()

        assert result == expected_bases
        meta_client._get.assert_called_once_with("api/v2/meta/bases/")

    def test_list_bases_empty_response(self, meta_client):
        """Test list_bases with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_bases()

        assert result == []

    def test_get_base(self, meta_client):
        """Test get_base method."""
        expected_base = {
            "id": "base123",
            "title": "My Project",
            "status": "active"
        }
        meta_client._get.return_value = expected_base

        result = meta_client.get_base("base123")

        assert result == expected_base
        meta_client._get.assert_called_once_with("api/v2/meta/bases/base123")

    def test_create_base(self, meta_client):
        """Test create_base method."""
        base_data = {
            "title": "New Project",
            "description": "Project database"
        }
        expected_response = {"id": "base_new", "title": "New Project"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_base("ws123", base_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/workspaces/ws123/bases", data=base_data)

    def test_update_base(self, meta_client):
        """Test update_base method."""
        update_data = {"title": "Updated Project"}
        expected_response = {"id": "base123", "title": "Updated Project"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_base("base123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/bases/base123", data=update_data)

    def test_delete_base(self, meta_client):
        """Test delete_base method."""
        expected_response = {"success": True, "message": "Base deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_base("base123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/bases/base123")


class TestColumnOperations:
    """Test column operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_columns = NocoDBMetaClient.list_columns.__get__(client)
        client.create_column = NocoDBMetaClient.create_column.__get__(client)
        client.update_column = NocoDBMetaClient.update_column.__get__(client)
        client.delete_column = NocoDBMetaClient.delete_column.__get__(client)
        return client

    def test_list_columns(self, meta_client):
        """Test list_columns method."""
        expected_columns = [
            {"id": "col1", "title": "Name", "uidt": "SingleLineText"},
            {"id": "col2", "title": "Email", "uidt": "Email"}
        ]
        expected_response = {"list": expected_columns}
        meta_client._get.return_value = expected_response

        result = meta_client.list_columns("table123")

        assert result == expected_columns
        meta_client._get.assert_called_once_with("api/v2/meta/tables/table123/columns")

    def test_list_columns_empty_response(self, meta_client):
        """Test list_columns with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_columns("table123")

        assert result == []

    def test_create_column(self, meta_client):
        """Test create_column method."""
        column_data = {
            "title": "Age",
            "uidt": "Number",
            "dtxp": "3",
            "dtxs": "0"
        }
        expected_response = {"id": "col_new", "title": "Age", "uidt": "Number"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_column("table123", column_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/tables/table123/columns", data=column_data)

    def test_update_column(self, meta_client):
        """Test update_column method."""
        update_data = {"title": "Updated Name"}
        expected_response = {"id": "col123", "title": "Updated Name"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_column("col123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/columns/col123", data=update_data)

    def test_delete_column(self, meta_client):
        """Test delete_column method."""
        expected_response = {"success": True, "message": "Column deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_column("col123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/columns/col123")


class TestViewOperations:
    """Test view operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_views = NocoDBMetaClient.list_views.__get__(client)
        client.get_view = NocoDBMetaClient.get_view.__get__(client)
        client.create_view = NocoDBMetaClient.create_view.__get__(client)
        client.update_view = NocoDBMetaClient.update_view.__get__(client)
        client.delete_view = NocoDBMetaClient.delete_view.__get__(client)
        return client

    def test_list_views(self, meta_client):
        """Test list_views method."""
        expected_views = [
            {"id": "view1", "title": "Grid View", "type": "Grid"},
            {"id": "view2", "title": "Gallery View", "type": "Gallery"}
        ]
        expected_response = {"list": expected_views}
        meta_client._get.return_value = expected_response

        result = meta_client.list_views("table123")

        assert result == expected_views
        meta_client._get.assert_called_once_with("api/v2/meta/tables/table123/views")

    def test_list_views_empty_response(self, meta_client):
        """Test list_views with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_views("table123")

        assert result == []

    def test_get_view(self, meta_client):
        """Test get_view method."""
        expected_view = {
            "id": "view123",
            "title": "Active Users",
            "type": "Grid"
        }
        meta_client._get.return_value = expected_view

        result = meta_client.get_view("view123")

        assert result == expected_view
        meta_client._get.assert_called_once_with("api/v2/meta/views/view123")

    def test_create_view(self, meta_client):
        """Test create_view method."""
        view_data = {
            "title": "New View",
            "type": "Grid",
            "show_system_fields": False
        }
        expected_response = {"id": "view_new", "title": "New View"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_view("table123", view_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/tables/table123/views", data=view_data)

    def test_update_view(self, meta_client):
        """Test update_view method."""
        update_data = {"title": "Updated View"}
        expected_response = {"id": "view123", "title": "Updated View"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_view("view123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/views/view123", data=update_data)

    def test_delete_view(self, meta_client):
        """Test delete_view method."""
        expected_response = {"success": True, "message": "View deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_view("view123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/views/view123")


class TestWebhookOperations:
    """Test webhook operations in meta client."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client with mocked HTTP methods."""
        client = Mock(spec=NocoDBMetaClient)
        client.list_webhooks = NocoDBMetaClient.list_webhooks.__get__(client)
        client.get_webhook = NocoDBMetaClient.get_webhook.__get__(client)
        client.create_webhook = NocoDBMetaClient.create_webhook.__get__(client)
        client.update_webhook = NocoDBMetaClient.update_webhook.__get__(client)
        client.delete_webhook = NocoDBMetaClient.delete_webhook.__get__(client)
        client.test_webhook = NocoDBMetaClient.test_webhook.__get__(client)
        return client

    def test_list_webhooks(self, meta_client):
        """Test list_webhooks method."""
        expected_webhooks = [
            {"id": "hook1", "title": "Slack Notification", "event": "after"},
            {"id": "hook2", "title": "Email Alert", "event": "before"}
        ]
        expected_response = {"list": expected_webhooks}
        meta_client._get.return_value = expected_response

        result = meta_client.list_webhooks("table123")

        assert result == expected_webhooks
        meta_client._get.assert_called_once_with("api/v2/meta/tables/table123/hooks")

    def test_list_webhooks_empty_response(self, meta_client):
        """Test list_webhooks with empty response."""
        meta_client._get.return_value = {"list": None}

        result = meta_client.list_webhooks("table123")

        assert result == []

    def test_get_webhook(self, meta_client):
        """Test get_webhook method."""
        expected_webhook = {
            "id": "hook123",
            "title": "Slack Notification",
            "event": "after",
            "operation": "insert"
        }
        meta_client._get.return_value = expected_webhook

        result = meta_client.get_webhook("hook123")

        assert result == expected_webhook
        meta_client._get.assert_called_once_with("api/v2/meta/hooks/hook123")

    def test_create_webhook(self, meta_client):
        """Test create_webhook method."""
        webhook_data = {
            "title": "Slack Notification",
            "event": "after",
            "operation": "insert",
            "notification": {
                "type": "URL",
                "payload": {
                    "method": "POST",
                    "url": "https://hooks.slack.com/...",
                    "body": "New record: {{title}}"
                }
            },
            "active": True
        }
        expected_response = {"id": "hook_new", "title": "Slack Notification"}
        meta_client._post.return_value = expected_response

        result = meta_client.create_webhook("table123", webhook_data)

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/tables/table123/hooks", data=webhook_data)

    def test_update_webhook(self, meta_client):
        """Test update_webhook method."""
        update_data = {"title": "Updated Webhook", "active": False}
        expected_response = {"id": "hook123", "title": "Updated Webhook"}
        meta_client._patch.return_value = expected_response

        result = meta_client.update_webhook("hook123", update_data)

        assert result == expected_response
        meta_client._patch.assert_called_once_with("api/v2/meta/hooks/hook123", data=update_data)

    def test_delete_webhook(self, meta_client):
        """Test delete_webhook method."""
        expected_response = {"success": True, "message": "Webhook deleted"}
        meta_client._delete.return_value = expected_response

        result = meta_client.delete_webhook("hook123")

        assert result == expected_response
        meta_client._delete.assert_called_once_with("api/v2/meta/hooks/hook123")

    def test_test_webhook(self, meta_client):
        """Test test_webhook method."""
        expected_response = {
            "success": True,
            "status_code": 200,
            "response": "OK"
        }
        meta_client._post.return_value = expected_response

        result = meta_client.test_webhook("hook123")

        assert result == expected_response
        meta_client._post.assert_called_once_with("api/v2/meta/hooks/hook123/test", data={})


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
