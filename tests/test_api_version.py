"""Tests for API version support (PathBuilder, QueryParamAdapter).

MIT License

Copyright (c) BAUER GROUP
"""

import pytest

from nocodb_simple_client.api_version import APIVersion, PathBuilder, QueryParamAdapter


class TestAPIVersion:
    """Test APIVersion enum."""

    def test_api_version_v2(self):
        """Test v2 API version."""
        assert APIVersion.V2 == "v2"
        assert str(APIVersion.V2) == "v2"

    def test_api_version_v3(self):
        """Test v3 API version."""
        assert APIVersion.V3 == "v3"
        assert str(APIVersion.V3) == "v3"

    def test_api_version_creation(self):
        """Test creating APIVersion from string."""
        assert APIVersion("v2") == APIVersion.V2
        assert APIVersion("v3") == APIVersion.V3


class TestQueryParamAdapter:
    """Test QueryParamAdapter for parameter conversion."""

    def test_convert_pagination_to_v3_basic(self):
        """Test basic offset/limit to page/pageSize conversion."""
        params = {"offset": 50, "limit": 25}
        result = QueryParamAdapter.convert_pagination_to_v3(params)

        assert result["page"] == 3
        assert result["pageSize"] == 25
        assert "offset" not in result
        assert "limit" not in result

    def test_convert_pagination_to_v3_first_page(self):
        """Test conversion for first page."""
        params = {"offset": 0, "limit": 10}
        result = QueryParamAdapter.convert_pagination_to_v3(params)

        assert result["page"] == 1
        assert result["pageSize"] == 10

    def test_convert_pagination_to_v3_no_params(self):
        """Test conversion with no pagination params."""
        params = {"where": "(Status,eq,Active)"}
        result = QueryParamAdapter.convert_pagination_to_v3(params)

        assert "page" not in result
        assert "pageSize" not in result
        assert result["where"] == "(Status,eq,Active)"

    def test_convert_pagination_to_v3_only_limit(self):
        """Test conversion with only limit."""
        params = {"limit": 20}
        result = QueryParamAdapter.convert_pagination_to_v3(params)

        assert result["page"] == 1
        assert result["pageSize"] == 20

    def test_convert_pagination_to_v2_basic(self):
        """Test basic page/pageSize to offset/limit conversion."""
        params = {"page": 3, "pageSize": 25}
        result = QueryParamAdapter.convert_pagination_to_v2(params)

        assert result["offset"] == 50
        assert result["limit"] == 25
        assert "page" not in result
        assert "pageSize" not in result

    def test_convert_pagination_to_v2_first_page(self):
        """Test conversion for first page."""
        params = {"page": 1, "pageSize": 10}
        result = QueryParamAdapter.convert_pagination_to_v2(params)

        assert result["offset"] == 0
        assert result["limit"] == 10

    def test_convert_sort_to_v3_single_field_asc(self):
        """Test sort conversion for single ascending field."""
        result = QueryParamAdapter.convert_sort_to_v3("name")

        assert len(result) == 1
        assert result[0]["field"] == "name"
        assert result[0]["direction"] == "asc"

    def test_convert_sort_to_v3_single_field_desc(self):
        """Test sort conversion for single descending field."""
        result = QueryParamAdapter.convert_sort_to_v3("-age")

        assert len(result) == 1
        assert result[0]["field"] == "age"
        assert result[0]["direction"] == "desc"

    def test_convert_sort_to_v3_multiple_fields(self):
        """Test sort conversion for multiple fields."""
        result = QueryParamAdapter.convert_sort_to_v3("name,-age,email")

        assert len(result) == 3
        assert result[0] == {"field": "name", "direction": "asc"}
        assert result[1] == {"field": "age", "direction": "desc"}
        assert result[2] == {"field": "email", "direction": "asc"}

    def test_convert_sort_to_v3_none(self):
        """Test sort conversion with None."""
        result = QueryParamAdapter.convert_sort_to_v3(None)
        assert result is None

    def test_convert_sort_to_v3_empty_string(self):
        """Test sort conversion with empty string."""
        result = QueryParamAdapter.convert_sort_to_v3("")
        assert result is None

    def test_convert_sort_to_v2_single_field_asc(self):
        """Test reverse sort conversion for ascending field."""
        sort_list = [{"field": "name", "direction": "asc"}]
        result = QueryParamAdapter.convert_sort_to_v2(sort_list)

        assert result == "name"

    def test_convert_sort_to_v2_single_field_desc(self):
        """Test reverse sort conversion for descending field."""
        sort_list = [{"field": "age", "direction": "desc"}]
        result = QueryParamAdapter.convert_sort_to_v2(sort_list)

        assert result == "-age"

    def test_convert_sort_to_v2_multiple_fields(self):
        """Test reverse sort conversion for multiple fields."""
        sort_list = [
            {"field": "name", "direction": "asc"},
            {"field": "age", "direction": "desc"},
            {"field": "email", "direction": "asc"},
        ]
        result = QueryParamAdapter.convert_sort_to_v2(sort_list)

        assert result == "name,-age,email"

    def test_convert_sort_to_v2_none(self):
        """Test reverse sort conversion with None."""
        result = QueryParamAdapter.convert_sort_to_v2(None)
        assert result is None

    def test_convert_where_operators_to_v3(self):
        """Test where clause operator conversion to v3."""
        where = {"field": {"ne": "value"}}
        result = QueryParamAdapter.convert_where_operators_to_v3(where)

        assert "neq" in result["field"]
        assert "ne" not in result["field"]
        assert result["field"]["neq"] == "value"

    def test_convert_where_operators_to_v3_nested(self):
        """Test nested where clause conversion."""
        where = {"and": [{"field1": {"ne": "val1"}}, {"field2": {"ne": "val2"}}]}
        result = QueryParamAdapter.convert_where_operators_to_v3(where)

        assert result["and"][0]["field1"]["neq"] == "val1"
        assert result["and"][1]["field2"]["neq"] == "val2"

    def test_convert_where_operators_to_v3_none(self):
        """Test where conversion with None."""
        result = QueryParamAdapter.convert_where_operators_to_v3(None)
        assert result is None

    def test_convert_where_operators_to_v2(self):
        """Test where clause operator conversion to v2."""
        where = {"field": {"neq": "value"}}
        result = QueryParamAdapter.convert_where_operators_to_v2(where)

        assert "ne" in result["field"]
        assert "neq" not in result["field"]
        assert result["field"]["ne"] == "value"


