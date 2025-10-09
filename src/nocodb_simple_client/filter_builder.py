"""Advanced filtering and sorting utilities for NocoDB.

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

from typing import Any


class FilterBuilder:
    """Fluent API for building NocoDB filter conditions.

    This class provides a convenient way to build complex filter conditions
    using method chaining, similar to SQL query builders.

    Example:
        >>> filter_builder = FilterBuilder()
        >>> filter_str = (filter_builder
        ...     .where('Status', 'eq', 'Active')
        ...     .and_('Age', 'gt', 21)
        ...     .or_('Role', 'eq', 'Admin')
        ...     .build())
        >>> # Result: "(Status,eq,Active)~and(Age,gt,21)~or(Role,eq,Admin)"
    """

    # Supported comparison operators
    OPERATORS = {
        "eq": "eq",  # Equal
        "neq": "neq",  # Not equal
        "gt": "gt",  # Greater than
        "gte": "gte",  # Greater than or equal
        "lt": "lt",  # Less than
        "lte": "lte",  # Less than or equal
        "like": "like",  # Like (contains)
        "nlike": "nlike",  # Not like
        "in": "in",  # In list
        "notin": "notin",  # Not in list
        "is": "is",  # Is (null checks)
        "isnot": "isnot",  # Is not
        "isblank": "blank",  # Is blank
        "isnotblank": "notblank",  # Is not blank
        "null": "null",  # Is null
        "notnull": "notnull",  # Is not null
        "empty": "empty",  # Is empty
        "notempty": "notempty",  # Is not empty
        "btw": "btw",  # Between
        "nbtw": "nbtw",  # Not between
        "checked": "checked",  # Checkbox is checked
        "notchecked": "notchecked",  # Checkbox is not checked
    }

    # Supported logical operators
    LOGICAL_OPERATORS = ["and", "or", "not"]

    def __init__(self) -> None:
        self._conditions: list[str] = []
        self._current_group_level = 0

    def where(self, field: str, operator: str, value: Any = None) -> "FilterBuilder":
        """Add a WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator (eq, gt, like, etc.)
            value: Value to compare against (None for operators like 'null')

        Returns:
            Self for method chaining

        Raises:
            ValueError: If operator is not supported
        """
        self._add_condition(field, operator, value)
        return self

    def and_(self, field: str, operator: str, value: Any = None) -> "FilterBuilder":
        """Add an AND condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        if self._conditions:
            self._conditions.append("~and")
        self._add_condition(field, operator, value)
        return self

    def or_(self, field: str, operator: str, value: Any = None) -> "FilterBuilder":
        """Add an OR condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        if self._conditions:
            self._conditions.append("~or")
        self._add_condition(field, operator, value)
        return self

    def not_(self, field: str, operator: str, value: Any = None) -> "FilterBuilder":
        """Add a NOT condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        if self._conditions:
            self._conditions.append("~not")
        self._add_condition(field, operator, value)
        return self

    def group_start(self) -> "FilterBuilder":
        """Start a grouping with parentheses.

        Returns:
            Self for method chaining
        """
        self._conditions.append("(")
        self._current_group_level += 1
        return self

    def group_end(self) -> "FilterBuilder":
        """End a grouping with parentheses.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If no group is open
        """
        if self._current_group_level <= 0:
            raise ValueError("No group to close")
        self._conditions.append(")")
        self._current_group_level -= 1
        return self

    def _add_condition(self, field: str, operator: str, value: Any = None) -> None:
        """Add a condition to the filter.

        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare

        Raises:
            ValueError: If operator is not supported
        """
        if operator not in self.OPERATORS:
            raise ValueError(
                f"Unsupported operator: {operator}. "
                f"Supported operators: {list(self.OPERATORS.keys())}"
            )

        mapped_operator = self.OPERATORS[operator]

        # Handle operators that don't need values
        if operator in [
            "isblank",
            "isnotblank",
            "null",
            "notnull",
            "empty",
            "notempty",
            "checked",
            "notchecked",
        ]:
            condition = f"({field},{mapped_operator})"
        elif operator == "btw" and isinstance(value, list | tuple) and len(value) == 2:
            # Between operator needs two values
            condition = f"({field},{mapped_operator},{value[0]},{value[1]})"
        elif operator in ["in", "notin"] and isinstance(value, list | tuple):
            # IN operator with multiple values
            value_str = ",".join(str(v) for v in value)
            condition = f"({field},{mapped_operator},{value_str})"
        else:
            # Standard operator with single value
            condition = f"({field},{mapped_operator},{value})"

        self._conditions.append(condition)

    def build(self) -> str:
        """Build the final filter string.

        Returns:
            NocoDB-compatible filter string

        Raises:
            ValueError: If groups are not properly closed
        """
        if self._current_group_level > 0:
            raise ValueError(f"Unclosed groups: {self._current_group_level}")

        if not self._conditions:
            return ""

        return "".join(self._conditions)

    def reset(self) -> "FilterBuilder":
        """Reset the filter builder to start fresh.

        Returns:
            Self for method chaining
        """
        self._conditions.clear()
        self._current_group_level = 0
        return self


class SortBuilder:
    """Builder for creating sort specifications.

    Example:
        >>> sort_builder = SortBuilder()
        >>> sort_str = (sort_builder
        ...     .add('Name', 'asc')
        ...     .add('CreatedAt', 'desc')
        ...     .build())
        >>> # Result: "Name,-CreatedAt"
    """

    def __init__(self) -> None:
        self._sorts: list[str] = []

    def add(self, field: str, direction: str = "asc") -> "SortBuilder":
        """Add a sort field.

        Args:
            field: Field name to sort by
            direction: Sort direction ('asc' or 'desc')

        Returns:
            Self for method chaining

        Raises:
            ValueError: If direction is not 'asc' or 'desc'
        """
        if direction.lower() not in ["asc", "desc"]:
            raise ValueError("Direction must be 'asc' or 'desc'")

        if direction.lower() == "desc":
            self._sorts.append(f"-{field}")
        else:
            self._sorts.append(field)

        return self

    def asc(self, field: str) -> "SortBuilder":
        """Add ascending sort.

        Args:
            field: Field name to sort by

        Returns:
            Self for method chaining
        """
        return self.add(field, "asc")

    def desc(self, field: str) -> "SortBuilder":
        """Add descending sort.

        Args:
            field: Field name to sort by

        Returns:
            Self for method chaining
        """
        return self.add(field, "desc")

    def build(self) -> str:
        """Build the final sort string.

        Returns:
            NocoDB-compatible sort string
        """
        return ",".join(self._sorts)

    def reset(self) -> "SortBuilder":
        """Reset the sort builder.

        Returns:
            Self for method chaining
        """
        self._sorts.clear()
        return self


def create_filter() -> FilterBuilder:
    """Create a new FilterBuilder instance.

    Returns:
        New FilterBuilder instance

    Example:
        >>> from nocodb_simple_client import create_filter
        >>> filter_str = (create_filter()
        ...     .where('Status', 'eq', 'Active')
        ...     .and_('Age', 'gt', 21)
        ...     .build())
    """
    return FilterBuilder()


def create_sort() -> SortBuilder:
    """Create a new SortBuilder instance.

    Returns:
        New SortBuilder instance

    Example:
        >>> from nocodb_simple_client import create_sort
        >>> sort_str = (create_sort()
        ...     .desc('CreatedAt')
        ...     .asc('Name')
        ...     .build())
    """
    return SortBuilder()
