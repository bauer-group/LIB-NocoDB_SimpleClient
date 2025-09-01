"""
Comprehensive tests for the QueryBuilder functionality.
"""

import os
import sys
from datetime import date
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.exceptions import NocoDBError, QueryBuilderError
from nocodb_simple_client.query_builder import QueryBuilder


class TestQueryBuilderInitialization:
    """Test QueryBuilder initialization and basic setup."""

    @pytest.fixture
    def client(self):
        """Create a mock client for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        return client

    @pytest.fixture
    def query_builder(self, client):
        """Create a QueryBuilder instance for testing."""
        return QueryBuilder(client, "users")

    def test_query_builder_initialization(self, query_builder, client):
        """Test QueryBuilder initialization with client and table."""
        assert query_builder.client == client
        assert query_builder.table_name == "users"
        assert query_builder._where_conditions == []
        assert query_builder._select_fields == []
        assert query_builder._sort_conditions == []
        assert query_builder._limit_value is None
        assert query_builder._offset_value is None

    def test_query_builder_from_table(self, client):
        """Test creating QueryBuilder from table name."""
        qb = QueryBuilder.from_table(client, "products")

        assert qb.client == client
        assert qb.table_name == "products"

    def test_query_builder_clone(self, query_builder):
        """Test cloning QueryBuilder instance."""
        # Add some conditions
        query_builder.where("name", "eq", "John").select("id", "name")

        # Clone the builder
        cloned = query_builder.clone()

        assert cloned is not query_builder
        assert cloned.table_name == query_builder.table_name
        assert cloned._where_conditions == query_builder._where_conditions
        assert cloned._select_fields == query_builder._select_fields


class TestWhereConditions:
    """Test WHERE condition building."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_simple_where_condition(self, query_builder):
        """Test simple WHERE condition."""
        result = query_builder.where("name", "eq", "John")

        assert result is query_builder  # Method chaining
        assert len(query_builder._where_conditions) == 1

        condition = query_builder._where_conditions[0]
        assert condition["field"] == "name"
        assert condition["operator"] == "eq"
        assert condition["value"] == "John"

    def test_multiple_where_conditions(self, query_builder):
        """Test multiple WHERE conditions (AND logic)."""
        query_builder.where("age", "gt", 18).where("status", "eq", "active")

        assert len(query_builder._where_conditions) == 2
        assert query_builder._where_conditions[0]["field"] == "age"
        assert query_builder._where_conditions[1]["field"] == "status"

    def test_where_in_condition(self, query_builder):
        """Test WHERE IN condition."""
        query_builder.where_in("category", ["electronics", "books", "clothing"])

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "in"
        assert condition["value"] == ["electronics", "books", "clothing"]

    def test_where_not_in_condition(self, query_builder):
        """Test WHERE NOT IN condition."""
        query_builder.where_not_in("status", ["deleted", "archived"])

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "not_in"
        assert condition["value"] == ["deleted", "archived"]

    def test_where_between_condition(self, query_builder):
        """Test WHERE BETWEEN condition."""
        query_builder.where_between("price", 10.0, 100.0)

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "between"
        assert condition["value"] == [10.0, 100.0]

    def test_where_like_condition(self, query_builder):
        """Test WHERE LIKE condition."""
        query_builder.where_like("name", "%john%")

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "like"
        assert condition["value"] == "%john%"

    def test_where_null_condition(self, query_builder):
        """Test WHERE NULL condition."""
        query_builder.where_null("deleted_at")

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "is_null"
        assert condition["value"] is None

    def test_where_not_null_condition(self, query_builder):
        """Test WHERE NOT NULL condition."""
        query_builder.where_not_null("email")

        condition = query_builder._where_conditions[0]
        assert condition["operator"] == "is_not_null"
        assert condition["value"] is None

    def test_where_date_conditions(self, query_builder):
        """Test WHERE conditions with dates."""
        test_date = date(2023, 1, 1)

        query_builder.where("created_at", "gte", test_date)

        condition = query_builder._where_conditions[0]
        assert condition["field"] == "created_at"
        assert condition["operator"] == "gte"
        assert condition["value"] == test_date

    def test_or_where_conditions(self, query_builder):
        """Test OR WHERE conditions."""
        query_builder.where("age", "lt", 18).or_where("status", "eq", "premium")

        assert len(query_builder._where_conditions) == 2
        assert query_builder._where_conditions[1]["logic"] == "OR"

    def test_where_group_conditions(self, query_builder):
        """Test grouped WHERE conditions with parentheses."""
        query_builder.where_group(
            lambda q: (q.where("age", "gte", 18).or_where("has_guardian", "eq", True))
        ).where("status", "eq", "active")

        # Should create grouped conditions
        assert len(query_builder._where_conditions) >= 1


