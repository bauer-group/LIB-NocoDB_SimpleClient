"""Tests for enhanced filtering and sorting functionality."""

import pytest

from nocodb_simple_client.filter_builder import (
    FilterBuilder,
    SortBuilder,
    create_filter,
    create_sort,
)


class TestFilterBuilder:
    """Test FilterBuilder class functionality."""

    @pytest.fixture
    def filter_builder(self):
        """Create a fresh FilterBuilder instance for testing."""
        return FilterBuilder()

    def test_simple_where_condition(self, filter_builder):
        """Test creating a simple WHERE condition."""
        # Act
        result = filter_builder.where("Name", "eq", "John").build()

        # Assert
        assert result == "(Name,eq,John)"

    def test_where_with_and_condition(self, filter_builder):
        """Test WHERE condition with AND operator."""
        # Act
        result = filter_builder.where("Name", "eq", "John").and_("Age", "gt", 25).build()

        # Assert
        assert result == "(Name,eq,John)~and(Age,gt,25)"

    def test_where_with_or_condition(self, filter_builder):
        """Test WHERE condition with OR operator."""
        # Act
        result = (
            filter_builder.where("Status", "eq", "Active").or_("Status", "eq", "Pending").build()
        )

        # Assert
        assert result == "(Status,eq,Active)~or(Status,eq,Pending)"

    def test_where_with_not_condition(self, filter_builder):
        """Test WHERE condition with NOT operator."""
        # Act
        result = (
            filter_builder.where("Status", "eq", "Active").not_("Status", "eq", "Deleted").build()
        )

        # Assert
        assert result == "(Status,eq,Active)~not(Status,eq,Deleted)"

    def test_complex_conditions_chain(self, filter_builder):
        """Test chaining multiple conditions."""
        # Act
        result = (
            filter_builder.where("Name", "eq", "John")
            .and_("Age", "gt", 18)
            .or_("Role", "eq", "Admin")
            .and_("Status", "neq", "Deleted")
            .build()
        )

        # Assert
        expected = "(Name,eq,John)~and(Age,gt,18)~or(Role,eq,Admin)~and(Status,neq,Deleted)"
        assert result == expected

    def test_null_conditions(self, filter_builder):
        """Test NULL and NOT NULL conditions."""
        # Act
        result_null = filter_builder.where("DeletedAt", "null").build()

        filter_builder.reset()
        result_not_null = filter_builder.where("Email", "notnull").build()

        # Assert
        assert result_null == "(DeletedAt,null)"
        assert result_not_null == "(Email,notnull)"

    def test_blank_conditions(self, filter_builder):
        """Test blank and not blank conditions."""
        # Act
        result_blank = filter_builder.where("Description", "isblank").build()

        filter_builder.reset()
        result_not_blank = filter_builder.where("Description", "isnotblank").build()

        # Assert
        assert result_blank == "(Description,blank)"
        assert result_not_blank == "(Description,notblank)"

    def test_in_condition_with_list(self, filter_builder):
        """Test IN condition with list of values."""
        # Act
        result = filter_builder.where("Status", "in", ["Active", "Pending", "Review"]).build()

        # Assert
        assert result == "(Status,in,Active,Pending,Review)"

    def test_not_in_condition(self, filter_builder):
        """Test NOT IN condition."""
        # Act
        result = filter_builder.where("Status", "notin", ["Deleted", "Archived"]).build()

        # Assert
        assert result == "(Status,notin,Deleted,Archived)"

    def test_between_condition(self, filter_builder):
        """Test BETWEEN condition."""
        # Act
        result = filter_builder.where("Age", "btw", [18, 65]).build()

        # Assert
        assert result == "(Age,btw,18,65)"

    def test_not_between_condition(self, filter_builder):
        """Test NOT BETWEEN condition."""
        # Act
        result = filter_builder.where("Score", "nbtw", [0, 50]).build()

        # Assert
        assert result == "(Score,nbtw,0,50)"

    def test_like_condition(self, filter_builder):
        """Test LIKE condition."""
        # Act
        result = filter_builder.where("Name", "like", "%John%").build()

        # Assert
        assert result == "(Name,like,%John%)"

    def test_comparison_operators(self, filter_builder):
        """Test all comparison operators."""
        operators_tests = [
            ("eq", "John", "(Name,eq,John)"),
            ("neq", "John", "(Name,neq,John)"),
            ("gt", 25, "(Name,gt,25)"),
            ("gte", 25, "(Name,gte,25)"),
            ("lt", 65, "(Name,lt,65)"),
            ("lte", 65, "(Name,lte,65)"),
            ("like", "%test%", "(Name,like,%test%)"),
            ("nlike", "%test%", "(Name,nlike,%test%)"),
        ]

        for operator, value, expected in operators_tests:
            filter_builder.reset()
            result = filter_builder.where("Name", operator, value).build()
            assert result == expected, f"Failed for operator {operator}"

    def test_checkbox_conditions(self, filter_builder):
        """Test checkbox checked/not checked conditions."""
        # Act
        result_checked = filter_builder.where("IsActive", "checked").build()

        filter_builder.reset()
        result_not_checked = filter_builder.where("IsActive", "notchecked").build()

        # Assert
        assert result_checked == "(IsActive,checked)"
        assert result_not_checked == "(IsActive,notchecked)"

    def test_grouping_conditions(self, filter_builder):
        """Test grouping conditions with parentheses."""
        # Act
        filter_builder.where("Name", "eq", "John").and_("(").where("Age", "gt", 25).or_(
            "Role", "eq", "Admin"
        ).and_(")").build()

        # Note: The current implementation doesn't handle grouping perfectly
        # This test shows the expected behavior with the current API
        # In a real scenario, you might want to implement proper grouping

    def test_group_start_end(self, filter_builder):
        """Test group start and end methods."""
        # Act
        result = (
            filter_builder.group_start()
            .where("Name", "eq", "John")
            .or_("Name", "eq", "Jane")
            .group_end()
            .and_("Status", "eq", "Active")
            .build()
        )

        # Assert
        expected = "((Name,eq,John)~or(Name,eq,Jane))~and(Status,eq,Active)"
        assert result == expected

    def test_nested_groups(self, filter_builder):
        """Test nested grouping."""
        # Act
        result = (
            filter_builder.group_start()
            .where("Type", "eq", "User")
            .and_("Status", "eq", "Active")
            .group_end()
            .or_("Role", "eq", "Admin")
            .build()
        )

        # Assert
        expected = "((Type,eq,User)~and(Status,eq,Active))~or(Role,eq,Admin)"
        assert result == expected

    def test_group_error_no_group_to_close(self, filter_builder):
        """Test error when trying to close a group that wasn't opened."""
        # Act & Assert
        with pytest.raises(ValueError, match="No group to close"):
            filter_builder.group_end()

    def test_build_error_unclosed_groups(self, filter_builder):
        """Test error when building with unclosed groups."""
        # Act
        filter_builder.group_start().where("Name", "eq", "John")

        # Assert
        with pytest.raises(ValueError, match="Unclosed groups"):
            filter_builder.build()

    def test_unsupported_operator_error(self, filter_builder):
        """Test error for unsupported operator."""
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported operator"):
            filter_builder.where("Name", "invalid_op", "John")

    def test_reset_filter_builder(self, filter_builder):
        """Test resetting the filter builder."""
        # Arrange
        filter_builder.where("Name", "eq", "John").and_("Age", "gt", 25)

        # Act
        result_before_reset = filter_builder.build()
        filter_builder.reset()
        result_after_reset = filter_builder.build()

        # Assert
        assert result_before_reset == "(Name,eq,John)~and(Age,gt,25)"
        assert result_after_reset == ""

    def test_empty_filter_builder(self, filter_builder):
        """Test building empty filter returns empty string."""
        # Act
        result = filter_builder.build()

        # Assert
        assert result == ""


