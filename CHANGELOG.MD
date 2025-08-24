# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release preparation
- Comprehensive documentation and examples

## [1.0.0] - 2024-01-XX

### Added
- Complete rewrite and restructuring of the original NocoDB client
- Full type hints support with Python 3.8+ compatibility
- Context manager support for automatic resource management
- Comprehensive error handling with specific exception types
- File operations: upload, download, and manage attachments
- Advanced querying capabilities with complex filtering
- Support for pagination (handled automatically)
- Multiple file attachment support
- Robust HTTP session management
- Configuration options for timeouts and redirects
- Production-ready code with proper resource cleanup

### Changed
- **BREAKING**: Package renamed from `NocoDB_SimpleClient` to `nocodb-simple-client`
- **BREAKING**: Module structure changed to `nocodb_simple_client`
- **BREAKING**: Improved API design with consistent method signatures
- Enhanced error messages and exception hierarchy
- Modern Python packaging with `pyproject.toml`
- Improved documentation with comprehensive examples

### Fixed
- Proper handling of HTTP errors and API responses
- Resource leaks in file operations
- Pagination issues with large datasets
- Memory efficiency improvements for file operations

### Security
- Secure file handling with proper path validation
- Enhanced input validation for API parameters
- Safe handling of authentication tokens

## [0.3.0] - 2023-XX-XX (Legacy Version)

### Added
- Basic CRUD operations
- File upload/download functionality
- Simple error handling
- Initial NocoDB API v2 support

### Notes
- This was the last version of the legacy `NocoDB_SimpleClient` package
- Users should migrate to v1.0.0+ for improved functionality and security

---

## Migration Guide from 0.x to 1.0.0

### Package Installation
```bash
# Old
pip install NocoDB_SimpleClient

# New  
pip install nocodb-simple-client
```

### Import Changes
```python
# Old
from NocoDB_SimpleClient import NocoDBClient, NocoDBTable, NocoDBException, RecordNotFoundException

# New
from nocodb_simple_client import NocoDBClient, NocoDBTable, NocoDBException, RecordNotFoundException
```

### API Changes

#### Client Initialization
```python
# Old - still works
client = NocoDBClient(base_url="...", db_auth_token="...")

# New - recommended with context manager
with NocoDBClient(base_url="...", db_auth_token="...") as client:
    # Your operations
    pass
```

#### File Operations
```python
# Old method signature
client.attach_file_to_record(table_id, record_id, field_name, file)

# New method signature (more consistent)
table.attach_file_to_record(record_id, field_name, file_path)
```

#### Error Handling
```python
# Old - basic error handling
try:
    records = table.get_records()
except Exception as e:
    print(f"Error: {e}")

# New - specific exception handling
try:
    records = table.get_records()
except RecordNotFoundException as e:
    print(f"Record not found: {e.message}")
except NocoDBException as e:
    print(f"NocoDB error: {e.error} - {e.message}")
```

### New Features in 1.0.0+

1. **Type Hints**: Full type annotation support
2. **Context Managers**: Automatic resource management
3. **Enhanced File Operations**: Multiple file support, better error handling
4. **Advanced Querying**: Complex filtering and sorting options
5. **Better Documentation**: Comprehensive examples and API documentation

### Deprecation Notices

- The legacy `NocoDB_SimpleClient` package will receive security updates only
- New features will only be added to `nocodb-simple-client` v1.0.0+
- Users are strongly encouraged to migrate to the new package