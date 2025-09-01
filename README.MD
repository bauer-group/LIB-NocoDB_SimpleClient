<!-- AUTO-GENERATED FILE. DO NOT EDIT. Edit docs/README.template.MD instead. -->
<!-- Generated on 2025-09-01 20:59:19 UTC -->

# BAUER GROUP - NocoDB Simple Client

[![PyPI Version](https://badge.fury.io/py/nocodb-simple-client.svg)](https://badge.fury.io/py/nocodb-simple-client)
[![Python Support](https://img.shields.io/pypi/pyversions/nocodb-simple-client.svg)](https://pypi.org/project/nocodb-simple-client/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![🐍 CI/CD](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/actions/workflows/python-automatic-release.yml/badge.svg)](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/actions/workflows/python-automatic-release.yml)


A simple and powerful Python client for interacting with [NocoDB](https://nocodb.com/) REST API. This client provides an intuitive interface for performing CRUD operations, managing file attachments, and handling complex queries on your NocoDB tables.

**Repository Information:**

- **Version:** v1.1.0 (2025-09-01)
- **Repository:** [bauer-group/LIB-NocoDB_SimpleClient](https://github.com/bauer-group/LIB-NocoDB_SimpleClient)
- **Branch:** main
- **Architecture:** Modular, Reusable, Enterprise-Ready

## 🌟 Features

- **Easy to Use**: Intuitive API design with comprehensive documentation
- **Full CRUD Operations**: Create, read, update, and delete records with ease
- **File Management**: Upload, download, and manage file attachments
- **Advanced Querying**: Complex filtering, sorting, and pagination support
- **Type Hints**: Full type annotation support for better IDE experience
- **Error Handling**: Comprehensive exception handling with specific error types
- **Context Manager**: Automatic resource management with context manager support
- **Flexible Configuration**: Support for custom timeouts, redirects, and authentication
- **Production Ready**: Robust error handling and resource management

## 🚀 Quick Start

### Installation

Install from PyPI using pip:

```bash
pip install nocodb-simple-client
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

## 📚 Documentation

### Client Configuration

The `NocoDBClient` supports various configuration options:

```python
client = NocoDBClient(
    base_url="https://your-nocodb-instance.com",
    db_auth_token="your-api-token",
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
- **[File Operations](examples/file_operations.py)**: File upload/download examples
- **[Advanced Querying](examples/advanced_querying.py)**: Complex filtering and sorting
- **[Context Manager Usage](examples/context_manager_usage.py)**: Proper resource management

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

See [CHANGELOG.MD](CHANGELOG.MD) for a detailed history of changes.

---

**Made with ❤️ by [BAUER GROUP](https://bauer-group.com)**

*If this library helps you build something awesome, we'd love to hear about it!*

---

*Generated on 2025-09-01 20:59:19 UTC from [docs/README.template.MD](docs/README.template.MD)*
