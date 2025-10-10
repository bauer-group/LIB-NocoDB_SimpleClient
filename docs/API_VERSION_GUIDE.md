# NocoDB API Version Guide (v2 vs v3)

## Overview

The NocoDB Simple Client now supports both **API v2** (default) and **API v3** with seamless switching between versions.

## Quick Start

### Using API v2 (Default)

```python
from nocodb_simple_client import NocoDBClient

# v2 is the default - no changes needed to existing code
client = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token"
)

# All existing code works without modification
records = client.get_records("table_id", limit=10)
```

### Using API v3

```python
from nocodb_simple_client import NocoDBClient

# Specify v3 and provide base_id
client = NocoDBClient(
    base_url="https://app.nocodb.com",
    db_auth_token="your-api-token",
    api_version="v3",
    base_id="your_base_id"  # Required for v3
)

# Same API, same syntax!
records = client.get_records("table_id", limit=10)
```

## Key Differences Between v2 and v3

### 1. **Base ID Requirement**

| Aspect | v2 | v3 |
|--------|----|----|
| **Base ID** | Optional (implicit) | **Required** in all operations |
| **How to provide** | Not needed | Set in constructor or per-method |

**v3 Examples:**

```python
# Option 1: Set default base_id in constructor (recommended)
client = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v3",
    base_id="base_abc123"  # Used for all operations
)

records = client.get_records("table_xyz")  # base_id used automatically

# Option 2: Provide base_id per method call
client = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v3"
)

records = client.get_records("table_xyz", base_id="base_abc123")
```

### 2. **Pagination**

| Aspect | v2 | v3 |
|--------|----|----|
| **Parameters** | `offset` and `limit` | `page` and `pageSize` |
| **Conversion** | Automatic | Handled internally |

**You don't need to change your code!** The client automatically converts:

```python
# Your code (same for both v2 and v3):
records = client.get_records("table_id", limit=25)

# v2 internally uses: offset=0, limit=25
# v3 internally converts to: page=1, pageSize=25
```

### 3. **Sort Format**

| Aspect | v2 | v3 |
|--------|----|----|
| **Format** | String: `"field1,-field2"` | JSON array |
| **Conversion** | Automatic | Handled internally |

**You don't need to change your code!**

```python
# Your code (same for both v2 and v3):
records = client.get_records(
    "table_id",
    sort="Name,-CreatedAt"  # Name ASC, CreatedAt DESC
)

# v2 uses as-is: "Name,-CreatedAt"
# v3 converts to: [{"field": "Name", "direction": "asc"},
#                  {"field": "CreatedAt", "direction": "desc"}]
```

### 4. **Query Operators**

| Operator | v2 | v3 |
|----------|----|----|
| Not Equal | `ne` | `neq` |
| Others | Same | Same |

**Conversion handled automatically!**

## API Methods Support

All methods support both v2 and v3:

✅ **Record Operations**
- `get_records()`
- `get_record()`
- `insert_record()`
- `update_record()`
- `delete_record()`
- `count_records()`

✅ **Bulk Operations**
- `bulk_insert_records()`
- `bulk_update_records()`
- `bulk_delete_records()`

✅ **File Operations**
- `attach_file_to_record()`
- `attach_files_to_record()`
- `delete_file_from_record()`
- `download_file_from_record()`
- `download_files_from_record()`

## Migration Guide

### Step 1: Test v3 in Parallel

```python
# Keep existing v2 client
client_v2 = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v2"
)

# Create v3 client for testing
client_v3 = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v3",
    base_id="your_base_id"
)

# Compare results
records_v2 = client_v2.get_records("table_id")
records_v3 = client_v3.get_records("table_id")
```

### Step 2: Switch When Ready

```python
# Simply change these two lines:
client = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v3",        # Changed from "v2"
    base_id="your_base_id"   # Added this line
)

# All other code remains the same!
```

## Advanced Features

### Base ID Resolver

For v3, the client includes automatic base ID resolution:

```python
client = NocoDBClient(
    base_url="...",
    db_auth_token="...",
    api_version="v3",
    base_id="default_base"
)

# Can manually set base_id mappings
client._base_resolver.set_base_id("table_123", "base_abc")

# Clear cache if needed
client._base_resolver.clear_cache()
```

### Query Parameter Adapter

Advanced users can access the parameter adapter directly:

```python
from nocodb_simple_client import QueryParamAdapter

adapter = QueryParamAdapter()

# Convert pagination
v3_params = adapter.convert_pagination_to_v3({"offset": 50, "limit": 25})
# Returns: {"page": 3, "pageSize": 25}

# Convert sort format
v3_sort = adapter.convert_sort_to_v3("name,-age")
# Returns: [{"field": "name", "direction": "asc"},
#           {"field": "age", "direction": "desc"}]
```

### Path Builder

Build API paths programmatically:

```python
from nocodb_simple_client import PathBuilder, APIVersion

# Create builder for v3
builder = PathBuilder(APIVersion.V3)

# Build record endpoint
path = builder.records_list("table_123", "base_abc")
# Returns: "api/v3/data/base_abc/table_123/records"
```

## Troubleshooting

### Error: "base_id is required for API v3"

**Solution:** Provide `base_id` either in the constructor or method call:

```python
# Option 1: In constructor
client = NocoDBClient(..., api_version="v3", base_id="your_base_id")

# Option 2: Per method
records = client.get_records("table_id", base_id="your_base_id")
```

### Pagination Not Working as Expected

The client automatically converts pagination parameters. If you experience issues, ensure you're using the standard `limit` parameter:

```python
# ✅ Correct
records = client.get_records("table_id", limit=25)

# ❌ Don't manually specify page/pageSize for v3
records = client.get_records("table_id", page=1, pageSize=25)  # Wrong!
```

## Performance Considerations

### Base ID Caching

When using v3, the client caches base_id lookups:

```python
# First call: Makes API request to resolve base_id
client.get_records("table_123")

# Subsequent calls: Uses cached base_id (faster)
client.get_records("table_123")

# Clear cache if base_id changes
client._base_resolver.clear_cache("table_123")
```

### Batch Operations

Both v2 and v3 support bulk operations for better performance:

```python
# Insert multiple records at once
records = [
    {"Name": "John", "Age": 30},
    {"Name": "Jane", "Age": 25},
]

record_ids = client.bulk_insert_records("table_id", records)
```

## Best Practices

1. **Use v3 for new projects** - v3 is the future of NocoDB API
2. **Set base_id in constructor** - Cleaner code and better performance
3. **Test thoroughly** - Use parallel testing before migrating production code
4. **Don't mix parameters** - Let the client handle conversions automatically
5. **Cache base_id mappings** - Pre-populate resolver for known tables

## Examples

See complete examples in:
- [`examples/api_version_example.py`](../examples/api_version_example.py)

## Resources

- [API v2 to v3 Migration Guide](../API_V2_V3_MIGRATION_GUIDE.md)
- [Detailed API Comparison](../NOCODB_API_V2_V3_COMPARISON.md)
- [Schema Differences](../NOCODB_API_SCHEMA_COMPARISON.md)
