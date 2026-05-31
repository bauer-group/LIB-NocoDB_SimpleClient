"""Regression tests for NocoDB query-parameter serialization.

All behavior here was verified against a live NocoDB instance
(releaseVersion 2026.05.2):

* ``sort`` for v3 must be a JSON-encoded array of ``{field, direction}``; the
  plain v2 string ("Name,-Age") is rejected with HTTP 422, and a raw Python
  list would be mangled by ``requests`` into repeated ?sort=field&sort=direction
  query pairs. v2 keeps the plain string.
* the not-equal operator ``ne`` is rejected on BOTH v2 and v3 by current
  NocoDB and must be sent as ``neq``; the client normalizes it transparently
  for both versions so the documented ``ne`` filter keeps working.
"""

import json
from unittest.mock import Mock

import pytest

from nocodb_simple_client.api_version import QueryParamAdapter
from nocodb_simple_client.client import NocoDBClient


class TestNormalizeWhereOperators:
    """Unit tests for the ne -> neq where-operator normalization."""

    def test_ne_becomes_neq(self):
        assert QueryParamAdapter.normalize_where_operators("(Status,ne,Active)") == (
            "(Status,neq,Active)"
        )

    def test_neq_is_left_unchanged(self):
        assert QueryParamAdapter.normalize_where_operators("(Status,neq,Active)") == (
            "(Status,neq,Active)"
        )

    def test_other_operators_unchanged(self):
        assert QueryParamAdapter.normalize_where_operators("(Age,gt,21)") == "(Age,gt,21)"

    def test_value_named_ne_is_preserved(self):
        """A value that happens to be 'ne' must not be rewritten."""
        assert QueryParamAdapter.normalize_where_operators("(Name,eq,ne)") == "(Name,eq,ne)"

    def test_multiple_clauses(self):
        result = QueryParamAdapter.normalize_where_operators("(Status,ne,Active)~and(Age,ne,5)")
        assert result == "(Status,neq,Active)~and(Age,neq,5)"

    def test_none_and_empty_passthrough(self):
        assert QueryParamAdapter.normalize_where_operators(None) is None
        assert QueryParamAdapter.normalize_where_operators("") == ""


@pytest.fixture
def v3_mock_session():
    """A mock requests.Session returning a valid empty v3 records response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"records": [], "next": None, "prev": None}
    session = Mock()
    session.get.return_value = response
    return session


@pytest.fixture
def v3_client(v3_mock_session, monkeypatch):
    """A v3 client with a fixed base_id (no resolver API calls) and mocked session."""
    monkeypatch.setattr("requests.Session", lambda *a, **k: v3_mock_session)
    return NocoDBClient(
        base_url="https://test.nocodb.com",
        db_auth_token="test-token",
        api_version="v3",
        base_id="base1",
    )


class TestV3GetRecordsWire:
    """Verify the actual query params the client puts on the wire for v3."""

    def test_sort_is_json_encoded_array(self, v3_client, v3_mock_session):
        v3_client.get_records("tbl1", sort="Name,-Age", limit=10)
        params = v3_mock_session.get.call_args.kwargs["params"]
        # Must be a JSON string, not a Python list (requests would mangle a
        # list), and not the plain v2 string (the live server rejects it 422).
        assert isinstance(params["sort"], str)
        assert json.loads(params["sort"]) == [
            {"field": "Name", "direction": "asc"},
            {"field": "Age", "direction": "desc"},
        ]

    def test_where_ne_normalized_to_neq(self, v3_client, v3_mock_session):
        v3_client.get_records("tbl1", where="(Status,ne,Active)", limit=10)
        params = v3_mock_session.get.call_args.kwargs["params"]
        assert params["where"] == "(Status,neq,Active)"

    def test_pagination_uses_page_pagesize(self, v3_client, v3_mock_session):
        v3_client.get_records("tbl1", limit=10)
        params = v3_mock_session.get.call_args.kwargs["params"]
        assert "pageSize" in params
        assert "offset" not in params and "limit" not in params


class TestV3CountWire:
    """count_records normalizes the where operator for v3."""

    def test_count_where_ne_normalized(self, v3_mock_session, monkeypatch):
        v3_mock_session.get.return_value.json.return_value = {"count": 0}
        monkeypatch.setattr("requests.Session", lambda *a, **k: v3_mock_session)
        client = NocoDBClient(
            base_url="https://test.nocodb.com",
            db_auth_token="test-token",
            api_version="v3",
            base_id="base1",
        )
        client.count_records("tbl1", where="(Status,ne,Active)")
        params = v3_mock_session.get.call_args.kwargs["params"]
        assert params["where"] == "(Status,neq,Active)"


class TestV2QueryParams:
    """v2 keeps the plain sort string, but the ne->neq normalization applies to
    v2 as well (current NocoDB rejects 'ne' on v2 too)."""

    @pytest.fixture
    def v2_session(self, monkeypatch):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"list": [], "pageInfo": {"isLastPage": True}}
        session = Mock()
        session.get.return_value = response
        monkeypatch.setattr("requests.Session", lambda *a, **k: session)
        return session

    def test_v2_sort_is_plain_string(self, v2_session):
        client = NocoDBClient(base_url="https://test.nocodb.com", db_auth_token="test-token")
        client.get_records("tbl1", sort="Name,-Age", limit=10)
        params = v2_session.get.call_args.kwargs["params"]
        assert params["sort"] == "Name,-Age"

    def test_v2_where_ne_normalized_to_neq(self, v2_session):
        client = NocoDBClient(base_url="https://test.nocodb.com", db_auth_token="test-token")
        client.get_records("tbl1", where="(Status,ne,Active)", limit=10)
        params = v2_session.get.call_args.kwargs["params"]
        assert params["where"] == "(Status,neq,Active)"
