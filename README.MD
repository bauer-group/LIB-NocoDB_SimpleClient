<!-- AUTO-GENERATED FILE. DO NOT EDIT. Edit docs/README.template.MD instead. -->
<!-- Generated on 2025-10-10 13:15:12 UTC -->

# BAUER GROUP - NocoDB Simple Client

[![PyPI Version](https://badge.fury.io/py/nocodb-simple-client.svg)](https://badge.fury.io/py/nocodb-simple-client)
[![Python Support](https://img.shields.io/pypi/pyversions/nocodb-simple-client.svg)](https://pypi.org/project/nocodb-simple-client/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![🐍 CI/CD](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/actions/workflows/python-automatic-release.yml/badge.svg)](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/actions/workflows/python-automatic-release.yml)


A simple and powerful Python client for interacting with [NocoDB](https://nocodb.com/) REST API. This client provides an intuitive interface for performing CRUD operations, managing file attachments, and handling complex queries on your NocoDB tables.

**Repository Information:**

- **Version:** 1.2.0 (2025-10-10)
- **Repository:** [bauer-group/LIB-NocoDB_SimpleClient](https://github.com/bauer-group/LIB-NocoDB_SimpleClient)
- **Branch:** main
- **Architecture:** Modular, Reusable, Enterprise-Ready

## 🌟 Features

- **Easy to Use**: Intuitive API design with comprehensive documentation
- **Full CRUD Operations**: Create, read, update, and delete records with ease
- **Bulk Operations**: High-performance bulk insert, update, and delete operations
- **File Management**: Upload, download, and manage file attachments
- **Advanced Querying**: Complex filtering, sorting, and pagination support with SQL-like query builder
- **API Version Support**: Seamlessly switch between NocoDB API v2 and v3
  - Default v2 support with full backward compatibility
  - Optional v3 support with automatic parameter conversion
  - Automatic base_id resolution for v3 API
  - Transparent pagination, sorting, and operator conversion
- **Meta API Support**: Full access to NocoDB Meta API for structure management
  - Workspace, Base, and Table operations
  - Column/Field management with type-specific helpers
  - View management (Grid, Gallery, Form, Kanban, Calendar)
  - Webhook automation (URL, Email, Slack, Teams)
  - Link/Relation management
  - Full v2/v3 API version support
- **Flexible Configuration**: Multiple configuration methods (environment variables, files, direct parameters)
- **Type Hints**: Full type annotation support for better IDE experience
- **Error Handling**: Comprehensive exception handling with specific error types
- **Context Manager**: Automatic resource management with context manager support
- **Production Ready**: Robust error handling and resource management

## 🚀 Quick Start

### Installation

Install from PyPI using pip:

```bash
pip install nocodb-simple-client
```

Or install directly from GitHub:

```bash
# Latest version from main branch
pip install git+https://github.com/bauer-group/LIB-NocoDB_SimpleClient.git

# Specific version/tag
pip install git+https://github.com/bauer-group/LIB-NocoDB_SimpleClient.git@v1.2.0

# Specific branch
pip install git+https://github.com/bauer-group/LIB-NocoDB_SimpleClient.git@main
```

### Basic Usage

```python
from nocodb_simple_client import NocoDBClient, NocoDBTable

# Initialize the client
client = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token"
)

# Create a table instance
table = NocoDBTable(client, table_id="your-table-id")

# Get records
records = table.get_records(limit=10)
print(f"Retrieved {len(records)} records")

# Create a new record
new_record = {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Age": 30
}
record_id = table.insert_record(new_record)
print(f"Created record with ID: {record_id}")

# Don't forget to close the client
client.close()
```

### Using Context Manager (Recommended)

```python
from nocodb_simple_client import NocoDBClient, NocoDBTable

with NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token"
) as client:
    table = NocoDBTable(client, table_id="your-table-id")

    # Your operations here
    records = table.get_records(where="(Status,eq,Active)", limit=5)

    # Client automatically closes when exiting the context
```

### API Version Support (v2 & v3)

The client supports both NocoDB API v2 (default) and v3 with automatic parameter conversion:

```python
from nocodb_simple_client import NocoDBClient

# Using v2 API (default - fully backward compatible)
client_v2 = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token"
)

# Using v3 API with automatic base_id resolution
client_v3 = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token",
    api_version="v3",
    base_id="your-base-id"  # Optional, can be auto-resolved
)

# All methods work the same way - conversion is automatic!
records = client_v3.get_records(
    table_id="your-table-id",
    limit=25,  # Automatically converts to page/pageSize for v3
    sort="-CreatedAt",  # Automatically converts to JSON array for v3
    where="(Status,ne,Inactive)"  # Operators converted automatically (ne -> neq)
)
```

**Key Features:**
- **Automatic Conversion**: Pagination (`offset/limit` ↔ `page/pageSize`), sort formats, and operators
- **Base ID Resolution**: Automatic table_id to base_id mapping with caching for v3
- **Full Compatibility**: All Data API and Meta API methods support both versions
- **No Code Changes**: Existing v2 code works without modifications

For detailed information, see the [API Version Guide](docs/API_VERSION_GUIDE.md) and [examples](examples/api_version_example.py).

## 📚 Documentation

### Client Configuration

The `NocoDBClient` supports various configuration options:

```python
client = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token",
    api_version="v2",                                       # API version: "v2" (default) or "v3"
    base_id="your-base-id",                                 # Base ID (optional, for v3 API)
    access_protection_auth="your-protection-token",        # Value for protection header
    access_protection_header="X-Custom-Auth",              # Custom header name (optional)
    max_redirects=3,                                        # Maximum number of redirects
    timeout=30                                              # Request timeout in seconds
)
```

#### Access Protection Header

If your NocoDB instance is protected by a reverse proxy that requires a custom authentication header:

```python
# Using default header name (X-BAUERGROUP-Auth)
client = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token",
    access_protection_auth="your-protection-token"
)

# Using custom header name
client = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token",
    access_protection_auth="your-protection-token",
    access_protection_header="X-My-Custom-Auth"
)
```

### CRUD Operations

#### Get Records

```python
# Basic retrieval
records = table.get_records()

# With filtering and sorting
records = table.get_records(
    where="(Age,gt,21)~and(Status,eq,Active)",  # Age > 21 AND Status = Active
    sort="-CreatedAt",                          # Sort by CreatedAt descending
    fields=["Id", "Name", "Email"],             # Select specific fields
    limit=50                                    # Limit results
)

# Get a single record
record = table.get_record(record_id=123, fields=["Id", "Name"])
```

#### Create Records

```python
# Insert a single record
new_record = {
    "Name": "Jane Smith",
    "Email": "jane@example.com",
    "Active": True
}
record_id = table.insert_record(new_record)
```

#### Update Records

```python
# Update an existing record
update_data = {
    "Name": "Jane Doe",
    "Status": "Updated"
}
updated_id = table.update_record(update_data, record_id=123)
```

#### Delete Records

```python
# Delete a record
deleted_id = table.delete_record(record_id=123)
```

#### Count Records

```python
# Count all records
total = table.count_records()

# Count with filter
active_count = table.count_records(where="(Status,eq,Active)")
```

### File Operations

NocoDB Simple Client provides comprehensive file management capabilities:

#### Upload Files

```python
# Attach a single file to a record
table.attach_file_to_record(
    record_id=123,
    field_name="Document",
    file_path="/path/to/your/file.pdf"
)

# Attach multiple files (appends to existing files)
table.attach_files_to_record(
    record_id=123,
    field_name="Documents",
    file_paths=["/path/file1.pdf", "/path/file2.jpg"]
)
```

#### Download Files

```python
# Download the first file from a record
table.download_file_from_record(
    record_id=123,
    field_name="Document",
    file_path="/path/to/save/downloaded_file.pdf"
)

# Download all files from a record
table.download_files_from_record(
    record_id=123,
    field_name="Documents",
    directory="/path/to/download/directory"
)
```

#### Manage Files

```python
# Remove all files from a field
table.delete_file_from_record(
    record_id=123,
    field_name="Document"
)
```

### Advanced Filtering

NocoDB Simple Client supports sophisticated filtering options:

#### Comparison Operators

```python
# Equality
records = table.get_records(where="(Status,eq,Active)")

# Numeric comparisons
records = table.get_records(where="(Age,gt,21)")      # Greater than
records = table.get_records(where="(Age,gte,21)")     # Greater than or equal
records = table.get_records(where="(Age,lt,65)")      # Less than
records = table.get_records(where="(Age,lte,65)")     # Less than or equal

# Text searches
records = table.get_records(where="(Name,like,%John%)")    # Contains "John"
records = table.get_records(where="(Email,like,%.com)")   # Ends with ".com"
```

#### Logical Operators

```python
# AND conditions
records = table.get_records(where="(Status,eq,Active)~and(Age,gt,18)")

# OR conditions
records = table.get_records(where="(Status,eq,Active)~or(Status,eq,Pending)")

# Complex combinations
records = table.get_records(
    where="((Status,eq,Active)~or(Status,eq,Pending))~and(Age,gt,18)"
)
```

#### NULL/Empty Checks

```python
# Check for empty values
records = table.get_records(where="(Email,isblank)")

# Check for non-empty values
records = table.get_records(where="(Email,isnotblank)")
```

### Sorting

```python
# Single column sorting
records = table.get_records(sort="Name")         # Ascending
records = table.get_records(sort="-CreatedAt")   # Descending

# Multiple column sorting
records = table.get_records(sort="-Status,Name") # Status desc, then Name asc
```

### Bulk Operations

Perform high-performance bulk operations for better efficiency:

```python
# Bulk insert multiple records
records_to_insert = [
    {"Name": "Alice", "Email": "alice@example.com", "Age": 28},
    {"Name": "Bob", "Email": "bob@example.com", "Age": 32},
    {"Name": "Charlie", "Email": "charlie@example.com", "Age": 45}
]
record_ids = table.bulk_insert_records(records_to_insert)
print(f"Inserted {len(record_ids)} records")

# Bulk update multiple records
records_to_update = [
    {"Id": 1, "Status": "Active"},
    {"Id": 2, "Status": "Active"},
    {"Id": 3, "Status": "Inactive"}
]
updated_ids = table.bulk_update_records(records_to_update)
print(f"Updated {len(updated_ids)} records")

# Bulk delete multiple records
record_ids_to_delete = [1, 2, 3]
deleted_ids = table.bulk_delete_records(record_ids_to_delete)
print(f"Deleted {len(deleted_ids)} records")
```

### Query Builder

Use SQL-like syntax for building complex queries:

```python
from nocodb_simple_client import NocoDBTable, NocoDBClient

client = NocoDBClient(base_url="...", db_auth_token="...")
table = NocoDBTable(client, table_id="your-table-id")

# Build a complex query
records = (table.query()
    .select('Name', 'Email', 'Status', 'Age')
    .where('Status', 'eq', 'Active')
    .where_and('Age', 'gt', 18)
    .where_or('Role', 'eq', 'Admin')
    .order_by('CreatedAt', 'desc')
    .limit(50)
    .offset(10)
    .execute())

# Use convenience methods
first_record = (table.query()
    .where('Email', 'eq', 'john@example.com')
    .first())

# Check if records exist
has_active_users = (table.query()
    .where('Status', 'eq', 'Active')
    .exists())

# Count matching records
active_count = (table.query()
    .where('Status', 'eq', 'Active')
    .count())

# Advanced filtering
records = (table.query()
    .select('Name', 'Email')
    .where_in('Status', ['Active', 'Pending'])
    .where_not_null('Email')
    .where_between('Age', 25, 65)
    .where_like('Name', '%John%')
    .order_by_desc('CreatedAt')
    .page(2, 25)  # Page 2 with 25 records per page
    .execute())
```

### Filter and Sort Builders

For advanced filtering and sorting without the full query builder:

```python
from nocodb_simple_client.filter_builder import FilterBuilder, SortBuilder

# Build complex filters
filter_builder = FilterBuilder()
filter_str = (filter_builder
    .where('Status', 'eq', 'Active')
    .and_('Age', 'gt', 21)
    .or_('Role', 'eq', 'Admin')
    .build())

# Use with get_records
records = table.get_records(where=filter_str, limit=100)

# Build sorts
sort_builder = SortBuilder()
sort_str = (sort_builder
    .desc('CreatedAt')
    .asc('Name')
    .build())

records = table.get_records(sort=sort_str)
```

### Configuration Management

Multiple ways to configure the client:

```python
from nocodb_simple_client import NocoDBClient, NocoDBConfig
from pathlib import Path

# Method 1: Direct parameters
client = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token"
)

# Method 2: From environment variables
# Set environment variables: NOCODB_BASE_URL, NOCODB_API_TOKEN
config = NocoDBConfig.from_env()
client = NocoDBClient(config)

# Method 3: From configuration file (JSON, YAML, or TOML)
config = NocoDBConfig.from_file(Path("config.json"))
client = NocoDBClient(config)

# Advanced configuration
config = NocoDBConfig(
    base_url="https://app.nocodb.com",
    api_token="your-token",
    timeout=60.0,
    max_retries=5,
    backoff_factor=0.5,
    pool_connections=20,
    pool_maxsize=40,
    verify_ssl=True,
    debug=False,
    log_level="INFO"
)
client = NocoDBClient(config)
```

## 🔧 Meta API Operations

The Meta API allows you to programmatically manage your NocoDB structure, including workspaces, bases, tables, columns, views, and webhooks.

### Meta Client Initialization

```python
from nocodb_simple_client import NocoDBMetaClient, NocoDBConfig

# Initialize Meta API client with v2 (default)
meta_client = NocoDBMetaClient(
    base_url="https://app.nocodb.com",
    api_token="your-api-token"
)

# Initialize with v3 API
meta_client_v3 = NocoDBMetaClient(
    base_url="https://app.nocodb.com",
    api_token="your-api-token",
    api_version="v3",
    base_id="your-base-id"  # Optional, can be auto-resolved
)

# Or with config
config = NocoDBConfig(base_url="...", api_token="...")
meta_client = NocoDBMetaClient(config)

# Meta client inherits all data operations from NocoDBClient
# So you can use it for both meta operations AND data operations
# Both v2 and v3 are fully supported!
records = meta_client.get_records("table_id")  # Data operation
tables = meta_client.list_tables("base_id")     # Meta operation
```

### Workspace Operations

```python
# List all workspaces
workspaces = meta_client.list_workspaces()
for workspace in workspaces:
    print(f"Workspace: {workspace['title']} (ID: {workspace['id']})")

# Get workspace details
workspace = meta_client.get_workspace("workspace_id")

# Create a new workspace
workspace_data = {
    "title": "My Workspace",
    "description": "Team workspace for projects"
}
new_workspace = meta_client.create_workspace(workspace_data)

# Update workspace
meta_client.update_workspace("workspace_id", {"title": "Updated Name"})

# Delete workspace (careful - deletes all bases!)
meta_client.delete_workspace("workspace_id")
```

### Base Operations

```python
# List all bases
bases = meta_client.list_bases()
for base in bases:
    print(f"Base: {base['title']} (ID: {base['id']})")

# Get base details
base = meta_client.get_base("base_id")

# Create a new base
base_data = {
    "title": "My Project Database",
    "description": "Project management database"
}
new_base = meta_client.create_base("workspace_id", base_data)

# Update base
meta_client.update_base("base_id", {"title": "Updated Project"})

# Delete base (careful - deletes all tables!)
meta_client.delete_base("base_id")
```

### Table Structure Operations

```python
# List all tables in a base
tables = meta_client.list_tables("base_id")
for table in tables:
    print(f"Table: {table['title']} (ID: {table['id']})")

# Get detailed table information (including columns and relationships)
table_info = meta_client.get_table_info("table_id")
print(f"Table has {len(table_info['columns'])} columns")

# Create a new table
table_data = {
    "title": "Users",
    "table_name": "users",
    "columns": [
        {"title": "Name", "column_name": "name", "uidt": "SingleLineText"},
        {"title": "Email", "column_name": "email", "uidt": "Email"},
        {"title": "Age", "column_name": "age", "uidt": "Number"}
    ]
}
new_table = meta_client.create_table("base_id", table_data)

# Update table metadata
meta_client.update_table("table_id", {"title": "Active Users"})

# Delete table (careful - deletes all data!)
meta_client.delete_table("table_id")
```

### Column Management

```python
from nocodb_simple_client import NocoDBMetaClient
from nocodb_simple_client.columns import NocoDBColumns

meta_client = NocoDBMetaClient(base_url="...", api_token="...")
columns_manager = NocoDBColumns(meta_client)

# List all columns in a table
columns = columns_manager.get_columns("table_id")
for col in columns:
    print(f"Column: {col['title']} - Type: {col['uidt']}")

# Create different types of columns

# Text column
text_col = columns_manager.create_text_column(
    "table_id",
    title="Description",
    max_length=500,
    default_value="N/A"
)

# Number column
number_col = columns_manager.create_number_column(
    "table_id",
    title="Price",
    precision=10,
    scale=2
)

# Checkbox column
checkbox_col = columns_manager.create_checkbox_column(
    "table_id",
    title="Is Active",
    default_value=True
)

# Single select column
select_col = columns_manager.create_singleselect_column(
    "table_id",
    title="Status",
    options=[
        {"title": "Active", "color": "#00ff00"},
        {"title": "Inactive", "color": "#ff0000"},
        {"title": "Pending", "color": "#ffaa00"}
    ]
)

# Date column
date_col = columns_manager.create_date_column(
    "table_id",
    title="Start Date",
    date_format="YYYY-MM-DD"
)

# Email column
email_col = columns_manager.create_email_column(
    "table_id",
    title="Contact Email",
    validate=True
)

# URL column
url_col = columns_manager.create_url_column(
    "table_id",
    title="Website",
    validate=True
)

# Rating column
rating_col = columns_manager.create_rating_column(
    "table_id",
    title="User Rating",
    max_rating=5,
    icon="star",
    color="#fcb401"
)

# Formula column
formula_col = columns_manager.create_formula_column(
    "table_id",
    title="Full Name",
    formula="{FirstName} & ' ' & {LastName}"
)

# Link/Relation column
link_col = columns_manager.create_link_column(
    "table_id",
    title="Orders",
    related_table_id="orders_table_id",
    relation_type="hm"  # has many
)

# Update a column
columns_manager.update_column(
    "table_id",
    "column_id",
    title="Updated Name",
    cdf="new default value"
)

# Delete a column
columns_manager.delete_column("table_id", "column_id")

# Find column by name
column = columns_manager.get_column_by_name("table_id", "Email")
if column:
    print(f"Found column: {column['id']}")
```

### View Management

```python
from nocodb_simple_client import NocoDBMetaClient
from nocodb_simple_client.views import NocoDBViews

meta_client = NocoDBMetaClient(base_url="...", api_token="...")
views_manager = NocoDBViews(meta_client)

# List all views for a table
views = views_manager.get_views("table_id")
for view in views:
    print(f"View: {view['title']} - Type: {view['type']}")

# Create different types of views
grid_view = views_manager.create_view(
    "table_id",
    title="Active Users",
    view_type="grid",
    options={"show_system_fields": False}
)

gallery_view = views_manager.create_view(
    "table_id",
    title="User Gallery",
    view_type="gallery"
)

form_view = views_manager.create_view(
    "table_id",
    title="User Registration Form",
    view_type="form"
)

kanban_view = views_manager.create_view(
    "table_id",
    title="Project Kanban",
    view_type="kanban"
)

# Add filters to a view
filter_data = views_manager.create_view_filter(
    "table_id",
    "view_id",
    column_id="column_id",
    comparison_op="eq",
    value="Active",
    logical_op="and"
)

# Add sorting to a view
sort_data = views_manager.create_view_sort(
    "table_id",
    "view_id",
    column_id="column_id",
    direction="desc"
)

# Update view column visibility and order
views_manager.update_view_column(
    "table_id",
    "view_id",
    "column_id",
    {"show": True, "order": 1, "width": 200}
)

# Get data from a view (with filters/sorts applied)
view_data = views_manager.get_view_data(
    "table_id",
    "view_id",
    fields=["Name", "Email", "Status"],
    limit=50
)

# Duplicate a view
duplicated_view = views_manager.duplicate_view(
    "table_id",
    "view_id",
    "Copy of Active Users"
)

# Delete a view
views_manager.delete_view("table_id", "view_id")
```

### Webhook Automation

```python
from nocodb_simple_client import NocoDBMetaClient
from nocodb_simple_client.webhooks import NocoDBWebhooks

meta_client = NocoDBMetaClient(base_url="...", api_token="...")
webhooks_manager = NocoDBWebhooks(meta_client)

# List all webhooks for a table
webhooks = webhooks_manager.get_webhooks("table_id")
for webhook in webhooks:
    print(f"Webhook: {webhook['title']} - Active: {webhook.get('active')}")

# Create a URL webhook
webhook = webhooks_manager.create_webhook(
    "table_id",
    title="New User Notification",
    event_type="after",
    operation="insert",
    url="https://api.example.com/webhook",
    method="POST",
    headers={"Authorization": "Bearer token123"},
    body='{"user": "{{Name}}", "email": "{{Email}}"}',
    active=True
)

# Create an Email webhook
email_webhook = webhooks_manager.create_email_webhook(
    "table_id",
    title="Alert on Update",
    event_type="after",
    operation="update",
    emails=["admin@example.com", "team@example.com"],
    subject="Record Updated: {{Name}}",
    body="Record {{Id}} has been updated.",
    active=True
)

# Create a Slack webhook
slack_webhook = webhooks_manager.create_slack_webhook(
    "table_id",
    title="Slack Notification",
    event_type="after",
    operation="insert",
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    message="New record created: {{Name}}",
    active=True
)

# Create a Microsoft Teams webhook
teams_webhook = webhooks_manager.create_teams_webhook(
    "table_id",
    title="Teams Notification",
    event_type="after",
    operation="delete",
    webhook_url="https://outlook.office.com/webhook/YOUR_WEBHOOK",
    message="Record deleted: {{Name}}",
    active=True
)

# Update a webhook
webhooks_manager.update_webhook(
    "table_id",
    "webhook_id",
    title="Updated Notification",
    url="https://new-api.example.com/webhook",
    active=False
)

# Test a webhook
test_result = webhooks_manager.test_webhook("table_id", "webhook_id")
print(f"Test result: {test_result}")

# Get webhook execution logs
logs = webhooks_manager.get_webhook_logs("table_id", "webhook_id", limit=10)
for log in logs:
    print(f"Execution at {log.get('created_at')}: {log.get('status')}")

# Toggle webhook active status
webhooks_manager.toggle_webhook("table_id", "webhook_id")

# Delete a webhook
webhooks_manager.delete_webhook("table_id", "webhook_id")
```

### Link/Relation Management

```python
from nocodb_simple_client import NocoDBClient
from nocodb_simple_client.links import NocoDBLinks

client = NocoDBClient(base_url="...", db_auth_token="...")
links_manager = NocoDBLinks(client)

# Get linked records
linked_records = links_manager.get_linked_records(
    "table_id",
    record_id=123,
    link_field_id="column_id",
    fields=["Name", "Email"],
    sort="-CreatedAt",
    limit=25
)

# Count linked records
count = links_manager.count_linked_records(
    "table_id",
    record_id=123,
    link_field_id="column_id"
)
print(f"This record has {count} linked records")

# Link records to a record
links_manager.link_records(
    "table_id",
    record_id=123,
    link_field_id="column_id",
    linked_record_ids=[456, 789, 101]
)

# Unlink specific records
links_manager.unlink_records(
    "table_id",
    record_id=123,
    link_field_id="column_id",
    linked_record_ids=[456, 789]
)

# Unlink all records
links_manager.unlink_all_records(
    "table_id",
    record_id=123,
    link_field_id="column_id"
)

# Replace all links with new ones
links_manager.replace_links(
    "table_id",
    record_id=123,
    link_field_id="column_id",
    new_linked_record_ids=[111, 222, 333]
)

# Bulk link operations
operations = [
    {
        "table_id": "table1",
        "record_id": 1,
        "link_field_id": "col1",
        "linked_record_ids": [10, 20],
        "action": "link"
    },
    {
        "table_id": "table1",
        "record_id": 2,
        "link_field_id": "col1",
        "linked_record_ids": [30],
        "action": "unlink"
    }
]
results = links_manager.bulk_link_records(operations)
print(f"Operations successful: {sum(results)}/{len(results)}")
```

## 🛡️ Error Handling

The client provides specific exceptions for different error scenarios:

```python
from nocodb_simple_client import NocoDBException, RecordNotFoundException

try:
    record = table.get_record(record_id=99999)
except RecordNotFoundException as e:
    print(f"Record not found: {e.message}")
except NocoDBException as e:
    print(f"NocoDB API error: {e.error} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Exception Types

- `NocoDBException`: Base exception for all NocoDB-related errors
- `RecordNotFoundException`: Thrown when a requested record doesn't exist

## 🧪 Examples

Check out the [`examples/`](examples/) directory for comprehensive examples:

- **[Basic Usage](examples/basic_usage.py)**: CRUD operations and fundamentals
- **[API Version Support](examples/api_version_example.py)**: Using v2 and v3 APIs with automatic conversion
- **[Meta API Version Support](examples/meta_api_version_example.py)**: Meta API operations with v2/v3
- **[File Operations](examples/file_operations.py)**: File upload/download examples
- **[Advanced Querying](examples/advanced_querying.py)**: Complex filtering and sorting with Query Builder
- **[Context Manager Usage](examples/context_manager_usage.py)**: Proper resource management
- **[Bulk Operations](examples/bulk_operations.py)**: High-performance bulk insert, update, and delete
- **[Meta API Operations](examples/meta_operations.py)**: Workspace, Base, Table, Column, View management
- **[Webhook Automation](examples/webhook_examples.py)**: Creating and managing webhooks
- **[Link Management](examples/link_examples.py)**: Managing relationships between tables
- **[Configuration](examples/config_examples.py)**: Different configuration methods

## 📋 Requirements

- Python 3.8 or higher
- `requests >= 2.25.0`
- `requests-toolbelt >= 0.9.1`

## 🔧 Development

### Quick Setup

Use the automated setup script for your platform:

```bash
# Windows
scripts\setup.cmd

# macOS/Linux
./scripts/setup.sh

# Or run Python directly (cross-platform)
python scripts/setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Setup pre-commit hooks
- Verify the installation

### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/bauer-group/LIB-NocoDB_SimpleClient.git
cd nocodb-simple-client
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev,docs]"
pre-commit install
```

### Local Validation

Use these commands to validate your code locally:

#### Quick Validation
```bash
# Windows
scripts\quick-test.cmd

# macOS/Linux
./scripts/quick-test.sh

# Or cross-platform
python scripts/quick-test.py
```

#### Complete Validation
```bash
# Windows
scripts\validate.cmd

# macOS/Linux
./scripts/validate.sh

# Or cross-platform
python scripts/validate.py
```

#### Individual Commands
```bash
# Code formatting
black src/ tests/
ruff --fix src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/nocodb_simple_client/

# Security scan
bandit -r src/

# Run tests
pytest

# Test with coverage
pytest --cov=src/nocodb_simple_client --cov-report=html

# Fast tests only (skip slow/integration tests)
pytest -m "not slow and not integration"

# Build package
python -m build
```

#### Using Makefile (macOS/Linux)
```bash
# See all available commands
make help

# Install dev dependencies
make install-dev

# Run all checks
make all-checks

# Quick test
make test-fast

# Format code
make format

# Generate coverage report
make test-cov
```

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit:

```bash
# Install hooks (done automatically by setup script)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Build and Test Package

```bash
# Build package
python -m build

# Test installation
pip install dist/nocodb_simple_client-*.whl

# Clean build artifacts (Windows)
rmdir /s build dist *.egg-info

# Clean build artifacts (macOS/Linux)
rm -rf build/ dist/ *.egg-info/
```

### Development Workflow

1. **Setup**: Run setup script for your platform
2. **Code**: Make your changes
3. **Quick Test**: Run `python scripts/quick-test.py`
4. **Full Validation**: Run `python scripts/validate.py`
5. **Commit**: Pre-commit hooks will run automatically
6. **Push**: CI will run full test suite

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.MD](CONTRIBUTING.MD) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run code quality checks (`black .`, `ruff check .`, `mypy src/nocodb_simple_client`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NocoDB](https://nocodb.com/) team for creating an amazing open-source Airtable alternative
- The Python community for excellent tooling and libraries
- Contributors who help improve this client

## 📞 Support

- **Documentation**: You're reading it! 📖
- **Issues**: [GitHub Issues](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/discussions)
- **Email**: support@bauer-group.com

## 📊 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Made with ❤️ by [BAUER GROUP](https://go.bauer-group.com)**

*If this library helps you build something awesome, we'd love to hear about it!*

---

*Generated on 2025-10-10 13:15:12 UTC from [docs/README.template.MD](docs/README.template.MD)*
