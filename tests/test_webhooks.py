"""Tests for webhooks and automation functionality."""

from unittest.mock import Mock

import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.exceptions import NocoDBException
from nocodb_simple_client.webhooks import NocoDBWebhooks, TableWebhooks


class TestNocoDBWebhooks:
    """Test NocoDBWebhooks class functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def webhooks_manager(self, mock_client):
        """Create a webhooks manager instance for testing."""
        return NocoDBWebhooks(mock_client)

    def test_get_webhooks_success(self, mock_client, webhooks_manager):
        """Test successful retrieval of webhooks."""
        # Arrange
        table_id = "table1"
        expected_webhooks = [
            {
                "id": "hook1",
                "title": "User Registration Hook",
                "event": "after",
                "operation": "insert",
                "active": True,
            },
            {
                "id": "hook2",
                "title": "Email Notification Hook",
                "event": "after",
                "operation": "update",
                "active": False,
            },
        ]

        mock_client._get.return_value = {"list": expected_webhooks}

        # Act
        result = webhooks_manager.get_webhooks(table_id)

        # Assert
        assert result == expected_webhooks
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/hooks")

    def test_get_webhook_success(self, mock_client, webhooks_manager):
        """Test successful retrieval of a single webhook."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"
        expected_webhook = {
            "id": webhook_id,
            "title": "User Registration Hook",
            "event": "after",
            "operation": "insert",
            "notification": {
                "type": "URL",
                "payload": {"method": "POST", "url": "https://api.example.com/webhook"},
            },
            "active": True,
        }

        mock_client._get.return_value = expected_webhook

        # Act
        result = webhooks_manager.get_webhook(table_id, webhook_id)

        # Assert
        assert result == expected_webhook
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/hooks/{webhook_id}")

    def test_create_webhook_success(self, mock_client, webhooks_manager):
        """Test successful webhook creation."""
        # Arrange
        table_id = "table1"
        title = "New User Webhook"
        event_type = "after"
        operation = "insert"
        url = "https://api.example.com/new-user"
        method = "POST"
        headers = {"Authorization": "Bearer token"}
        body = '{"message": "New user created"}'

        expected_webhook = {
            "id": "new_hook_id",
            "title": title,
            "event": event_type,
            "operation": operation,
            "active": True,
        }

        mock_client._post.return_value = expected_webhook

        # Act
        result = webhooks_manager.create_webhook(
            table_id, title, event_type, operation, url, method, headers, body
        )

        # Assert
        assert result == expected_webhook
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/hooks" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == title
        assert data["event"] == event_type
        assert data["operation"] == operation
        assert data["notification"]["type"] == "URL"
        assert data["notification"]["payload"]["method"] == method
        assert data["notification"]["payload"]["url"] == url
        assert data["notification"]["payload"]["headers"] == headers
        assert data["notification"]["payload"]["body"] == body
        assert data["active"] is True

    def test_create_webhook_invalid_event_type(self, mock_client, webhooks_manager):
        """Test creating webhook with invalid event type."""
        # Arrange
        table_id = "table1"
        title = "Test Hook"
        invalid_event_type = "invalid_event"
        operation = "insert"
        url = "https://example.com"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid event_type"):
            webhooks_manager.create_webhook(table_id, title, invalid_event_type, operation, url)

    def test_create_webhook_invalid_operation(self, mock_client, webhooks_manager):
        """Test creating webhook with invalid operation."""
        # Arrange
        table_id = "table1"
        title = "Test Hook"
        event_type = "after"
        invalid_operation = "invalid_op"
        url = "https://example.com"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid operation"):
            webhooks_manager.create_webhook(table_id, title, event_type, invalid_operation, url)

    def test_create_webhook_invalid_http_method(self, mock_client, webhooks_manager):
        """Test creating webhook with invalid HTTP method."""
        # Arrange
        table_id = "table1"
        title = "Test Hook"
        event_type = "after"
        operation = "insert"
        url = "https://example.com"
        invalid_method = "INVALID"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid HTTP method"):
            webhooks_manager.create_webhook(
                table_id, title, event_type, operation, url, invalid_method
            )

    def test_update_webhook_success(self, mock_client, webhooks_manager):
        """Test successful webhook update."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"
        new_title = "Updated Webhook"
        new_url = "https://api.example.com/updated"
        new_headers = {"X-API-Key": "new_key"}

        expected_webhook = {"id": webhook_id, "title": new_title, "active": True}

        mock_client._patch.return_value = expected_webhook

        # Act
        result = webhooks_manager.update_webhook(
            table_id, webhook_id, title=new_title, url=new_url, headers=new_headers
        )

        # Assert
        assert result == expected_webhook
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/hooks/{webhook_id}" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == new_title
        assert data["notification"]["payload"]["url"] == new_url
        assert data["notification"]["payload"]["headers"] == new_headers

    def test_update_webhook_no_changes(self, mock_client, webhooks_manager):
        """Test updating webhook with no changes raises ValueError."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        # Act & Assert
        with pytest.raises(ValueError, match="At least one parameter must be provided"):
            webhooks_manager.update_webhook(table_id, webhook_id)

    def test_delete_webhook_success(self, mock_client, webhooks_manager):
        """Test successful webhook deletion."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = webhooks_manager.delete_webhook(table_id, webhook_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(f"api/v2/tables/{table_id}/hooks/{webhook_id}")

    def test_test_webhook_success(self, mock_client, webhooks_manager):
        """Test webhook testing functionality."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"
        sample_data = {"name": "Test User", "email": "test@example.com"}

        expected_result = {"success": True, "status_code": 200, "response": "OK"}

        mock_client._post.return_value = expected_result

        # Act
        result = webhooks_manager.test_webhook(table_id, webhook_id, sample_data)

        # Assert
        assert result == expected_result
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/hooks/{webhook_id}/test" in call_args[0][0]
        assert call_args[1]["data"]["data"] == sample_data

    def test_test_webhook_without_data(self, mock_client, webhooks_manager):
        """Test webhook testing without sample data."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        expected_result = {"success": True}
        mock_client._post.return_value = expected_result

        # Act
        result = webhooks_manager.test_webhook(table_id, webhook_id)

        # Assert
        assert result == expected_result
        call_args = mock_client._post.call_args
        assert call_args[1]["data"] == {}

    def test_get_webhook_logs_success(self, mock_client, webhooks_manager):
        """Test getting webhook execution logs."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"
        limit = 50
        offset = 10

        expected_logs = [
            {
                "id": "log1",
                "timestamp": "2023-12-01T10:00:00Z",
                "status": "success",
                "response_code": 200,
            },
            {
                "id": "log2",
                "timestamp": "2023-12-01T09:30:00Z",
                "status": "failed",
                "response_code": 500,
            },
        ]

        mock_client._get.return_value = {"list": expected_logs}

        # Act
        result = webhooks_manager.get_webhook_logs(table_id, webhook_id, limit, offset)

        # Assert
        assert result == expected_logs
        mock_client._get.assert_called_once()
        call_args = mock_client._get.call_args
        assert f"api/v2/tables/{table_id}/hooks/{webhook_id}/logs" in call_args[0][0]

        params = call_args[1]["params"]
        assert params["limit"] == limit
        assert params["offset"] == offset

    def test_clear_webhook_logs_success(self, mock_client, webhooks_manager):
        """Test clearing webhook logs."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = webhooks_manager.clear_webhook_logs(table_id, webhook_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(
            f"api/v2/tables/{table_id}/hooks/{webhook_id}/logs"
        )

    def test_create_email_webhook_success(self, mock_client, webhooks_manager):
        """Test creating an email webhook."""
        # Arrange
        table_id = "table1"
        title = "Email Notification"
        event_type = "after"
        operation = "insert"
        emails = ["admin@example.com", "manager@example.com"]
        subject = "New record created"
        body = "A new record has been created in the system."

        expected_webhook = {
            "id": "email_hook_id",
            "title": title,
            "event": event_type,
            "operation": operation,
        }

        mock_client._post.return_value = expected_webhook

        # Act
        result = webhooks_manager.create_email_webhook(
            table_id, title, event_type, operation, emails, subject, body
        )

        # Assert
        assert result == expected_webhook
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args

        data = call_args[1]["data"]
        assert data["notification"]["type"] == "Email"
        assert data["notification"]["payload"]["emails"] == "admin@example.com,manager@example.com"
        assert data["notification"]["payload"]["subject"] == subject
        assert data["notification"]["payload"]["body"] == body

    def test_create_email_webhook_invalid_emails(self, mock_client, webhooks_manager):
        """Test creating email webhook with invalid emails list."""
        # Arrange
        table_id = "table1"
        title = "Email Hook"
        event_type = "after"
        operation = "insert"
        invalid_emails = "not_a_list"  # Should be a list
        subject = "Test"
        body = "Test body"

        # Act & Assert
        with pytest.raises(ValueError, match="emails must be a non-empty list"):
            webhooks_manager.create_email_webhook(
                table_id, title, event_type, operation, invalid_emails, subject, body
            )

    def test_create_slack_webhook_success(self, mock_client, webhooks_manager):
        """Test creating a Slack webhook."""
        # Arrange
        table_id = "table1"
        title = "Slack Notification"
        event_type = "after"
        operation = "update"
        webhook_url = (
            "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        )
        message = "Record has been updated!"

        expected_webhook = {
            "id": "slack_hook_id",
            "title": title,
            "event": event_type,
            "operation": operation,
        }

        mock_client._post.return_value = expected_webhook

        # Act
        result = webhooks_manager.create_slack_webhook(
            table_id, title, event_type, operation, webhook_url, message
        )

        # Assert
        assert result == expected_webhook
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args

        data = call_args[1]["data"]
        assert data["notification"]["type"] == "Slack"
        assert data["notification"]["payload"]["webhook_url"] == webhook_url
        assert data["notification"]["payload"]["message"] == message

    def test_create_teams_webhook_success(self, mock_client, webhooks_manager):
        """Test creating a Microsoft Teams webhook."""
        # Arrange
        table_id = "table1"
        title = "Teams Notification"
        event_type = "before"
        operation = "delete"
        webhook_url = "https://outlook.office.com/webhook/..."
        message = "Record is about to be deleted!"

        expected_webhook = {
            "id": "teams_hook_id",
            "title": title,
            "event": event_type,
            "operation": operation,
        }

        mock_client._post.return_value = expected_webhook

        # Act
        result = webhooks_manager.create_teams_webhook(
            table_id, title, event_type, operation, webhook_url, message
        )

        # Assert
        assert result == expected_webhook
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args

        data = call_args[1]["data"]
        assert data["notification"]["type"] == "MicrosoftTeams"
        assert data["notification"]["payload"]["webhook_url"] == webhook_url
        assert data["notification"]["payload"]["message"] == message

    def test_toggle_webhook_success(self, mock_client, webhooks_manager):
        """Test toggling webhook active status."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        # Mock current webhook state (active)
        current_webhook = {"id": webhook_id, "title": "Test Hook", "active": True}

        # Mock updated webhook state (inactive)
        updated_webhook = {"id": webhook_id, "title": "Test Hook", "active": False}

        mock_client._get.return_value = current_webhook
        mock_client._patch.return_value = updated_webhook

        # Act
        result = webhooks_manager.toggle_webhook(table_id, webhook_id)

        # Assert
        assert result == updated_webhook
        mock_client._get.assert_called_once()  # Get current state
        mock_client._patch.assert_called_once()  # Update with opposite state

        patch_call_args = mock_client._patch.call_args
        assert patch_call_args[1]["data"]["active"] is False


