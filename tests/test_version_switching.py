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
        """Test get_records uses v3 endpoint."""
        client = NocoDBClient(
            base_url="https://test.com",
            db_auth_token="token",
            api_version="v3",
            base_id="base_abc",
        )

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
        mock_session.get.return_value.status_code = 200

        client.get_records("table_123", limit=10)

        # Check that v3 endpoint was called
        call_args = mock_session.get.call_args
        assert "api/v3/data/base_abc/table_123/records" in call_args[0][0]

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

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
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

        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
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
        mock_session.get.return_value.json.return_value = {"list": [], "pageInfo": {}}
        meta_client.get_records("table_123")
        data_call = mock_session.get.call_args[0][0]
        assert "api/v3/data/base_abc/table_123/records" in data_call