class TestPathBuilderDataAPI:
    """Test PathBuilder for Data API endpoints."""

    def test_records_list_v2(self):
        """Test records list path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.records_list("table_123")

        assert path == "api/v2/tables/table_123/records"

    def test_records_list_v3(self):
        """Test records list path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.records_list("table_123", "base_abc")

        assert path == "api/v3/data/base_abc/table_123/records"

    def test_records_list_v3_no_base_id(self):
        """Test v3 records list requires base_id."""
        builder = PathBuilder(APIVersion.V3)

        with pytest.raises(ValueError, match="base_id is required"):
            builder.records_list("table_123")

    def test_records_get_v2(self):
        """Test get record path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.records_get("table_123", "rec_456")

        assert path == "api/v2/tables/table_123/records/rec_456"

    def test_records_get_v3(self):
        """Test get record path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.records_get("table_123", "rec_456", "base_abc")

        assert path == "api/v3/data/base_abc/table_123/records/rec_456"

    def test_records_count_v2(self):
        """Test count records path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.records_count("table_123")

        assert path == "api/v2/tables/table_123/records/count"

    def test_records_count_v3(self):
        """Test count records path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.records_count("table_123", "base_abc")

        assert path == "api/v3/data/base_abc/table_123/count"

    def test_links_list_v2(self):
        """Test links list path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.links_list("table_123", "link_field_456", "rec_789")

        assert path == "api/v2/tables/table_123/links/link_field_456/records/rec_789"

    def test_links_list_v3(self):
        """Test links list path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.links_list("table_123", "link_field_456", "rec_789", "base_abc")

        assert path == "api/v3/data/base_abc/table_123/links/link_field_456/rec_789"

    def test_file_upload_v2(self):
        """Test file upload path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.file_upload("table_123")

        assert path == "api/v2/storage/upload"

    def test_file_upload_v3(self):
        """Test file upload path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.file_upload("table_123", "base_abc")

        assert path == "api/v3/data/base_abc/table_123/attachments"


class TestPathBuilderMetaAPI:
    """Test PathBuilder for Meta API endpoints."""

    def test_bases_list_v2(self):
        """Test bases list path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.bases_list()

        assert path == "api/v2/meta/bases"

    def test_bases_list_v3(self):
        """Test bases list path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.bases_list()

        assert path == "api/v3/meta/bases"

    def test_base_get_v2(self):
        """Test get base path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.base_get("base_123")

        assert path == "api/v2/meta/bases/base_123"

    def test_base_get_v3(self):
        """Test get base path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.base_get("base_123")

        assert path == "api/v3/meta/bases/base_123"

    def test_tables_list_meta_v2(self):
        """Test tables list path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.tables_list_meta("base_123")

        assert path == "api/v2/meta/bases/base_123/tables"

    def test_tables_list_meta_v3(self):
        """Test tables list path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.tables_list_meta("base_123")

        assert path == "api/v3/meta/bases/base_123/tables"

    def test_table_get_meta_v2(self):
        """Test get table metadata path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.table_get_meta("table_123")

        assert path == "api/v2/meta/tables/table_123"

    def test_table_get_meta_v3(self):
        """Test get table metadata path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.table_get_meta("table_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/tables/table_123"

    def test_column_get_v2(self):
        """Test get column path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.column_get("col_123")

        assert path == "api/v2/meta/columns/col_123"

    def test_column_get_v3(self):
        """Test get field path for v3 (columns → fields)."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.column_get("field_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/fields/field_123"

    def test_columns_create_v2(self):
        """Test create column path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.columns_create("table_123")

        assert path == "api/v2/meta/tables/table_123/columns"

    def test_columns_create_v3(self):
        """Test create field path for v3 (columns → fields)."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.columns_create("table_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/tables/table_123/fields"

    def test_view_get_v2(self):
        """Test get view path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.view_get("view_123")

        assert path == "api/v2/meta/views/view_123"

    def test_view_get_v3(self):
        """Test get view path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.view_get("view_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/views/view_123"

    def test_views_list_v2(self):
        """Test list views path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.views_list("table_123")

        assert path == "api/v2/meta/tables/table_123/views"

    def test_views_list_v3(self):
        """Test list views path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.views_list("table_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/tables/table_123/views"

    def test_webhook_get_v2(self):
        """Test get webhook path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.webhook_get("hook_123")

        assert path == "api/v2/meta/hooks/hook_123"

    def test_webhook_get_v3(self):
        """Test get webhook path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.webhook_get("hook_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/hooks/hook_123"

    def test_webhooks_list_v2(self):
        """Test list webhooks path for v2."""
        builder = PathBuilder(APIVersion.V2)
        path = builder.webhooks_list("table_123")

        assert path == "api/v2/meta/tables/table_123/hooks"

    def test_webhooks_list_v3(self):
        """Test list webhooks path for v3."""
        builder = PathBuilder(APIVersion.V3)
        path = builder.webhooks_list("table_123", "base_abc")

        assert path == "api/v3/meta/bases/base_abc/tables/table_123/hooks"
