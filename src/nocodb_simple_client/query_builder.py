"""SQL-like query builder for NocoDB operations.

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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from .filter_builder import FilterBuilder, SortBuilder


class QueryBuilder:
    """SQL-like query builder for NocoDB table operations.

    Provides a fluent interface for building and executing queries against
    NocoDB tables with familiar SQL-like syntax.

    Example:
        >>> table = NocoDBTable(client, "table_id")
        >>> records = (QueryBuilder(table)
        ...     .select('Name', 'Email', 'Status')
        ...     .where('Status', 'eq', 'Active')
        ...     .order_by('CreatedAt', 'desc')
        ...     .limit(50)
        ...     .execute())
    """

    def __init__(self, client_or_table: Any, table_name: str | None = None) -> None:
        """Initialize QueryBuilder with a client and table name OR table instance.

        Args:
            client_or_table: NocoDBClient instance and table_name, or NocoDBTable instance
            table_name: Table name (when first arg is client)
        """
        if table_name is not None:
            # Legacy API: QueryBuilder(client, table_name)
            self.client = client_or_table
            self.table_name = table_name
            self._table = None  # Will be created lazily if needed
        else:
            # New API: QueryBuilder(table)
            self._table = client_or_table
            self.client = getattr(client_or_table, "client", client_or_table)
            self.table_name = getattr(client_or_table, "table_id", "unknown")

        # Initialize state
        self._select_fields: list[str] = []
        self._where_conditions: list[dict[str, Any]] = []  # For backward compatibility
        self._sort_conditions: list[dict[str, Any]] = []  # For backward compatibility
        self._limit_value: int | None = None  # For backward compatibility
        self._offset_value: int | None = None  # For backward compatibility

        # New implementation state
        self._filter_builder = FilterBuilder()
        self._sort_builder = SortBuilder()
        self._limit_count: int | None = None
        self._offset_count: int = 0
        self._where_conditions_added = False

    def select(self, *fields: str) -> "QueryBuilder":
        """Specify fields to select (equivalent to SQL SELECT).

        Args:
            *fields: Field names to select

        Returns:
            Self for method chaining

        Example:
            >>> query.select('Name', 'Email', 'Status')
        """
        self._select_fields = list(fields) if fields else []
        return self

    def where(self, field: str, operator: str, value: Any = None) -> "QueryBuilder":
        """Add WHERE condition (equivalent to SQL WHERE).

        Args:
            field: Field name to filter on
            operator: Comparison operator (eq, gt, like, etc.)
            value: Value to compare against

        Returns:
            Self for method chaining

        Example:
            >>> query.where('Status', 'eq', 'Active')
        """
        if not self._where_conditions_added:
            self._filter_builder.where(field, operator, value)
            self._where_conditions_added = True
        else:
            self._filter_builder.and_(field, operator, value)
        return self

    def where_or(self, field: str, operator: str, value: Any = None) -> "QueryBuilder":
        """Add OR WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining

        Example:
            >>> query.where('Status', 'eq', 'Active').where_or('Status', 'eq', 'Pending')
        """
        self._filter_builder.or_(field, operator, value)
        return self

    def where_and(self, field: str, operator: str, value: Any = None) -> "QueryBuilder":
        """Add AND WHERE condition (explicit).

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining

        Example:
            >>> query.where('Status', 'eq', 'Active').where_and('Age', 'gt', 18)
        """
        self._filter_builder.and_(field, operator, value)
        return self

    def where_not(self, field: str, operator: str, value: Any = None) -> "QueryBuilder":
        """Add NOT WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining

        Example:
            >>> query.where_not('Status', 'eq', 'Deleted')
        """
        self._filter_builder.not_(field, operator, value)
        return self

    def where_null(self, field: str) -> "QueryBuilder":
        """Add IS NULL condition.

        Args:
            field: Field name to check for NULL

        Returns:
            Self for method chaining

        Example:
            >>> query.where_null('DeletedAt')
        """
        return self.where(field, "null")

    def where_not_null(self, field: str) -> "QueryBuilder":
        """Add IS NOT NULL condition.

        Args:
            field: Field name to check for NOT NULL

        Returns:
            Self for method chaining

        Example:
            >>> query.where_not_null('Email')
        """
        return self.where(field, "notnull")

    def where_in(self, field: str, values: list[Any]) -> "QueryBuilder":
        """Add IN condition.

        Args:
            field: Field name
            values: List of values to match

        Returns:
            Self for method chaining

        Example:
            >>> query.where_in('Status', ['Active', 'Pending', 'Review'])
        """
        return self.where(field, "in", values)

    def where_not_in(self, field: str, values: list[Any]) -> "QueryBuilder":
        """Add NOT IN condition.

        Args:
            field: Field name
            values: List of values to exclude

        Returns:
            Self for method chaining

        Example:
            >>> query.where_not_in('Status', ['Deleted', 'Archived'])
        """
        return self.where(field, "notin", values)

    def where_like(self, field: str, pattern: str) -> "QueryBuilder":
        """Add LIKE condition for text search.

        Args:
            field: Field name
            pattern: Search pattern (use % for wildcards)

        Returns:
            Self for method chaining

        Example:
            >>> query.where_like('Name', '%John%')  # Contains "John"
            >>> query.where_like('Email', '%.com')  # Ends with ".com"
        """
        return self.where(field, "like", pattern)

    def where_between(self, field: str, start: Any, end: Any) -> "QueryBuilder":
        """Add BETWEEN condition.

        Args:
            field: Field name
            start: Start value
            end: End value

        Returns:
            Self for method chaining

        Example:
            >>> query.where_between('Age', 18, 65)
            >>> query.where_between('CreatedAt', '2023-01-01', '2023-12-31')
        """
        return self.where(field, "btw", [start, end])

    def order_by(self, field: str, direction: str = "asc") -> "QueryBuilder":
        """Add ORDER BY clause (equivalent to SQL ORDER BY).

        Args:
            field: Field name to sort by
            direction: Sort direction ('asc' or 'desc')

        Returns:
            Self for method chaining

        Example:
            >>> query.order_by('CreatedAt', 'desc')
            >>> query.order_by('Name')  # Default ascending
        """
        self._sort_builder.add(field, direction)
        return self

    def order_by_asc(self, field: str) -> "QueryBuilder":
        """Add ascending ORDER BY.

        Args:
            field: Field name to sort by

        Returns:
            Self for method chaining

        Example:
            >>> query.order_by_asc('Name')
        """
        return self.order_by(field, "asc")

    def order_by_desc(self, field: str) -> "QueryBuilder":
        """Add descending ORDER BY.

        Args:
            field: Field name to sort by

        Returns:
            Self for method chaining

        Example:
            >>> query.order_by_desc('CreatedAt')
        """
        return self.order_by(field, "desc")

    def limit(self, count: int) -> "QueryBuilder":
        """Set LIMIT clause (equivalent to SQL LIMIT).

        Args:
            count: Maximum number of records to return

        Returns:
            Self for method chaining

        Example:
            >>> query.limit(100)
        """
        if count < 1:
            raise ValueError("Limit must be greater than 0")
        self._limit_count = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """Set OFFSET clause (equivalent to SQL OFFSET).

        Args:
            count: Number of records to skip

        Returns:
            Self for method chaining

        Example:
            >>> query.offset(50)  # Skip first 50 records
        """
        if count < 0:
            raise ValueError("Offset must be non-negative")
        self._offset_count = count
        return self

    def page(self, page_number: int, page_size: int = 25) -> "QueryBuilder":
        """Set pagination (convenience method).

        Args:
            page_number: Page number (1-based)
            page_size: Number of records per page

        Returns:
            Self for method chaining

        Example:
            >>> query.page(2, 50)  # Get page 2 with 50 records per page
        """
        if page_number < 1:
            raise ValueError("Page number must be greater than 0")
        if page_size < 1:
            raise ValueError("Page size must be greater than 0")

        self._limit_count = page_size
        self._offset_count = (page_number - 1) * page_size
        return self

    def execute(self) -> list[dict[str, Any]]:
        """Execute the query and return results.

        Returns:
            List of record dictionaries

        Raises:
            NocoDBException: If the query execution fails
        """
        # Build filter string
        where_clause = self._filter_builder.build() if self._where_conditions_added else None

        # Build sort string
        sort_result = self._sort_builder.build()
        sort_clause: str | None = sort_result if sort_result else None

        # Calculate effective limit (considering offset)
        effective_limit = self._limit_count
        if self._offset_count > 0 and self._limit_count:
            # For offset, we need to fetch offset + limit records
            # and then slice the results
            effective_limit = self._offset_count + self._limit_count

        # Execute query using the table's get_records method or client directly
        if self._table is not None:
            records = self._table.get_records(
                sort=sort_clause,
                where=where_clause,
                fields=self._select_fields,
                limit=effective_limit if effective_limit else 25,
            )
        else:
            # Legacy API - use client directly
            records = self.client.get_records(
                self.table_name,
                sort=sort_clause,
                where=where_clause,
                fields=self._select_fields,
                limit=effective_limit if effective_limit else 25,
            )

        # Apply offset if specified
        if self._offset_count > 0:
            records = records[self._offset_count :]

        # Apply limit if we had to fetch extra for offset
        if self._limit_count and len(records) > self._limit_count:
            records = records[: self._limit_count]

        # Ensure return type is correct
        if isinstance(records, list):
            return records
        else:
            return []

    def count(self) -> int:
        """Get count of records matching the query conditions.

        Returns:
            Number of matching records

        Raises:
            NocoDBException: If the count operation fails
        """
        where_clause = self._filter_builder.build() if self._where_conditions_added else None
        if self._table is not None:
            result = self._table.count_records(where=where_clause)
        else:
            result = self.client.count_records(self.table_name, where=where_clause)

        # Ensure return type is int
        if isinstance(result, int):
            return result
        else:
            return 0

    def first(self) -> dict[str, Any] | None:
        """Get the first record matching the query.

        Returns:
            First matching record or None if no matches

        Example:
            >>> user = (QueryBuilder(users_table)
            ...     .where('Email', 'eq', 'john@example.com')
            ...     .first())
        """
        original_limit = self._limit_count
        self._limit_count = 1

        try:
            records = self.execute()
            return records[0] if records else None
        finally:
            self._limit_count = original_limit

    def exists(self) -> bool:
        """Check if any records match the query conditions.

        Returns:
            True if at least one record matches, False otherwise

        Example:
            >>> has_active_users = (QueryBuilder(users_table)
            ...     .where('Status', 'eq', 'Active')
            ...     .exists())
        """
        return self.count() > 0

    def clone(self) -> "QueryBuilder":
        """Create a copy of this query builder.

        Returns:
            New QueryBuilder instance with same configuration

        Example:
            >>> base_query = QueryBuilder(table).where('Status', 'eq', 'Active')
            >>> active_users = base_query.clone().where('Type', 'eq', 'User').execute()
            >>> active_admins = base_query.clone().where('Type', 'eq', 'Admin').execute()
        """
        new_builder = QueryBuilder(self._table)
        new_builder._select_fields = self._select_fields.copy() if self._select_fields else []
        new_builder._filter_builder = FilterBuilder()
        new_builder._sort_builder = SortBuilder()
        new_builder._limit_count = self._limit_count
        new_builder._offset_count = self._offset_count
        new_builder._where_conditions_added = self._where_conditions_added

        # Copy filter conditions
        if self._where_conditions_added:
            filter_string = self._filter_builder.build()
            if filter_string:
                # This is a simplified copy - for production, you'd want a proper deep copy
                new_builder._filter_builder._conditions = self._filter_builder._conditions.copy()
                new_builder._where_conditions_added = True

        # Copy sort conditions
        sort_string = self._sort_builder.build()
        if sort_string:
            new_builder._sort_builder._sorts = self._sort_builder._sorts.copy()

        return new_builder

    def reset(self) -> "QueryBuilder":
        """Reset all query conditions.

        Returns:
            Self for method chaining

        Example:
            >>> query.reset().where('Status', 'eq', 'Active')  # Start fresh
        """
        self._select_fields = []
        self._filter_builder.reset()
        self._sort_builder.reset()
        self._limit_count = None
        self._offset_count = 0
        self._where_conditions_added = False
        return self

    def to_params(self) -> dict[str, Any]:
        """Convert query to parameter dictionary for debugging.

        Returns:
            Dictionary with query parameters

        Example:
            >>> params = query.where('Status', 'eq', 'Active').limit(10).to_params()
            >>> print(params)
            {'fields': None, 'where': '(Status,eq,Active)', 'sort': None, 'limit': 10}
        """
        return {
            "fields": self._select_fields,
            "where": self._filter_builder.build() if self._where_conditions_added else None,
            "sort": self._sort_builder.build() or None,
            "limit": self._limit_count,
            "offset": self._offset_count,
        }

    def __str__(self) -> str:
        """String representation of the query.

        Returns:
            Human-readable query description
        """
        parts = []

        if self._select_fields:
            parts.append(f"SELECT {', '.join(self._select_fields)}")
        else:
            parts.append("SELECT *")

        table_id = self._table.table_id if self._table else self.table_name
        parts.append(f"FROM {table_id}")

        if self._where_conditions_added:
            where_clause = self._filter_builder.build()
            if where_clause:
                parts.append(f"WHERE {where_clause}")

        sort_clause = self._sort_builder.build()
        if sort_clause:
            parts.append(f"ORDER BY {sort_clause}")

        if self._limit_count:
            parts.append(f"LIMIT {self._limit_count}")

        if self._offset_count > 0:
            parts.append(f"OFFSET {self._offset_count}")

        return " ".join(parts)
