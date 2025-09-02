"""
Comprehensive tests for the async client functionality.
"""

import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.async_client import AsyncNocoDBClient
from nocodb_simple_client.config import NocoDBConfig
from nocodb_simple_client.exceptions import (
    AuthenticationException,
    ConnectionTimeoutException,
    NetworkException,
    ServerErrorException,
)


class MockResponse:
    """Mock aiohttp response for testing."""

    def __init__(
        self,
        status=200,
        content_type="application/json",
        json_data=None,
        text_data=None,
        side_effect=None,
    ):
        self.status = status
        self.content_type = content_type
        self._json_data = json_data
        self._text_data = text_data
        self._json_side_effect = side_effect

    async def json(self):
        if self._json_side_effect:
            raise self._json_side_effect
        return self._json_data

    async def text(self):
        return self._text_data


class MockSession:
    """Mock aiohttp session for testing."""

    def __init__(self):
        self.request_call_count = 0
        self.request_calls = []
        self._response = None
        self._exception = None

    def set_response(self, response):
        self._response = response

    def set_exception(self, exception):
        self._exception = exception

    def request(self, method, url, **kwargs):
        """Return a context manager for the request."""
        self.request_call_count += 1
        self.request_calls.append((method, url, kwargs))

        if self._exception:
            raise self._exception

        return MockRequestContext(self._response)


class MockRequestContext:
    """Mock context manager for aiohttp requests."""

    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestAsyncNocoDBClient:
    """Test the main async client functionality."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test async client initialization."""
        assert client.config.base_url == "http://localhost:8080"
        assert client.config.api_token == "test-token"
        assert client._session is None  # Not created until first use

    @pytest.mark.asyncio
    async def test_session_creation(self, client):
        """Test that aiohttp session is created on first use."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            await client._create_session()
            session = client._session

            assert session == mock_session
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_reuse(self, client):
        """Test that session is created once and reused in _request method."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MockSession()
            mock_response = MockResponse(json_data={"success": True})
            mock_session.set_response(mock_response)

            mock_session_class.return_value = mock_session

            # Make multiple requests - session should be created once and reused
            await client._request("GET", "test1")
            await client._request("GET", "test2")

            # Session should be created only once
            mock_session_class.assert_called_once()
            assert mock_session.request_call_count == 2

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="token")
        async with AsyncNocoDBClient(config) as client:
            assert client is not None
            assert client._session is not None  # Session should be created by context manager


