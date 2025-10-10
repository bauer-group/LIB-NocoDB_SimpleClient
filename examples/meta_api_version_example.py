"""
Example demonstrating NocoDB Meta API v2 and v3 usage.

This example shows how to use the Meta API client with both versions
for managing database structure (tables, columns, views, webhooks).
"""

from nocodb_simple_client import NocoDBMetaClient

# ============================================================================
# Meta API v2 Example (Default)
# ============================================================================

print("=" * 60)
print("Meta API v2 Example (Default)")
print("=" * 60)

# Create Meta API client with v2 (default)
meta_v2 = NocoDBMetaClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    # api_version="v2"  # Default, can be omitted
)

print(f"Client API Version: {meta_v2.api_version}")

# List all bases
bases = meta_v2.list_bases()
print(f"Found {len(bases)} bases")

# List tables in a base
tables = meta_v2.list_tables(base_id="base_abc123")
print(f"Found {len(tables)} tables")

# Get table metadata (v2 - no base_id required)
table_info = meta_v2.get_table_info(table_id="tbl_xyz789")
print(f"Table: {table_info.get('title', 'Unknown')}")

# List columns in a table (v2 - no base_id required)
columns = meta_v2.list_columns(table_id="tbl_xyz789")
print(f"Table has {len(columns)} columns")

# Create a new column
new_column = {
    "title": "Status",
    "uidt": "SingleSelect",  # UI Data Type
    "dtxp": "Active,Inactive,Pending",  # Options
}

column = meta_v2.create_column(
    table_id="tbl_xyz789",
    column_data=new_column,
)
print(f"Created column: {column.get('title', 'Unknown')}")

# List views
views = meta_v2.list_views(table_id="tbl_xyz789")
print(f"Table has {len(views)} views")

# List webhooks
webhooks = meta_v2.list_webhooks(table_id="tbl_xyz789")
print(f"Table has {len(webhooks)} webhooks")

# ============================================================================
# Meta API v3 Example
# ============================================================================

print("\n" + "=" * 60)
print("Meta API v3 Example")
print("=" * 60)

# Create Meta API client with v3
meta_v3 = NocoDBMetaClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v3",
    base_id="base_abc123",  # Default base_id for all operations
)

print(f"Client API Version: {meta_v3.api_version}")
print(f"Default Base ID: {meta_v3.base_id}")

# ============================================================================
# Workspace & Base Operations (Same for v2 and v3)
# ============================================================================

print("\n" + "=" * 60)
print("Workspace & Base Operations (v2/v3 Compatible)")
print("=" * 60)

# List workspaces (same endpoint for v2 and v3)
workspaces = meta_v3.list_workspaces()
print(f"Found {len(workspaces)} workspaces")

# Get workspace details
if workspaces:
    workspace = meta_v3.get_workspace(workspaces[0]["id"])
    print(f"Workspace: {workspace.get('title', 'Unknown')}")

# List all bases
bases_v3 = meta_v3.list_bases()
print(f"Found {len(bases_v3)} bases")

# Get base details
base = meta_v3.get_base(base_id="base_abc123")
print(f"Base: {base.get('title', 'Unknown')}")

# ============================================================================
# Table Operations (v3 with base_id)
# ============================================================================

print("\n" + "=" * 60)
print("Table Operations (v3)")
print("=" * 60)

# List tables (base_id already known)
tables_v3 = meta_v3.list_tables(base_id="base_abc123")
print(f"Found {len(tables_v3)} tables")

# Get table info (v3 - uses default base_id)
table_info_v3 = meta_v3.get_table_info(table_id="tbl_xyz789")
print(f"Table: {table_info_v3.get('title', 'Unknown')}")

# Or override with specific base_id
table_info_alt = meta_v3.get_table_info(
    table_id="tbl_different",
    base_id="base_different123",
)
print(f"Alternate table: {table_info_alt.get('title', 'Unknown')}")

# Create a new table
table_data = {
    "title": "Customers",
    "description": "Customer database",
    "columns": [
        {
            "title": "Name",
            "uidt": "SingleLineText",
            "pv": True,  # Primary value
        },
        {
            "title": "Email",
            "uidt": "Email",
        },
        {
            "title": "Phone",
            "uidt": "PhoneNumber",
        },
        {
            "title": "Created At",
            "uidt": "DateTime",
            "dtxp": "YYYY-MM-DD HH:mm:ss",
        },
    ],
}

new_table = meta_v3.create_table(
    base_id="base_abc123",
    table_data=table_data,
)
print(f"Created table: {new_table.get('title', 'Unknown')}")

# Update table metadata
updated_table = meta_v3.update_table(
    table_id=new_table["id"],
    table_data={"description": "Updated customer database"},
    # base_id automatically used from client's default
)
print("Updated table description")

# ============================================================================
# Column Operations (v3 - columns are called "fields")
# ============================================================================

print("\n" + "=" * 60)
print("Column/Field Operations (v3)")
print("=" * 60)

# List columns (v3 - automatically uses default base_id)
columns_v3 = meta_v3.list_columns(table_id="tbl_xyz789")
print(f"Table has {len(columns_v3)} columns/fields")

# Create a new column/field
column_data = {
    "title": "Priority",
    "uidt": "SingleSelect",
    "dtxp": "Low,Medium,High,Urgent",  # Options
    "dtxs": "Medium",  # Default value
}

new_column_v3 = meta_v3.create_column(
    table_id="tbl_xyz789",
    column_data=column_data,
    # base_id automatically used
)
print(f"Created field: {new_column_v3.get('title', 'Unknown')}")

