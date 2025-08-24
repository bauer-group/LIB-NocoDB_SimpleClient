# Advanced Usage Guide

This guide covers advanced features and usage patterns for the NocoDB Simple Client.

## Table of Contents

- [Configuration Management](#configuration-management)
- [Async Support](#async-support)
- [Caching](#caching)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)
- [Error Handling](#error-handling)
- [Logging and Monitoring](#logging-and-monitoring)
- [CLI Usage](#cli-usage)

## Configuration Management

### Environment-based Configuration

The client supports loading configuration from environment variables:

```python
from nocodb_simple_client.config import load_config

# Load from environment variables with NOCODB_ prefix
config = load_config()

# Custom prefix
config = load_config(env_prefix="MY_APP_")
```

Required environment variables:

- `NOCODB_BASE_URL`: Your NocoDB instance URL
- `NOCODB_API_TOKEN`: Your API authentication token

Optional environment variables:

- `NOCODB_PROTECTION_AUTH`: Access protection token
- `NOCODB_PROTECTION_HEADER`: Custom protection header name
- `NOCODB_TIMEOUT`: Request timeout (default: 30.0)
- `NOCODB_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `NOCODB_DEBUG`: Enable debug mode (default: false)

### File-based Configuration

Load configuration from JSON, YAML, or TOML files:

```python
from pathlib import Path
from nocodb_simple_client.config import load_config

# Load from file
config = load_config(config_path=Path("config.yaml"))
```

Example configuration file:

```yaml
# config.yaml
base_url: "https://your-nocodb-instance.com"
api_token: "your-api-token"
timeout: 30.0
max_retries: 3
debug: false
verify_ssl: true
```

### Advanced Configuration

```python
from nocodb_simple_client.config import NocoDBConfig

config = NocoDBConfig(
    base_url="https://nocodb.example.com",
    api_token="your-token",
    # Connection pooling
    pool_connections=10,
    pool_maxsize=20,
    # Timeouts and retries
    timeout=30.0,
    max_retries=3,
    backoff_factor=0.3,
    # Security
    verify_ssl=True,
    # Custom headers
    extra_headers={"X-Custom": "value"}
)

# Setup logging based on config
config.setup_logging()
```

## Async Support

For high-performance applications, use the async client:

```python
import asyncio
from nocodb_simple_client.async_client import AsyncNocoDBClient, AsyncNocoDBTable
from nocodb_simple_client.config import NocoDBConfig

async def main():
    config = NocoDBConfig(
        base_url="https://nocodb.example.com",
        api_token="your-token"
    )

    async with AsyncNocoDBClient(config) as client:
        table = AsyncNocoDBTable(client, "your-table-id")

        # Async operations
        records = await table.get_records(limit=100)
        new_record = await table.insert_record({"name": "async record"})

        # Bulk operations (parallel execution)
        records_to_insert = [
            {"name": f"record_{i}"} for i in range(100)
        ]
        inserted_ids = await table.bulk_insert_records(records_to_insert)

# Run async code
asyncio.run(main())
```

### Async Best Practices

```python
# Use semaphores to limit concurrency
import asyncio

async def process_records_with_limit(table, records, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single(record):
        async with semaphore:
            return await table.insert_record(record)

    tasks = [process_single(record) for record in records]
    results = await asyncio.gather(*tasks)
    return results
```

## Caching

Implement caching to improve performance:

```python
from nocodb_simple_client.cache import create_cache_manager, CacheManager
from nocodb_simple_client import NocoDBClient, NocoDBTable

# Create cache manager
cache_manager = create_cache_manager(
    backend_type='memory',  # or 'disk', 'redis'
    max_size=1000
)

# Manual caching
def get_cached_records(table: NocoDBTable, cache: CacheManager):
    cache_key = cache.get_records_cache_key(
        table.table_id,
        limit=100
    )

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # Fetch from API
    records = table.get_records(limit=100)

    # Cache result
    cache.set(cache_key, records, ttl=300)  # 5 minutes

    return records
```

### Redis Caching

For distributed caching:

```python
from nocodb_simple_client.cache import create_cache_manager

# Redis cache
cache_manager = create_cache_manager(
    backend_type='redis',
    host='localhost',
    port=6379,
    db=0,
    key_prefix='nocodb:'
)
```

### Disk Caching

For persistent caching:

```python
from nocodb_simple_client.cache import create_cache_manager

# Disk cache
cache_manager = create_cache_manager(
    backend_type='disk',
    directory='./cache',
    size_limit=100_000_000  # 100MB
)
```

## Performance Optimization

### Connection Pooling

Configure connection pooling for better performance:

```python
from nocodb_simple_client.config import NocoDBConfig

config = NocoDBConfig(
    base_url="https://nocodb.example.com",
    api_token="your-token",
    pool_connections=20,    # Number of connection pools
    pool_maxsize=100,       # Maximum connections per pool
    timeout=30.0
)
```

### Batch Operations

Use batch operations for bulk data processing:

```python
# Sync batch operations
def bulk_insert_with_batches(table, records, batch_size=100):
    results = []
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        for record in batch:
            result = table.insert_record(record)
            results.append(result)
    return results

# Async batch operations (much faster)
async def bulk_insert_async(async_table, records):
    return await async_table.bulk_insert_records(records)
```

### Field Selection

Reduce payload size by selecting only needed fields:

```python
# Only fetch specific fields
records = table.get_records(
    fields=['Id', 'Name', 'Email'],
    limit=1000
)
```

### Pagination

Implement efficient pagination:

```python
def get_all_records_paginated(table, page_size=100):
    all_records = []
    offset = 0

    while True:
        # Note: This example shows the concept
        # The actual client handles pagination automatically
        records = table.get_records(limit=page_size)

        if not records:
            break

        all_records.extend(records)

        if len(records) < page_size:
            break

        offset += page_size

    return all_records
```

## Security Best Practices

### Secure Configuration

```python
import os
from nocodb_simple_client.config import NocoDBConfig

# Use environment variables for sensitive data
config = NocoDBConfig(
    base_url=os.getenv('NOCODB_BASE_URL'),
    api_token=os.getenv('NOCODB_API_TOKEN'),
    verify_ssl=True,  # Always verify SSL in production
)

# Never hardcode secrets
# ❌ Bad
config = NocoDBConfig(
    base_url="https://nocodb.example.com",
    api_token="hardcoded-secret-token"
)

# ✅ Good
config = NocoDBConfig(
    base_url=os.getenv('NOCODB_BASE_URL'),
    api_token=os.getenv('NOCODB_API_TOKEN')
)
```

### Input Validation

```python
from nocodb_simple_client.validation import (
    validate_table_id,
    validate_record_data,
    sanitize_string
)

# Validate inputs
def safe_get_records(table, user_input):
    # Sanitize user input
    safe_where = sanitize_string(user_input, max_length=500)

    # Validate and get records
    return table.get_records(where=safe_where)
```

### Error Handling

```python
from nocodb_simple_client.exceptions import (
    NocoDBException,
    AuthenticationException,
    ValidationException
)

def robust_operation(table):
    try:
        return table.get_records()
    except AuthenticationException:
        # Handle auth issues
        logger.error("Authentication failed - check API token")
        raise
    except ValidationException as e:
        # Handle validation errors
        logger.error(f"Validation error: {e.message}")
        raise
    except NocoDBException as e:
        # Handle other NocoDB errors
        logger.error(f"NocoDB error: {e.error} - {e.message}")
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise
```

## Error Handling

### Exception Hierarchy

```python
from nocodb_simple_client.exceptions import *

# Specific exception handling
try:
    record = table.get_record(record_id)
except RecordNotFoundException:
    # Handle missing record
    return None
except TableNotFoundException:
    # Handle missing table
    raise ValueError("Table not found")
except AuthenticationException:
    # Handle auth failure
    raise PermissionError("Invalid credentials")
except RateLimitException as e:
    # Handle rate limiting
    time.sleep(e.retry_after or 60)
    # Retry operation
except NocoDBException as e:
    # Handle any NocoDB error
    logger.error(f"API Error: {e}")
    raise
```

### Retry Logic

```python
import time
from nocodb_simple_client.exceptions import RateLimitException, NetworkException

def retry_operation(operation, max_retries=3, backoff_factor=1.0):
    for attempt in range(max_retries):
        try:
            return operation()
        except RateLimitException as e:
            if attempt == max_retries - 1:
                raise

            # Wait for retry-after header or default backoff
            wait_time = e.retry_after or (backoff_factor * (2 ** attempt))
            time.sleep(wait_time)
        except NetworkException:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff for network errors
            time.sleep(backoff_factor * (2 ** attempt))
```

## Logging and Monitoring

### Configure Logging

```python
import logging
from nocodb_simple_client.config import NocoDBConfig

# Configure logging through config
config = NocoDBConfig(
    base_url="https://nocodb.example.com",
    api_token="your-token",
    debug=True,
    log_level="DEBUG"
)

config.setup_logging()

# Or configure manually
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('nocodb_simple_client')
logger.setLevel(logging.DEBUG)
```

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def timing_context(operation_name):
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation_name} took {duration:.2f} seconds")

# Usage
with timing_context("get_records"):
    records = table.get_records(limit=1000)
```

### Metrics Collection

```python
from collections import defaultdict, Counter
import time

class MetricsCollector:
    def __init__(self):
        self.operation_counts = Counter()
        self.operation_times = defaultdict(list)
        self.errors = Counter()

    def record_operation(self, operation, duration, success=True):
        self.operation_counts[operation] += 1
        self.operation_times[operation].append(duration)

        if not success:
            self.errors[operation] += 1

    def get_stats(self):
        stats = {}
        for op in self.operation_counts:
            times = self.operation_times[op]
            stats[op] = {
                'count': self.operation_counts[op],
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'errors': self.errors[op]
            }
        return stats

# Usage
metrics = MetricsCollector()

def monitored_operation(table):
    start_time = time.time()
    success = True

    try:
        return table.get_records()
    except Exception:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        metrics.record_operation('get_records', duration, success)
```

## CLI Usage

The client includes a comprehensive CLI tool:

### Installation

```bash
# Install with CLI dependencies
pip install "nocodb-simple-client[cli]"
```

### Basic Usage

```bash
# Set environment variables
export NOCODB_BASE_URL="https://your-nocodb-instance.com"
export NOCODB_API_TOKEN="your-api-token"

# Get client info
nocodb info

# List records
nocodb table list TABLE_ID --limit 10 --output json

# Get specific record
nocodb table get TABLE_ID RECORD_ID --fields Id,Name,Email

# Create record
nocodb table create TABLE_ID --data '{"name": "New Record", "email": "test@example.com"}'

# Update record
nocodb table update TABLE_ID RECORD_ID --data '{"name": "Updated Name"}'

# Delete record
nocodb table delete TABLE_ID RECORD_ID --confirm

# Count records
nocodb table count TABLE_ID --where "(Status,eq,Active)"

# File operations
nocodb files upload TABLE_ID RECORD_ID FIELD_NAME /path/to/file.pdf
nocodb files download TABLE_ID RECORD_ID FIELD_NAME /path/to/save/file.pdf
```

### Advanced CLI Usage

```bash
# Use configuration file
nocodb --config config.yaml table list TABLE_ID

# Enable debug mode
nocodb --debug table list TABLE_ID

# Custom output format
nocodb table list TABLE_ID --output csv > records.csv

# Filtering and sorting
nocodb table list TABLE_ID \
  --where "(Age,gt,21)~and(Status,eq,Active)" \
  --sort "-CreatedAt,Name" \
  --fields "Id,Name,Email,CreatedAt" \
  --limit 100
```

### Automation Scripts

```bash
#!/bin/bash
# backup_table.sh - Export table data

TABLE_ID="$1"
OUTPUT_FILE="backup_$(date +%Y%m%d_%H%M%S).json"

echo "Backing up table $TABLE_ID to $OUTPUT_FILE..."

nocodb table list "$TABLE_ID" \
  --output json \
  --limit 10000 > "$OUTPUT_FILE"

echo "Backup completed: $OUTPUT_FILE"
```

This advanced usage guide covers the most important features for power users. For basic usage, refer to the main README.md file.