class TestAsyncAPIOperations:
    """Test async API operations."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_async_get_records(self, client):
        """Test async get records operation."""
        mock_response_data = {
            "list": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
            "pageInfo": {"isLastPage": True, "totalRows": 2},
        }

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = mock_response_data

            result = await client.get_records("table1")

            assert result == mock_response_data["list"]
            # Check that _request was called with correct params (excluding None values)
            mock_request.assert_called_once_with(
                "GET", "api/v2/tables/table1/records", params={"limit": 25, "offset": 0}
            )

    @pytest.mark.asyncio
    async def test_async_create_record(self, client):
        """Test async create record operation."""
        test_data = {"name": "New Item", "status": "active"}
        mock_response = {"Id": 123, **test_data}

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.insert_record("table1", test_data)

            assert result == 123
            mock_request.assert_called_once_with(
                "POST", "api/v2/tables/table1/records", json_data=test_data
            )

    @pytest.mark.asyncio
    async def test_async_update_record(self, client):
        """Test async update record operation."""
        test_data = {"name": "Updated Item"}
        mock_response = {"Id": 123, "name": "Updated Item"}

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.update_record("table1", test_data, 123)

            assert result == 123
            mock_request.assert_called_once_with(
                "PATCH",
                "api/v2/tables/table1/records",
                json_data={"name": "Updated Item", "Id": 123},
            )

    @pytest.mark.asyncio
    async def test_async_delete_record(self, client):
        """Test async delete record operation."""
        mock_response = {"Id": 123}

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.delete_record("table1", 123)

            assert result == 123
            mock_request.assert_called_once_with(
                "DELETE", "api/v2/tables/table1/records", json_data={"Id": 123}
            )

    @pytest.mark.asyncio
    async def test_async_bulk_operations(self, client):
        """Test async bulk operations."""
        test_records = [{"name": "Item 1"}, {"name": "Item 2"}, {"name": "Item 3"}]
        mock_response_ids = [1, 2, 3]

        with patch.object(client, "insert_record") as mock_insert:
            mock_insert.side_effect = mock_response_ids

            result = await client.bulk_insert_records("table1", test_records)

            assert result == mock_response_ids
            assert mock_insert.call_count == 3


class TestAsyncRequestHandling:
    """Test async request handling and error management."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_successful_request(self, client):
        """Test successful async request handling."""
        mock_response_data = {"success": True, "data": "test"}

        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_response = MockResponse(json_data=mock_response_data)
            mock_session.set_response(mock_response)

            client._session = mock_session

            result = await client._request("GET", "test-endpoint")

            assert result == mock_response_data
            assert mock_session.request_call_count == 1

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client):
        """Test handling of authentication errors."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_response = MockResponse(status=401, json_data={"message": "Unauthorized"})
            mock_session.set_response(mock_response)

            client._session = mock_session

            with pytest.raises(AuthenticationException):
                await client._request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_http_error_handling(self, client):
        """Test handling of HTTP errors."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_response = MockResponse(status=500, json_data={"message": "Internal Server Error"})
            mock_session.set_response(mock_response)

            client._session = mock_session

            with pytest.raises(ServerErrorException):
                await client._request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client):
        """Test handling of connection errors."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_session.set_exception(aiohttp.ClientConnectionError("Connection failed"))
            client._session = mock_session

            with pytest.raises(NetworkException, match="Network error"):
                await client._request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test handling of request timeouts."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_session.set_exception(TimeoutError("Request timed out"))
            client._session = mock_session

            with pytest.raises(ConnectionTimeoutException, match="Request timeout after"):
                await client._request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client):
        """Test handling of invalid JSON responses with application/json content type."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_response = MockResponse(
                status=200,
                content_type="application/json",
                text_data="Invalid response",
                side_effect=json.JSONDecodeError("Invalid JSON", "", 0),
            )
            mock_session.set_response(mock_response)

            client._session = mock_session

            # For application/json content type, JSON decode errors are not caught
            # and will bubble up as JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                await client._request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_invalid_json_response_fallback(self, client):
        """Test handling of invalid JSON responses with non-JSON content type (fallback behavior)."""
        with patch.object(client, "_create_session"):
            mock_session = MockSession()
            mock_response = MockResponse(
                status=200,
                content_type="text/html",  # Non-JSON content type
                text_data="Invalid JSON content",
            )
            mock_session.set_response(mock_response)

            client._session = mock_session

            # For non-JSON content types, the client tries to parse as JSON and falls back to text
            result = await client._request("GET", "test-endpoint")
            assert result == {"data": "Invalid JSON content"}