# Update column (v3 requires base_id for column_id operations)
updated_column = meta_v3.update_column(
    column_id=new_column_v3["id"],
    column_data={"title": "Task Priority"},
    base_id="base_abc123",  # Required for v3 when using column_id
)
print("Updated field title")

# ============================================================================
# View Operations (v3)
# ============================================================================

print("\n" + "=" * 60)
print("View Operations (v3)")
print("=" * 60)

# List views for a table
views_v3 = meta_v3.list_views(table_id="tbl_xyz789")
print(f"Table has {len(views_v3)} views")

# Create a new view
view_data = {
    "title": "Active Customers",
    "type": "Grid",
    "show_system_fields": False,
    "lock_type": "collaborative",
}

new_view = meta_v3.create_view(
    table_id="tbl_xyz789",
    view_data=view_data,
    # base_id automatically used
)
print(f"Created view: {new_view.get('title', 'Unknown')}")

# Update view (requires base_id for view_id operations)
updated_view = meta_v3.update_view(
    view_id=new_view["id"],
    view_data={"title": "All Active Customers"},
    base_id="base_abc123",  # Required for v3
)
print("Updated view title")

# Get view details
view_details = meta_v3.get_view(
    view_id=new_view["id"],
    base_id="base_abc123",
)
print(f"View type: {view_details.get('type', 'Unknown')}")

# ============================================================================
# Webhook Operations (v3)
# ============================================================================

print("\n" + "=" * 60)
print("Webhook Operations (v3)")
print("=" * 60)

# List webhooks for a table
webhooks_v3 = meta_v3.list_webhooks(table_id="tbl_xyz789")
print(f"Table has {len(webhooks_v3)} webhooks")

# Create a webhook
webhook_data = {
    "title": "New Customer Notification",
    "event": "after",
    "operation": "insert",
    "notification": {
        "type": "URL",
        "payload": {
            "method": "POST",
            "url": "https://hooks.example.com/customer-webhook",
            "body": '{"customer": "{{Name}}", "email": "{{Email}}"}',
            "headers": [{"name": "Content-Type", "value": "application/json"}],
        },
    },
    "condition": [],  # No conditions, trigger on all inserts
    "active": True,
}

new_webhook = meta_v3.create_webhook(
    table_id="tbl_xyz789",
    webhook_data=webhook_data,
    # base_id automatically used
)
print(f"Created webhook: {new_webhook.get('title', 'Unknown')}")

# Update webhook
updated_webhook = meta_v3.update_webhook(
    hook_id=new_webhook["id"],
    webhook_data={"active": False},
    base_id="base_abc123",  # Required for v3
)
print("Disabled webhook")

# Test webhook
test_result = meta_v3.test_webhook(
    hook_id=new_webhook["id"],
    base_id="base_abc123",
)
print(f"Webhook test result: {test_result.get('status', 'Unknown')}")

# ============================================================================
# Migration: Comparing v2 and v3 Side-by-Side
# ============================================================================

print("\n" + "=" * 60)
print("Migration Example: v2 vs v3 Comparison")
print("=" * 60)

# Same operation in v2 and v3
print("\nGetting table info:")

# v2 - no base_id needed
table_v2 = meta_v2.get_table_info(table_id="tbl_xyz789")
print(f"v2: {table_v2.get('title', 'Unknown')}")

# v3 - uses default base_id from client
table_v3 = meta_v3.get_table_info(table_id="tbl_xyz789")
print(f"v3: {table_v3.get('title', 'Unknown')}")

print("\nListing columns:")

# v2 - no base_id needed
cols_v2 = meta_v2.list_columns(table_id="tbl_xyz789")
print(f"v2: {len(cols_v2)} columns")

# v3 - uses default base_id, columns are called "fields"
cols_v3 = meta_v3.list_columns(table_id="tbl_xyz789")
print(f"v3: {len(cols_v3)} fields")

# ============================================================================
# Advanced: Using Multiple Bases in v3
# ============================================================================

print("\n" + "=" * 60)
print("Advanced: Working with Multiple Bases (v3)")
print("=" * 60)

# Client configured with default base
meta_multi = NocoDBMetaClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token-here",
    api_version="v3",
    base_id="base_primary",
)

# Use default base
tables_primary = meta_multi.list_tables(base_id="base_primary")
print(f"Primary base: {len(tables_primary)} tables")

# Override for different base
tables_secondary = meta_multi.list_tables(base_id="base_secondary")
print(f"Secondary base: {len(tables_secondary)} tables")

# Table operations with explicit base_id override
table_from_other_base = meta_multi.get_table_info(
    table_id="tbl_from_secondary",
    base_id="base_secondary",  # Override default
)
print(f"Table from secondary base: {table_from_other_base.get('title', 'Unknown')}")

# ============================================================================
# Best Practices Summary
# ============================================================================

print("\n" + "=" * 60)
print("BEST PRACTICES")
print("=" * 60)
print("1. v2: Simple, no base_id needed for table operations")
print("2. v3: Set base_id in constructor for cleaner code")
print("3. v3: For column/view/webhook operations by ID, always provide base_id")
print("4. Migration: Test v3 in parallel before switching")
print("5. Columns → Fields: v3 terminology (PathBuilder handles this)")
print("6. Workspace/Base endpoints: Same for v2 and v3")
print("=" * 60)

print("\n✅ All Meta API examples completed!")
