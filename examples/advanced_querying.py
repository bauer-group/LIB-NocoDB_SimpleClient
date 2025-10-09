"""
Advanced querying examples for NocoDB Simple Client.

This example demonstrates advanced filtering, sorting, and querying
techniques including the SQL-like Query Builder and Filter/Sort builders.
"""

from datetime import datetime, timedelta

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable
from nocodb_simple_client.filter_builder import FilterBuilder, SortBuilder

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


def demonstrate_query_builder(table: NocoDBTable):
    """Demonstrate SQL-like Query Builder."""
    print("\n🏗️ Query Builder Examples:")

    # Example 1: Simple query with method chaining
    print("\n1. Simple query with Query Builder:")
    records = (
        table.query()
        .select("Name", "Email", "Status")
        .where("Status", "eq", "Active")
        .order_by("Name", "asc")
        .limit(5)
        .execute()
    )
    print(f"   Found {len(records)} active records")
    for record in records:
        print(f"   - {record.get('Name')} ({record.get('Email')})")

    # Example 2: Complex filtering with AND/OR
    print("\n2. Complex filtering with AND/OR:")
    records = (
        table.query()
        .select("Name", "Age", "Status")
        .where("Status", "eq", "Active")
        .where_and("Age", "gt", 21)
        .where_or("Role", "eq", "Admin")
        .order_by_desc("Age")
        .limit(10)
        .execute()
    )
    print(f"   Found {len(records)} records")

    # Example 3: Using convenience methods
    print("\n3. Query Builder convenience methods:")

    # Get first matching record
    first_record = table.query().where("Email", "like", "%@example.com").first()
    if first_record:
        print(f"   First record: {first_record.get('Name')}")

    # Check if records exist
    has_vip_users = table.query().where("UserType", "eq", "VIP").exists()
    print(f"   Has VIP users: {has_vip_users}")

    # Count matching records
    active_count = table.query().where("Status", "eq", "Active").count()
    print(f"   Active users count: {active_count}")

    # Example 4: Advanced filtering methods
    print("\n4. Advanced filtering methods:")
    records = (
        table.query()
        .select("Name", "Email", "Status", "Age")
        .where_in("Status", ["Active", "Pending"])
        .where_not_null("Email")
        .where_between("Age", 25, 65)
        .where_like("Name", "%Smith%")
        .order_by_desc("CreatedAt")
        .limit(15)
        .execute()
    )
    print(f"   Found {len(records)} records with advanced filters")

    # Example 5: Pagination with Query Builder
    print("\n5. Pagination with Query Builder:")
    page_2_records = (
        table.query()
        .select("Name", "Email")
        .where("Status", "eq", "Active")
        .order_by("Name")
        .page(2, 10)  # Page 2 with 10 records per page
        .execute()
    )
    print(f"   Page 2 contains {len(page_2_records)} records")

    # Example 6: Query debugging
    print("\n6. Query debugging:")
    query = (
        table.query()
        .select("Name", "Status")
        .where("Age", "gt", 18)
        .where_and("Status", "eq", "Active")
        .order_by_desc("CreatedAt")
        .limit(50)
    )

    print(f"   Query string: {str(query)}")
    print(f"   Query params: {query.to_params()}")


def demonstrate_filter_builder():
    """Demonstrate advanced Filter Builder."""
    print("\n🔧 Filter Builder Examples:")

    # Example 1: Building complex filters
    print("\n1. Building complex filters:")
    filter_builder = FilterBuilder()
    filter_str = (
        filter_builder.where("Status", "eq", "Active")
        .and_("Age", "gt", 21)
        .and_("Email", "isnotblank")
        .or_("Role", "eq", "Admin")
        .build()
    )
    print(f"   Filter string: {filter_str}")

    # Example 2: Using different operators
    print("\n2. Different comparison operators:")

    # Equality
    fb1 = FilterBuilder()
    print(f"   Equal: {fb1.where('Status', 'eq', 'Active').build()}")

    # Numeric comparisons
    fb2 = FilterBuilder()
    print(f"   Greater than: {fb2.where('Age', 'gt', 21).build()}")

    # Text search
    fb3 = FilterBuilder()
    print(f"   Like: {fb3.where('Name', 'like', '%John%').build()}")

    # IN operator
    fb4 = FilterBuilder()
    print(f"   In: {fb4.where('Status', 'in', ['Active', 'Pending']).build()}")

    # Between operator
    fb5 = FilterBuilder()
    print(f"   Between: {fb5.where('Age', 'btw', [18, 65]).build()}")

    # Example 3: NULL checks
    print("\n3. NULL and empty checks:")
    fb_null = FilterBuilder()
    print(f"   Is null: {fb_null.where('DeletedAt', 'null').build()}")

    fb_not_null = FilterBuilder()
    print(f"   Not null: {fb_not_null.where('Email', 'notnull').build()}")

    fb_blank = FilterBuilder()
    print(f"   Is blank: {fb_blank.where('Description', 'isblank').build()}")


def demonstrate_sort_builder():
    """Demonstrate Sort Builder."""
    print("\n📐 Sort Builder Examples:")

    # Example 1: Simple sorting
    print("\n1. Simple sorting:")
    sort_builder = SortBuilder()
    sort_str = sort_builder.desc("CreatedAt").build()
    print(f"   Sort string: {sort_str}")

    # Example 2: Multiple sort fields
    print("\n2. Multiple sort fields:")
    sort_builder = SortBuilder()
    sort_str = sort_builder.desc("Status").asc("Name").desc("CreatedAt").build()
    print(f"   Sort string: {sort_str}")

    # Example 3: Using with get_records
    print("\n3. Combining builders:")
    filter_builder = FilterBuilder()
    filter_str = filter_builder.where("Status", "eq", "Active").and_("Age", "gt", 18).build()

    sort_builder = SortBuilder()
    sort_str = sort_builder.desc("Priority").asc("Name").build()

    print(f"   Filter: {filter_str}")
    print(f"   Sort: {sort_str}")
    print("   Ready to use with: table.get_records(where=filter_str, sort=sort_str)")


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
        demonstrate_query_builder(table)
        demonstrate_filter_builder()  # No table needed for this demo
        demonstrate_sort_builder()  # No table needed for this demo

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