class TestSelectFields:
    """Test SELECT field specification."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_select_specific_fields(self, query_builder):
        """Test selecting specific fields."""
        result = query_builder.select("id", "name", "email")

        assert result is query_builder  # Method chaining
        assert query_builder._select_fields == ["id", "name", "email"]

    def test_select_fields_as_list(self, query_builder):
        """Test selecting fields as a list."""
        fields = ["id", "name", "created_at"]
        query_builder.select(fields)

        assert query_builder._select_fields == fields

    def test_select_all_fields(self, query_builder):
        """Test selecting all fields (default behavior)."""
        # Don't call select() - should select all by default
        assert query_builder._select_fields == []  # Empty means all

    def test_select_with_aliases(self, query_builder):
        """Test selecting fields with aliases."""
        query_builder.select_with_alias(
            {"full_name": "name", "email_address": "email", "user_id": "id"}
        )

        # Should store field mappings for aliases
        assert hasattr(query_builder, "_field_aliases")
        assert "full_name" in query_builder._field_aliases

    def test_add_select_field(self, query_builder):
        """Test adding additional select fields."""
        query_builder.select("id", "name")
        query_builder.add_select("email", "created_at")

        expected_fields = ["id", "name", "email", "created_at"]
        assert query_builder._select_fields == expected_fields


class TestSortingOrdering:
    """Test sorting and ordering functionality."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_order_by_ascending(self, query_builder):
        """Test ORDER BY ascending."""
        result = query_builder.order_by("name", "asc")

        assert result is query_builder
        assert len(query_builder._sort_conditions) == 1

        sort_condition = query_builder._sort_conditions[0]
        assert sort_condition["field"] == "name"
        assert sort_condition["direction"] == "asc"

    def test_order_by_descending(self, query_builder):
        """Test ORDER BY descending."""
        query_builder.order_by("created_at", "desc")

        sort_condition = query_builder._sort_conditions[0]
        assert sort_condition["field"] == "created_at"
        assert sort_condition["direction"] == "desc"

    def test_order_by_default_direction(self, query_builder):
        """Test ORDER BY with default direction (ASC)."""
        query_builder.order_by("name")

        sort_condition = query_builder._sort_conditions[0]
        assert sort_condition["direction"] == "asc"

    def test_multiple_order_by(self, query_builder):
        """Test multiple ORDER BY conditions."""
        query_builder.order_by("category", "asc").order_by("price", "desc")

        assert len(query_builder._sort_conditions) == 2
        assert query_builder._sort_conditions[0]["field"] == "category"
        assert query_builder._sort_conditions[1]["field"] == "price"

    def test_order_by_with_nulls(self, query_builder):
        """Test ORDER BY with NULL handling."""
        query_builder.order_by_with_nulls("updated_at", "asc", nulls="last")

        sort_condition = query_builder._sort_conditions[0]
        assert sort_condition["nulls"] == "last"


class TestLimitOffset:
    """Test LIMIT and OFFSET functionality."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_limit(self, query_builder):
        """Test LIMIT clause."""
        result = query_builder.limit(10)

        assert result is query_builder
        assert query_builder._limit_value == 10

    def test_offset(self, query_builder):
        """Test OFFSET clause."""
        result = query_builder.offset(50)

        assert result is query_builder
        assert query_builder._offset_value == 50

    def test_limit_and_offset(self, query_builder):
        """Test LIMIT and OFFSET together."""
        query_builder.limit(25).offset(100)

        assert query_builder._limit_value == 25
        assert query_builder._offset_value == 100

    def test_page_method(self, query_builder):
        """Test page() method for pagination."""
        query_builder.page(3, per_page=20)  # Page 3 with 20 items per page

        assert query_builder._limit_value == 20
        assert query_builder._offset_value == 40  # (3-1) * 20

    def test_take_method(self, query_builder):
        """Test take() method (alias for limit)."""
        query_builder.take(15)

        assert query_builder._limit_value == 15

    def test_skip_method(self, query_builder):
        """Test skip() method (alias for offset)."""
        query_builder.skip(30)

        assert query_builder._offset_value == 30


class TestQueryExecution:
    """Test query execution and result handling."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance with mock client."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_get_all_records(self, query_builder):
        """Test executing query to get all records."""
        mock_response = {
            "list": [{"id": 1, "name": "John", "age": 25}, {"id": 2, "name": "Jane", "age": 30}],
            "pageInfo": {"totalRows": 2},
        }

        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.return_value = mock_response["list"]

            result = query_builder.get()

            assert result == mock_response["list"]
            mock_get.assert_called_once()

    def test_get_first_record(self, query_builder):
        """Test getting the first record."""
        mock_response = [{"id": 1, "name": "John", "age": 25}]

        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.return_value = mock_response

            result = query_builder.first()

            assert result == mock_response[0]
            # Should have added limit(1)
            assert query_builder._limit_value == 1

    def test_get_first_record_empty_result(self, query_builder):
        """Test getting first record when result is empty."""
        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.return_value = []

            result = query_builder.first()

            assert result is None

    def test_count_records(self, query_builder):
        """Test counting records."""
        mock_response = {"count": 150}

        with patch.object(query_builder.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = query_builder.count()

            assert result == 150
            mock_request.assert_called_once()

    def test_exists_check(self, query_builder):
        """Test checking if records exist."""
        with patch.object(query_builder, "count") as mock_count:
            mock_count.return_value = 5

            result = query_builder.exists()

            assert result is True
            mock_count.assert_called_once()

    def test_does_not_exist_check(self, query_builder):
        """Test checking if no records exist."""
        with patch.object(query_builder, "count") as mock_count:
            mock_count.return_value = 0

            result = query_builder.exists()

            assert result is False

    def test_find_by_id(self, query_builder):
        """Test finding record by ID."""
        mock_record = {"id": 123, "name": "Test User"}

        with patch.object(query_builder.client, "get_record") as mock_get:
            mock_get.return_value = mock_record

            result = query_builder.find(123)

            assert result == mock_record
            mock_get.assert_called_once_with("users", 123)

    def test_pluck_field_values(self, query_builder):
        """Test plucking specific field values."""
        mock_records = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"},
        ]

        with patch.object(query_builder, "get") as mock_get:
            mock_get.return_value = mock_records

            result = query_builder.pluck("email")

            expected = ["john@example.com", "jane@example.com"]
            assert result == expected


