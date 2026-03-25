"""Integration tests for API version switching between v2 and v3.

MIT License

Copyright (c) BAUER GROUP
"""

from unittest.mock import patch

import pytest

from nocodb_simple_client import NocoDBClient, NocoDBMetaClient
from nocodb_simple_client.api_version import APIVersion


class TestClientVersionSwitching:
    """Test version switching for NocoDBClient."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session."""
        with patch("nocodb_simple_client.client.requests.Session") as mock:
            yield mock.return_value

    def test_client_default_v2(self, mock_session):
        """Test client defaults to v2."""
        client = NocoDBClient(base_url="https://test.com", db_auth_token="token")

        assert client.api_version == APIVersion.V2
        assert client.base_id is None
        assert client._path_builder is not None
        assert client._param_adapter is not None
        assert client._base_resolver is None  # Only created for v3

    def test_client_explicit_v2(self, mock_session):
        """Test client with explicit v2."""
        client = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        assert client.api_version == APIVersion.V2

    def test_client_explicit_v3(self, mock_session):
        """Test client with explicit v3."""
        client = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_123",
        )

        assert client.api_version == APIVersion.V3
        assert client.base_id == "base_123"
        assert client._base_resolver is not None  # Created for v3

    def test_client_v3_without_base_id(self, mock_session):
        """Test v3 client can be created without base_id."""
        client = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v3"
        )

        assert client.api_version == APIVersion.V3
        assert client.base_id is None
        assert client._base_resolver is not None

    def test_get_records_v2_endpoint(self, mock_session):
        """Test get_records uses v2 endpoint."""
        client = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", limit=10)

        # Check that v2 endpoint was called
        call_args = mock_session.get.call_args
        assert "api/v2/tables/table_123/records" in call_args[0][0]

    def test_get_records_v3_endpoint(self, mock_session):
        """Test get_records uses v3 endpoint and parses v3 response format."""
        client = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        # v3 uses "records" key with nested "fields" and lowercase "id"
        mock_session.get.return_value.json.return_value = {
            "records": [
                {"id": 1, "fields": {"Name": "Record 1"}},
                {"id": 2, "fields": {"Name": "Record 2"}},
            ],
            "next": None,
        }
        mock_session.get.return_value.status_code = 200

        result = client.get_records("table_123", limit=10)

        # Check that v3 endpoint was called
        call_args = mock_session.get.call_args
        assert "api/v3/data/base_abc/table_123/records" in call_args[0][0]

        # Check that v3 response was normalized to v2-compatible format
        assert len(result) == 2
        assert result[0]["Id"] == 1
        assert result[0]["Name"] == "Record 1"

    def test_v2_pagination_params(self, mock_session):
        """Test v2 uses offset/limit parameters."""
        client = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", limit=25)

        # Check parameters
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]

        assert "limit" in params
        assert params["limit"] == 25
        assert "page" not in params
        assert "pageSize" not in params

    def test_v3_pagination_params(self, mock_session):
        """Test v3 converts to page/pageSize parameters."""
        client = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"records": [], "next": None}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", limit=25)

        # Check parameters
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]

        assert "page" in params
        assert "pageSize" in params
        assert params["page"] == 1
        assert params["pageSize"] == 25
        assert "offset" not in params
        assert "limit" not in params

    def test_v2_sort_string_format(self, mock_session):
        """Test v2 uses string sort format."""
        client = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", sort="name,-age")

        # Check parameters
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]

        assert params["sort"] == "name,-age"

    def test_v3_sort_json_format(self, mock_session):
        """Test v3 converts sort to JSON format."""
        client = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"records": [], "next": None}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", sort="name,-age")

        # Check parameters
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]

        assert isinstance(params["sort"], list)
        assert len(params["sort"]) == 2
        assert params["sort"][0] == {"field": "name", "direction": "asc"}
        assert params["sort"][1] == {"field": "age", "direction": "desc"}


