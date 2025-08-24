"""
Advanced querying examples for NocoDB Simple Client.

This example demonstrates advanced filtering, sorting, and querying
techniques with the NocoDB Simple Client.
"""

from datetime import datetime, timedelta

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-here"


def demonstrate_filtering(table: NocoDBTable):
    """Demonstrate various filtering options."""
    print("🔍 Advanced Filtering Examples:")

    # Example 1: Simple equality filter
    print("\n1. Simple equality filter:")
    records = table.get_records(where="(Status,eq,Active)", limit=3)
    print(f"   Found {len(records)} active records")

    # Example 2: Numeric comparisons
    print("\n2. Numeric comparisons:")
    records = table.get_records(
        where="(Age,gt,25)", fields=["Id", "Name", "Age"], limit=5  # Greater than 25
    )
    print(f"   Found {len(records)} records with age > 25")

    # Example 3: Date filtering
    print("\n3. Date filtering:")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    records = table.get_records(
        where=f"(CreatedAt,gt,{yesterday})", fields=["Id", "Name", "CreatedAt"], limit=5
    )
    print(f"   Found {len(records)} records created after {yesterday}")

    # Example 4: Text search (contains)
    print("\n4. Text search:")
    records = table.get_records(
        where="(Name,like,%John%)", fields=["Id", "Name"], limit=5  # Contains 'John'
    )
    print(f"   Found {len(records)} records with 'John' in name")

    # Example 5: Multiple conditions with AND
    print("\n5. Multiple conditions (AND):")
    records = table.get_records(
        where="(Status,eq,Active)~and(Age,gt,18)", fields=["Id", "Name", "Age", "Status"], limit=5
    )
    print(f"   Found {len(records)} active adult records")

    # Example 6: Multiple conditions with OR
    print("\n6. Multiple conditions (OR):")
    records = table.get_records(
        where="(Status,eq,Active)~or(Status,eq,Pending)", fields=["Id", "Name", "Status"], limit=5
    )
    print(f"   Found {len(records)} active or pending records")

    # Example 7: NULL/Empty checks
    print("\n7. NULL/Empty checks:")
    records = table.get_records(
        where="(Email,isblank)", fields=["Id", "Name", "Email"], limit=3  # Email is empty
    )
    print(f"   Found {len(records)} records with empty email")

    # Example 8: NOT NULL checks
    print("\n8. NOT NULL checks:")
    records = table.get_records(
        where="(Email,isnotblank)", fields=["Id", "Name", "Email"], limit=3  # Email is not empty
    )
    print(f"   Found {len(records)} records with email address")


def demonstrate_sorting(table: NocoDBTable):
    """Demonstrate various sorting options."""
    print("\n📊 Advanced Sorting Examples:")

    # Example 1: Simple ascending sort
    print("\n1. Sort by name (ascending):")
    records = table.get_records(sort="Name", fields=["Id", "Name"], limit=5)
    for record in records:
        print(f"   - {record.get('Name')} (ID: {record.get('Id')})")

    # Example 2: Descending sort
    print("\n2. Sort by ID (descending):")
    records = table.get_records(
        sort="-Id", fields=["Id", "Name"], limit=5  # Minus sign for descending
    )
    for record in records:
        print(f"   - {record.get('Name')} (ID: {record.get('Id')})")

    # Example 3: Multiple column sorting
    print("\n3. Multiple column sort (Status desc, Name asc):")
    records = table.get_records(
        sort="-Status,Name",  # Status descending, then Name ascending
        fields=["Id", "Name", "Status"],
        limit=5,
    )
    for record in records:
        print(f"   - {record.get('Name')} - {record.get('Status')} (ID: {record.get('Id')})")


def demonstrate_field_selection(table: NocoDBTable):
    """Demonstrate field selection and data shaping."""
    print("\n🎯 Field Selection Examples:")

    # Example 1: Select specific fields only
    print("\n1. Select only essential fields:")
    records = table.get_records(fields=["Id", "Name", "Email"], limit=3)
    print(f"   Retrieved {len(records)} records with limited fields")
    for record in records:
        print(
            f"   - ID: {record.get('Id')}, Name: {record.get('Name')}, Email: {record.get('Email')}"
        )

    # Example 2: Get all fields (default behavior)
    print("\n2. Get all fields:")
    records = table.get_records(limit=1)
    if records:
        print(f"   Record has {len(records[0])} fields: {list(records[0].keys())}")


def demonstrate_pagination(table: NocoDBTable):
    """Demonstrate handling large datasets with pagination."""
    print("\n📄 Pagination Examples:")

    # Example 1: Get total count first
    total_count = table.count_records()
    print(f"\n1. Total records in table: {total_count}")

    # Example 2: Process records in batches
    print("\n2. Processing records in batches:")
    batch_size = 10
    processed = 0

    # Note: This is handled automatically by the client, but shown for understanding
    records = table.get_records(limit=batch_size)
    while records:
        processed += len(records)
        print(f"   Processed batch of {len(records)} records (total: {processed})")

        # Process your records here
        for _record in records:
            pass  # Your processing logic

        # For demo, we'll break after first batch
        break

    # Example 3: Get large dataset (client handles pagination automatically)
    print("\n3. Getting large dataset:")
    large_dataset = table.get_records(limit=250)  # More than single API call limit
    print(f"   Retrieved {len(large_dataset)} records across multiple API calls")


def demonstrate_complex_queries(table: NocoDBTable):
    """Demonstrate complex query combinations."""
    print("\n🔬 Complex Query Examples:")

    # Example 1: Complex business logic
    print("\n1. Complex business query:")
    # Find active users over 21 with email, created in last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    records = table.get_records(
        where=f"(Status,eq,Active)~and(Age,gt,21)~and(Email,isnotblank)~and(CreatedAt,gt,{thirty_days_ago})",
        sort="-CreatedAt",
        fields=["Id", "Name", "Email", "Age", "Status", "CreatedAt"],
        limit=10,
    )
    print(f"   Found {len(records)} records matching complex criteria")

    # Example 2: Statistical query
    print("\n2. Statistical analysis:")
    # Get counts for different status values
    status_values = ["Active", "Inactive", "Pending", "Suspended"]
    for status in status_values:
        count = table.count_records(where=f"(Status,eq,{status})")
        print(f"   {status}: {count} records")


def main():
    """Run all advanced querying examples."""

    # Initialize client and table
    client = NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN, timeout=30)

    table = NocoDBTable(client, table_id=TABLE_ID)

    try:
        print("🚀 NocoDB Advanced Querying Examples")
        print("=" * 50)

        # Run all examples
        demonstrate_filtering(table)
        demonstrate_sorting(table)
        demonstrate_field_selection(table)
        demonstrate_pagination(table)
        demonstrate_complex_queries(table)

        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")

    except NocoDBException as e:
        print(f"❌ NocoDB error: {e.error} - {e.message}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        client.close()
        print("\n✓ Client session closed")


if __name__ == "__main__":
    main()
