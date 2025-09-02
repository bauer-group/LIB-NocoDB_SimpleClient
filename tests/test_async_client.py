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
from nocodb_simple_client.exceptions import AuthenticationException, NocoDBException


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

            session = await client._get_session()

            assert session == mock_session
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_reuse(self, client):
        """Test that session is reused across requests."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            session1 = await client._get_session()
            session2 = await client._get_session()

            assert session1 == session2
            mock_session_class.assert_called_once()  # Only called once

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="token")
        async with AsyncNocoDBClient(config) as client:
            assert client is not None

            with patch.object(client, "_get_session", return_value=AsyncMock()) as mock_get_session:
                mock_session = await mock_get_session.return_value
                mock_session.close = AsyncMock()

                # Session should be available
                session = await client._get_session()
                assert session is not None


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
            "pageInfo": {"totalRows": 2},
        }

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response_data

            result = await client.get_records("table1")

            assert result == mock_response_data["list"]
            mock_request.assert_called_once_with("GET", "/api/v2/tables/table1/records")

    @pytest.mark.asyncio
    async def test_async_create_record(self, client):
        """Test async create record operation."""
        test_data = {"name": "New Item", "status": "active"}
        mock_response = {"id": 123, **test_data}

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.create_record("table1", test_data)

            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST", "/api/v2/tables/table1/records", json=test_data
            )

    @pytest.mark.asyncio
    async def test_async_update_record(self, client):
        """Test async update record operation."""
        test_data = {"name": "Updated Item"}
        mock_response = {"id": 123, **test_data}

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.update_record("table1", 123, test_data)

            assert result == mock_response
            mock_request.assert_called_once_with(
                "PATCH", "/api/v2/tables/table1/records/123", json=test_data
            )

    @pytest.mark.asyncio
    async def test_async_delete_record(self, client):
        """Test async delete record operation."""
        mock_response = {"deleted": True}

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.delete_record("table1", 123)

            assert result == mock_response
            mock_request.assert_called_once_with("DELETE", "/api/v2/tables/table1/records/123")

    @pytest.mark.asyncio
    async def test_async_bulk_operations(self, client):
        """Test async bulk operations."""
        test_records = [{"name": "Item 1"}, {"name": "Item 2"}, {"name": "Item 3"}]
        mock_response = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
        ]

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.bulk_insert_records("table1", test_records)

            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST", "/api/v2/tables/table1/records", json=test_records
            )


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

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_session.request.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await client._make_request("GET", "/test-endpoint")

            assert result == mock_response_data
            mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client):
        """Test handling of authentication errors."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_response.json.return_value = {"message": "Unauthorized"}
            mock_session.request.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(AuthenticationException):
                await client._make_request("GET", "/test-endpoint")

    @pytest.mark.asyncio
    async def test_http_error_handling(self, client):
        """Test handling of HTTP errors."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.json.return_value = {"message": "Internal Server Error"}
            mock_session.request.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(NocoDBException):
                await client._make_request("GET", "/test-endpoint")

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client):
        """Test handling of connection errors."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request.side_effect = aiohttp.ClientConnectionError("Connection failed")
            mock_get_session.return_value = mock_session

            with pytest.raises(NocoDBException, match="Connection failed"):
                await client._make_request("GET", "/test-endpoint")

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test handling of request timeouts."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request.side_effect = TimeoutError("Request timed out")
            mock_get_session.return_value = mock_session

            with pytest.raises(NocoDBException, match="Request timed out"):
                await client._make_request("GET", "/test-endpoint")

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client):
        """Test handling of invalid JSON responses."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.text.return_value = "Invalid response"
            mock_session.request.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(NocoDBException, match="Invalid JSON response"):
                await client._make_request("GET", "/test-endpoint")


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

        with patch.object(client, "_make_request") as mock_request:
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

        mock_responses = [
            [{"id": i + j * 10, **item} for i, item in enumerate(batch, 1)]
            for j, batch in enumerate(bulk_data_sets)
        ]

        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = mock_responses

            # Execute concurrent bulk inserts
            tasks = [
                client.bulk_insert_records(f"table{i}", batch)
                for i, batch in enumerate(bulk_data_sets, 1)
            ]

            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert mock_request.call_count == 3

            # Verify results
            for result in results:
                assert len(result) == 3

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # Configure rate limiting
        client.configure_rate_limiting(requests_per_second=2)

        start_time = asyncio.get_event_loop().time()

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"success": True}

            # Make multiple requests that should be rate limited
            tasks = [client.get_record("table1", i) for i in range(1, 6)]

            await asyncio.gather(*tasks)

            end_time = asyncio.get_event_loop().time()

            # With 2 req/sec and 5 requests, should take at least 2 seconds
            assert end_time - start_time >= 2.0

    @pytest.mark.asyncio
    async def test_connection_pooling(self, client):
        """Test connection pooling behavior."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.request.return_value.__aenter__.return_value.status = 200
            mock_session.request.return_value.__aenter__.return_value.json.return_value = {
                "success": True
            }

            # Make multiple requests
            tasks = [client._make_request("GET", f"/endpoint{i}") for i in range(10)]

            await asyncio.gather(*tasks)

            # Should only create one session (connection pool)
            mock_session_class.assert_called_once()
            assert mock_session.request.call_count == 10