class TestMetaClientVersionSwitching:
    """Test version switching for NocoDBMetaClient."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session."""
        with patch("nocodb_simple_client.client.requests.Session") as mock:
            yield mock.return_value

    def test_meta_client_default_v2(self, mock_session):
        """Test meta client defaults to v2."""
        client = NocoDBMetaClient(base_url="https://test.com", db_auth_token="token")

        assert client.api_version == APIVersion.V2

    def test_meta_client_explicit_v3(self, mock_session):
        """Test meta client with explicit v3."""
        client = NocoDBMetaClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_123",
        )

        assert client.api_version == APIVersion.V3
        assert client.base_id == "base_123"

    def test_list_tables_v2_endpoint(self, mock_session):
        """Test list_tables uses v2 endpoint."""
        client = NocoDBMetaClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"list": []}
        mock_session.get.return_value.status_code = 200

        client.list_tables("base_123")

        # Check that v2 endpoint was called
        call_args = mock_session.get.call_args
        assert "api/v2/meta/bases/base_123/tables" in call_args[0][0]

    def test_list_tables_v3_endpoint(self, mock_session):
        """Test list_tables uses v3 endpoint."""
        client = NocoDBMetaClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"list": []}
        mock_session.get.return_value.status_code = 200

        client.list_tables("base_abc")

        # Check that v3 endpoint was called
        call_args = mock_session.get.call_args
        assert "api/v3/meta/bases/base_abc/tables" in call_args[0][0]

    def test_get_table_info_v2_no_base_id(self, mock_session):
        """Test get_table_info in v2 doesn't require base_id."""
        client = NocoDBMetaClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"id": "table_123"}
        mock_session.get.return_value.status_code = 200

        client.get_table_info("table_123")

        # Check endpoint
        call_args = mock_session.get.call_args
        assert "api/v2/meta/tables/table_123" in call_args[0][0]

    def test_get_table_info_v3_with_base_id(self, mock_session):
        """Test get_table_info in v3 uses base_id."""
        client = NocoDBMetaClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"id": "table_123"}
        mock_session.get.return_value.status_code = 200

        client.get_table_info("table_123")

        # Check endpoint includes base_id
        call_args = mock_session.get.call_args
        assert "api/v3/meta/bases/base_abc/tables/table_123" in call_args[0][0]

    def test_columns_v2_terminology(self, mock_session):
        """Test v2 uses 'columns' terminology."""
        client = NocoDBMetaClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        mock_session.get.return_value.json.return_value = {"list": []}
        mock_session.get.return_value.status_code = 200

        client.list_columns("table_123")

        # Check endpoint uses "columns"
        call_args = mock_session.get.call_args
        assert "columns" in call_args[0][0]
        assert "fields" not in call_args[0][0]

    def test_columns_v3_becomes_fields(self, mock_session):
        """Test v3 uses 'fields' terminology."""
        client = NocoDBMetaClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"list": []}
        mock_session.get.return_value.status_code = 200

        # API is still list_columns, but endpoint uses "fields"
        client.list_columns("table_123")

        # Check endpoint uses "fields"
        call_args = mock_session.get.call_args
        assert "fields" in call_args[0][0]
        assert "columns" not in call_args[0][0]


class TestCrossFunctionalityBetweenVersions:
    """Test that clients work correctly across different features."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session."""
        with patch("nocodb_simple_client.client.requests.Session") as mock:
            yield mock.return_value

    def test_file_upload_v2_v3_paths(self, mock_session):
        """Test file upload uses correct paths for v2 and v3."""
        # v2 client
        client_v2 = NocoDBClient(
            base_url="https://test.com", db_auth_token="token", api_version="v2"
        )

        # v3 client
        client_v3 = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        # Check path construction
        v2_path = client_v2._path_builder.file_upload("table_123")
        v3_path = client_v3._path_builder.file_upload("table_123", "base_abc")

        assert v2_path == "api/v2/storage/upload"
        assert v3_path == "api/v3/data/base_abc/table_123/attachments"

    def test_both_data_and_meta_operations(self, mock_session):
        """Test client can perform both data and meta operations."""
        # Create v3 meta client
        meta_client = NocoDBMetaClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"list": []}
        mock_session.get.return_value.status_code = 200

        # Meta operation
        meta_client.list_tables("base_abc")
        meta_call = mock_session.get.call_args[0][0]
        assert "api/v3/meta/bases/base_abc/tables" in meta_call

        # Data operation (inherited from NocoDBClient)
        mock_session.get.return_value.json.return_value = {"records": [], "next": None}
        meta_client.get_records("table_123")
        data_call = mock_session.get.call_args[0][0]
        assert "api/v3/data/base_abc/table_123/records" in data_call


