"""Tests for NocoDB Webhooks operations based on actual implementation."""

from unittest.mock import Mock, patch
import pytest

from nocodb_simple_client.webhooks import NocoDBWebhooks, TableWebhooks
from nocodb_simple_client.meta_client import NocoDBMetaClient
from nocodb_simple_client.table import NocoDBTable
from nocodb_simple_client.exceptions import NocoDBException, ValidationException


class TestNocoDBWebhooks:
    """Test NocoDBWebhooks functionality."""

    @pytest.fixture
    def meta_client(self):
        """Create mock meta client."""
        return Mock(spec=NocoDBMetaClient)

    @pytest.fixture
    def webhooks(self, meta_client):
        """Create webhooks instance."""
        return NocoDBWebhooks(meta_client)

    def test_webhooks_initialization(self, meta_client):
        """Test webhooks initialization."""
        webhooks = NocoDBWebhooks(meta_client)

        assert webhooks.meta_client == meta_client
        assert hasattr(webhooks, 'EVENT_TYPES')
        assert hasattr(webhooks, 'OPERATION_TYPES')

    def test_get_webhooks(self, webhooks, meta_client):
        """Test get_webhooks method."""
        expected_webhooks = [
            {"id": "webhook_1", "title": "Test Webhook 1"},
            {"id": "webhook_2", "title": "Test Webhook 2"}
        ]
        meta_client.list_webhooks.return_value = expected_webhooks

        result = webhooks.get_webhooks("table_123")

        assert result == expected_webhooks
        meta_client.list_webhooks.assert_called_once_with("table_123")

    def test_get_webhook(self, webhooks, meta_client):
        """Test get_webhook method."""
        expected_webhook = {"id": "webhook_123", "title": "Test Webhook"}
        meta_client.get_webhook.return_value = expected_webhook

        result = webhooks.get_webhook("table_123", "webhook_123")

        assert result == expected_webhook
        meta_client.get_webhook.assert_called_once_with("table_123", "webhook_123")

    def test_create_webhook(self, webhooks, meta_client):
        """Test create_webhook method."""
        webhook_data = {
            "title": "New Webhook",
            "event": "after_insert",
            "notification": {
                "type": "URL",
                "payload": {"method": "POST", "url": "https://example.com/webhook"}
            }
        }
        expected_webhook = {"id": "new_webhook_123", **webhook_data}
        meta_client.create_webhook.return_value = expected_webhook

        result = webhooks.create_webhook("table_123", **webhook_data)

        assert result == expected_webhook
        meta_client.create_webhook.assert_called_once_with("table_123", **webhook_data)

    def test_update_webhook(self, webhooks, meta_client):
        """Test update_webhook method."""
        update_data = {"title": "Updated Webhook"}
        expected_webhook = {"id": "webhook_123", "title": "Updated Webhook"}
        meta_client.update_webhook.return_value = expected_webhook

        result = webhooks.update_webhook("table_123", "webhook_123", **update_data)

        assert result == expected_webhook
        meta_client.update_webhook.assert_called_once_with("table_123", "webhook_123", **update_data)

    def test_delete_webhook(self, webhooks, meta_client):
        """Test delete_webhook method."""
        meta_client.delete_webhook.return_value = True

        result = webhooks.delete_webhook("table_123", "webhook_123")

        assert result is True
        meta_client.delete_webhook.assert_called_once_with("table_123", "webhook_123")

    def test_test_webhook(self, webhooks, meta_client):
        """Test test_webhook method."""
        test_response = {"status": "success", "message": "Webhook test successful"}
        meta_client.test_webhook.return_value = test_response

        result = webhooks.test_webhook("table_123", "webhook_123", {"test": "data"})

        assert result == test_response
        meta_client.test_webhook.assert_called_once_with("table_123", "webhook_123", {"test": "data"})

    def test_get_webhook_logs(self, webhooks, meta_client):
        """Test get_webhook_logs method."""
        expected_logs = [
            {"id": "log_1", "status": "success"},
            {"id": "log_2", "status": "error"}
        ]
        meta_client.get_webhook_logs.return_value = expected_logs

        result = webhooks.get_webhook_logs("table_123", "webhook_123", limit=10)

        assert result == expected_logs
        meta_client.get_webhook_logs.assert_called_once_with("table_123", "webhook_123", limit=10)

    def test_clear_webhook_logs(self, webhooks, meta_client):
        """Test clear_webhook_logs method."""
        meta_client.clear_webhook_logs.return_value = True

        result = webhooks.clear_webhook_logs("table_123", "webhook_123")

        assert result is True
        meta_client.clear_webhook_logs.assert_called_once_with("table_123", "webhook_123")

    def test_create_email_webhook(self, webhooks, meta_client):
        """Test create_email_webhook method."""
        expected_webhook = {"id": "email_webhook_123", "type": "Email"}
        meta_client.create_webhook.return_value = expected_webhook

        result = webhooks.create_email_webhook(
            "table_123", "Email Alert", "after_insert",
            ["user@example.com"], "New Record Created"
        )

        assert result == expected_webhook
        meta_client.create_webhook.assert_called_once()

    def test_create_slack_webhook(self, webhooks, meta_client):
        """Test create_slack_webhook method."""
        expected_webhook = {"id": "slack_webhook_123", "type": "Slack"}
        meta_client.create_webhook.return_value = expected_webhook

        result = webhooks.create_slack_webhook(
            "table_123", "Slack Alert", "after_insert",
            "https://hooks.slack.com/webhook", "#general"
        )

        assert result == expected_webhook
        meta_client.create_webhook.assert_called_once()

    def test_create_teams_webhook(self, webhooks, meta_client):
        """Test create_teams_webhook method."""
        expected_webhook = {"id": "teams_webhook_123", "type": "Teams"}
        meta_client.create_webhook.return_value = expected_webhook

        result = webhooks.create_teams_webhook(
            "table_123", "Teams Alert", "after_insert",
            "https://outlook.office.com/webhook"
        )

        assert result == expected_webhook
        meta_client.create_webhook.assert_called_once()

    def test_toggle_webhook(self, webhooks, meta_client):
        """Test toggle_webhook method."""
        expected_webhook = {"id": "webhook_123", "active": False}
        meta_client.update_webhook.return_value = expected_webhook

        result = webhooks.toggle_webhook("table_123", "webhook_123")

        assert result == expected_webhook
        meta_client.update_webhook.assert_called_once()


