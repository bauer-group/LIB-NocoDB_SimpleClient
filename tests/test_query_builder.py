"""Tests for QueryBuilder class based on actual implementation."""

from unittest.mock import Mock
import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.query_builder import QueryBuilder
from nocodb_simple_client.table import NocoDBTable


class TestQueryBuilderInitialization:
    """Test QueryBuilder initialization."""

    def test_query_builder_init_with_client_and_table_name(self):
        """Test QueryBuilder initialization with client and table name (legacy API)."""
        client = Mock(spec=NocoDBClient)
        qb = QueryBuilder(client, "users")

        assert qb.client == client
        assert qb.table_name == "users"
        assert qb._table is None

    def test_query_builder_init_with_table(self):
        """Test QueryBuilder initialization with table (new API)."""
        client = Mock(spec=NocoDBClient)
        table = Mock(spec=NocoDBTable)
        table.client = client
        table.table_id = "users"

        qb = QueryBuilder(table)

        assert qb.client == client
        assert qb.table_name == "users"
        assert qb._table == table

    def test_query_builder_init_state(self):
        """Test QueryBuilder initial state."""
        client = Mock(spec=NocoDBClient)
        qb = QueryBuilder(client, "users")

        assert qb._select_fields == []
        assert qb._limit_count is None
        assert qb._offset_count == 0
        assert qb._filter_builder is not None
        assert qb._sort_builder is not None


class TestQueryBuilderSelect:
    """Test SELECT functionality."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_select_single_field(self, qb):
        """Test selecting a single field."""
        result = qb.select("name")

        assert result is qb  # Method chaining
        assert qb._select_fields == ["name"]

    def test_select_multiple_fields(self, qb):
        """Test selecting multiple fields."""
        result = qb.select("id", "name", "email", "status")

        assert result is qb
        assert qb._select_fields == ["id", "name", "email", "status"]

    def test_select_empty_fields(self, qb):
        """Test selecting with no fields (select all)."""
        result = qb.select()

        assert result is qb
        assert qb._select_fields == []

    def test_select_overwrites_previous(self, qb):
        """Test that select overwrites previous selections."""
        qb.select("id", "name")
        qb.select("email", "status")

        assert qb._select_fields == ["email", "status"]


class TestQueryBuilderWhere:
    """Test WHERE conditions."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_where_condition(self, qb):
        """Test basic WHERE condition."""
        result = qb.where("status", "eq", "active")

        assert result is qb  # Method chaining
        # Verify it was added to filter builder
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_or_condition(self, qb):
        """Test WHERE OR condition."""
        result = qb.where("status", "eq", "active").where_or("status", "eq", "pending")

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_and_condition(self, qb):
        """Test WHERE AND condition."""
        result = qb.where("status", "eq", "active").where_and("role", "eq", "admin")

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None


    def test_where_null_condition(self, qb):
        """Test WHERE NULL condition."""
        result = qb.where_null("deleted_at")

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_not_null_condition(self, qb):
        """Test WHERE NOT NULL condition."""
        result = qb.where_not_null("email")

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_in_condition(self, qb):
        """Test WHERE IN condition."""
        result = qb.where_in("status", ["active", "pending", "inactive"])

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_not_in_condition(self, qb):
        """Test WHERE NOT IN condition."""
        result = qb.where_not_in("status", ["deleted", "archived"])

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_like_condition(self, qb):
        """Test WHERE LIKE condition."""
        result = qb.where_like("name", "john%")

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None

    def test_where_between_condition(self, qb):
        """Test WHERE BETWEEN condition."""
        result = qb.where_between("age", 18, 65)

        assert result is qb
        params = qb.to_params()
        assert params["where"] is not None


