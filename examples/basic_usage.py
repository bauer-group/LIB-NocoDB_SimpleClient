"""
Basic usage examples for NocoDB Simple Client.

This example demonstrates the core functionality of the NocoDB Simple Client
including CRUD operations and basic table interactions.
"""

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable, RecordNotFoundException

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-here"


def main():
    """Demonstrate basic NocoDB operations."""

    # Initialize the client
    client = NocoDBClient(
        base_url=NOCODB_BASE_URL,
        db_auth_token=API_TOKEN,
        timeout=30,  # 30 second timeout
        # Optional: Custom protection header for reverse proxy
        # access_protection_auth="your-protection-token",
        # access_protection_header="X-Custom-Auth"  # Defaults to "X-BAUERGROUP-Auth"
    )

    # Initialize a table wrapper for easier operations
    table = NocoDBTable(client, table_id=TABLE_ID)

    try:
        # Example 1: Insert a new record
        print("1. Inserting a new record...")
        new_record = {
            "Name": "John Doe",
            "Email": "john.doe@example.com",
            "Age": 30,
            "Active": True,
        }

        record_id = table.insert_record(new_record)
        print(f"   ✓ Inserted record with ID: {record_id}")

        # Example 2: Get the record we just created
        print("\n2. Retrieving the record...")
        record = table.get_record(record_id=record_id, fields=["Id", "Name", "Email", "Age"])
        print(f"   ✓ Retrieved record: {record}")

        # Example 3: Update the record
        print("\n3. Updating the record...")
        updated_data = {"Name": "John Smith", "Age": 31}

        updated_id = table.update_record(updated_data, record_id)
        print(f"   ✓ Updated record ID: {updated_id}")

        # Example 4: Get multiple records with filtering
        print("\n4. Getting multiple records with filtering...")
        records = table.get_records(
            where="(Age,gt,25)",  # Age greater than 25
            sort="-Id",  # Sort by ID descending
            fields=["Id", "Name", "Email", "Age"],
            limit=5,
        )
        print(f"   ✓ Found {len(records)} records:")
        for record in records:
            print(f"      - {record.get('Name')} (ID: {record.get('Id')})")

        # Example 5: Count records
        print("\n5. Counting records...")
        total_count = table.count_records()
        active_count = table.count_records(where="(Active,eq,true)")
        print(f"   ✓ Total records: {total_count}")
        print(f"   ✓ Active records: {active_count}")

        # Example 6: Delete the record we created
        print("\n6. Deleting the test record...")
        deleted_id = table.delete_record(record_id)
        print(f"   ✓ Deleted record ID: {deleted_id}")

    except RecordNotFoundException as e:
        print(f"❌ Record not found: {e.message}")

    except NocoDBException as e:
        print(f"❌ NocoDB error: {e.error} - {e.message}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        # Close the client session
        client.close()
        print("\n✓ Client session closed")


if __name__ == "__main__":
    main()