class TestTableWebhooks:
    """Test TableWebhooks helper class."""

    @pytest.fixture
    def mock_webhooks_manager(self):
        """Create a mock webhooks manager."""
        return Mock(spec=NocoDBWebhooks)

    @pytest.fixture
    def table_webhooks(self, mock_webhooks_manager):
        """Create a table webhooks instance."""
        return TableWebhooks(mock_webhooks_manager, "test_table_id")

    def test_get_webhooks_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that get_webhooks delegates to webhooks manager."""
        # Arrange
        expected_webhooks = [{"id": "hook1", "title": "Test Hook"}]
        mock_webhooks_manager.get_webhooks.return_value = expected_webhooks

        # Act
        result = table_webhooks.get_webhooks()

        # Assert
        assert result == expected_webhooks
        mock_webhooks_manager.get_webhooks.assert_called_once_with("test_table_id")

    def test_get_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that get_webhook delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        expected_webhook = {"id": webhook_id, "title": "Test Hook"}
        mock_webhooks_manager.get_webhook.return_value = expected_webhook

        # Act
        result = table_webhooks.get_webhook(webhook_id)

        # Assert
        assert result == expected_webhook
        mock_webhooks_manager.get_webhook.assert_called_once_with("test_table_id", webhook_id)

    def test_create_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that create_webhook delegates to webhooks manager."""
        # Arrange
        title = "New Hook"
        event_type = "after"
        operation = "insert"
        url = "https://example.com"
        expected_webhook = {"id": "new_hook", "title": title}

        mock_webhooks_manager.create_webhook.return_value = expected_webhook

        # Act
        result = table_webhooks.create_webhook(title, event_type, operation, url)

        # Assert
        assert result == expected_webhook
        mock_webhooks_manager.create_webhook.assert_called_once_with(
            "test_table_id", title, event_type, operation, url
        )

    def test_create_webhook_with_kwargs(self, mock_webhooks_manager, table_webhooks):
        """Test create_webhook passes kwargs correctly."""
        # Arrange
        title = "New Hook"
        event_type = "after"
        operation = "insert"
        url = "https://example.com"
        method = "PUT"
        headers = {"Auth": "token"}

        expected_webhook = {"id": "new_hook", "title": title}
        mock_webhooks_manager.create_webhook.return_value = expected_webhook

        # Act
        result = table_webhooks.create_webhook(
            title, event_type, operation, url, method=method, headers=headers
        )

        # Assert
        assert result == expected_webhook
        mock_webhooks_manager.create_webhook.assert_called_once_with(
            "test_table_id", title, event_type, operation, url, method=method, headers=headers
        )

    def test_update_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that update_webhook delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        title = "Updated Hook"
        expected_webhook = {"id": webhook_id, "title": title}

        mock_webhooks_manager.update_webhook.return_value = expected_webhook

        # Act
        result = table_webhooks.update_webhook(webhook_id, title=title)

        # Assert
        assert result == expected_webhook
        mock_webhooks_manager.update_webhook.assert_called_once_with(
            "test_table_id", webhook_id, title=title
        )

    def test_delete_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that delete_webhook delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        mock_webhooks_manager.delete_webhook.return_value = True

        # Act
        result = table_webhooks.delete_webhook(webhook_id)

        # Assert
        assert result is True
        mock_webhooks_manager.delete_webhook.assert_called_once_with("test_table_id", webhook_id)

    def test_test_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that test_webhook delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        sample_data = {"test": "data"}
        expected_result = {"success": True}

        mock_webhooks_manager.test_webhook.return_value = expected_result

        # Act
        result = table_webhooks.test_webhook(webhook_id, sample_data)

        # Assert
        assert result == expected_result
        mock_webhooks_manager.test_webhook.assert_called_once_with(
            "test_table_id", webhook_id, sample_data
        )

    def test_get_webhook_logs_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that get_webhook_logs delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        limit = 100
        offset = 20
        expected_logs = [{"id": "log1"}]

        mock_webhooks_manager.get_webhook_logs.return_value = expected_logs

        # Act
        result = table_webhooks.get_webhook_logs(webhook_id, limit, offset)

        # Assert
        assert result == expected_logs
        mock_webhooks_manager.get_webhook_logs.assert_called_once_with(
            "test_table_id", webhook_id, limit, offset
        )

    def test_toggle_webhook_delegates(self, mock_webhooks_manager, table_webhooks):
        """Test that toggle_webhook delegates to webhooks manager."""
        # Arrange
        webhook_id = "hook1"
        expected_webhook = {"id": webhook_id, "active": False}

        mock_webhooks_manager.toggle_webhook.return_value = expected_webhook

        # Act
        result = table_webhooks.toggle_webhook(webhook_id)

        # Assert
        assert result == expected_webhook
        mock_webhooks_manager.toggle_webhook.assert_called_once_with("test_table_id", webhook_id)


