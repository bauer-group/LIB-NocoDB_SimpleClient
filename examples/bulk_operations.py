"""
Bulk operations examples for NocoDB Simple Client.

This example demonstrates high-performance bulk operations for inserting,
updating, and deleting multiple records at once.
"""

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-here"


def main():
    """Demonstrate bulk operations."""

    client = NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN)
    table = NocoDBTable(client, table_id=TABLE_ID)

    try:
        # Example 1: Bulk Insert
        print("1. Bulk inserting records...")
        records_to_insert = [
            {"Name": "Alice Smith", "Email": "alice@example.com", "Age": 28, "Active": True},
            {"Name": "Bob Johnson", "Email": "bob@example.com", "Age": 32, "Active": True},
            {"Name": "Charlie Brown", "Email": "charlie@example.com", "Age": 45, "Active": False},
            {"Name": "Diana Prince", "Email": "diana@example.com", "Age": 29, "Active": True},
            {"Name": "Eve Wilson", "Email": "eve@example.com", "Age": 37, "Active": True},
        ]

        record_ids = table.bulk_insert_records(records_to_insert)
        print(f"   ✓ Inserted {len(record_ids)} records")
        print(f"   Record IDs: {record_ids}")

        # Example 2: Bulk Update
        print("\n2. Bulk updating records...")
        records_to_update = [
            {"Id": record_ids[0], "Active": False, "Status": "Updated"},
            {"Id": record_ids[1], "Active": False, "Status": "Updated"},
            {"Id": record_ids[2], "Active": True, "Status": "Updated"},
        ]

        updated_ids = table.bulk_update_records(records_to_update)
        print(f"   ✓ Updated {len(updated_ids)} records")
        print(f"   Updated IDs: {updated_ids}")

        # Example 3: Verify updates
        print("\n3. Verifying updates...")
        for record_id in updated_ids:
            record = table.get_record(record_id, fields=["Id", "Name", "Active", "Status"])
            print(
                f"   Record {record_id}: {record.get('Name')} - Active: {record.get('Active')}, Status: {record.get('Status')}"
            )

        # Example 4: Bulk Delete
        print("\n4. Bulk deleting records...")
        deleted_ids = table.bulk_delete_records(record_ids)
        print(f"   ✓ Deleted {len(deleted_ids)} records")
        print(f"   Deleted IDs: {deleted_ids}")

        # Example 5: Performance comparison
        print("\n5. Performance comparison (inserting 100 records)...")

        # Single inserts (for comparison - commented out for brevity)
        # import time
        # start = time.time()
        # for i in range(100):
        #     table.insert_record({"Name": f"User {i}", "Email": f"user{i}@example.com"})
        # single_time = time.time() - start

        # Bulk insert
        import time

        bulk_records = [
            {"Name": f"User {i}", "Email": f"user{i}@example.com", "Age": 20 + (i % 50)}
            for i in range(100)
        ]
        start = time.time()
        bulk_ids = table.bulk_insert_records(bulk_records)
        bulk_time = time.time() - start

        print(f"   Bulk insert time: {bulk_time:.2f} seconds for {len(bulk_ids)} records")
        # print(f"   Single insert time: {single_time:.2f} seconds")
        # print(f"   Performance improvement: {single_time / bulk_time:.1f}x faster")

        # Cleanup
        print("\n6. Cleaning up test records...")
        table.bulk_delete_records(bulk_ids)
        print("   ✓ Cleanup complete")

        # Example 6: Error handling in bulk operations
        print("\n7. Demonstrating error handling...")
        try:
            # Attempt to update non-existent records
            invalid_updates = [
                {"Id": 99999999, "Name": "Invalid"},
                {"Id": 88888888, "Name": "Also Invalid"},
            ]
            table.bulk_update_records(invalid_updates)
        except NocoDBException as e:
            print(f"   Expected error caught: {e.message}")

    except NocoDBException as e:
        print(f"❌ NocoDB error: {e.error} - {e.message}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        client.close()
        print("\n✓ Client session closed")


if __name__ == "__main__":
    main()