class TestTableWebhooks:
    """Test TableWebhooks functionality."""

    @pytest.fixture
    def mock_table(self):
        """Create mock table."""
        table = Mock(spec=NocoDBTable)
        table.table_id = "test_table_123"
        return table

    @pytest.fixture
    def table_webhooks(self, mock_table):
        """Create table webhooks instance."""
        return TableWebhooks(mock_table)

    def test_table_webhooks_initialization(self, mock_table):
        """Test table webhooks initialization."""
        table_webhooks = TableWebhooks(mock_table)

        assert table_webhooks.table == mock_table
        assert table_webhooks.table_id == "test_table_123"

    def test_get_webhooks_table_delegation(self, table_webhooks, mock_table):
        """Test get_webhooks delegation to table's client."""
        expected_webhooks = [{"id": "webhook_1", "title": "Test Webhook"}]

        # Mock the client's webhooks property
        mock_webhooks = Mock()
        mock_webhooks.get_webhooks.return_value = expected_webhooks
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.get_webhooks()

        assert result == expected_webhooks
        mock_webhooks.get_webhooks.assert_called_once_with("test_table_123")

    def test_create_webhook_table_delegation(self, table_webhooks, mock_table):
        """Test create_webhook delegation to table's client."""
        webhook_data = {"title": "New Webhook", "event": "after_insert"}
        expected_webhook = {"id": "new_webhook_123", **webhook_data}

        # Mock the client's webhooks property
        mock_webhooks = Mock()
        mock_webhooks.create_webhook.return_value = expected_webhook
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.create_webhook(**webhook_data)

        assert result == expected_webhook
        mock_webhooks.create_webhook.assert_called_once_with("test_table_123", **webhook_data)

    def test_delete_webhook_table_delegation(self, table_webhooks, mock_table):
        """Test delete_webhook delegation to table's client."""
        mock_webhooks = Mock()
        mock_webhooks.delete_webhook.return_value = True
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.delete_webhook("webhook_123")

        assert result is True
        mock_webhooks.delete_webhook.assert_called_once_with("test_table_123", "webhook_123")

    def test_test_webhook_table_delegation(self, table_webhooks, mock_table):
        """Test test_webhook delegation to table's client."""
        test_data = {"test": "payload"}
        expected_response = {"status": "success"}

        mock_webhooks = Mock()
        mock_webhooks.test_webhook.return_value = expected_response
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.test_webhook("webhook_123", test_data)

        assert result == expected_response
        mock_webhooks.test_webhook.assert_called_once_with("test_table_123", "webhook_123", test_data)

    def test_get_webhook_logs_table_delegation(self, table_webhooks, mock_table):
        """Test get_webhook_logs delegation to table's client."""
        expected_logs = [{"id": "log_1", "status": "success"}]

        mock_webhooks = Mock()
        mock_webhooks.get_webhook_logs.return_value = expected_logs
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.get_webhook_logs("webhook_123", limit=5)

        assert result == expected_logs
        mock_webhooks.get_webhook_logs.assert_called_once_with("test_table_123", "webhook_123", limit=5)

    def test_toggle_webhook_table_delegation(self, table_webhooks, mock_table):
        """Test toggle_webhook delegation to table's client."""
        expected_webhook = {"id": "webhook_123", "active": False}

        mock_webhooks = Mock()
        mock_webhooks.toggle_webhook.return_value = expected_webhook
        mock_table.client.webhooks = mock_webhooks

        result = table_webhooks.toggle_webhook("webhook_123")

        assert result == expected_webhook
        mock_webhooks.toggle_webhook.assert_called_once_with("test_table_123", "webhook_123")


class TestWebhookConstants:
    """Test webhook constants and utilities."""

    def test_event_types_constant(self):
        """Test EVENT_TYPES constant."""
        webhooks = NocoDBWebhooks(Mock())

        assert "after_insert" in webhooks.EVENT_TYPES
        assert "after_update" in webhooks.EVENT_TYPES
        assert "after_delete" in webhooks.EVENT_TYPES
        assert "before_insert" in webhooks.EVENT_TYPES
        assert "before_update" in webhooks.EVENT_TYPES
        assert "before_delete" in webhooks.EVENT_TYPES

    def test_operation_types_constant(self):
        """Test OPERATION_TYPES constant."""
        webhooks = NocoDBWebhooks(Mock())

        assert "insert" in webhooks.OPERATION_TYPES
        assert "update" in webhooks.OPERATION_TYPES
        assert "delete" in webhooks.OPERATION_TYPES