class TestWebhooksIntegration:
    """Integration tests for webhooks functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with realistic responses."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def webhooks_manager(self, mock_client):
        """Create webhooks manager with mock client."""
        return NocoDBWebhooks(mock_client)

    def test_complete_webhook_lifecycle(self, mock_client, webhooks_manager):
        """Test complete webhook lifecycle: create, test, update, delete."""
        # Arrange
        table_id = "users_table"

        # Mock responses for the workflow
        created_webhook = {
            "id": "webhook_123",
            "title": "User Registration Hook",
            "event": "after",
            "operation": "insert",
            "active": True,
        }

        test_result = {
            "success": True,
            "status_code": 200,
            "response": "Webhook received successfully",
        }

        updated_webhook = {"id": "webhook_123", "title": "Updated User Hook", "active": True}

        mock_client._post.side_effect = [created_webhook, test_result]
        mock_client._patch.return_value = updated_webhook
        mock_client._delete.return_value = {"success": True}

        # Act - Complete workflow
        # 1. Create webhook
        webhook = webhooks_manager.create_webhook(
            table_id,
            "User Registration Hook",
            "after",
            "insert",
            "https://api.example.com/user-registered",
            "POST",
        )

        # 2. Test webhook
        test_response = webhooks_manager.test_webhook(
            table_id, webhook["id"], {"name": "John Doe", "email": "john@example.com"}
        )

        # 3. Update webhook
        updated = webhooks_manager.update_webhook(
            table_id, webhook["id"], title="Updated User Hook"
        )

        # 4. Delete webhook
        deleted = webhooks_manager.delete_webhook(table_id, webhook["id"])

        # Assert
        assert webhook["title"] == "User Registration Hook"
        assert webhook["event"] == "after"
        assert webhook["operation"] == "insert"

        assert test_response["success"] is True
        assert test_response["status_code"] == 200

        assert updated["title"] == "Updated User Hook"

        assert deleted is True

        # Verify all calls were made
        assert mock_client._post.call_count == 2  # create + test
        assert mock_client._patch.call_count == 1  # update
        assert mock_client._delete.call_count == 1  # delete

    def test_webhook_condition_handling(self, mock_client, webhooks_manager):
        """Test webhook creation with conditions."""
        # Arrange
        table_id = "orders_table"
        condition = {"field": "total_amount", "operator": "gt", "value": 1000}

        expected_webhook = {
            "id": "conditional_hook",
            "title": "High Value Order Hook",
            "condition": condition,
        }

        mock_client._post.return_value = expected_webhook

        # Act
        result = webhooks_manager.create_webhook(
            table_id,
            "High Value Order Hook",
            "after",
            "insert",
            "https://api.example.com/high-value-order",
            condition=condition,
        )

        # Assert
        assert result == expected_webhook
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["condition"] == condition


class TestWebhooksErrorHandling:
    """Test error handling in webhooks functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        return Mock(spec=NocoDBClient)

    @pytest.fixture
    def webhooks_manager(self, mock_client):
        """Create webhooks manager."""
        return NocoDBWebhooks(mock_client)

    def test_webhook_creation_api_error(self, mock_client, webhooks_manager):
        """Test webhook creation with API error."""
        # Arrange
        table_id = "table1"
        mock_client._post.side_effect = NocoDBException("API Error")

        # Act & Assert
        with pytest.raises(NocoDBException):
            webhooks_manager.create_webhook(
                table_id, "Test Hook", "after", "insert", "https://example.com"
            )

    def test_webhook_test_failure(self, mock_client, webhooks_manager):
        """Test webhook test failure handling."""
        # Arrange
        table_id = "table1"
        webhook_id = "hook1"

        error_response = {
            "success": False,
            "status_code": 500,
            "error": "Webhook endpoint unreachable",
        }

        mock_client._post.return_value = error_response

        # Act
        result = webhooks_manager.test_webhook(table_id, webhook_id)

        # Assert
        assert result["success"] is False
        assert result["status_code"] == 500
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__])
