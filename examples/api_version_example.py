"""
Example demonstrating NocoDB API v2 and v3 usage.

This example shows how to use the NocoDB client with both API versions.
"""

from nocodb_simple_client import NocoDBClient

# ============================================================================
# API v2 Example (Default)
# ============================================================================

print("=" * 60)
print("API v2 Example (Default)")
print("=" * 60)

# Create client with v2 API (default)
client_v2 = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    # api_version="v2"  # This is the default, can be omitted
)

print(f"Client API Version: {client_v2.api_version}")

# Get records from a table (v2 style)
# No base_id required for v2
records = client_v2.get_records(
    table_id="tbl_abc123",
    limit=10,
    where="(Status,eq,Active)",
    sort="-CreatedAt",  # v2 uses string format: "-field" for DESC
)

print(f"Found {len(records)} records")

# Insert a record (v2 style)
new_record = {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Status": "Active",
}

record_id = client_v2.insert_record(
    table_id="tbl_abc123",
    record=new_record,
)

print(f"Inserted record with ID: {record_id}")

# Update a record (v2 style)
update_data = {"Status": "Inactive"}

client_v2.update_record(
    table_id="tbl_abc123",
    record=update_data,
    record_id=record_id,
)

print(f"Updated record {record_id}")

# ============================================================================
# API v3 Example
# ============================================================================

print("\n" + "=" * 60)
print("API v3 Example")
print("=" * 60)

# Create client with v3 API
# Option 1: Provide base_id in constructor (recommended)
client_v3 = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v3",
    base_id="base_xyz789",  # Default base_id for all operations
)

print(f"Client API Version: {client_v3.api_version}")
print(f"Default Base ID: {client_v3.base_id}")

# Get records from a table (v3 style)
# base_id is automatically used from client's default
records_v3 = client_v3.get_records(
    table_id="tbl_abc123",
    limit=10,
    where="(Status,eq,Active)",
    sort="-CreatedAt",  # Still uses v2 string format, converted internally
)

print(f"Found {len(records_v3)} records")

# You can also override the base_id for specific calls
records_v3_alt = client_v3.get_records(
    table_id="tbl_def456",
    base_id="base_different123",  # Override default base_id
    limit=5,
)

print(f"Found {len(records_v3_alt)} records from different base")

# Insert a record (v3 style)
new_record_v3 = {
    "Name": "Jane Smith",
    "Email": "jane@example.com",
    "Status": "Active",
}

record_id_v3 = client_v3.insert_record(
    table_id="tbl_abc123",
    record=new_record_v3,
    # base_id is automatically used from client's default
)

print(f"Inserted record with ID: {record_id_v3}")

# ============================================================================
# API v3 with Manual Base ID Resolution
# ============================================================================

print("\n" + "=" * 60)
print("API v3 with Manual Base ID (No Auto-Resolution)")
print("=" * 60)

# Option 2: No default base_id, provide it with each call
client_v3_manual = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v3",
    # No base_id provided - must specify for each call
)

# This requires base_id in every method call
try:
    records_manual = client_v3_manual.get_records(
        table_id="tbl_abc123",
        base_id="base_xyz789",  # Required!
        limit=10,
    )
    print(f"Found {len(records_manual)} records")
except ValueError as e:
    print(f"Error: {e}")

# ============================================================================
# Pagination Differences (Handled Automatically)
# ============================================================================

print("\n" + "=" * 60)
print("Pagination Handling (Automatic Conversion)")
print("=" * 60)

# v2 client - uses offset/limit internally
print("\\nv2 Pagination:")
records_v2_page = client_v2.get_records(
    table_id="tbl_abc123",
    limit=25,
    # Internally uses: offset=0, limit=25
)
print(f"Retrieved {len(records_v2_page)} records")

# v3 client - automatically converts to page/pageSize
print("\\nv3 Pagination:")
records_v3_page = client_v3.get_records(
    table_id="tbl_abc123",
    limit=25,
    # Internally converts to: page=1, pageSize=25
)
print(f"Retrieved {len(records_v3_page)} records")

# ============================================================================
# Sort Format Differences (Handled Automatically)
# ============================================================================

print("\n" + "=" * 60)
print("Sort Format Handling (Automatic Conversion)")
print("=" * 60)

# v2 uses string format
records_v2_sorted = client_v2.get_records(
    table_id="tbl_abc123",
    sort="Name,-CreatedAt",  # Sort by Name ASC, then CreatedAt DESC
    limit=10,
)
print(f"v2 sorted {len(records_v2_sorted)} records")

# v3 automatically converts to JSON format
records_v3_sorted = client_v3.get_records(
    table_id="tbl_abc123",
    sort="Name,-CreatedAt",  # Same syntax! Converted internally to JSON
    limit=10,
)
print(f"v3 sorted {len(records_v3_sorted)} records")

# ============================================================================
# File Operations (Both Versions)
# ============================================================================

print("\n" + "=" * 60)
print("File Operations")
print("=" * 60)

# v2 file upload
print("\\nv2 File Upload:")
record_id_v2 = client_v2.attach_file_to_record(
    table_id="tbl_abc123",
    record_id=123,
    field_name="Attachments",
    file_path="/path/to/document.pdf",
)
print(f"Attached file to record {record_id_v2}")

# v3 file upload (with base_id)
print("\\nv3 File Upload:")
record_id_v3_file = client_v3.attach_file_to_record(
    table_id="tbl_abc123",
    record_id=123,
    field_name="Attachments",
    file_path="/path/to/document.pdf",
    # base_id automatically used from client's default
)
print(f"Attached file to record {record_id_v3_file}")

# ============================================================================
# Migration Path: Gradual Transition from v2 to v3
# ============================================================================

print("\n" + "=" * 60)
print("Migration Path: v2 to v3 Transition")
print("=" * 60)

# Step 1: Start with v2 (current code)
legacy_client = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v2",  # Explicitly set to v2
)

# Step 2: Test v3 in parallel
test_client_v3 = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v3",
    base_id="base_xyz789",
)

# Step 3: Compare results
records_legacy = legacy_client.get_records("tbl_abc123", limit=5)
records_new = test_client_v3.get_records("tbl_abc123", limit=5)

print(f"v2 returned {len(records_legacy)} records")
print(f"v3 returned {len(records_new)} records")

# Step 4: Once validated, switch to v3 by changing api_version parameter

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)

# ============================================================================
# Best Practices
# ============================================================================

print("\\n\\nBEST PRACTICES:")
print("-" * 60)
print("1. For v2: Use default settings (api_version='v2', no base_id)")
print("2. For v3: Set api_version='v3' and provide base_id in constructor")
print("3. Migration: Test v3 in parallel before switching production code")
print("4. Use same query syntax - conversion happens automatically")
print("5. base_id can be set per-client (recommended) or per-method call")
print("-" * 60)
