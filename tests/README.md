# NocoDB Simple Client Tests

This directory contains comprehensive tests for the NocoDB Simple Client library.

## Test Structure

### Test Types

1. **Unit Tests** (`test_*.py`) - Mock-based tests for individual components
2. **Integration Tests** (`test_*_integration.py`) - Tests requiring real NocoDB instance
3. **Performance Tests** (marked with `@pytest.mark.performance`) - Optional performance benchmarks

### Test Configuration

Tests are configured to use environment variables or a local `.env` file for configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your NocoDB instance details
NOCODB_BASE_URL=http://localhost:8080
NOCODB_TOKEN=your-api-token-here
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOCODB_BASE_URL` | `http://localhost:8080` | NocoDB server URL |
| `NOCODB_TOKEN` | **Required** | API token for authentication |
| `NOCODB_PROJECT_ID` | Auto-generated | Specific project ID (optional) |
| `TEST_TABLE_PREFIX` | `test_` | Prefix for test table names |
| `CLEANUP_TEST_DATA` | `true` | Clean up test data after tests |
| `RUN_INTEGRATION_TESTS` | `true` | Enable/disable integration tests |
| `SKIP_SLOW_TESTS` | `false` | Skip slow-running tests |
| `TEST_TIMEOUT` | `30` | Test timeout in seconds |
| `TEST_UPLOAD_DIR` | `./test_uploads` | Directory for temporary test files |
| `MAX_FILE_SIZE_MB` | `1` | Maximum file size for upload tests (MB) |
| `PERFORMANCE_TEST_RECORDS` | `1000` | Number of records for performance tests |
| `BULK_TEST_BATCH_SIZE` | `100` | Batch size for bulk operations |

## Running Tests

### Local Development

```bash
# Standard pytest commands
python -m pytest                                    # Unit tests only
python -m pytest -m "not integration and not performance"  # Explicit unit tests
python -m pytest -m integration                     # Integration tests only
python -m pytest -m performance                     # Performance tests only
python -m pytest tests/test_client.py               # Specific test file
python -m pytest --cov=src/nocodb_simple_client --cov-report=html  # With coverage

# Using the project runner script (recommended)
python scripts/run-all.py                           # Unit tests only (CI safe)
python scripts/run-all.py --integration             # Include integration tests
python scripts/run-all.py --performance             # Include performance tests
python scripts/run-all.py --all-tests               # All test types
python scripts/run-all.py --ci                      # CI mode (minimal output)
python scripts/run-all.py --no-cleanup              # Skip cleanup (debugging)
python scripts/run-all.py --help                    # Show all options
```

### Test Markers

- `@pytest.mark.integration` - Requires real NocoDB instance
- `@pytest.mark.slow` - May take longer to execute
- `@pytest.mark.performance` - Performance benchmarks (optional)
- `@pytest.mark.unit` - Unit tests with mocks

### Continuous Integration

The `scripts/run-all.py` script handles test execution in different environments:

**CI Mode (`--ci` flag):**
- Runs unit tests only (no NocoDB required)
- Skips build validation for faster execution
- Minimal output and cleanup
- Safe for automated CI/CD pipelines

**Local Development Mode:**
- Default: unit tests only
- `--integration`: includes integration tests (requires NocoDB)
- `--performance`: includes performance tests (slower)
- `--all-tests`: runs all test types

**GitHub Actions Integration:**
- Standard CI job: unit tests on all Python versions
- Optional integration tests: with NocoDB service container
- Performance tests: manual trigger only via PR labels

## Test Data Management

### Fixtures

- `nocodb_client` - Real NocoDB client instance
- `test_table` - Temporary test table (auto-cleanup)
- `test_table_with_data` - Test table with sample records
- `test_data_manager` - Helper for creating and cleaning up test data
- `test_config` - Test configuration from environment

### Data Cleanup

Tests automatically clean up created data:

- Test tables are deleted after test sessions
- Created records are tracked and removed
- Test files are generated during tests and automatically deleted
- Temporary upload directories are cleaned up
- Set `CLEANUP_TEST_DATA=false` to preserve data for debugging

### File Upload Tests

File upload tests generate test files dynamically:

- Files are created during test execution (not stored in repository)
- Multiple file types: text, CSV, JSON, fake images, binary data
- File sizes range from 1KB to 1MB (configurable via `MAX_FILE_SIZE_MB`)
- All test files are automatically cleaned up after tests
- No permanent files are committed to version control

## Test Coverage

Test files cover all major functionality:

- `test_client.py` - Core client functionality
- `test_table.py` - Table operations
- `test_bulk_operations_integration.py` - Bulk operations with real DB
- `test_links_integration.py` - Links and relationships
- `test_views_integration.py` - View management
- `test_filter_builder_integration.py` - Query filtering
- `test_webhooks_integration.py` - Webhook management
- `test_columns_integration.py` - Column management
- `test_pagination_integration.py` - Pagination handling
- `test_cache_integration.py` - Caching functionality
- `test_async_client_integration.py` - Async operations
- `test_file_operations_integration.py` - File handling
- `test_query_builder_integration.py` - SQL-like query building

## Debugging Tests

### Verbose Output

```bash
# Show detailed test output
python -m pytest -v -s

# Show full tracebacks
python -m pytest --tb=long

# Stop on first failure
python -m pytest -x

# Drop into debugger on failure
python -m pytest --pdb
```

### Preserving Test Data

```bash
# Keep test data for inspection
CLEANUP_TEST_DATA=false python -m pytest -m integration
```

### Performance Analysis

```bash
# Show slowest tests
python -m pytest --durations=10

# Profile memory usage (if pytest-memray installed)
python -m pytest --memray
```

## Common Issues

### NocoDB Connection

If integration tests fail:

1. Ensure NocoDB server is running
2. Verify `NOCODB_TOKEN` is valid
3. Check firewall/network connectivity
4. Try manual API call: `curl -H "xc-token: YOUR_TOKEN" http://localhost:8080/api/v1/db/meta/projects`

### Permissions

Ensure the API token has sufficient permissions:
- Create/delete tables
- Insert/update/delete records
- Manage views and columns
- File upload/download

### Rate Limiting

If tests fail due to rate limiting:
- Reduce `PERFORMANCE_TEST_RECORDS`
- Increase `TEST_TIMEOUT`
- Run tests with fewer parallel processes

## Contributing

When adding new tests:

1. Use appropriate markers (`@pytest.mark.integration`, etc.)
2. Add proper cleanup in fixtures
3. Include both positive and negative test cases
4. Test error conditions and edge cases
5. Use descriptive test names and docstrings
6. Update this README if adding new test categories