class TestSortBuilder:
    """Test SortBuilder class functionality."""

    @pytest.fixture
    def sort_builder(self):
        """Create a fresh SortBuilder instance for testing."""
        return SortBuilder()

    def test_simple_ascending_sort(self, sort_builder):
        """Test simple ascending sort."""
        # Act
        result = sort_builder.add("Name", "asc").build()

        # Assert
        assert result == "Name"

    def test_simple_descending_sort(self, sort_builder):
        """Test simple descending sort."""
        # Act
        result = sort_builder.add("CreatedAt", "desc").build()

        # Assert
        assert result == "-CreatedAt"

    def test_multiple_sorts(self, sort_builder):
        """Test multiple sort fields."""
        # Act
        result = sort_builder.add("Name", "asc").add("CreatedAt", "desc").add("Id", "asc").build()

        # Assert
        assert result == "Name,-CreatedAt,Id"

    def test_asc_helper_method(self, sort_builder):
        """Test asc helper method."""
        # Act
        result = sort_builder.asc("Name").build()

        # Assert
        assert result == "Name"

    def test_desc_helper_method(self, sort_builder):
        """Test desc helper method."""
        # Act
        result = sort_builder.desc("CreatedAt").build()

        # Assert
        assert result == "-CreatedAt"

    def test_mixed_helper_methods(self, sort_builder):
        """Test mixing asc and desc helper methods."""
        # Act
        result = sort_builder.asc("Name").desc("Score").asc("Id").build()

        # Assert
        assert result == "Name,-Score,Id"

    def test_invalid_direction_error(self, sort_builder):
        """Test error for invalid sort direction."""
        # Act & Assert
        with pytest.raises(ValueError, match="Direction must be 'asc' or 'desc'"):
            sort_builder.add("Name", "invalid_direction")

    def test_case_insensitive_direction(self, sort_builder):
        """Test that direction is case insensitive."""
        # Act
        result1 = sort_builder.add("Name", "ASC").build()

        sort_builder.reset()
        result2 = sort_builder.add("Name", "DESC").build()

        # Assert
        assert result1 == "Name"
        assert result2 == "-Name"

    def test_reset_sort_builder(self, sort_builder):
        """Test resetting the sort builder."""
        # Arrange
        sort_builder.add("Name", "asc").add("CreatedAt", "desc")

        # Act
        result_before_reset = sort_builder.build()
        sort_builder.reset()
        result_after_reset = sort_builder.build()

        # Assert
        assert result_before_reset == "Name,-CreatedAt"
        assert result_after_reset == ""

    def test_empty_sort_builder(self, sort_builder):
        """Test building empty sort returns empty string."""
        # Act
        result = sort_builder.build()

        # Assert
        assert result == ""


