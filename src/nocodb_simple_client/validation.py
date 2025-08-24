"""Input validation utilities for NocoDB Simple Client.

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

import re
from pathlib import Path
from typing import Any

from .exceptions import ValidationException


def validate_table_id(table_id: str) -> str:
    """Validate table ID format.

    Args:
        table_id: The table ID to validate

    Returns:
        The validated table ID

    Raises:
        ValidationException: If table ID format is invalid
    """
    if not isinstance(table_id, str):
        raise ValidationException("Table ID must be a string", field_name="table_id")

    if not table_id.strip():
        raise ValidationException("Table ID cannot be empty", field_name="table_id")

    # Allow alphanumeric characters, underscores, hyphens, and some special chars
    if not re.match(r"^[a-zA-Z0-9_-]+$", table_id):
        raise ValidationException(
            "Table ID can only contain alphanumeric characters, underscores, and hyphens",
            field_name="table_id",
        )

    return table_id


def validate_record_id(record_id: int | str) -> int | str:
    """Validate record ID format.

    Args:
        record_id: The record ID to validate

    Returns:
        The validated record ID

    Raises:
        ValidationException: If record ID format is invalid
    """
    if isinstance(record_id, int):
        if record_id <= 0:
            raise ValidationException("Record ID must be positive", field_name="record_id")
        return record_id

    if isinstance(record_id, str):
        record_id = record_id.strip()
        if not record_id:
            raise ValidationException("Record ID cannot be empty", field_name="record_id")

        # Check for potentially dangerous characters/patterns
        dangerous_patterns = [";", "--", "/*", "*/", "DROP", "DELETE", "UPDATE", "INSERT", "SELECT"]
        record_id_upper = record_id.upper()
        for pattern in dangerous_patterns:
            if pattern in record_id_upper:
                raise ValidationException(
                    f"Record ID contains potentially dangerous pattern: {pattern}",
                    field_name="record_id",
                )

        return record_id

    raise ValidationException("Record ID must be an integer or string", field_name="record_id")


def validate_field_names(fields: list[str]) -> list[str]:
    """Validate field names list.

    Args:
        fields: List of field names to validate

    Returns:
        The validated field names list

    Raises:
        ValidationException: If field names are invalid
    """
    if not isinstance(fields, list):
        raise ValidationException("Fields must be a list", field_name="fields")

    if not fields:
        raise ValidationException("Fields list cannot be empty", field_name="fields")

    validated_fields = []
    for i, field in enumerate(fields):
        if not isinstance(field, str):
            raise ValidationException(f"Field at index {i} must be a string", field_name="fields")

        if not field.strip():
            raise ValidationException(f"Field at index {i} cannot be empty", field_name="fields")

        validated_fields.append(field.strip())

    return validated_fields


def validate_record_data(record: dict[str, Any]) -> dict[str, Any]:
    """Validate record data dictionary.

    Args:
        record: Record data to validate

    Returns:
        The validated record data

    Raises:
        ValidationException: If record data is invalid
    """
    if not isinstance(record, dict):
        raise ValidationException("Record must be a dictionary", field_name="record")

    if not record:
        raise ValidationException("Record cannot be empty", field_name="record")

    # Check for potentially dangerous keys
    dangerous_keys = ["__proto__", "constructor", "prototype"]
    for key in record.keys():
        if key in dangerous_keys:
            raise ValidationException(f"Field name '{key}' is not allowed", field_name="record")

        # Validate field name format
        if not isinstance(key, str):
            raise ValidationException("All field names must be strings", field_name="record")

    return record


def validate_where_clause(where: str) -> str:
    """Validate WHERE clause format.

    Args:
        where: WHERE clause to validate

    Returns:
        The validated WHERE clause

    Raises:
        ValidationException: If WHERE clause format is invalid
    """
    if not isinstance(where, str):
        raise ValidationException("WHERE clause must be a string", field_name="where")

    if not where.strip():
        raise ValidationException("WHERE clause cannot be empty", field_name="where")

    # Basic validation - check for balanced parentheses
    open_count = where.count("(")
    close_count = where.count(")")
    if open_count != close_count:
        raise ValidationException("Unbalanced parentheses in WHERE clause", field_name="where")

    # Check for potentially dangerous SQL injection patterns
    dangerous_patterns = [
        r";\s*(drop|delete|truncate|alter)\s+",
        r"union\s+select",
        r"--\s*$",
        r"/\*.*\*/",
        r"xp_cmdshell",
        r"sp_executesql",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, where.lower()):
            raise ValidationException(
                "Potentially dangerous pattern detected in WHERE clause", field_name="where"
            )

    return where.strip()


def validate_sort_clause(sort: str) -> str:
    """Validate SORT clause format.

    Args:
        sort: SORT clause to validate

    Returns:
        The validated SORT clause

    Raises:
        ValidationException: If SORT clause format is invalid
    """
    if not isinstance(sort, str):
        raise ValidationException("SORT clause must be a string", field_name="sort")

    if not sort.strip():
        raise ValidationException("SORT clause cannot be empty", field_name="sort")

    # Validate sort format: field_name or -field_name, comma-separated
    sort_fields = [field.strip() for field in sort.split(",")]

    for field in sort_fields:
        if not field:
            continue

        # Remove leading minus for DESC sorting
        field_name = field.lstrip("-")

        # Validate field name
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field_name):
            raise ValidationException(
                f"Invalid field name in SORT clause: {field_name}", field_name="sort"
            )

    return sort.strip()


def validate_limit(limit: int) -> int:
    """Validate limit parameter.

    Args:
        limit: Limit value to validate

    Returns:
        The validated limit

    Raises:
        ValidationException: If limit is invalid
    """
    if not isinstance(limit, int):
        raise ValidationException("Limit must be an integer", field_name="limit")

    if limit <= 0:
        raise ValidationException("Limit must be positive", field_name="limit")

    if limit > 10000:  # Reasonable upper limit to prevent abuse
        raise ValidationException("Limit cannot exceed 10,000", field_name="limit")

    return limit


def validate_file_path(file_path: str | Path) -> Path:
    """Validate file path.

    Args:
        file_path: File path to validate

    Returns:
        The validated file path as Path object

    Raises:
        ValidationException: If file path is invalid
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    elif not isinstance(file_path, Path):
        raise ValidationException(
            "File path must be a string or Path object", field_name="file_path"
        )

    if not file_path.exists():
        raise ValidationException(f"File does not exist: {file_path}", field_name="file_path")

    if not file_path.is_file():
        raise ValidationException(f"Path is not a file: {file_path}", field_name="file_path")

    # Check file size (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    if file_path.stat().st_size > max_size:
        raise ValidationException(
            f"File size exceeds maximum allowed size of {max_size} bytes", field_name="file_path"
        )

    return file_path


