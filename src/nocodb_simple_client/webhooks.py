"""Webhooks and automation management for NocoDB.

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


class NocoDBWebhooks:
    """Manager for NocoDB webhooks and automation.

    Provides methods to manage webhooks that trigger on various database
    events like record creation, updates, and deletions.
    """

    EVENT_TYPES = {
        "after_insert": "after",
        "after_update": "after",
        "after_delete": "after",
        "before_insert": "before",
        "before_update": "before",
        "before_delete": "before",
    }

    OPERATION_TYPES = ["insert", "update", "delete"]

    def __init__(self, meta_client: "NocoDBMetaClient") -> None:
        """Initialize the webhooks manager.

        Args:
            meta_client: NocoDBMetaClient instance (inherits from NocoDBClient)
        """
        self.meta_client = meta_client

    def get_webhooks(self, table_id: str) -> list[dict[str, Any]]:
        """Get all webhooks for a table.

        Args:
            table_id: ID of the table

        Returns:
            List of webhook dictionaries

        Raises:
            NocoDBException: For API errors
        """
        return self.meta_client.list_webhooks(table_id)

    def get_webhook(self, table_id: str, webhook_id: str) -> dict[str, Any]:
        """Get a specific webhook by ID.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook

        Returns:
            Webhook dictionary

        Raises:
            NocoDBException: For API errors
            WebhookNotFoundException: If the webhook is not found
        """
        return self.meta_client.get_webhook(webhook_id)

    def create_webhook(
        self,
        table_id: str,
        title: str,
        event_type: str,
        operation: str,
        url: str,
        method: str = "POST",
        headers: dict[str, str] | None = None,
        body: str | None = None,
        condition: dict[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        """Create a new webhook.

        Args:
            table_id: ID of the table
            title: Title of the webhook
            event_type: When to trigger (before, after)
            operation: Database operation (insert, update, delete)
            url: URL to send the webhook to
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            headers: HTTP headers to include
            body: Request body template
            condition: Condition for when to trigger webhook
            active: Whether the webhook is active

        Returns:
            Created webhook dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If parameters are invalid
        """
        if event_type not in self.EVENT_TYPES.values():
            raise ValueError(
                f"Invalid event_type: {event_type}. "
                f"Must be one of: {list(self.EVENT_TYPES.values())}"
            )

        if operation not in self.OPERATION_TYPES:
            raise ValueError(
                f"Invalid operation: {operation}. " f"Must be one of: {self.OPERATION_TYPES}"
            )

        if method.upper() not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            raise ValueError("Invalid HTTP method")

        notification_payload: dict[str, Any] = {"method": method.upper(), "url": url}

        if headers:
            notification_payload["headers"] = headers

        if body:
            notification_payload["body"] = body

        data = {
            "title": title,
            "event": event_type,
            "operation": operation,
            "notification": {"type": "URL", "payload": notification_payload},
            "active": active,
        }

        if condition:
            data["condition"] = condition

        response = self.meta_client.create_webhook(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from webhook creation")

    def update_webhook(
        self,
        table_id: str,
        webhook_id: str,
        title: str | None = None,
        url: str | None = None,
        method: str | None = None,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        condition: dict[str, Any] | None = None,
        active: bool | None = None,
    ) -> dict[str, Any]:
        """Update an existing webhook.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook to update
            title: New title
            url: New URL
            method: New HTTP method
            headers: New headers
            body: New body template
            condition: New condition
            active: New active status

        Returns:
            Updated webhook dictionary

        Raises:
            NocoDBException: For API errors
            WebhookNotFoundException: If the webhook is not found
        """
        data: dict[str, Any] = {}

        if title:
            data["title"] = title

        if active is not None:
            data["active"] = active

        if condition is not None:
            data["condition"] = condition

        # Update notification payload if any URL/method/headers/body changed
        notification_update: dict[str, Any] = {}
        if url:
            notification_update["url"] = url
        if method:
            notification_update["method"] = method.upper()
        if headers is not None:
            notification_update["headers"] = headers
        if body is not None:
            notification_update["body"] = body

        if notification_update:
            data["notification"] = {"type": "URL", "payload": notification_update}

        if not data:
            raise ValueError("At least one parameter must be provided for update")

        response = self.meta_client.update_webhook(webhook_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from webhook update")

    def delete_webhook(self, table_id: str, webhook_id: str) -> bool:
        """Delete a webhook.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook to delete

        Returns:
            True if deletion was successful

        Raises:
            NocoDBException: For API errors
            WebhookNotFoundException: If the webhook is not found
        """
        response = self.meta_client.delete_webhook(webhook_id)
        return response is not None

    def test_webhook(
        self, table_id: str, webhook_id: str, sample_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Test a webhook by sending a sample request.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook to test
            sample_data: Sample data to send in the test

        Returns:
            Test result dictionary

        Raises:
            NocoDBException: For API errors
        """
        data: dict[str, Any] = {}
        if sample_data:
            data["data"] = sample_data

        return self.meta_client.test_webhook(webhook_id)

    def get_webhook_logs(
        self, table_id: str, webhook_id: str, limit: int = 25, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get execution logs for a webhook.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook
            limit: Maximum number of logs to retrieve
            offset: Number of logs to skip

        Returns:
            List of log dictionaries

        Raises:
            NocoDBException: For API errors
        """
        params = {"limit": limit, "offset": offset}

        endpoint = f"api/v2/tables/{table_id}/hooks/{webhook_id}/logs"
        response = self.meta_client._get(endpoint, params=params)
        webhook_list = response.get("list", [])
        return webhook_list if isinstance(webhook_list, list) else []

    def clear_webhook_logs(self, table_id: str, webhook_id: str) -> bool:
        """Clear all logs for a webhook.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook

        Returns:
            True if clearing was successful

        Raises:
            NocoDBException: For API errors
        """
        endpoint = f"api/v2/tables/{table_id}/hooks/{webhook_id}/logs"
        response = self.meta_client._delete(endpoint)
        return response is not None

    def create_email_webhook(
        self,
        table_id: str,
        title: str,
        event_type: str,
        operation: str,
        emails: list[str],
        subject: str,
        body: str,
        condition: dict[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        """Create an email notification webhook.

        Args:
            table_id: ID of the table
            title: Title of the webhook
            event_type: When to trigger (before, after)
            operation: Database operation (insert, update, delete)
            emails: List of email addresses to notify
            subject: Email subject template
            body: Email body template
            condition: Condition for when to trigger webhook
            active: Whether the webhook is active

        Returns:
            Created webhook dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If parameters are invalid
        """
        if event_type not in self.EVENT_TYPES.values():
            raise ValueError(f"Invalid event_type: {event_type}")

        if operation not in self.OPERATION_TYPES:
            raise ValueError(f"Invalid operation: {operation}")

        if not emails or not isinstance(emails, list):
            raise ValueError("emails must be a non-empty list")

        data = {
            "title": title,
            "event": event_type,
            "operation": operation,
            "notification": {
                "type": "Email",
                "payload": {"emails": ",".join(emails), "subject": subject, "body": body},
            },
            "active": active,
        }

        if condition:
            data["condition"] = condition

        response = self.meta_client.create_webhook(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from email webhook creation")

    def create_slack_webhook(
        self,
        table_id: str,
        title: str,
        event_type: str,
        operation: str,
        webhook_url: str,
        message: str,
        condition: dict[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        """Create a Slack notification webhook.

        Args:
            table_id: ID of the table
            title: Title of the webhook
            event_type: When to trigger (before, after)
            operation: Database operation (insert, update, delete)
            webhook_url: Slack webhook URL
            message: Message template
            condition: Condition for when to trigger webhook
            active: Whether the webhook is active

        Returns:
            Created webhook dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If parameters are invalid
        """
        if event_type not in self.EVENT_TYPES.values():
            raise ValueError(f"Invalid event_type: {event_type}")

        if operation not in self.OPERATION_TYPES:
            raise ValueError(f"Invalid operation: {operation}")

        data = {
            "title": title,
            "event": event_type,
            "operation": operation,
            "notification": {
                "type": "Slack",
                "payload": {"webhook_url": webhook_url, "message": message},
            },
            "active": active,
        }

        if condition:
            data["condition"] = condition

        response = self.meta_client.create_webhook(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from Slack webhook creation")

    def create_teams_webhook(
        self,
        table_id: str,
        title: str,
        event_type: str,
        operation: str,
        webhook_url: str,
        message: str,
        condition: dict[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        """Create a Microsoft Teams notification webhook.

        Args:
            table_id: ID of the table
            title: Title of the webhook
            event_type: When to trigger (before, after)
            operation: Database operation (insert, update, delete)
            webhook_url: Teams webhook URL
            message: Message template
            condition: Condition for when to trigger webhook
            active: Whether the webhook is active

        Returns:
            Created webhook dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If parameters are invalid
        """
        if event_type not in self.EVENT_TYPES.values():
            raise ValueError(f"Invalid event_type: {event_type}")

        if operation not in self.OPERATION_TYPES:
            raise ValueError(f"Invalid operation: {operation}")

        data = {
            "title": title,
            "event": event_type,
            "operation": operation,
            "notification": {
                "type": "MicrosoftTeams",
                "payload": {"webhook_url": webhook_url, "message": message},
            },
            "active": active,
        }

        if condition:
            data["condition"] = condition

        response = self.meta_client.create_webhook(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from Teams webhook creation")

    def toggle_webhook(self, table_id: str, webhook_id: str) -> dict[str, Any]:
        """Toggle a webhook's active status.

        Args:
            table_id: ID of the table
            webhook_id: ID of the webhook

        Returns:
            Updated webhook dictionary

        Raises:
            NocoDBException: For API errors
        """
        webhook = self.get_webhook(table_id, webhook_id)
        current_status = webhook.get("active", True)

        return self.update_webhook(
            table_id=table_id, webhook_id=webhook_id, active=not current_status
        )


class TableWebhooks:
    """Helper class for managing webhooks on a specific table.

    This is a convenience wrapper that automatically includes table_id
    in all webhook operations.
    """

    def __init__(self, webhooks_manager: NocoDBWebhooks, table_id: str) -> None:
        """Initialize table-specific webhooks manager.

        Args:
            webhooks_manager: NocoDBWebhooks instance
            table_id: ID of the table
        """
        self._webhooks = webhooks_manager
        self._table_id = table_id

    def get_webhooks(self) -> list[dict[str, Any]]:
        """Get all webhooks for this table."""
        return self._webhooks.get_webhooks(self._table_id)

    def get_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Get a specific webhook by ID."""
        return self._webhooks.get_webhook(self._table_id, webhook_id)

    def create_webhook(
        self, title: str, event_type: str, operation: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Create a new webhook for this table."""
        return self._webhooks.create_webhook(
            self._table_id, title, event_type, operation, url, **kwargs
        )

    def update_webhook(self, webhook_id: str, **kwargs: Any) -> dict[str, Any]:
        """Update an existing webhook."""
        return self._webhooks.update_webhook(self._table_id, webhook_id, **kwargs)

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        return self._webhooks.delete_webhook(self._table_id, webhook_id)

    def test_webhook(
        self, webhook_id: str, sample_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Test a webhook."""
        return self._webhooks.test_webhook(self._table_id, webhook_id, sample_data)

    def get_webhook_logs(
        self, webhook_id: str, limit: int = 25, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get webhook logs."""
        return self._webhooks.get_webhook_logs(self._table_id, webhook_id, limit, offset)

    def toggle_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Toggle webhook active status."""
        return self._webhooks.toggle_webhook(self._table_id, webhook_id)