class TestAsyncConcurrency:
    """Test async concurrency and performance."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        mock_responses = [{"id": i, "name": f"Item {i}"} for i in range(1, 6)]

        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = mock_responses

            # Create multiple concurrent tasks
            tasks = [client.get_record("table1", i) for i in range(1, 6)]

            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert mock_request.call_count == 5

            # Verify all responses are correct
            for i, result in enumerate(results, 1):
                assert result["id"] == i
                assert result["name"] == f"Item {i}"

    @pytest.mark.asyncio
    async def test_concurrent_bulk_operations(self, client):
        """Test concurrent bulk operations."""
        bulk_data_sets = [
            [{"name": f"Batch1-Item{i}"} for i in range(1, 4)],
            [{"name": f"Batch2-Item{i}"} for i in range(1, 4)],
            [{"name": f"Batch3-Item{i}"} for i in range(1, 4)],
        ]

        mock_response_ids = [
            [i + j * 10 for i in range(1, 4)] for j, batch in enumerate(bulk_data_sets)
        ]

        with patch.object(client, "insert_record") as mock_insert:
            # Flatten the response IDs for side_effect
            all_ids = [id for batch in mock_response_ids for id in batch]
            mock_insert.side_effect = all_ids

            # Execute concurrent bulk inserts
            tasks = [
                client.bulk_insert_records(f"table{i}", batch)
                for i, batch in enumerate(bulk_data_sets, 1)
            ]

            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert mock_insert.call_count == 9  # 3 batches × 3 items each

            # Verify results
            for result in results:
                assert len(result) == 3

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test concurrent request handling (rate limiting not implemented in current client)."""
        start_time = asyncio.get_event_loop().time()

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"success": True}

            # Make multiple requests concurrently
            tasks = [client.get_record("table1", i) for i in range(1, 6)]

            await asyncio.gather(*tasks)

            end_time = asyncio.get_event_loop().time()

            # Should complete quickly as there's no rate limiting in current implementation
            assert end_time - start_time < 1.0
            assert mock_request.call_count == 5

    @pytest.mark.asyncio
    async def test_connection_pooling(self, client):
        """Test connection pooling behavior."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MockSession()
            mock_response = MockResponse(json_data={"success": True})
            mock_session.set_response(mock_response)
            mock_session_class.return_value = mock_session

            # Make multiple requests
            tasks = [client._request("GET", f"endpoint{i}") for i in range(10)]

            await asyncio.gather(*tasks)

            # Should only create one session (connection pool)
            mock_session_class.assert_called_once()
            assert mock_session.request_call_count == 10


class TestAsyncTableOperations:
    """Test async table-specific operations."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_async_table_operations_not_implemented(self, client):
        """Test that table management operations are not implemented in current client."""
        # The current AsyncNocoDBClient doesn't implement table management methods
        # like create_table, list_tables, etc. These would need to be added.
        assert hasattr(client, "get_records")
        assert hasattr(client, "insert_record")
        assert hasattr(client, "update_record")
        assert hasattr(client, "delete_record")

        # Table management methods are not implemented
        assert not hasattr(client, "create_table")
        assert not hasattr(client, "list_tables")
        assert not hasattr(client, "get_table_info")


class TestAsyncPerformance:
    """Test async performance characteristics."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, client):
        """Test handling of large datasets asynchronously."""
        # Simulate large dataset
        large_dataset = [
            {"id": i, "name": f"Item {i}", "data": "x" * 100} for i in range(100)
        ]  # Reduced size for testing
        mock_ids = list(range(1, 101))

        with patch.object(client, "insert_record") as mock_insert:
            mock_insert.side_effect = mock_ids

            start_time = asyncio.get_event_loop().time()
            result = await client.bulk_insert_records("table1", large_dataset)
            end_time = asyncio.get_event_loop().time()

            assert len(result) == 100
            assert mock_insert.call_count == 100
            # Should complete in reasonable time (async should be faster)
            assert end_time - start_time < 5.0  # 5 seconds max

    @pytest.mark.asyncio
    async def test_streaming_not_implemented(self, client):
        """Test that streaming is not implemented in current client."""
        # The current AsyncNocoDBClient doesn't implement streaming methods
        assert not hasattr(client, "stream_records")

        # The client currently loads records in batches internally in get_records
        # but doesn't expose a streaming interface

    @pytest.mark.asyncio
    async def test_connection_efficiency(self, client):
        """Test connection reuse efficiency."""
        with patch.object(client, "_create_session") as mock_create_session:
            mock_session = MockSession()
            mock_response = MockResponse(json_data={"success": True})
            mock_session.set_response(mock_response)

            client._session = mock_session

            # Make many requests
            tasks = [client._request("GET", f"endpoint{i}") for i in range(50)]

            await asyncio.gather(*tasks)

            # Session should be created only once (or not at all since we set it manually)
            assert mock_create_session.call_count <= 1  # Should reuse connection
            assert mock_session.request_call_count == 50
