"""
Webhook automation examples for NocoDB Simple Client.

This example demonstrates how to create and manage webhooks for
automating actions based on database events.
"""

from nocodb_simple_client import NocoDBMetaClient
from nocodb_simple_client.webhooks import NocoDBWebhooks

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-here"


def main():
    """Demonstrate webhook automation."""

    meta_client = NocoDBMetaClient(base_url=NOCODB_BASE_URL, api_token=API_TOKEN)
    webhooks_manager = NocoDBWebhooks(meta_client)

    try:
        print("=" * 60)
        print("WEBHOOK AUTOMATION EXAMPLES")
        print("=" * 60)

        # ===================================================================
        # LIST EXISTING WEBHOOKS
        # ===================================================================
        print("\n1. Listing existing webhooks...")
        webhooks = webhooks_manager.get_webhooks(TABLE_ID)
        if webhooks:
            for webhook in webhooks:
                status = "Active" if webhook.get("active") else "Inactive"
                print(f"   • {webhook.get('title')} ({status})")
        else:
            print("   No webhooks configured yet")

        # ===================================================================
        # URL WEBHOOK
        # ===================================================================
        print("\n2. Creating a URL webhook...")
        url_webhook = webhooks_manager.create_webhook(
            TABLE_ID,
            title="API Notification",
            event_type="after",  # after the event
            operation="insert",  # on insert operation
            url="https://api.example.com/notifications",
            method="POST",
            headers={"Authorization": "Bearer your-api-token", "Content-Type": "application/json"},
            body='{"event": "new_record", "name": "{{Name}}", "email": "{{Email}}", "id": "{{Id}}"}',
            active=True,
        )
        print(f"   ✓ Created URL webhook: {url_webhook.get('title')}")
        url_webhook_id = url_webhook.get("id")

        # ===================================================================
        # EMAIL WEBHOOK
        # ===================================================================
        print("\n3. Creating an email webhook...")
        email_webhook = webhooks_manager.create_email_webhook(
            TABLE_ID,
            title="Email Alert",
            event_type="after",
            operation="update",
            emails=["admin@example.com", "team@example.com"],
            subject="Record Updated: {{Name}}",
            body="""
            Record has been updated:

            ID: {{Id}}
            Name: {{Name}}
            Email: {{Email}}
            Updated At: {{UpdatedAt}}

            Please review the changes.
            """,
            active=True,
        )
        print(f"   ✓ Created email webhook: {email_webhook.get('title')}")

        # ===================================================================
        # SLACK WEBHOOK
        # ===================================================================
        print("\n4. Creating a Slack webhook...")
        slack_webhook = webhooks_manager.create_slack_webhook(
            TABLE_ID,
            title="Slack Notification",
            event_type="after",
            operation="insert",
            webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            message=":tada: New record created!\n*Name:* {{Name}}\n*Email:* {{Email}}",
            active=True,
        )
        print(f"   ✓ Created Slack webhook: {slack_webhook.get('title')}")

        # ===================================================================
        # TEAMS WEBHOOK
        # ===================================================================
        print("\n5. Creating a Microsoft Teams webhook...")
        teams_webhook = webhooks_manager.create_teams_webhook(
            TABLE_ID,
            title="Teams Notification",
            event_type="after",
            operation="delete",
            webhook_url="https://outlook.office.com/webhook/YOUR_WEBHOOK_URL",
            message="Record deleted: {{Name}} ({{Email}})",
            active=True,
        )
        print(f"   ✓ Created Teams webhook: {teams_webhook.get('title')}")

        # ===================================================================
        # CONDITIONAL WEBHOOK
        # ===================================================================
        print("\n6. Creating a conditional webhook...")
        # Webhook only triggers if specific conditions are met
        conditional_webhook = webhooks_manager.create_webhook(
            TABLE_ID,
            title="VIP Customer Alert",
            event_type="after",
            operation="insert",
            url="https://api.example.com/vip-alert",
            method="POST",
            body='{"customer": "{{Name}}", "tier": "{{CustomerTier}}"}',
            condition={"column_name": "CustomerTier", "comparison_op": "eq", "value": "VIP"},
            active=True,
        )
        print(f"   ✓ Created conditional webhook: {conditional_webhook.get('title')}")

        # ===================================================================
        # TEST WEBHOOK
        # ===================================================================
        print("\n7. Testing a webhook...")
        try:
            test_result = webhooks_manager.test_webhook(TABLE_ID, url_webhook_id)
            print("   ✓ Webhook test completed")
            print(f"   Response: {test_result}")
        except Exception as e:
            print(f"   ⚠ Webhook test failed (expected if endpoint doesn't exist): {e}")

        # ===================================================================
        # UPDATE WEBHOOK
        # ===================================================================
        print("\n8. Updating a webhook...")
        webhooks_manager.update_webhook(
            TABLE_ID,
            url_webhook_id,
            title="Updated API Notification",
            url="https://api.example.com/v2/notifications",
            active=False,  # Temporarily disable
        )
        print("   ✓ Updated webhook (deactivated)")

        # ===================================================================
        # GET WEBHOOK LOGS
        # ===================================================================
        print("\n9. Getting webhook execution logs...")
        try:
            logs = webhooks_manager.get_webhook_logs(TABLE_ID, url_webhook_id, limit=5)
            if logs:
                print(f"   Found {len(logs)} recent executions:")
                for log in logs:
                    print(f"   • {log.get('created_at')}: {log.get('status')}")
            else:
                print("   No execution logs yet")
        except Exception as e:
            print(f"   ⚠ Could not retrieve logs: {e}")

        # ===================================================================
        # TOGGLE WEBHOOK
        # ===================================================================
        print("\n10. Toggling webhook status...")
        webhooks_manager.toggle_webhook(TABLE_ID, url_webhook_id)
        print("   ✓ Toggled webhook active status")

        # ===================================================================
        # PRACTICAL EXAMPLES
        # ===================================================================
        print("\n" + "=" * 60)
        print("PRACTICAL USE CASES")
        print("=" * 60)

        print("\n11. Creating practical webhooks...")

        # Order notification
        order_webhook = webhooks_manager.create_webhook(
            TABLE_ID,
            title="New Order Alert",
            event_type="after",
            operation="insert",
            url="https://api.yourcompany.com/orders/notify",
            method="POST",
            headers={"X-API-Key": "your-api-key"},
            body='{"order_id": "{{Id}}", "customer": "{{CustomerName}}", "total": "{{OrderTotal}}"}',
            active=True,
        )
        print("   ✓ Order notification webhook")

        # Status change webhook
        status_webhook = webhooks_manager.create_webhook(
            TABLE_ID,
            title="Status Change Webhook",
            event_type="after",
            operation="update",
            url="https://api.yourcompany.com/status-changed",
            method="POST",
            body='{"record_id": "{{Id}}", "old_status": "{{__old__.Status}}", "new_status": "{{Status}}"}',
            active=True,
        )
        print("   ✓ Status change tracking webhook")

        # Backup webhook
        backup_webhook = webhooks_manager.create_webhook(
            TABLE_ID,
            title="Backup Important Changes",
            event_type="before",  # before the change
            operation="delete",
            url="https://api.yourcompany.com/backup",
            method="POST",
            body='{"backup": {{__data__}}}',  # Full record data
            active=True,
        )
        print("   ✓ Backup webhook for deleted records")

        # ===================================================================
        # CLEANUP
        # ===================================================================
        print("\n" + "=" * 60)
        print("CLEANUP")
        print("=" * 60)

        print("\n12. Cleaning up demo webhooks...")

        # List all webhooks we created
        demo_webhooks = [
            url_webhook_id,
            email_webhook.get("id"),
            slack_webhook.get("id"),
            teams_webhook.get("id"),
            conditional_webhook.get("id"),
            order_webhook.get("id"),
            status_webhook.get("id"),
            backup_webhook.get("id"),
        ]

        for webhook_id in demo_webhooks:
            if webhook_id:
                try:
                    webhooks_manager.delete_webhook(TABLE_ID, webhook_id)
                    print(f"   ✓ Deleted webhook {webhook_id}")
                except Exception as e:
                    print(f"   ⚠ Could not delete webhook {webhook_id}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        meta_client.close()
        print("\n✓ Meta client session closed")


if __name__ == "__main__":
    main()
