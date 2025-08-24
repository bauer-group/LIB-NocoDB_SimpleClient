"""Pytest configuration and fixtures."""

from unittest.mock import Mock

import pytest

from nocodb_simple_client import NocoDBClient, NocoDBTable


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"list": [], "pageInfo": {"isLastPage": True}}
    return response


@pytest.fixture
def mock_session(mock_response):
    """Create a mock requests session."""
    session = Mock()
    session.get.return_value = mock_response
    session.post.return_value = mock_response
    session.patch.return_value = mock_response
    session.put.return_value = mock_response
    session.delete.return_value = mock_response
    return session


@pytest.fixture
def client(mock_session, monkeypatch):
    """Create a NocoDBClient instance with mocked session."""

    def mock_session_init(*args, **kwargs):
        return mock_session

    monkeypatch.setattr("requests.Session", mock_session_init)

    return NocoDBClient(base_url="https://test.nocodb.com", db_auth_token="test-token")


@pytest.fixture
def table(client):
    """Create a NocoDBTable instance."""
    return NocoDBTable(client, table_id="test-table-id")


@pytest.fixture
def sample_record():
    """Sample record data for testing."""
    return {"Id": 1, "Name": "Test Record", "Email": "test@example.com", "Age": 25, "Active": True}


@pytest.fixture
def sample_records(sample_record):
    """Sample list of records for testing."""
    return [
        sample_record,
        {
            "Id": 2,
            "Name": "Test Record 2",
            "Email": "test2@example.com",
            "Age": 30,
            "Active": False,
        },
    ]
