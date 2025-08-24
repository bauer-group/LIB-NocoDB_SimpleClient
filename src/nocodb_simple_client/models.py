"""
MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""Pydantic models for type safety and validation."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

try:
    from pydantic import BaseModel, Field, root_validator, validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for when Pydantic is not installed
    PYDANTIC_AVAILABLE = False

    class BaseModel:
        """Fallback BaseModel when Pydantic is not available."""

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


class SortDirection(str, Enum):
    """Sort direction enumeration."""

    ASC = "asc"
    DESC = "desc"


class RecordStatus(str, Enum):
    """Record status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


if PYDANTIC_AVAILABLE:

    class NocoDBRecord(BaseModel):
        """Pydantic model for NocoDB record."""

        Id: Union[int, str] = Field(..., description="Record ID")
        CreatedAt: Optional[datetime] = Field(None, description="Creation timestamp")
        UpdatedAt: Optional[datetime] = Field(None, description="Last update timestamp")
        data: dict[str, Any] = Field(default_factory=dict, description="Record data")

        class Config:
            extra = "allow"  # Allow additional fields
            validate_assignment = True
            use_enum_values = True

        @validator("Id")
        def validate_id(cls, v):
            """Validate record ID."""
            if isinstance(v, str) and not v.strip():
                raise ValueError("Record ID cannot be empty string")
            if isinstance(v, int) and v <= 0:
                raise ValueError("Record ID must be positive integer")
            return v

        @root_validator
        def validate_record(cls, values):
            """Validate entire record."""
            data = values.get("data", {})
            if not isinstance(data, dict):
                raise ValueError("Record data must be a dictionary")
            return values

        def get_field(self, field_name: str, default: Any = None) -> Any:
            """Get field value with fallback to default."""
            return self.data.get(field_name, default)

        def set_field(self, field_name: str, value: Any) -> None:
            """Set field value."""
            self.data[field_name] = value

        def to_api_format(self) -> dict[str, Any]:
            """Convert to API format."""
            result = {"Id": self.Id}
            result.update(self.data)
            return result

    class QueryParams(BaseModel):
        """Pydantic model for query parameters."""

        sort: Optional[str] = Field(None, description="Sort criteria")
        where: Optional[str] = Field(None, description="Filter conditions")
        fields: Optional[list[str]] = Field(None, description="Fields to retrieve")
        limit: int = Field(25, gt=0, le=10000, description="Record limit")
        offset: int = Field(0, ge=0, description="Record offset")

        @validator("sort")
        def validate_sort(cls, v):
            """Validate sort parameter."""
            if v is None:
                return v
            # Basic validation for sort format
            for field in v.split(","):
                field = field.strip()
                if field.startswith("-"):
                    field = field[1:]
                if not field.replace("_", "").replace("-", "").isalnum():
                    raise ValueError(f"Invalid sort field: {field}")
            return v

        @validator("where")
        def validate_where(cls, v):
            """Validate where parameter."""
            if v is None:
                return v
            # Basic validation for where clause
            if not v.strip():
                raise ValueError("Where clause cannot be empty")
            return v.strip()

        @validator("fields")
        def validate_fields(cls, v):
            """Validate fields parameter."""
            if v is None:
                return v
            if not v:
                raise ValueError("Fields list cannot be empty")
            for field in v:
                if not isinstance(field, str) or not field.strip():
                    raise ValueError("All field names must be non-empty strings")
            return [field.strip() for field in v]

    class FileUploadInfo(BaseModel):
        """Pydantic model for file upload information."""

        filename: str = Field(..., description="Original filename")
        file_path: Union[str, Path] = Field(..., description="Local file path")
        mime_type: Optional[str] = Field(None, description="MIME type")
        file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
        field_name: str = Field(..., description="Target field name")

        @validator("filename")
        def validate_filename(cls, v):
            """Validate filename."""
            if not v.strip():
                raise ValueError("Filename cannot be empty")
            # Check for dangerous characters
            dangerous_chars = ["..", "/", "\\", "<", ">", "|", ":", "*", "?", '"']
            if any(char in v for char in dangerous_chars):
                raise ValueError("Filename contains dangerous characters")
            return v.strip()

        @validator("file_path")
        def validate_file_path(cls, v):
            """Validate file path."""
            path = Path(v) if isinstance(v, str) else v
            if not path.exists():
                raise ValueError(f"File does not exist: {path}")
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            return path

        @validator("file_size")
        def validate_file_size(cls, v, values):
            """Validate file size."""
            if v is None:
                file_path = values.get("file_path")
                if file_path:
                    path = Path(file_path) if isinstance(file_path, str) else file_path
                    return path.stat().st_size
            return v

    class ApiResponse(BaseModel):
        """Pydantic model for API response."""

        success: bool = Field(True, description="Request success status")
        data: Optional[Any] = Field(None, description="Response data")
        error: Optional[str] = Field(None, description="Error message")
        status_code: Optional[int] = Field(None, description="HTTP status code")
        message: Optional[str] = Field(None, description="Response message")

        @validator("status_code")
        def validate_status_code(cls, v):
            """Validate HTTP status code."""
            if v is not None and not (100 <= v <= 599):
                raise ValueError("Invalid HTTP status code")
            return v

    class TableInfo(BaseModel):
        """Pydantic model for table information."""

        id: str = Field(..., description="Table ID")
        title: str = Field(..., description="Table title")
        table_name: str = Field(..., description="Table name in database")
        type: str = Field("table", description="Table type")
        enabled: bool = Field(True, description="Table enabled status")

        @validator("id")
        def validate_id(cls, v):
            """Validate table ID."""
            if not v.strip():
                raise ValueError("Table ID cannot be empty")
            return v.strip()

    class ConnectionConfig(BaseModel):
        """Pydantic model for connection configuration."""

        base_url: str = Field(..., description="NocoDB base URL")
        api_token: str = Field(..., description="API authentication token")
        access_protection_auth: Optional[str] = Field(None, description="Access protection token")
        access_protection_header: str = Field(
            "X-BAUERGROUP-Auth", description="Protection header name"
        )
        timeout: float = Field(30.0, gt=0, description="Request timeout")
        max_retries: int = Field(3, ge=0, description="Maximum retries")
        verify_ssl: bool = Field(True, description="Verify SSL certificates")

        @validator("base_url")
        def validate_base_url(cls, v):
            """Validate base URL."""
            if not v.strip():
                raise ValueError("Base URL cannot be empty")
            url = v.strip().rstrip("/")
            if not url.startswith(("http://", "https://")):
                raise ValueError("Base URL must start with http:// or https://")
            return url

        @validator("api_token")
        def validate_api_token(cls, v):
            """Validate API token."""
            if not v.strip():
                raise ValueError("API token cannot be empty")
            if len(v.strip()) < 10:
                raise ValueError("API token must be at least 10 characters")
            return v.strip()