class TestAsyncTableOperations:
    """Test async table-specific operations."""

    @pytest.fixture
    def client(self):
        """Create an async client instance for testing."""
        config = NocoDBConfig(base_url="http://localhost:8080", api_token="test-token")
        return AsyncNocoDBClient(config)

    @pytest.mark.asyncio
    async def test_async_table_creation(self, client):
        """Test async table creation."""
        table_data = {
            "title": "Test Table",
            "columns": [
                {"title": "Name", "uidt": "SingleLineText"},
                {"title": "Email", "uidt": "Email"},
            ],
        }

        mock_response = {"id": "tbl_123", "title": "Test Table", **table_data}

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.create_table("project_123", table_data)

            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST", "/api/v2/meta/projects/project_123/tables", json=table_data
            )

    @pytest.mark.asyncio
    async def test_async_table_listing(self, client):
        """Test async table listing."""
        mock_response = {
            "list": [{"id": "tbl_1", "title": "Table 1"}, {"id": "tbl_2", "title": "Table 2"}]
        }

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.list_tables("project_123")

            assert result == mock_response["list"]
            mock_request.assert_called_once_with("GET", "/api/v2/meta/projects/project_123/tables")

    @pytest.mark.asyncio
    async def test_async_table_info(self, client):
        """Test async table information retrieval."""
        mock_response = {
            "id": "tbl_123",
            "title": "Test Table",
            "columns": [
                {"id": "col_1", "title": "Name", "uidt": "SingleLineText"},
                {"id": "col_2", "title": "Email", "uidt": "Email"},
            ],
        }

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_table_info("tbl_123")

            assert result == mock_response
            mock_request.assert_called_once_with("GET", "/api/v2/meta/tables/tbl_123")


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
        large_dataset = [{"id": i, "name": f"Item {i}", "data": "x" * 100} for i in range(1000)]

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = large_dataset

            start_time = asyncio.get_event_loop().time()
            result = await client.bulk_insert_records("table1", large_dataset)
            end_time = asyncio.get_event_loop().time()

            assert len(result) == 1000
            # Should complete in reasonable time (async should be faster)
            assert end_time - start_time < 5.0  # 5 seconds max

    @pytest.mark.asyncio
    async def test_memory_efficient_streaming(self, client):
        """Test memory-efficient streaming for large result sets."""

        # Mock streaming response
        async def mock_stream_records():
            for i in range(100):
                yield {"id": i, "name": f"Item {i}"}

        with patch.object(client, "stream_records", return_value=mock_stream_records()):
            records = []
            async for record in client.stream_records("table1"):
                records.append(record)
                # Simulate processing
                await asyncio.sleep(0.001)

            assert len(records) == 100

    @pytest.mark.asyncio
    async def test_connection_efficiency(self, client):
        """Test connection reuse efficiency."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.return_value.status = 200
            mock_session.request.return_value.__aenter__.return_value.json.return_value = {
                "success": True
            }
            mock_get_session.return_value = mock_session

            # Make many requests
            tasks = [client._make_request("GET", f"/endpoint{i}") for i in range(50)]

            await asyncio.gather(*tasks)

            # Session should be created only once
            assert mock_get_session.call_count <= 1  # Should reuse connection
            assert mock_session.request.call_count == 50