class TestQueryBuilderOrderBy:
    """Test ORDER BY functionality."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_order_by_asc(self, qb):
        """Test ORDER BY ascending."""
        result = qb.order_by("name", "asc")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None

    def test_order_by_desc(self, qb):
        """Test ORDER BY descending."""
        result = qb.order_by("created_at", "desc")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None

    def test_order_by_default_direction(self, qb):
        """Test ORDER BY with default direction (ASC)."""
        result = qb.order_by("name")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None

    def test_order_by_asc_helper(self, qb):
        """Test order_by_asc helper method."""
        result = qb.order_by_asc("name")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None

    def test_order_by_desc_helper(self, qb):
        """Test order_by_desc helper method."""
        result = qb.order_by_desc("created_at")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None

    def test_multiple_order_by(self, qb):
        """Test multiple ORDER BY conditions."""
        result = qb.order_by("department", "asc").order_by("salary", "desc")

        assert result is qb
        params = qb.to_params()
        assert params["sort"] is not None


class TestQueryBuilderPagination:
    """Test pagination functionality."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_limit(self, qb):
        """Test LIMIT clause."""
        result = qb.limit(25)

        assert result is qb
        assert qb._limit_count == 25

    def test_offset(self, qb):
        """Test OFFSET clause."""
        result = qb.offset(100)

        assert result is qb
        assert qb._offset_count == 100

    def test_limit_and_offset(self, qb):
        """Test LIMIT and OFFSET together."""
        result = qb.limit(20).offset(40)

        assert result is qb
        assert qb._limit_count == 20
        assert qb._offset_count == 40

    def test_page_method(self, qb):
        """Test page() method for pagination."""
        result = qb.page(3, 15)  # Page 3 with 15 items per page

        assert result is qb
        assert qb._limit_count == 15
        assert qb._offset_count == 30  # (3-1) * 15

    def test_page_method_validation(self, qb):
        """Test page() method input validation."""
        with pytest.raises(ValueError, match="Page number must be greater than 0"):
            qb.page(0, 25)

        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            qb.page(1, 0)


class TestQueryBuilderUtilities:
    """Test utility methods."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_to_params_basic(self, qb):
        """Test to_params() method with basic query."""
        qb.select("id", "name").limit(10).offset(5)

        params = qb.to_params()

        assert params["fields"] == ["id", "name"]
        assert params["limit"] == 10
        assert params["offset"] == 5

    def test_to_params_with_where(self, qb):
        """Test to_params() method with WHERE conditions."""
        qb.select("id", "name").where("status", "eq", "active")

        params = qb.to_params()

        assert params["fields"] == ["id", "name"]
        assert params["where"] is not None

    def test_to_params_empty_query(self, qb):
        """Test to_params() method with empty query."""
        params = qb.to_params()

        assert params["fields"] == []
        assert params["limit"] is None
        assert params["offset"] == 0

    def test_clone(self, qb):
        """Test cloning QueryBuilder."""
        qb.select("id", "name").where("status", "eq", "active").limit(10)

        cloned = qb.clone()

        assert cloned is not qb
        assert cloned._select_fields == qb._select_fields
        assert cloned._limit_count == qb._limit_count
        assert cloned._offset_count == qb._offset_count

    def test_reset(self, qb):
        """Test resetting QueryBuilder state."""
        qb.select("id", "name").where("status", "eq", "active").limit(10).offset(5)

        qb.reset()

        assert qb._select_fields == []
        assert qb._limit_count is None
        assert qb._offset_count == 0

    def test_str_representation(self, qb):
        """Test string representation."""
        qb.select("id", "name").limit(10)

        str_repr = str(qb)

        assert "SELECT" in str_repr
        assert "id, name" in str_repr
        assert "FROM users" in str_repr
        assert "LIMIT 10" in str_repr


class TestQueryBuilderExecution:
    """Test query execution."""

    @pytest.fixture
    def qb(self):
        """Create QueryBuilder for testing."""
        client = Mock(spec=NocoDBClient)
        return QueryBuilder(client, "users")

    def test_execute(self, qb):
        """Test query execution."""
        expected_records = [{"id": "1", "name": "John"}, {"id": "2", "name": "Jane"}]
        qb.client.get_records.return_value = expected_records

        result = qb.execute()

        assert result == expected_records
        qb.client.get_records.assert_called_once()

    def test_count(self, qb):
        """Test count execution."""
        qb.client.count_records.return_value = 42

        result = qb.count()

        assert result == 42
        qb.client.count_records.assert_called_once()

    def test_first(self, qb):
        """Test first record retrieval."""
        expected_records = [{"id": "1", "name": "John"}]
        qb.client.get_records.return_value = expected_records

        result = qb.first()

        assert result == expected_records[0]
        # Limit is restored to original value after first() completes
        assert qb._limit_count is None

    def test_first_empty_result(self, qb):
        """Test first record retrieval with empty result."""
        qb.client.get_records.return_value = []

        result = qb.first()

        assert result is None

    def test_exists(self, qb):
        """Test exists check."""
        qb.client.count_records.return_value = 5

        result = qb.exists()

        assert result is True

    def test_exists_false(self, qb):
        """Test exists check with no records."""
        qb.client.count_records.return_value = 0

        result = qb.exists()

        assert result is False
