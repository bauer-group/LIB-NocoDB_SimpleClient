"""Field/Column management for NocoDB tables.

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
    from .meta_client import NocoDBMetaClient


class NocoDBColumns:
    """Manager for NocoDB table columns/fields.

    Provides methods to manage table schema including creating, updating,
    and deleting columns of various types.
    """

    COLUMN_TYPES = {
        "id": "ID",
        "singlelinetext": "SingleLineText",
        "longtext": "LongText",
        "attachment": "Attachment",
        "checkbox": "Checkbox",
        "multiselect": "MultiSelect",
        "singleselect": "SingleSelect",
        "collaborator": "Collaborator",
        "date": "Date",
        "year": "Year",
        "time": "Time",
        "phonenumber": "PhoneNumber",
        "email": "Email",
        "url": "URL",
        "number": "Number",
        "decimal": "Decimal",
        "currency": "Currency",
        "percent": "Percent",
        "duration": "Duration",
        "rating": "Rating",
        "formula": "Formula",
        "rollup": "Rollup",
        "count": "Count",
        "lookup": "Lookup",
        "datetime": "DateTime",
        "createdtime": "CreatedTime",
        "lastmodifiedtime": "LastModifiedTime",
        "autoincrement": "AutoNumber",
        "geometry": "Geometry",
        "json": "JSON",
        "specificdbtype": "SpecificDBType",
        "barcode": "Barcode",
        "button": "Button",
        "linktoanotherrecord": "LinkToAnotherRecord",
    }

    def __init__(self, meta_client: "NocoDBMetaClient") -> None:
        """Initialize the columns manager.

        Args:
            meta_client: NocoDBMetaClient instance (inherits from NocoDBClient)
        """
        self.meta_client = meta_client

    def get_columns(self, table_id: str) -> list[dict[str, Any]]:
        """Get all columns for a table.

        Args:
            table_id: ID of the table

        Returns:
            List of column dictionaries

        Raises:
            NocoDBException: For API errors
        """
        return self.meta_client.list_columns(table_id)

    def get_column(self, table_id: str, column_id: str) -> dict[str, Any]:
        """Get a specific column by ID.

        Args:
            table_id: ID of the table
            column_id: ID of the column

        Returns:
            Column dictionary

        Raises:
            NocoDBException: For API errors
            ColumnNotFoundException: If the column is not found
        """
        endpoint = f"api/v2/tables/{table_id}/columns/{column_id}"
        return self.meta_client._get(endpoint)

    def create_column(
        self, table_id: str, title: str, column_type: str, **options: Any
    ) -> dict[str, Any]:
        """Create a new column.

        Args:
            table_id: ID of the table
            title: Title/name of the column
            column_type: Type of column (text, number, date, etc.)
            **options: Additional column-specific options

        Returns:
            Created column dictionary

        Raises:
            NocoDBException: For API errors
            ValidationException: If column_type is invalid
        """
        if column_type.lower() not in self.COLUMN_TYPES:
            raise ValueError(
                f"Invalid column type: {column_type}. "
                f"Supported types: {list(self.COLUMN_TYPES.keys())}"
            )

        data = {
            "title": title,
            "column_name": title.lower().replace(" ", "_"),
            "uidt": self.COLUMN_TYPES[column_type.lower()],
        }

        # Add column-specific options
        data.update(options)

        response = self.meta_client.create_column(table_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from column creation")

    def update_column(
        self, table_id: str, column_id: str, title: str | None = None, **options: Any
    ) -> dict[str, Any]:
        """Update an existing column.

        Args:
            table_id: ID of the table
            column_id: ID of the column to update
            title: New title for the column
            **options: Updated column options

        Returns:
            Updated column dictionary

        Raises:
            NocoDBException: For API errors
            ColumnNotFoundException: If the column is not found
        """
        data = {}

        if title:
            data["title"] = title
            data["column_name"] = title.lower().replace(" ", "_")

        data.update(options)

        if not data:
            raise ValueError("At least one parameter must be provided for update")

        response = self.meta_client.update_column(column_id, data)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError("Expected dict response from column update")

    def delete_column(self, table_id: str, column_id: str) -> bool:
        """Delete a column.

        Args:
            table_id: ID of the table
            column_id: ID of the column to delete

        Returns:
            True if deletion was successful

        Raises:
            NocoDBException: For API errors
            ColumnNotFoundException: If the column is not found
        """
        response = self.meta_client.delete_column(column_id)
        return response is not None

    def create_text_column(
        self,
        table_id: str,
        title: str,
        max_length: int | None = None,
        default_value: str | None = None,
    ) -> dict[str, Any]:
        """Create a single line text column.

        Args:
            table_id: ID of the table
            title: Title of the column
            max_length: Maximum character length
            default_value: Default value

        Returns:
            Created column dictionary
        """
        options: dict[str, Any] = {}
        if max_length:
            options["dtxp"] = str(max_length)
        if default_value:
            options["cdf"] = default_value

        return self.create_column(table_id, title, "singlelinetext", **options)

    def create_longtext_column(
        self, table_id: str, title: str, default_value: str | None = None
    ) -> dict[str, Any]:
        """Create a long text column.

        Args:
            table_id: ID of the table
            title: Title of the column
            default_value: Default value

        Returns:
            Created column dictionary
        """
        options = {}
        if default_value:
            options["cdf"] = default_value

        return self.create_column(table_id, title, "longtext", **options)

    def create_number_column(
        self,
        table_id: str,
        title: str,
        precision: int | None = None,
        scale: int | None = None,
        default_value: int | float | None = None,
    ) -> dict[str, Any]:
        """Create a number column.

        Args:
            table_id: ID of the table
            title: Title of the column
            precision: Total number of digits
            scale: Number of digits after decimal point
            default_value: Default value

        Returns:
            Created column dictionary
        """
        options: dict[str, Any] = {}
        if precision:
            options["dtxp"] = str(precision)
        if scale:
            options["dtxs"] = str(scale)
        if default_value is not None:
            options["cdf"] = str(default_value)

        return self.create_column(table_id, title, "number", **options)

    def create_checkbox_column(
        self, table_id: str, title: str, default_value: bool = False
    ) -> dict[str, Any]:
        """Create a checkbox column.

        Args:
            table_id: ID of the table
            title: Title of the column
            default_value: Default checked state

        Returns:
            Created column dictionary
        """
        options = {"cdf": "1" if default_value else "0"}

        return self.create_column(table_id, title, "checkbox", **options)

    def create_singleselect_column(
        self, table_id: str, title: str, options: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Create a single select column.

        Args:
            table_id: ID of the table
            title: Title of the column
            options: List of option dictionaries with 'title' and optionally 'color'

        Returns:
            Created column dictionary

        Example:
            >>> create_singleselect_column('table1', 'Status', [
            ...     {'title': 'Active', 'color': '#00ff00'},
            ...     {'title': 'Inactive', 'color': '#ff0000'}
            ... ])
        """
        column_options = {"dtxp": options}

        return self.create_column(table_id, title, "singleselect", **column_options)

    def create_multiselect_column(
        self, table_id: str, title: str, options: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Create a multi select column.

        Args:
            table_id: ID of the table
            title: Title of the column
            options: List of option dictionaries with 'title' and optionally 'color'

        Returns:
            Created column dictionary
        """
        column_options = {"dtxp": options}

        return self.create_column(table_id, title, "multiselect", **column_options)

    def create_date_column(
        self, table_id: str, title: str, date_format: str = "YYYY-MM-DD"
    ) -> dict[str, Any]:
        """Create a date column.

        Args:
            table_id: ID of the table
            title: Title of the column
            date_format: Date display format

        Returns:
            Created column dictionary
        """
        options = {"meta": {"date_format": date_format}}

        return self.create_column(table_id, title, "date", **options)

    def create_datetime_column(
        self, table_id: str, title: str, date_format: str = "YYYY-MM-DD", time_format: str = "HH:mm"
    ) -> dict[str, Any]:
        """Create a datetime column.

        Args:
            table_id: ID of the table
            title: Title of the column
            date_format: Date display format
            time_format: Time display format

        Returns:
            Created column dictionary
        """
        options = {"meta": {"date_format": date_format, "time_format": time_format}}

        return self.create_column(table_id, title, "datetime", **options)

    def create_email_column(
        self, table_id: str, title: str, validate: bool = True
    ) -> dict[str, Any]:
        """Create an email column.

        Args:
            table_id: ID of the table
            title: Title of the column
            validate: Whether to validate email format

        Returns:
            Created column dictionary
        """
        options = {"meta": {"validate": validate}}

        return self.create_column(table_id, title, "email", **options)

    def create_url_column(self, table_id: str, title: str, validate: bool = True) -> dict[str, Any]:
        """Create a URL column.

        Args:
            table_id: ID of the table
            title: Title of the column
            validate: Whether to validate URL format

        Returns:
            Created column dictionary
        """
        options = {"meta": {"validate": validate}}

        return self.create_column(table_id, title, "url", **options)

    def create_attachment_column(self, table_id: str, title: str) -> dict[str, Any]:
        """Create an attachment column.

        Args:
            table_id: ID of the table
            title: Title of the column

        Returns:
            Created column dictionary
        """
        return self.create_column(table_id, title, "attachment")

    def create_rating_column(
        self,
        table_id: str,
        title: str,
        max_rating: int = 5,
        icon: str = "star",
        color: str = "#fcb401",
    ) -> dict[str, Any]:
        """Create a rating column.

        Args:
            table_id: ID of the table
            title: Title of the column
            max_rating: Maximum rating value
            icon: Icon to use (star, heart, thumb)
            color: Color of the rating icon

        Returns:
            Created column dictionary
        """
        options = {
            "meta": {
                "max": max_rating,
                "icon": {"full": icon, "empty": f"{icon}_outline"},
                "color": color,
            }
        }

        return self.create_column(table_id, title, "rating", **options)

    def create_formula_column(self, table_id: str, title: str, formula: str) -> dict[str, Any]:
        """Create a formula column.

        Args:
            table_id: ID of the table
            title: Title of the column
            formula: Formula expression

        Returns:
            Created column dictionary
        """
        options = {"formula": formula}

        return self.create_column(table_id, title, "formula", **options)

    def create_link_column(
        self, table_id: str, title: str, related_table_id: str, relation_type: str = "mm"
    ) -> dict[str, Any]:
        """Create a link/relation column.

        Args:
            table_id: ID of the source table
            title: Title of the column
            related_table_id: ID of the related table
            relation_type: Type of relation (hm, mm, oo)
                          hm = has many, mm = many to many, oo = one to one

        Returns:
            Created column dictionary
        """
        options = {"childId": related_table_id, "type": relation_type}

        return self.create_column(table_id, title, "LinkToAnotherRecord", **options)

    def get_column_by_name(self, table_id: str, column_name: str) -> dict[str, Any] | None:
        """Get a column by its name/title.

        Args:
            table_id: ID of the table
            column_name: Name or title of the column

        Returns:
            Column dictionary if found, None otherwise
        """
        columns = self.get_columns(table_id)

        for column in columns:
            if (
                column.get("title", "").lower() == column_name.lower()
                or column.get("column_name", "").lower() == column_name.lower()
            ):
                return column

        return None

    def duplicate_column(self, table_id: str, column_id: str, new_title: str) -> dict[str, Any]:
        """Duplicate an existing column with a new title.

        Args:
            table_id: ID of the table
            column_id: ID of the column to duplicate
            new_title: Title for the duplicated column

        Returns:
            Created column dictionary

        Raises:
            NocoDBException: For API errors
        """
        original_column = self.get_column(table_id, column_id)

        # Extract column configuration
        column_type = original_column.get("uidt", "SingleLineText")

        # Map internal type back to our types
        type_mapping = {v: k for k, v in self.COLUMN_TYPES.items()}
        column_type_key = type_mapping.get(column_type, "singlelinetext")

        # Copy relevant properties
        options = {}
        for key in ["dtxp", "dtxs", "cdf", "meta", "formula"]:
            if key in original_column:
                options[key] = original_column[key]

        return self.create_column(table_id, new_title, column_type_key, **options)


class TableColumns:
    """Helper class for managing columns on a specific table.

    This is a convenience wrapper that automatically includes table_id
    in all column operations.
    """

    def __init__(self, columns_manager: NocoDBColumns, table_id: str) -> None:
        """Initialize table-specific columns manager.

        Args:
            columns_manager: NocoDBColumns instance
            table_id: ID of the table
        """
        self._columns = columns_manager
        self._table_id = table_id

    def get_columns(self) -> list[dict[str, Any]]:
        """Get all columns for this table."""
        return self._columns.get_columns(self._table_id)

    def get_column(self, column_id: str) -> dict[str, Any]:
        """Get a specific column by ID."""
        return self._columns.get_column(self._table_id, column_id)

    def create_column(self, title: str, column_type: str, **options: Any) -> dict[str, Any]:
        """Create a new column for this table."""
        return self._columns.create_column(self._table_id, title, column_type, **options)

    def update_column(
        self, column_id: str, title: str | None = None, **options: Any
    ) -> dict[str, Any]:
        """Update an existing column."""
        return self._columns.update_column(self._table_id, column_id, title, **options)

    def delete_column(self, column_id: str) -> bool:
        """Delete a column."""
        return self._columns.delete_column(self._table_id, column_id)

    def get_column_by_name(self, column_name: str) -> dict[str, Any] | None:
        """Get a column by its name/title."""
        return self._columns.get_column_by_name(self._table_id, column_name)