class TestV3ResponseFormatHandling:
    """Test that v3 API response formats are correctly parsed."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session."""
        with patch("nocodb_simple_client.client.requests.Session") as mock:
            yield mock.return_value

    @pytest.fixture
    def v3_client(self, mock_session):
        """Create v3 client for testing."""
        return NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

    def test_get_record_v3_normalizes_fields(self, v3_client, mock_session):
        """Test get_record normalizes v3 {id, fields} to flat format."""
        mock_session.get.return_value.json.return_value = {
            "id": 42,
            "fields": {"Name": "Test", "Email": "test@example.com"},
        }
        mock_session.get.return_value.status_code = 200

        result = v3_client.get_record("table_123", 42)

        assert result["Id"] == 42
        assert result["Name"] == "Test"
        assert result["Email"] == "test@example.com"

    def test_insert_record_v3_formats_request_and_response(self, v3_client, mock_session):
        """Test insert_record wraps data in fields and parses v3 response."""
        mock_session.post.return_value.json.return_value = {
            "records": [{"id": 99, "fields": {"Name": "New"}}]
        }
        mock_session.post.return_value.status_code = 200

        result = v3_client.insert_record("table_123", {"Name": "New"})

        assert result == 99

        # Verify request was formatted for v3
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert "fields" in request_data
        assert request_data["fields"]["Name"] == "New"

    def test_update_record_v3_formats_request_and_response(self, v3_client, mock_session):
        """Test update_record wraps data in fields and parses v3 response."""
        mock_session.patch.return_value.json.return_value = {
            "records": [{"id": 42, "fields": {"Name": "Updated"}}]
        }
        mock_session.patch.return_value.status_code = 200

        result = v3_client.update_record("table_123", {"Name": "Updated"}, record_id=42)

        assert result == 42

        # Verify request was formatted for v3
        call_args = mock_session.patch.call_args
        request_data = call_args[1]["json"]
        assert "fields" in request_data
        assert request_data["id"] == 42

    def test_delete_record_v3_formats_request_and_response(self, v3_client, mock_session):
        """Test delete_record uses lowercase 'id' for v3."""
        mock_session.delete.return_value.json.return_value = {
            "records": [{"id": 42, "deleted": True}]
        }
        mock_session.delete.return_value.status_code = 200

        result = v3_client.delete_record("table_123", 42)

        assert result == 42

        # Verify request was formatted for v3
        call_args = mock_session.delete.call_args
        request_data = call_args[1]["json"]
        assert "id" in request_data
        assert request_data["id"] == 42

    def test_get_records_v3_pagination_with_next(self, v3_client, mock_session):
        """Test get_records handles v3 cursor-based pagination."""
        # First call returns records with next token
        mock_session.get.return_value.json.return_value = {
            "records": [
                {"id": 1, "fields": {"Name": "A"}},
                {"id": 2, "fields": {"Name": "B"}},
            ],
            "next": "https://test.com/api/v3/data/base_abc/table_123/records?page=2",
        }
        mock_session.get.return_value.status_code = 200

        result = v3_client.get_records("table_123", limit=2)

        assert len(result) == 2
        assert result[0]["Id"] == 1
        assert result[1]["Name"] == "B"

    def test_bulk_insert_v3_formats_records(self, v3_client, mock_session):
        """Test bulk_insert formats records for v3 with records wrapper."""
        mock_session.post.return_value.json.return_value = {
            "records": [
                {"id": 10, "fields": {"Name": "A"}},
                {"id": 11, "fields": {"Name": "B"}},
            ]
        }
        mock_session.post.return_value.status_code = 200

        result = v3_client.bulk_insert_records(
            "table_123", [{"Name": "A"}, {"Name": "B"}]
        )

        assert result == [10, 11]

    def test_bulk_delete_v3_formats_ids(self, v3_client, mock_session):
        """Test bulk_delete formats IDs for v3."""
        mock_session.delete.return_value.json.return_value = {
            "records": [{"id": 1, "deleted": True}, {"id": 2, "deleted": True}]
        }
        mock_session.delete.return_value.status_code = 200

        result = v3_client.bulk_delete_records("table_123", [1, 2])

        assert result == [1, 2]
