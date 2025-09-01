"""Tests for field/column management functionality."""

from unittest.mock import Mock

import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.columns import NocoDBColumns, TableColumns


class TestNocoDBColumns:
    """Test NocoDBColumns class functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def columns_manager(self, mock_client):
        """Create a columns manager instance for testing."""
        return NocoDBColumns(mock_client)

    def test_get_columns_success(self, mock_client, columns_manager):
        """Test successful retrieval of columns."""
        # Arrange
        table_id = "table1"
        expected_columns = [
            {
                "id": "col1",
                "title": "Name",
                "column_name": "name",
                "uidt": "SingleLineText",
                "dt": "varchar",
            },
            {
                "id": "col2",
                "title": "Email",
                "column_name": "email",
                "uidt": "Email",
                "dt": "varchar",
            },
        ]

        mock_client._get.return_value = {"list": expected_columns}

        # Act
        result = columns_manager.get_columns(table_id)

        # Assert
        assert result == expected_columns
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/columns")

    def test_get_column_success(self, mock_client, columns_manager):
        """Test successful retrieval of a single column."""
        # Arrange
        table_id = "table1"
        column_id = "col1"
        expected_column = {
            "id": column_id,
            "title": "Name",
            "column_name": "name",
            "uidt": "SingleLineText",
            "dt": "varchar",
            "dtxp": 255,
        }

        mock_client._get.return_value = expected_column

        # Act
        result = columns_manager.get_column(table_id, column_id)

        # Assert
        assert result == expected_column
        mock_client._get.assert_called_once_with(f"api/v2/tables/{table_id}/columns/{column_id}")

    def test_create_column_success(self, mock_client, columns_manager):
        """Test successful column creation."""
        # Arrange
        table_id = "table1"
        title = "New Column"
        column_type = "singlelinetext"
        options = {"dtxp": 100}

        expected_column = {
            "id": "new_col_id",
            "title": title,
            "column_name": "new_column",
            "uidt": "SingleLineText",
        }

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_column(table_id, title, column_type, **options)

        # Assert
        assert result == expected_column
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args
        assert f"api/v2/tables/{table_id}/columns" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == title
        assert data["column_name"] == "new_column"
        assert data["uidt"] == "SingleLineText"
        assert data["dtxp"] == 100

    def test_create_column_invalid_type(self, mock_client, columns_manager):
        """Test creating column with invalid type raises ValueError."""
        # Arrange
        table_id = "table1"
        title = "New Column"
        invalid_type = "invalid_type"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid column type"):
            columns_manager.create_column(table_id, title, invalid_type)

    def test_update_column_success(self, mock_client, columns_manager):
        """Test successful column update."""
        # Arrange
        table_id = "table1"
        column_id = "col1"
        new_title = "Updated Column"
        options = {"dtxp": 200}

        expected_column = {
            "id": column_id,
            "title": new_title,
            "column_name": "updated_column",
            "dtxp": 200,
        }

        mock_client._patch.return_value = expected_column

        # Act
        result = columns_manager.update_column(table_id, column_id, title=new_title, **options)

        # Assert
        assert result == expected_column
        mock_client._patch.assert_called_once()
        call_args = mock_client._patch.call_args
        assert f"api/v2/tables/{table_id}/columns/{column_id}" in call_args[0][0]

        data = call_args[1]["data"]
        assert data["title"] == new_title
        assert data["column_name"] == "updated_column"
        assert data["dtxp"] == 200

    def test_update_column_no_changes(self, mock_client, columns_manager):
        """Test updating column with no changes raises ValueError."""
        # Arrange
        table_id = "table1"
        column_id = "col1"

        # Act & Assert
        with pytest.raises(ValueError, match="At least one parameter must be provided"):
            columns_manager.update_column(table_id, column_id)

    def test_delete_column_success(self, mock_client, columns_manager):
        """Test successful column deletion."""
        # Arrange
        table_id = "table1"
        column_id = "col1"

        mock_client._delete.return_value = {"success": True}

        # Act
        result = columns_manager.delete_column(table_id, column_id)

        # Assert
        assert result is True
        mock_client._delete.assert_called_once_with(f"api/v2/tables/{table_id}/columns/{column_id}")

    def test_create_text_column_success(self, mock_client, columns_manager):
        """Test creating a text column with specific options."""
        # Arrange
        table_id = "table1"
        title = "Full Name"
        max_length = 255
        default_value = "Unknown"

        expected_column = {"id": "text_col_id", "title": title, "uidt": "SingleLineText"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_text_column(
            table_id, title, max_length=max_length, default_value=default_value
        )

        # Assert
        assert result == expected_column
        mock_client._post.assert_called_once()
        call_args = mock_client._post.call_args

        data = call_args[1]["data"]
        assert data["title"] == title
        assert data["uidt"] == "SingleLineText"
        assert data["dtxp"] == max_length
        assert data["cdf"] == default_value

    def test_create_longtext_column_success(self, mock_client, columns_manager):
        """Test creating a long text column."""
        # Arrange
        table_id = "table1"
        title = "Description"
        default_value = "No description provided"

        expected_column = {"id": "longtext_col_id", "title": title, "uidt": "LongText"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_longtext_column(
            table_id, title, default_value=default_value
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "LongText"
        assert data["cdf"] == default_value

    def test_create_number_column_success(self, mock_client, columns_manager):
        """Test creating a number column with precision and scale."""
        # Arrange
        table_id = "table1"
        title = "Price"
        precision = 10
        scale = 2
        default_value = 0.00

        expected_column = {"id": "number_col_id", "title": title, "uidt": "Number"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_number_column(
            table_id, title, precision=precision, scale=scale, default_value=default_value
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Number"
        assert data["dtxp"] == precision
        assert data["dtxs"] == scale
        assert data["cdf"] == "0.0"

    def test_create_checkbox_column_success(self, mock_client, columns_manager):
        """Test creating a checkbox column."""
        # Arrange
        table_id = "table1"
        title = "Is Active"
        default_value = True

        expected_column = {"id": "checkbox_col_id", "title": title, "uidt": "Checkbox"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_checkbox_column(
            table_id, title, default_value=default_value
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Checkbox"
        assert data["cdf"] == "1"  # True should be converted to "1"

    def test_create_checkbox_column_false_default(self, mock_client, columns_manager):
        """Test creating checkbox column with False default."""
        # Arrange
        table_id = "table1"
        title = "Is Deleted"
        default_value = False

        expected_column = {"id": "checkbox_col_id", "title": title}
        mock_client._post.return_value = expected_column

        # Act
        columns_manager.create_checkbox_column(table_id, title, default_value=default_value)

        # Assert
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["cdf"] == "0"  # False should be converted to "0"

    def test_create_singleselect_column_success(self, mock_client, columns_manager):
        """Test creating a single select column."""
        # Arrange
        table_id = "table1"
        title = "Status"
        options = [
            {"title": "Active", "color": "#00ff00"},
            {"title": "Inactive", "color": "#ff0000"},
            {"title": "Pending", "color": "#ffff00"},
        ]

        expected_column = {"id": "select_col_id", "title": title, "uidt": "SingleSelect"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_singleselect_column(table_id, title, options)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "SingleSelect"
        assert data["dtxp"] == options

    def test_create_multiselect_column_success(self, mock_client, columns_manager):
        """Test creating a multi select column."""
        # Arrange
        table_id = "table1"
        title = "Tags"
        options = [
            {"title": "Important", "color": "#ff0000"},
            {"title": "Urgent", "color": "#ff8800"},
            {"title": "Review", "color": "#0088ff"},
        ]

        expected_column = {"id": "multiselect_col_id", "title": title, "uidt": "MultiSelect"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_multiselect_column(table_id, title, options)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "MultiSelect"
        assert data["dtxp"] == options

    def test_create_date_column_success(self, mock_client, columns_manager):
        """Test creating a date column."""
        # Arrange
        table_id = "table1"
        title = "Created Date"
        date_format = "DD/MM/YYYY"

        expected_column = {"id": "date_col_id", "title": title, "uidt": "Date"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_date_column(table_id, title, date_format=date_format)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Date"
        assert data["meta"]["date_format"] == date_format

    def test_create_datetime_column_success(self, mock_client, columns_manager):
        """Test creating a datetime column."""
        # Arrange
        table_id = "table1"
        title = "Last Updated"
        date_format = "YYYY-MM-DD"
        time_format = "HH:mm:ss"

        expected_column = {"id": "datetime_col_id", "title": title, "uidt": "DateTime"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_datetime_column(
            table_id, title, date_format=date_format, time_format=time_format
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "DateTime"
        assert data["meta"]["date_format"] == date_format
        assert data["meta"]["time_format"] == time_format

    def test_create_email_column_success(self, mock_client, columns_manager):
        """Test creating an email column."""
        # Arrange
        table_id = "table1"
        title = "Email Address"
        validate = True

        expected_column = {"id": "email_col_id", "title": title, "uidt": "Email"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_email_column(table_id, title, validate=validate)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Email"
        assert data["meta"]["validate"] == validate

    def test_create_url_column_success(self, mock_client, columns_manager):
        """Test creating a URL column."""
        # Arrange
        table_id = "table1"
        title = "Website"
        validate = False

        expected_column = {"id": "url_col_id", "title": title, "uidt": "URL"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_url_column(table_id, title, validate=validate)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "URL"
        assert data["meta"]["validate"] == validate

    def test_create_attachment_column_success(self, mock_client, columns_manager):
        """Test creating an attachment column."""
        # Arrange
        table_id = "table1"
        title = "Profile Picture"

        expected_column = {"id": "attachment_col_id", "title": title, "uidt": "Attachment"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_attachment_column(table_id, title)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Attachment"

    def test_create_rating_column_success(self, mock_client, columns_manager):
        """Test creating a rating column."""
        # Arrange
        table_id = "table1"
        title = "Rating"
        max_rating = 10
        icon = "heart"
        color = "#ff0066"

        expected_column = {"id": "rating_col_id", "title": title, "uidt": "Rating"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_rating_column(
            table_id, title, max_rating=max_rating, icon=icon, color=color
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Rating"
        assert data["meta"]["max"] == max_rating
        assert data["meta"]["icon"]["full"] == icon
        assert data["meta"]["icon"]["empty"] == "heart_outline"
        assert data["meta"]["color"] == color

    def test_create_formula_column_success(self, mock_client, columns_manager):
        """Test creating a formula column."""
        # Arrange
        table_id = "table1"
        title = "Full Name"
        formula = "CONCATENATE({FirstName}, ' ', {LastName})"

        expected_column = {"id": "formula_col_id", "title": title, "uidt": "Formula"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_formula_column(table_id, title, formula)

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "Formula"
        assert data["formula"] == formula

    def test_create_link_column_success(self, mock_client, columns_manager):
        """Test creating a link/relation column."""
        # Arrange
        table_id = "table1"
        title = "Related Orders"
        related_table_id = "orders_table"
        relation_type = "hm"  # has many

        expected_column = {"id": "link_col_id", "title": title, "uidt": "LinkToAnotherRecord"}

        mock_client._post.return_value = expected_column

        # Act
        result = columns_manager.create_link_column(
            table_id, title, related_table_id, relation_type
        )

        # Assert
        assert result == expected_column
        call_args = mock_client._post.call_args
        data = call_args[1]["data"]
        assert data["uidt"] == "LinkToAnotherRecord"
        assert data["childId"] == related_table_id
        assert data["type"] == relation_type

    def test_get_column_by_name_found(self, mock_client, columns_manager):
        """Test finding column by name successfully."""
        # Arrange
        table_id = "table1"
        column_name = "email"

        columns = [
            {"id": "col1", "title": "Name", "column_name": "name"},
            {"id": "col2", "title": "Email", "column_name": "email"},
            {"id": "col3", "title": "Status", "column_name": "status"},
        ]

        mock_client._get.return_value = {"list": columns}

        # Act
        result = columns_manager.get_column_by_name(table_id, column_name)

        # Assert
        assert result is not None
        assert result["id"] == "col2"
        assert result["title"] == "Email"
        assert result["column_name"] == "email"

    def test_get_column_by_name_by_title(self, mock_client, columns_manager):
        """Test finding column by title."""
        # Arrange
        table_id = "table1"
        column_title = "Email"

        columns = [
            {"id": "col1", "title": "Name", "column_name": "name"},
            {"id": "col2", "title": "Email", "column_name": "email"},
        ]

        mock_client._get.return_value = {"list": columns}

        # Act
        result = columns_manager.get_column_by_name(table_id, column_title)

        # Assert
        assert result is not None
        assert result["id"] == "col2"
        assert result["title"] == "Email"

    def test_get_column_by_name_not_found(self, mock_client, columns_manager):
        """Test column not found by name."""
        # Arrange
        table_id = "table1"
        column_name = "nonexistent"

        columns = [
            {"id": "col1", "title": "Name", "column_name": "name"},
            {"id": "col2", "title": "Email", "column_name": "email"},
        ]

        mock_client._get.return_value = {"list": columns}

        # Act
        result = columns_manager.get_column_by_name(table_id, column_name)

        # Assert
        assert result is None

    def test_duplicate_column_success(self, mock_client, columns_manager):
        """Test duplicating an existing column."""
        # Arrange
        table_id = "table1"
        column_id = "col1"
        new_title = "Duplicated Column"

        original_column = {
            "id": column_id,
            "title": "Original Column",
            "uidt": "SingleLineText",
            "dtxp": 255,
            "cdf": "default_value",
        }

        expected_new_column = {"id": "new_col_id", "title": new_title, "uidt": "SingleLineText"}

        mock_client._get.return_value = original_column
        mock_client._post.return_value = expected_new_column

        # Act
        result = columns_manager.duplicate_column(table_id, column_id, new_title)

        # Assert
        assert result == expected_new_column
        mock_client._get.assert_called_once()  # Get original column
        mock_client._post.assert_called_once()  # Create new column

        post_call_args = mock_client._post.call_args
        data = post_call_args[1]["data"]
        assert data["title"] == new_title
        assert data["uidt"] == "SingleLineText"
        assert data["dtxp"] == 255
        assert data["cdf"] == "default_value"


class TestTableColumns:
    """Test TableColumns helper class."""

    @pytest.fixture
    def mock_columns_manager(self):
        """Create a mock columns manager."""
        return Mock(spec=NocoDBColumns)

    @pytest.fixture
    def table_columns(self, mock_columns_manager):
        """Create a table columns instance."""
        return TableColumns(mock_columns_manager, "test_table_id")

    def test_get_columns_delegates(self, mock_columns_manager, table_columns):
        """Test that get_columns delegates to columns manager."""
        # Arrange
        expected_columns = [{"id": "col1", "title": "Test Column"}]
        mock_columns_manager.get_columns.return_value = expected_columns

        # Act
        result = table_columns.get_columns()

        # Assert
        assert result == expected_columns
        mock_columns_manager.get_columns.assert_called_once_with("test_table_id")

    def test_get_column_delegates(self, mock_columns_manager, table_columns):
        """Test that get_column delegates to columns manager."""
        # Arrange
        column_id = "col1"
        expected_column = {"id": column_id, "title": "Test Column"}
        mock_columns_manager.get_column.return_value = expected_column

        # Act
        result = table_columns.get_column(column_id)

        # Assert
        assert result == expected_column
        mock_columns_manager.get_column.assert_called_once_with("test_table_id", column_id)

    def test_create_column_delegates(self, mock_columns_manager, table_columns):
        """Test that create_column delegates to columns manager."""
        # Arrange
        title = "New Column"
        column_type = "text"
        options = {"max_length": 100}
        expected_column = {"id": "new_col", "title": title}

        mock_columns_manager.create_column.return_value = expected_column

        # Act
        result = table_columns.create_column(title, column_type, **options)

        # Assert
        assert result == expected_column
        mock_columns_manager.create_column.assert_called_once_with(
            "test_table_id", title, column_type, **options
        )

    def test_update_column_delegates(self, mock_columns_manager, table_columns):
        """Test that update_column delegates to columns manager."""
        # Arrange
        column_id = "col1"
        title = "Updated Column"
        options = {"max_length": 200}
        expected_column = {"id": column_id, "title": title}

        mock_columns_manager.update_column.return_value = expected_column

        # Act
        result = table_columns.update_column(column_id, title, **options)

        # Assert
        assert result == expected_column
        mock_columns_manager.update_column.assert_called_once_with(
            "test_table_id", column_id, title, **options
        )

    def test_delete_column_delegates(self, mock_columns_manager, table_columns):
        """Test that delete_column delegates to columns manager."""
        # Arrange
        column_id = "col1"
        mock_columns_manager.delete_column.return_value = True

        # Act
        result = table_columns.delete_column(column_id)

        # Assert
        assert result is True
        mock_columns_manager.delete_column.assert_called_once_with("test_table_id", column_id)

    def test_get_column_by_name_delegates(self, mock_columns_manager, table_columns):
        """Test that get_column_by_name delegates to columns manager."""
        # Arrange
        column_name = "email"
        expected_column = {"id": "col2", "title": "Email", "column_name": "email"}
        mock_columns_manager.get_column_by_name.return_value = expected_column

        # Act
        result = table_columns.get_column_by_name(column_name)

        # Assert
        assert result == expected_column
        mock_columns_manager.get_column_by_name.assert_called_once_with(
            "test_table_id", column_name
        )


class TestColumnsIntegration:
    """Integration tests for columns functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with realistic responses."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def columns_manager(self, mock_client):
        """Create columns manager with mock client."""
        return NocoDBColumns(mock_client)

    def test_complete_column_management_workflow(self, mock_client, columns_manager):
        """Test complete column management workflow."""
        # Arrange
        table_id = "users_table"

        # Mock responses for the workflow
        created_column = {
            "id": "new_col_123",
            "title": "Phone Number",
            "column_name": "phone_number",
            "uidt": "SingleLineText",
        }

        updated_column = {
            "id": "new_col_123",
            "title": "Mobile Number",
            "column_name": "mobile_number",
            "uidt": "SingleLineText",
        }

        mock_client._post.return_value = created_column
        mock_client._patch.return_value = updated_column
        mock_client._delete.return_value = {"success": True}

        # Act - Complete workflow
        # 1. Create column
        column = columns_manager.create_text_column(table_id, "Phone Number", max_length=20)

        # 2. Update column
        updated = columns_manager.update_column(table_id, column["id"], title="Mobile Number")

        # 3. Delete column
        deleted = columns_manager.delete_column(table_id, column["id"])

        # Assert
        assert column["title"] == "Phone Number"
        assert column["uidt"] == "SingleLineText"

        assert updated["title"] == "Mobile Number"

        assert deleted is True

        # Verify all calls were made
        assert mock_client._post.call_count == 1  # create
        assert mock_client._patch.call_count == 1  # update
        assert mock_client._delete.call_count == 1  # delete

    def test_create_comprehensive_table_schema(self, mock_client, columns_manager):
        """Test creating a comprehensive table schema with various column types."""
        # Arrange
        table_id = "products_table"

        columns_to_create = [
            ("Name", "text"),
            ("Description", "longtext"),
            ("Price", "number"),
            ("Is Active", "checkbox"),
            ("Category", "singleselect"),
            ("Tags", "multiselect"),
            ("Created Date", "date"),
            ("Rating", "rating"),
            ("Website", "url"),
            ("Contact Email", "email"),
            ("Product Images", "attachment"),
        ]

        # Mock successful creation for all columns
        mock_responses = []
        for i, (title, col_type) in enumerate(columns_to_create):
            mock_responses.append(
                {
                    "id": f"col_{i+1}",
                    "title": title,
                    "uidt": columns_manager.COLUMN_TYPES.get(col_type, "SingleLineText"),
                }
            )

        mock_client._post.side_effect = mock_responses

        # Act - Create all columns
        created_columns = []

        # Text columns
        created_columns.append(columns_manager.create_text_column(table_id, "Name", max_length=255))
        created_columns.append(columns_manager.create_longtext_column(table_id, "Description"))

        # Number column
        created_columns.append(
            columns_manager.create_number_column(table_id, "Price", precision=10, scale=2)
        )

        # Boolean column
        created_columns.append(
            columns_manager.create_checkbox_column(table_id, "Is Active", default_value=True)
        )

        # Select columns
        category_options = [
            {"title": "Electronics", "color": "#0088ff"},
            {"title": "Clothing", "color": "#00ff88"},
            {"title": "Books", "color": "#ff8800"},
        ]
        created_columns.append(
            columns_manager.create_singleselect_column(table_id, "Category", category_options)
        )

        tag_options = [
            {"title": "New", "color": "#00ff00"},
            {"title": "Sale", "color": "#ff0000"},
            {"title": "Featured", "color": "#ffff00"},
        ]
        created_columns.append(
            columns_manager.create_multiselect_column(table_id, "Tags", tag_options)
        )

        # Date column
        created_columns.append(columns_manager.create_date_column(table_id, "Created Date"))

        # Rating column
        created_columns.append(
            columns_manager.create_rating_column(table_id, "Rating", max_rating=5)
        )

        # URL and Email columns
        created_columns.append(
            columns_manager.create_url_column(table_id, "Website", validate=True)
        )
        created_columns.append(
            columns_manager.create_email_column(table_id, "Contact Email", validate=True)
        )

        # Attachment column
        created_columns.append(columns_manager.create_attachment_column(table_id, "Product Images"))

        # Assert
        assert len(created_columns) == len(columns_to_create)
        assert mock_client._post.call_count == len(columns_to_create)

        # Verify each column was created with correct type
        for i, column in enumerate(created_columns):
            expected_title = columns_to_create[i][0]
            assert column["title"] == expected_title
            assert "id" in column


if __name__ == "__main__":
    pytest.main([__file__])