else:
    # Fallback models when Pydantic is not available
    class NocoDBRecord(BaseModel):
        """Fallback model for NocoDB record."""

        def __init__(self, Id, data=None, **kwargs):
            self.Id = Id
            self.data = data or {}
            for key, value in kwargs.items():
                setattr(self, key, value)

    class QueryParams(BaseModel):
        """Fallback model for query parameters."""

        def __init__(self, sort=None, where=None, fields=None, limit=25, offset=0):
            self.sort = sort
            self.where = where
            self.fields = fields
            self.limit = limit
            self.offset = offset

    class FileUploadInfo(BaseModel):
        """Fallback model for file upload information."""

        def __init__(self, filename, file_path, field_name, **kwargs):
            self.filename = filename
            self.file_path = Path(file_path)
            self.field_name = field_name
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ApiResponse(BaseModel):
        """Fallback model for API response."""

        def __init__(self, success=True, data=None, error=None, **kwargs):
            self.success = success
            self.data = data
            self.error = error
            for key, value in kwargs.items():
                setattr(self, key, value)

    class TableInfo(BaseModel):
        """Fallback model for table information."""

        def __init__(self, id, title, table_name, **kwargs):
            self.id = id
            self.title = title
            self.table_name = table_name
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ConnectionConfig(BaseModel):
        """Fallback model for connection configuration."""

        def __init__(self, base_url, api_token, **kwargs):
            self.base_url = base_url.rstrip("/")
            self.api_token = api_token
            for key, value in kwargs.items():
                setattr(self, key, value)