def validate_url(url: str) -> str:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        The validated URL

    Raises:
        ValidationException: If URL format is invalid
    """
    if not isinstance(url, str):
        raise ValidationException("URL must be a string", field_name="url")

    url = url.strip()
    if not url:
        raise ValidationException("URL cannot be empty", field_name="url")

    # Basic URL validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        raise ValidationException("Invalid URL format", field_name="url")

    # Security check - only allow http/https
    if not url.lower().startswith(("http://", "https://")):
        raise ValidationException("Only HTTP and HTTPS URLs are allowed", field_name="url")

    return url


def validate_api_token(token: str) -> str:
    """Validate API token format.

    Args:
        token: API token to validate

    Returns:
        The validated token

    Raises:
        ValidationException: If token format is invalid
    """
    if not isinstance(token, str):
        raise ValidationException("API token must be a string", field_name="api_token")

    token = token.strip()
    if not token:
        raise ValidationException("API token cannot be empty", field_name="api_token")

    # Basic token validation - should be at least 10 characters
    if len(token) < 10:
        raise ValidationException(
            "API token must be at least 10 characters", field_name="api_token"
        )

    # Check for common token formats (UUID, Base64, etc.)
    # This is a basic check - real tokens can vary widely
    if not re.match(r"^[a-zA-Z0-9_-]+$", token):
        raise ValidationException("API token contains invalid characters", field_name="api_token")

    return token


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationException: If string is invalid
    """
    if not isinstance(value, str):
        raise ValidationException("Value must be a string")

    # Remove null bytes and control characters
    value = "".join(char for char in value if ord(char) >= 32 or char in "\n\r\t")

    if len(value) > max_length:
        raise ValidationException(f"String length exceeds maximum of {max_length} characters")

    return value
