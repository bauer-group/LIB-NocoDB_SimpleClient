# API Reference

Complete API reference for NocoDB Simple Client.

## Client Classes

### NocoDBClient

Main client class for interacting with NocoDB REST API.

```python
class NocoDBClient:
    def __init__(
        self,
        config: NocoDBConfig
    ) -> None
```

#### Parameters

- `config` (NocoDBConfig): Configuration object with connection settings

#### Methods

##### get_records

```python
def get_records(
    self,
    table_id: str,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    fields: Optional[List[str]] = None,
    limit: int = 25,
) -> List[Dict[str, Any]]
```

Get multiple records from a table.

**Parameters:**

- `table_id` (str): The ID of the table
- `sort` (str, optional): Sort criteria (e.g., "Id", "-CreatedAt")
- `where` (str, optional): Filter condition (e.g., "(Name,eq,John)")
- `fields` (List[str], optional): List of fields to retrieve
- `limit` (int): Maximum number of records to retrieve (default: 25)

**Returns:** List of record dictionaries

**Raises:**

- `ValidationException`: If parameters are invalid
- `TableNotFoundException`: If table doesn't exist
- `NocoDBException`: For API errors

##### get_record

```python
def get_record(
    self,
    table_id: str,
    record_id: Union[int, str],
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]
```

Get a single record by ID.

**Parameters:**

- `table_id` (str): The ID of the table
- `record_id` (Union[int, str]): The ID of the record
- `fields` (List[str], optional): List of fields to retrieve

**Returns:** Record dictionary

**Raises:**

- `RecordNotFoundException`: If record doesn't exist
- `ValidationException`: If parameters are invalid
- `NocoDBException`: For API errors

##### insert_record

```python
def insert_record(
    self,
    table_id: str,
    record: Dict[str, Any]
) -> Union[int, str]
```

Insert a new record into a table.

**Parameters:**

- `table_id` (str): The ID of the table
- `record` (Dict[str, Any]): Dictionary containing the record data

**Returns:** The ID of the inserted record

**Raises:**

- `ValidationException`: If record data is invalid
- `NocoDBException`: For API errors

##### update_record

```python
def update_record(
    self,
    table_id: str,
    record: Dict[str, Any],
    record_id: Optional[Union[int, str]] = None,
) -> Union[int, str]
```

Update an existing record.

**Parameters:**

- `table_id` (str): The ID of the table
- `record` (Dict[str, Any]): Dictionary containing the updated record data
- `record_id` (Union[int, str], optional): The ID of the record to update

**Returns:** The ID of the updated record

**Raises:**

- `RecordNotFoundException`: If record doesn't exist
- `ValidationException`: If parameters are invalid
- `NocoDBException`: For API errors

##### delete_record

```python
def delete_record(
    self,
    table_id: str,
    record_id: Union[int, str]
) -> Union[int, str]
```

Delete a record from a table.

**Parameters:**

- `table_id` (str): The ID of the table
- `record_id` (Union[int, str]): The ID of the record to delete

**Returns:** The ID of the deleted record

**Raises:**

- `RecordNotFoundException`: If record doesn't exist
- `ValidationException`: If parameters are invalid
- `NocoDBException`: For API errors

##### count_records

```python
def count_records(
    self,
    table_id: str,
    where: Optional[str] = None
) -> int
```

Count records in a table.

**Parameters:**

- `table_id` (str): The ID of the table
- `where` (str, optional): Filter condition

**Returns:** Number of records matching the criteria

**Raises:**

- `ValidationException`: If parameters are invalid
- `NocoDBException`: For API errors

##### File Operations

###### attach_file_to_record

```python
def attach_file_to_record(
    self,
    table_id: str,
    record_id: Union[int, str],
    field_name: str,
    file_path: Union[str, Path],
) -> None
```

Attach a file to a record.

**Parameters:**

- `table_id` (str): The ID of the table
- `record_id` (Union[int, str]): The ID of the record
- `field_name` (str): The name of the file field
- `file_path` (Union[str, Path]): Path to the file to attach

**Raises:**

- `FileUploadException`: If file upload fails
- `ValidationException`: If parameters are invalid

###### download_file_from_record

```python
def download_file_from_record(
    self,
    table_id: str,
    record_id: Union[int, str],
    field_name: str,
    file_path: Union[str, Path],
    file_index: int = 0,
) -> None
```

Download a file from a record.

**Parameters:**

- `table_id` (str): The ID of the table
- `record_id` (Union[int, str]): The ID of the record
- `field_name` (str): The name of the file field
- `file_path` (Union[str, Path]): Path where to save the file
- `file_index` (int): Index of the file to download (default: 0)

**Raises:**