class TestAdvancedQueryFeatures:
    """Test advanced query building features."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_when_conditional_query(self, query_builder):
        """Test conditional query building with when()."""
        include_inactive = True

        query_builder.where("age", "gte", 18).when(
            include_inactive, lambda q: q.or_where("status", "eq", "inactive")
        )

        # Should include the conditional clause
        assert len(query_builder._where_conditions) == 2

    def test_when_conditional_query_false(self, query_builder):
        """Test conditional query building when condition is false."""
        include_inactive = False

        query_builder.where("age", "gte", 18).when(
            include_inactive, lambda q: q.or_where("status", "eq", "inactive")
        )

        # Should not include the conditional clause
        assert len(query_builder._where_conditions) == 1

    def test_unless_conditional_query(self, query_builder):
        """Test unless() conditional query building."""
        exclude_admin = True

        query_builder.where("status", "eq", "active").unless(
            exclude_admin, lambda q: q.where("role", "neq", "admin")
        )

        # Should not include the clause because condition is true
        assert len(query_builder._where_conditions) == 1

    def test_tap_method(self, query_builder):
        """Test tap() method for side effects."""

        def add_default_conditions(q):
            q.where("deleted_at", "is_null").where("status", "eq", "active")

        result = query_builder.tap(add_default_conditions)

        assert result is query_builder  # Returns same instance
        assert len(query_builder._where_conditions) == 2

    def test_where_has_relation(self, query_builder):
        """Test filtering by related table existence."""
        query_builder.where_has("posts", lambda q: q.where("published", "eq", True))

        # Should add a complex condition for relationship
        assert len(query_builder._where_conditions) == 1
        condition = query_builder._where_conditions[0]
        assert condition["type"] == "has_relation"

    def test_with_relations(self, query_builder):
        """Test eager loading related data."""
        result = query_builder.with_relations(["posts", "profile", "roles"])

        assert result is query_builder
        assert hasattr(query_builder, "_with_relations")
        assert "posts" in query_builder._with_relations

    def test_group_by_functionality(self, query_builder):
        """Test GROUP BY functionality."""
        result = query_builder.group_by("department", "role")

        assert result is query_builder
        assert hasattr(query_builder, "_group_by_fields")
        assert query_builder._group_by_fields == ["department", "role"]

    def test_having_conditions(self, query_builder):
        """Test HAVING conditions for grouped queries."""
        query_builder.group_by("department").having("COUNT(*)", "gt", 5)

        assert hasattr(query_builder, "_having_conditions")
        having_condition = query_builder._having_conditions[0]
        assert having_condition["field"] == "COUNT(*)"
        assert having_condition["operator"] == "gt"
        assert having_condition["value"] == 5


class TestQueryBuilderParameterBuilding:
    """Test building parameters for API requests."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_build_where_parameters(self, query_builder):
        """Test building WHERE parameters for API."""
        query_builder.where("name", "eq", "John").where("age", "gt", 18)

        params = query_builder._build_where_params()

        assert "where" in params
        # Should encode conditions properly for NocoDB API

    def test_build_sort_parameters(self, query_builder):
        """Test building sort parameters for API."""
        query_builder.order_by("name", "asc").order_by("created_at", "desc")

        params = query_builder._build_sort_params()

        assert "sort" in params
        # Should format as comma-separated string

    def test_build_field_parameters(self, query_builder):
        """Test building field selection parameters."""
        query_builder.select("id", "name", "email")

        params = query_builder._build_field_params()

        assert "fields" in params
        assert "id,name,email" in params["fields"]

    def test_build_pagination_parameters(self, query_builder):
        """Test building pagination parameters."""
        query_builder.limit(25).offset(50)

        params = query_builder._build_pagination_params()

        assert params["limit"] == 25
        assert params["offset"] == 50

    def test_build_complete_parameters(self, query_builder):
        """Test building complete parameter set."""
        query_builder.select("id", "name", "email").where("status", "eq", "active").order_by(
            "name", "asc"
        ).limit(10).offset(20)

        params = query_builder.build_params()

        assert "fields" in params
        assert "where" in params
        assert "sort" in params
        assert "limit" in params
        assert "offset" in params


