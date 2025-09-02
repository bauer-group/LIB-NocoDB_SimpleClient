"""Tests for NocoDB Meta Client operations based on actual implementation."""

from unittest.mock import Mock, patch
import pytest

from nocodb_simple_client.meta_client import NocoDBMetaClient
from nocodb_simple_client.exceptions import NocoDBException, ValidationException


class TestNocoDBMetaClientInitialization:
    """Test NocoDBMetaClient initialization."""

    def test_meta_client_initialization(self):
        """Test meta client initialization."""
        meta_client = NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

        assert meta_client._base_url == "https://app.nocodb.com"
        assert meta_client.headers["xc-token"] == "test_token"
        # Verify it inherits from NocoDBClient
        assert hasattr(meta_client, 'get_records')
        assert hasattr(meta_client, 'insert_record')

    def test_meta_client_with_access_protection(self):
        """Test meta client initialization with access protection."""
        meta_client = NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token",
            access_protection_auth="protection_value",
            access_protection_header="X-Custom-Auth"
        )

        assert meta_client.headers["xc-token"] == "test_token"
        assert meta_client.headers["X-Custom-Auth"] == "protection_value"


class TestTableOperations:
    """Test table metadata operations."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_list_tables(self, meta_client):
        """Test list_tables operation."""
        expected_tables = [
            {"id": "table_1", "title": "Users", "table_name": "users"},
            {"id": "table_2", "title": "Orders", "table_name": "orders"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_tables

            result = meta_client.list_tables("base_123")

            assert result == expected_tables
            mock_get.assert_called_once_with("api/v1/db/meta/projects/base_123/tables")

    def test_get_table_info(self, meta_client):
        """Test get_table_info operation."""
        expected_table = {"id": "table_123", "title": "Users", "columns": []}

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_table

            result = meta_client.get_table_info("table_123")

            assert result == expected_table
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123")

    def test_create_table(self, meta_client):
        """Test create_table operation."""
        table_data = {
            "title": "New Table",
            "table_name": "new_table",
            "columns": [
                {"title": "ID", "column_name": "id", "uidt": "ID"},
                {"title": "Name", "column_name": "name", "uidt": "SingleLineText"}
            ]
        }
        expected_table = {"id": "new_table_123", **table_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_table

            result = meta_client.create_table("base_123", table_data)

            assert result == expected_table
            mock_post.assert_called_once_with("api/v1/db/meta/projects/base_123/tables", data=table_data)

    def test_update_table(self, meta_client):
        """Test update_table operation."""
        table_data = {"title": "Updated Table"}
        expected_table = {"id": "table_123", "title": "Updated Table"}

        with patch.object(meta_client, '_patch') as mock_patch:
            mock_patch.return_value = expected_table

            result = meta_client.update_table("table_123", table_data)

            assert result == expected_table
            mock_patch.assert_called_once_with("api/v1/db/meta/tables/table_123", data=table_data)

    def test_delete_table(self, meta_client):
        """Test delete_table operation."""
        expected_response = {"msg": "Table deleted successfully"}

        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.return_value = expected_response

            result = meta_client.delete_table("table_123")

            assert result == expected_response
            mock_delete.assert_called_once_with("api/v1/db/meta/tables/table_123")


class TestColumnOperations:
    """Test column metadata operations."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_list_columns(self, meta_client):
        """Test list_columns operation."""
        expected_columns = [
            {"id": "col_1", "title": "ID", "column_name": "id", "uidt": "ID"},
            {"id": "col_2", "title": "Name", "column_name": "name", "uidt": "SingleLineText"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_columns

            result = meta_client.list_columns("table_123")

            assert result == expected_columns
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/columns")

    def test_create_column(self, meta_client):
        """Test create_column operation."""
        column_data = {
            "title": "Email",
            "column_name": "email",
            "uidt": "Email"
        }
        expected_column = {"id": "col_123", **column_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_column

            result = meta_client.create_column("table_123", column_data)

            assert result == expected_column
            mock_post.assert_called_once_with("api/v1/db/meta/tables/table_123/columns", data=column_data)

    def test_update_column(self, meta_client):
        """Test update_column operation."""
        column_data = {"title": "Updated Email"}
        expected_column = {"id": "col_123", "title": "Updated Email"}

        with patch.object(meta_client, '_patch') as mock_patch:
            mock_patch.return_value = expected_column

            result = meta_client.update_column("col_123", column_data)

            assert result == expected_column
            mock_patch.assert_called_once_with("api/v1/db/meta/columns/col_123", data=column_data)

    def test_delete_column(self, meta_client):
        """Test delete_column operation."""
        expected_response = {"msg": "Column deleted successfully"}

        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.return_value = expected_response

            result = meta_client.delete_column("col_123")

            assert result == expected_response
            mock_delete.assert_called_once_with("api/v1/db/meta/columns/col_123")


class TestViewOperations:
    """Test view metadata operations."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_list_views(self, meta_client):
        """Test list_views operation."""
        expected_views = [
            {"id": "view_1", "title": "Grid View", "type": "Grid"},
            {"id": "view_2", "title": "Gallery View", "type": "Gallery"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_views

            result = meta_client.list_views("table_123")

            assert result == expected_views
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/views")

    def test_get_view(self, meta_client):
        """Test get_view operation."""
        expected_view = {"id": "view_123", "title": "Test View", "type": "Grid"}

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_view

            result = meta_client.get_view("table_123", "view_123")

            assert result == expected_view
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123")

    def test_create_view(self, meta_client):
        """Test create_view operation."""
        view_data = {
            "title": "New View",
            "type": "Grid"
        }
        expected_view = {"id": "view_123", **view_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_view

            result = meta_client.create_view("table_123", view_data)

            assert result == expected_view
            mock_post.assert_called_once_with("api/v1/db/meta/tables/table_123/views", data=view_data)

    def test_update_view(self, meta_client):
        """Test update_view operation."""
        view_data = {"title": "Updated View"}
        expected_view = {"id": "view_123", "title": "Updated View"}

        with patch.object(meta_client, '_patch') as mock_patch:
            mock_patch.return_value = expected_view

            result = meta_client.update_view("table_123", "view_123", view_data)

            assert result == expected_view
            mock_patch.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123", data=view_data)

    def test_delete_view(self, meta_client):
        """Test delete_view operation."""
        expected_response = {"msg": "View deleted successfully"}

        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.return_value = expected_response

            result = meta_client.delete_view("table_123", "view_123")

            assert result == expected_response
            mock_delete.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123")

    def test_get_view_records(self, meta_client):
        """Test get_view_records operation."""
        expected_data = {
            "list": [{"Id": "1", "Name": "Record 1"}],
            "pageInfo": {"totalRows": 1}
        }

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_data

            result = meta_client.get_view_records("table_123", "view_123", limit=10)

            assert result == expected_data
            mock_get.assert_called_once()


class TestWebhookOperations:
    """Test webhook metadata operations."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_list_webhooks(self, meta_client):
        """Test list_webhooks operation."""
        expected_webhooks = [
            {"id": "hook_1", "title": "User Created Hook", "event": "after_insert"},
            {"id": "hook_2", "title": "User Updated Hook", "event": "after_update"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_webhooks

            result = meta_client.list_webhooks("table_123")

            assert result == expected_webhooks
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks")

    def test_get_webhook(self, meta_client):
        """Test get_webhook operation."""
        expected_webhook = {"id": "hook_123", "title": "Test Hook", "active": True}

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_webhook

            result = meta_client.get_webhook("table_123", "hook_123")

            assert result == expected_webhook
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks/hook_123")

    def test_create_webhook(self, meta_client):
        """Test create_webhook operation."""
        webhook_data = {
            "title": "New Hook",
            "event": "after_insert",
            "notification": {
                "type": "URL",
                "payload": {"method": "POST", "url": "https://example.com/webhook"}
            }
        }
        expected_webhook = {"id": "hook_123", **webhook_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_webhook

            result = meta_client.create_webhook("table_123", **webhook_data)

            assert result == expected_webhook
            mock_post.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks", data=webhook_data)

    def test_update_webhook(self, meta_client):
        """Test update_webhook operation."""
        webhook_data = {"title": "Updated Hook", "active": False}
        expected_webhook = {"id": "hook_123", **webhook_data}

        with patch.object(meta_client, '_patch') as mock_patch:
            mock_patch.return_value = expected_webhook

            result = meta_client.update_webhook("table_123", "hook_123", **webhook_data)

            assert result == expected_webhook
            mock_patch.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks/hook_123", data=webhook_data)

    def test_delete_webhook(self, meta_client):
        """Test delete_webhook operation."""
        expected_response = True

        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.return_value = {"msg": "Hook deleted"}

            result = meta_client.delete_webhook("table_123", "hook_123")

            assert result is True
            mock_delete.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks/hook_123")

    def test_test_webhook(self, meta_client):
        """Test test_webhook operation."""
        test_data = {"sample": "data"}
        expected_response = {"status": "success", "message": "Hook tested successfully"}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_response

            result = meta_client.test_webhook("table_123", "hook_123", test_data)

            assert result == expected_response
            mock_post.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks/hook_123/test", data=test_data)

    def test_get_webhook_logs(self, meta_client):
        """Test get_webhook_logs operation."""
        expected_logs = [
            {"id": "log_1", "response": "success", "triggered": "2023-01-01T12:00:00Z"},
            {"id": "log_2", "response": "error", "triggered": "2023-01-01T12:05:00Z"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_logs

            result = meta_client.get_webhook_logs("table_123", "hook_123", limit=10)

            assert result == expected_logs
            mock_get.assert_called_once()

    def test_clear_webhook_logs(self, meta_client):
        """Test clear_webhook_logs operation."""
        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.return_value = {"msg": "Logs cleared"}

            result = meta_client.clear_webhook_logs("table_123", "hook_123")

            assert result is True
            mock_delete.assert_called_once_with("api/v1/db/meta/tables/table_123/hooks/hook_123/logs")


class TestViewFiltersAndSorts:
    """Test view filter and sort metadata operations."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_get_view_columns(self, meta_client):
        """Test get_view_columns operation."""
        expected_columns = [
            {"id": "vcol_1", "fk_column_id": "col_1", "show": True, "width": 200},
            {"id": "vcol_2", "fk_column_id": "col_2", "show": False, "width": 150}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_columns

            result = meta_client.get_view_columns("table_123", "view_123")

            assert result == expected_columns
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123/columns")

    def test_update_view_column(self, meta_client):
        """Test update_view_column operation."""
        column_data = {"show": False, "width": 300}
        expected_column = {"id": "vcol_123", **column_data}

        with patch.object(meta_client, '_patch') as mock_patch:
            mock_patch.return_value = expected_column

            result = meta_client.update_view_column("table_123", "view_123", "vcol_123", **column_data)

            assert result == expected_column
            mock_patch.assert_called_once_with(
                "api/v1/db/meta/tables/table_123/views/view_123/columns/vcol_123", data=column_data
            )

    def test_get_view_filters(self, meta_client):
        """Test get_view_filters operation."""
        expected_filters = [
            {"id": "filter_1", "fk_column_id": "col_1", "comparison_op": "eq", "value": "active"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_filters

            result = meta_client.get_view_filters("table_123", "view_123")

            assert result == expected_filters
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123/filters")

    def test_create_view_filter(self, meta_client):
        """Test create_view_filter operation."""
        filter_data = {
            "fk_column_id": "col_123",
            "comparison_op": "eq",
            "value": "test"
        }
        expected_filter = {"id": "filter_123", **filter_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_filter

            result = meta_client.create_view_filter("table_123", "view_123", **filter_data)

            assert result == expected_filter
            mock_post.assert_called_once_with(
                "api/v1/db/meta/tables/table_123/views/view_123/filters", data=filter_data
            )

    def test_get_view_sorts(self, meta_client):
        """Test get_view_sorts operation."""
        expected_sorts = [
            {"id": "sort_1", "fk_column_id": "col_1", "direction": "asc"}
        ]

        with patch.object(meta_client, '_get') as mock_get:
            mock_get.return_value = expected_sorts

            result = meta_client.get_view_sorts("table_123", "view_123")

            assert result == expected_sorts
            mock_get.assert_called_once_with("api/v1/db/meta/tables/table_123/views/view_123/sorts")

    def test_create_view_sort(self, meta_client):
        """Test create_view_sort operation."""
        sort_data = {
            "fk_column_id": "col_123",
            "direction": "desc"
        }
        expected_sort = {"id": "sort_123", **sort_data}

        with patch.object(meta_client, '_post') as mock_post:
            mock_post.return_value = expected_sort

            result = meta_client.create_view_sort("table_123", "view_123", **sort_data)

            assert result == expected_sort
            mock_post.assert_called_once_with(
                "api/v1/db/meta/tables/table_123/views/view_123/sorts", data=sort_data
            )


class TestMetaClientUtilities:
    """Test meta client utility methods."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_meta_client_inherits_from_client(self, meta_client):
        """Test that meta client inherits all client functionality."""
        # Should have all base client methods
        assert hasattr(meta_client, 'get_records')
        assert hasattr(meta_client, 'insert_record')
        assert hasattr(meta_client, 'update_record')
        assert hasattr(meta_client, 'delete_record')
        assert hasattr(meta_client, 'bulk_insert_records')

    def test_meta_client_additional_methods(self, meta_client):
        """Test that meta client has additional meta methods."""
        # Should have meta-specific methods
        assert hasattr(meta_client, 'list_tables')
        assert hasattr(meta_client, 'create_table')
        assert hasattr(meta_client, 'list_columns')
        assert hasattr(meta_client, 'create_column')
        assert hasattr(meta_client, 'list_views')
        assert hasattr(meta_client, 'create_view')
        assert hasattr(meta_client, 'list_webhooks')
        assert hasattr(meta_client, 'create_webhook')

    def test_meta_client_close(self, meta_client):
        """Test meta client close method."""
        # Should not raise any exceptions (inherited from base client)
        meta_client.close()


class TestMetaClientErrorHandling:
    """Test meta client error handling."""

    @pytest.fixture
    def meta_client(self):
        """Create meta client for testing."""
        return NocoDBMetaClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_create_table_validation_error(self, meta_client):
        """Test create_table with validation error."""
        with patch.object(meta_client, '_post') as mock_post:
            mock_post.side_effect = ValidationException("Invalid table structure")

            with pytest.raises(ValidationException, match="Invalid table structure"):
                meta_client.create_table("base_123", {"title": ""})

    def test_delete_table_not_found_error(self, meta_client):
        """Test delete_table with table not found error."""
        with patch.object(meta_client, '_delete') as mock_delete:
            mock_delete.side_effect = NocoDBException("TABLE_NOT_FOUND", "Table not found")

            with pytest.raises(NocoDBException, match="Table not found"):
                meta_client.delete_table("nonexistent_table")

    def test_webhook_operation_error(self, meta_client):
        """Test webhook operation with API error."""
        with patch.object(meta_client, '_post') as mock_post:
            mock_post.side_effect = NocoDBException("WEBHOOK_ERROR", "Failed to create webhook")

            with pytest.raises(NocoDBException, match="Failed to create webhook"):
                meta_client.create_webhook("table_123", title="Test Hook", event="after_insert")