- `RecordNotFoundException`: If record doesn't exist
- `ValidationException`: If parameters are invalid
- `NocoDBException`: For API errors

##### Context Manager Support

```python
def __enter__(self) -> 'NocoDBClient':
    return self

def __exit__(self, exc_type, exc_val, exc_tb) -> None:
    self.close()

def close(self) -> None:
    """Close the HTTP session."""
```

### NocoDBTable

Wrapper class for table-specific operations.

```python
class NocoDBTable:
    def __init__(
        self,
        client: NocoDBClient,
        table_id: str
    ) -> None
```

#### Parameters

- `client` (NocoDBClient): An instance of NocoDBClient
- `table_id` (str): The ID of the table to operate on

#### Methods

All methods mirror the NocoDBClient methods but automatically pass the table_id.

### AsyncNocoDBClient

Async version of NocoDBClient for high-performance applications.

```python
class AsyncNocoDBClient:
    def __init__(self, config: NocoDBConfig) -> None

    async def __aenter__(self) -> 'AsyncNocoDBClient':
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
```

#### Async Methods

All methods are async versions of the sync client methods:

```python
async def get_records(...) -> List[Dict[str, Any]]
async def get_record(...) -> Dict[str, Any]
async def insert_record(...) -> Union[int, str]
async def update_record(...) -> Union[int, str]
async def delete_record(...) -> Union[int, str]
async def count_records(...) -> int
```

#### Bulk Operations

```python
async def bulk_insert_records(
    self,
    table_id: str,
    records: List[Dict[str, Any]]
) -> List[Union[int, str]]
```

Insert multiple records in parallel.

```python
async def bulk_update_records(
    self,
    table_id: str,
    records: List[Dict[str, Any]]
) -> List[Union[int, str]]
```

Update multiple records in parallel.

## Configuration

### NocoDBConfig

Configuration class for client settings.

```python
@dataclass
class NocoDBConfig:
    base_url: str
    api_token: str
    access_protection_auth: Optional[str] = None
    access_protection_header: str = "X-BAUERGROUP-Auth"
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 0.3
    pool_connections: int = 10
    pool_maxsize: int = 20
    verify_ssl: bool = True
    user_agent: str = "nocodb-simple-client"
    debug: bool = False
    log_level: str = "INFO"
    extra_headers: Dict[str, str] = field(default_factory=dict)
```

#### Class Methods

##### from_env

```python
@classmethod
def from_env(cls, env_prefix: str = "NOCODB_") -> "NocoDBConfig"
```

Create configuration from environment variables.

##### from_file

```python
@classmethod
def from_file(cls, config_path: Path) -> "NocoDBConfig"
```

Load configuration from a file (JSON, YAML, or TOML).

#### Instance Methods

##### setup_logging

```python
def setup_logging(self) -> None
```

Configure logging based on configuration settings.

##### validate

```python
def validate(self) -> None
```

Validate configuration settings.

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert configuration to dictionary (masks sensitive data).

### load_config

```python
def load_config(
    config_path: Optional[Path] = None,
    env_prefix: str = "NOCODB_",
    use_env: bool = True
) -> NocoDBConfig
```

Load configuration from file or environment variables.

## Exceptions

### Exception Hierarchy

```
Exception
└── NocoDBException
    ├── RecordNotFoundException
    ├── ValidationException
    ├── AuthenticationException
    ├── AuthorizationException
    ├── ConnectionTimeoutException
    ├── RateLimitException
    ├── ServerErrorException
    ├── NetworkException
    ├── TableNotFoundException
    ├── FileUploadException
    └── InvalidResponseException
```

### NocoDBException

Base exception for all NocoDB operations.

```python
class NocoDBException(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    )

    error: str
    message: str
    status_code: Optional[int]
    response_data: Dict[str, Any]
```

### Specific Exceptions

#### RecordNotFoundException

```python
class RecordNotFoundException(NocoDBException):
    def __init__(
        self,
        message: str = "Record not found",
        record_id: Optional[str] = None
    )

    record_id: Optional[str]
```

#### ValidationException

```python
class ValidationException(NocoDBException):
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None
    )

    field_name: Optional[str]
```

#### AuthenticationException

```python
class AuthenticationException(NocoDBException):
    def __init__(self, message: str = "Authentication failed")
```

#### RateLimitException

```python
class RateLimitException(NocoDBException):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    )

    retry_after: Optional[int]
```

## Validation Functions

### Input Validation

```python
def validate_table_id(table_id: str) -> str
def validate_record_id(record_id: Union[int, str]) -> Union[int, str]
def validate_field_names(fields: List[str]) -> List[str]
def validate_record_data(record: Dict[str, Any]) -> Dict[str, Any]
def validate_where_clause(where: str) -> str
def validate_sort_clause(sort: str) -> str
def validate_limit(limit: int) -> int
def validate_file_path(file_path: Union[str, Path]) -> Path
def validate_url(url: str) -> str
def validate_api_token(token: str) -> str
def sanitize_string(value: str, max_length: int = 1000) -> str
```