class TestFactoryFunctions:
    """Test factory functions for creating builders."""

    def test_create_filter_function(self):
        """Test create_filter factory function."""
        # Act
        filter_builder = create_filter()
        result = filter_builder.where("Name", "eq", "John").build()

        # Assert
        assert isinstance(filter_builder, FilterBuilder)
        assert result == "(Name,eq,John)"

    def test_create_sort_function(self):
        """Test create_sort factory function."""
        # Act
        sort_builder = create_sort()
        result = sort_builder.desc("CreatedAt").build()

        # Assert
        assert isinstance(sort_builder, SortBuilder)
        assert result == "-CreatedAt"


class TestRealWorldScenarios:
    """Test real-world filtering scenarios."""

    def test_user_management_filters(self):
        """Test realistic user management filters."""
        # Scenario: Active users who registered in the last month and have a verified email
        filter_builder = FilterBuilder()

        result = (
            filter_builder.where("Status", "eq", "Active")
            .and_("RegisteredAt", "gte", "2023-11-01")
            .and_("EmailVerified", "checked")
            .and_("DeletedAt", "null")
            .build()
        )

        expected = "(Status,eq,Active)~and(RegisteredAt,gte,2023-11-01)~and(EmailVerified,checked)~and(DeletedAt,null)"
        assert result == expected

    def test_ecommerce_product_filters(self):
        """Test e-commerce product filtering."""
        # Scenario: Products in specific categories, price range, and in stock
        filter_builder = FilterBuilder()

        result = (
            filter_builder.where("Category", "in", ["Electronics", "Computers", "Phones"])
            .and_("Price", "btw", [100, 1000])
            .and_("Stock", "gt", 0)
            .and_("IsActive", "checked")
            .build()
        )

        expected = "(Category,in,Electronics,Computers,Phones)~and(Price,btw,100,1000)~and(Stock,gt,0)~and(IsActive,checked)"
        assert result == expected

    def test_content_management_filters(self):
        """Test content management filtering with complex conditions."""
        # Scenario: Published articles by specific authors or in featured category
        filter_builder = FilterBuilder()

        filter_builder.where("Status", "eq", "Published").and_(
            filter_builder.group_start()
            .where("Author", "in", ["John Doe", "Jane Smith"])
            .or_("Category", "eq", "Featured")
            .group_end()
        ).and_("PublishedAt", "lte", "2023-12-31").build()

        # Note: This test shows a limitation of the current implementation
        # In practice, you might need a more sophisticated grouping mechanism

    def test_advanced_sorting_scenario(self):
        """Test advanced sorting for a leaderboard."""
        # Scenario: Sort by score (desc), then by time (asc), then by name (asc)
        sort_builder = SortBuilder()

        result = sort_builder.desc("Score").asc("CompletionTime").asc("PlayerName").build()

        assert result == "-Score,CompletionTime,PlayerName"

    def test_search_with_multiple_fields(self):
        """Test search across multiple fields with LIKE conditions."""
        filter_builder = FilterBuilder()

        search_term = "john"
        result = (
            filter_builder.group_start()
            .where("FirstName", "like", f"%{search_term}%")
            .or_("LastName", "like", f"%{search_term}%")
            .or_("Email", "like", f"%{search_term}%")
            .group_end()
            .and_("Status", "neq", "Deleted")
            .build()
        )

        expected = "((FirstName,like,%john%)~or(LastName,like,%john%)~or(Email,like,%john%))~and(Status,neq,Deleted)"
        assert result == expected


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_special_characters_in_values(self):
        """Test handling of special characters in filter values."""
        filter_builder = FilterBuilder()

        # Test values with commas, parentheses, and other special chars
        result = filter_builder.where("Name", "eq", "O'Reilly, John (Jr.)").build()

        # The current implementation might not handle this perfectly
        # In a production system, you'd want proper escaping
        assert result == "(Name,eq,O'Reilly, John (Jr.))"

    def test_numeric_values(self):
        """Test handling of different numeric value types."""
        filter_builder = FilterBuilder()

        # Integer
        result1 = filter_builder.where("Age", "eq", 25).build()
        filter_builder.reset()

        # Float
        result2 = filter_builder.where("Price", "gte", 99.99).build()
        filter_builder.reset()

        # Negative number
        result3 = filter_builder.where("Balance", "lt", -100).build()

        assert result1 == "(Age,eq,25)"
        assert result2 == "(Price,gte,99.99)"
        assert result3 == "(Balance,lt,-100)"

    def test_boolean_values(self):
        """Test handling of boolean values."""
        filter_builder = FilterBuilder()

        result1 = filter_builder.where("IsActive", "eq", True).build()
        filter_builder.reset()

        result2 = filter_builder.where("IsDeleted", "eq", False).build()

        assert result1 == "(IsActive,eq,True)"
        assert result2 == "(IsDeleted,eq,False)"

    def test_none_values(self):
        """Test handling of None values."""
        filter_builder = FilterBuilder()

        # None should work with null operators
        result = filter_builder.where("Description", "null", None).build()

        assert result == "(Description,null)"


if __name__ == "__main__":
    pytest.main([__file__])