class TestQueryBuilderErrorHandling:
    """Test error handling in QueryBuilder."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_invalid_operator_error(self, query_builder):
        """Test error handling for invalid operators."""
        with pytest.raises(QueryBuilderError, match="Invalid operator"):
            query_builder.where("name", "invalid_op", "John")

    def test_invalid_sort_direction_error(self, query_builder):
        """Test error handling for invalid sort directions."""
        with pytest.raises(QueryBuilderError, match="Invalid sort direction"):
            query_builder.order_by("name", "invalid_direction")

    def test_negative_limit_error(self, query_builder):
        """Test error handling for negative limit values."""
        with pytest.raises(QueryBuilderError, match="Limit must be positive"):
            query_builder.limit(-10)

    def test_negative_offset_error(self, query_builder):
        """Test error handling for negative offset values."""
        with pytest.raises(QueryBuilderError, match="Offset must be non-negative"):
            query_builder.offset(-5)

    def test_empty_field_selection_error(self, query_builder):
        """Test error handling for empty field selection."""
        with pytest.raises(QueryBuilderError, match="At least one field must be selected"):
            query_builder.select()  # Empty select

    def test_api_error_handling(self, query_builder):
        """Test handling API errors during execution."""
        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.side_effect = NocoDBError("API Error", status_code=500)

            with pytest.raises(QueryBuilderError, match="Query execution failed"):
                query_builder.get()

    def test_network_error_handling(self, query_builder):
        """Test handling network errors during execution."""
        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.side_effect = ConnectionError("Network error")

            with pytest.raises(QueryBuilderError, match="Network error"):
                query_builder.get()


class TestQueryBuilderFluentInterface:
    """Test the fluent interface and method chaining."""

    @pytest.fixture
    def query_builder(self):
        """Create a QueryBuilder instance for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_method_chaining(self, query_builder):
        """Test that all methods support chaining."""
        result = (
            query_builder.select("id", "name")
            .where("age", "gte", 18)
            .where("status", "eq", "active")
            .order_by("name", "asc")
            .limit(10)
            .offset(5)
        )

        assert result is query_builder
        assert len(query_builder._select_fields) == 2
        assert len(query_builder._where_conditions) == 2
        assert len(query_builder._sort_conditions) == 1
        assert query_builder._limit_value == 10
        assert query_builder._offset_value == 5

    def test_complex_query_building(self, query_builder):
        """Test building complex queries with multiple conditions."""
        mock_records = [{"id": 1, "name": "John"}]

        with patch.object(query_builder.client, "get_records") as mock_get:
            mock_get.return_value = mock_records

            result = (
                query_builder.select("id", "name", "email", "created_at")
                .where("age", "between", [18, 65])
                .where_in("department", ["engineering", "design"])
                .where_not_null("email")
                .order_by("created_at", "desc")
                .order_by("name", "asc")
                .limit(50)
                .get()
            )

            assert result == mock_records
            # Verify all conditions were applied
            assert len(query_builder._where_conditions) == 3
            assert len(query_builder._sort_conditions) == 2

    def test_query_builder_reusability(self, query_builder):
        """Test that QueryBuilder instances can be reused."""
        # Build base query
        base_query = query_builder.where("status", "eq", "active").order_by("created_at", "desc")

        # Create variations
        recent_users = base_query.clone().limit(10)
        older_users = base_query.clone().where("age", "gte", 30)

        # Should be different instances with different conditions
        assert recent_users is not older_users
        assert recent_users._limit_value == 10
        assert older_users._limit_value is None
        assert len(older_users._where_conditions) > len(base_query._where_conditions)