## Caching

### Cache Backends

#### CacheBackend (ABC)

```python
class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]: ...
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    @abstractmethod
    def delete(self, key: str) -> None: ...
    @abstractmethod
    def clear(self) -> None: ...
    @abstractmethod
    def exists(self, key: str) -> bool: ...
```

#### MemoryCache

```python
class MemoryCache(CacheBackend):
    def __init__(self, max_size: int = 1000)
```

#### DiskCache

```python
class DiskCache(CacheBackend):
    def __init__(
        self,
        directory: str = "./cache",
        size_limit: int = 100_000_000
    )
```

#### RedisCache

```python
class RedisCache(CacheBackend):
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = 'nocodb:'
    )
```

### CacheManager

```python
class CacheManager:
    def __init__(
        self,
        backend: CacheBackend,
        default_ttl: Optional[int] = 300
    )

    def get_records_cache_key(...) -> str
    def get_record_cache_key(...) -> str
    def count_records_cache_key(...) -> str
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None
    def delete(self, key: str) -> None
    def clear(self) -> None
    def invalidate_table_cache(self, table_id: str) -> None
```

### Factory Function

```python
def create_cache_manager(
    backend_type: str = 'memory',
    **backend_kwargs
) -> CacheManager
```

## Models (Optional Pydantic Support)

When Pydantic is installed, the following models provide additional type safety:

### NocoDBRecord

```python
class NocoDBRecord(BaseModel):
    Id: Union[int, str]
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None
    data: Dict[str, Any] = Field(default_factory=dict)

    def get_field(self, field_name: str, default: Any = None) -> Any
    def set_field(self, field_name: str, value: Any) -> None
    def to_api_format(self) -> Dict[str, Any]
```

### QueryParams

```python
class QueryParams(BaseModel):
    sort: Optional[str] = None
    where: Optional[str] = None
    fields: Optional[List[str]] = None
    limit: int = Field(25, gt=0, le=10000)
    offset: int = Field(0, ge=0)
```

### ConnectionConfig

```python
class ConnectionConfig(BaseModel):
    base_url: str
    api_token: str
    access_protection_auth: Optional[str] = None
    access_protection_header: str = "X-BAUERGROUP-Auth"
    timeout: float = Field(30.0, gt=0)
    max_retries: int = Field(3, ge=0)
    verify_ssl: bool = True
```

## CLI Reference

### Commands

#### Global Options

```bash
--config, -c          Configuration file path
--base-url, -u        NocoDB base URL
--api-token, -t       API token
--debug               Enable debug output
```

#### info

```bash
nocodb info
```

Display client and connection information.

#### table

##### list

```bash
nocodb table list TABLE_ID [OPTIONS]
```

**Options:**

- `--limit, -l`: Number of records to retrieve (default: 25)
- `--where, -w`: Filter conditions
- `--sort, -s`: Sort criteria
- `--fields, -f`: Comma-separated list of fields
- `--output, -o`: Output format (table, json, csv)

##### get

```bash
nocodb table get TABLE_ID RECORD_ID [OPTIONS]
```

**Options:**

- `--fields, -f`: Comma-separated list of fields
- `--output, -o`: Output format (table, json)

##### create

```bash
nocodb table create TABLE_ID [OPTIONS]
```

**Options:**

- `--data, -d`: JSON data for the record
- `--file, -f`: JSON file with record data

##### update

```bash
nocodb table update TABLE_ID RECORD_ID [OPTIONS]
```

**Options:**

- `--data, -d`: JSON data for the record
- `--file, -f`: JSON file with record data

##### delete

```bash
nocodb table delete TABLE_ID RECORD_ID [OPTIONS]
```

**Options:**

- `--confirm`: Skip confirmation prompt

##### count

```bash
nocodb table count TABLE_ID [OPTIONS]
```

**Options:**

- `--where, -w`: Filter conditions

#### files

##### upload

```bash
nocodb files upload TABLE_ID RECORD_ID FIELD_NAME FILE_PATH
```

##### download

```bash
nocodb files download TABLE_ID RECORD_ID FIELD_NAME OUTPUT_PATH
```

## Constants and Enums

### SortDirection

```python
class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
```

### RecordStatus

```python
class RecordStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
```

## Version Information

```python
from nocodb_simple_client import __version__, __author__, __email__

print(f"NocoDB Simple Client v{__version__}")
print(f"Author: {__author__}")
print(f"Email: {__email__}")
```
