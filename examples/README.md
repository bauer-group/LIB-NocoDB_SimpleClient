# NocoDB Simple Client - Examples

This directory contains comprehensive examples demonstrating how to use the NocoDB Simple Client library.

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

**Purpose**: Introduction to core CRUD operations

**What you'll learn**:

- Client initialization and configuration
- Creating, reading, updating, and deleting records
- Basic filtering and sorting
- Record counting
- Error handling fundamentals

**Best for**: Beginners getting started with the library

### 2. File Operations (`file_operations.py`)

**Purpose**: Working with file attachments in NocoDB

**What you'll learn**:

- Uploading files to records
- Downloading files from records
- Managing multiple file attachments
- Handling file metadata
- Bulk file operations

**Best for**: Applications that need document/media management

### 3. Advanced Querying (`advanced_querying.py`)

**Purpose**: Sophisticated data retrieval techniques

**What you'll learn**:

- Complex filtering with multiple conditions
- Advanced sorting strategies
- Field selection optimization
- Pagination handling
- Statistical queries
- Date and numeric comparisons

**Best for**: Applications with complex data analysis needs

### 4. Context Manager Usage (`context_manager_usage.py`)

**Purpose**: Proper resource management and error handling

**What you'll learn**:

- Using context managers for automatic cleanup
- Proper exception handling
- Working with multiple tables
- Resource management best practices
- Error recovery strategies

**Best for**: Production applications requiring robust error handling

## Configuration

Before running the examples, you'll need to configure:

1. **NocoDB Instance URL**: Your NocoDB server URL
2. **API Token**: Your authentication token from NocoDB
3. **Table ID**: The ID of the table you want to work with

### Getting Your Configuration Values

#### 1. NocoDB Base URL

Your NocoDB instance URL, for example:

- Self-hosted: `https://your-nocodb-domain.com`
- NocoDB Cloud: `https://app.nocodb.com`

#### 2. API Token

1. Log into your NocoDB instance
2. Go to your profile settings
3. Generate an API token
4. Copy the token value

#### 3. Table ID

1. Open your table in NocoDB
2. Look at the URL in your browser
3. The table ID is the string after `/table/`

Example URL: `https://app.nocodb.com/dashboard/table/m12345abcdef`
Table ID: `m12345abcdef`

## Running the Examples

### Method 1: Direct Execution

```bash
# Update configuration in the example file first
python examples/basic_usage.py
```

### Method 2: Environment Variables

Create a `.env` file in the project root:

```env
NOCODB_BASE_URL=https://your-nocodb-instance.com
NOCODB_API_TOKEN=your-api-token-here
NOCODB_TABLE_ID=your-table-id-here
```

Then modify the examples to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

NOCODB_BASE_URL = os.getenv('NOCODB_BASE_URL')
API_TOKEN = os.getenv('NOCODB_API_TOKEN')
TABLE_ID = os.getenv('NOCODB_TABLE_ID')
```

### Method 3: Interactive Configuration

Run the interactive setup script:

```bash
python examples/setup_config.py
```

## Example Data Structure

Most examples assume your NocoDB table has these common fields:

- `Id` (Auto-generated)
- `Name` (Single Line Text)
- `Email` (Email)
- `Age` (Number)
- `Status` (Single Select: Active, Inactive, Pending)
- `CreatedAt` (DateTime)
- `Description` (Long Text)

For file examples, you'll also need:

- `Document` (Attachment field)

## Common Patterns

### Error Handling Pattern

```python
try:
    # Your NocoDB operations
    records = table.get_records(limit=10)
except RecordNotFoundException as e:
    print(f"Record not found: {e.message}")
except NocoDBException as e:
    print(f"NocoDB error: {e.error} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Context Manager Pattern

```python
with NocoDBClient(base_url=URL, db_auth_token=TOKEN) as client:
    table = NocoDBTable(client, table_id=TABLE_ID)
    # Your operations here
    # Client automatically closes
```

### Pagination Pattern

```python
# The client handles pagination automatically
all_records = table.get_records(limit=500)  # Gets all records up to 500
```

## Tips for Using Examples

1. **Start Small**: Begin with `basic_usage.py` to understand fundamentals
2. **Test Safely**: Use a test table first, not production data
3. **Check Your Schema**: Ensure your table has the expected fields
4. **Handle Errors**: Always implement proper error handling
5. **Use Context Managers**: Prefer the `with` statement for resource management

## Troubleshooting

### Common Issues

**"Table not found" error**:

- Verify your table ID is correct
- Check that your API token has access to the table

**"Authentication failed" error**:

- Verify your API token is valid and not expired
- Check your base URL is correct

**"Field not found" error**:

- Ensure the field names match your table schema
- Field names are case-sensitive

**Connection timeout**:

- Increase the timeout parameter in client initialization
- Check your network connection to NocoDB

### Getting Help

1. Check the main README.md for basic setup
2. Review the API documentation at [NocoDB Docs](https://docs.nocodb.com/)
3. Open an issue on GitHub if you find bugs
4. Contact the maintainers for specific questions

## Contributing Examples

We welcome additional examples! If you create a useful example:

1. Follow the existing code style
2. Include comprehensive comments
3. Add error handling
4. Update this README with a description
5. Submit a pull request

## Next Steps

After working through these examples:

1. Read the full API documentation
2. Check out the test files for more usage patterns
3. Consider contributing back to the project
4. Build something awesome! 🚀
