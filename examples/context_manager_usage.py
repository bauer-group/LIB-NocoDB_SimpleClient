"""
Context manager usage examples for NocoDB Simple Client.

This example demonstrates how to use the NocoDB client with context managers
for proper resource management and error handling.
"""

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable, RecordNotFoundException

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-here"


def example_with_context_manager():
    """Demonstrate proper usage with context manager."""

    print("📦 Using NocoDB Client with Context Manager")
    print("-" * 50)

    # The recommended way: using context manager
    with NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN, timeout=30) as client:

        # Create table wrapper
        table = NocoDBTable(client, table_id=TABLE_ID)

        try:
            # Example operations within context
            print("1. Getting record count...")
            count = table.count_records()
            print(f"   ✓ Total records: {count}")

            print("\n2. Getting recent records...")
            records = table.get_records(sort="-Id", limit=3, fields=["Id", "Name"])
            print(f"   ✓ Retrieved {len(records)} records:")
            for record in records:
                print(f"      - {record.get('Name')} (ID: {record.get('Id')})")

            print("\n3. Creating a test record...")
            test_record = {
                "Name": "Context Manager Test",
                "Description": "Created using context manager example",
            }

            record_id = table.insert_record(test_record)
            print(f"   ✓ Created record with ID: {record_id}")

            # Clean up the test record
            table.delete_record(record_id)
            print("   ✓ Cleaned up test record")

        except NocoDBException as e:
            print(f"❌ NocoDB error: {e.error} - {e.message}")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    # Client is automatically closed here
    print("\n✅ Context manager automatically closed the client connection")


def example_without_context_manager():
    """Demonstrate manual resource management (not recommended)."""

    print("\n🔧 Manual Resource Management (Alternative approach)")
    print("-" * 60)

    client = None

    try:
        # Manual client creation
        client = NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN, timeout=30)

        table = NocoDBTable(client, table_id=TABLE_ID)

        print("1. Manual client - Getting record count...")
        count = table.count_records()
        print(f"   ✓ Total records: {count}")

    except NocoDBException as e:
        print(f"❌ NocoDB error: {e.error} - {e.message}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        # Manual cleanup - IMPORTANT!
        if client:
            client.close()
            print("   ✓ Manually closed client connection")


def example_error_handling_in_context():
    """Demonstrate error handling within context manager."""

    print("\n🚨 Error Handling with Context Manager")
    print("-" * 45)

    with NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN, timeout=30) as client:

        table = NocoDBTable(client, table_id=TABLE_ID)

        # Example 1: Handle specific errors
        try:
            print("1. Attempting to get non-existent record...")
            record = table.get_record(record_id=99999999)
            print("   This shouldn't print if record doesn't exist")

        except RecordNotFoundException as e:
            print(f"   ✓ Correctly handled missing record: {e.message}")

        except NocoDBException as e:
            print(f"   ❌ Other NocoDB error: {e.error} - {e.message}")

        # Example 2: Bulk operations with error recovery
        print("\n2. Bulk operations with error handling...")
        test_records = [
            {"Name": "Test Record 1", "Email": "test1@example.com"},
            {"Name": "Test Record 2", "Email": "test2@example.com"},
            {"Name": "Test Record 3"},  # Missing email might cause issues
        ]

        created_ids = []
        for i, record in enumerate(test_records, 1):
            try:
                record_id = table.insert_record(record)
                created_ids.append(record_id)
                print(f"   ✓ Created record {i}: ID {record_id}")

            except NocoDBException as e:
                print(f"   ❌ Failed to create record {i}: {e.message}")

        # Clean up created records
        print("\n3. Cleaning up created records...")
        for record_id in created_ids:
            try:
                table.delete_record(record_id)
                print(f"   ✓ Deleted record ID: {record_id}")

            except Exception as e:
                print(f"   ⚠️  Could not delete record {record_id}: {e}")

    print("   ✓ Context manager handled cleanup even with errors")


def example_multiple_tables():
    """Demonstrate working with multiple tables in one session."""

    print("\n🗂️  Working with Multiple Tables")
    print("-" * 40)

    # You would need multiple table IDs for this example
    TABLE_IDS = [
        "your-first-table-id",
        "your-second-table-id",
        # Add more table IDs as needed
    ]

    with NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN, timeout=30) as client:

        tables = [NocoDBTable(client, table_id) for table_id in TABLE_IDS]

        print(f"Working with {len(tables)} tables...")

        for i, table in enumerate(tables, 1):
            try:
                count = table.count_records()
                print(f"   Table {i}: {count} records")

            except NocoDBException as e:
                print(f"   Table {i}: Error - {e.message}")


def main():
    """Run all context manager examples."""

    print("🎯 NocoDB Simple Client - Context Manager Examples")
    print("=" * 55)

    # Run examples
    example_with_context_manager()
    example_without_context_manager()
    example_error_handling_in_context()
    example_multiple_tables()

    print("\n" + "=" * 55)
    print("✅ All context manager examples completed!")
    print("\n💡 Key Takeaways:")
    print("   • Always use context managers (with statement) when possible")
    print("   • Context managers automatically handle resource cleanup")
    print("   • Proper error handling is crucial for robust applications")
    print("   • One client can work with multiple tables efficiently")


if __name__ == "__main__":
    main()
