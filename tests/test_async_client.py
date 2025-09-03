"""Tests for NocoDB Async Client based on actual implementation."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch
import pytest

from nocodb_simple_client.exceptions import NocoDBException, ValidationException

# Test if async dependencies are available
try:
    from nocodb_simple_client.async_client import AsyncNocoDBClient, ASYNC_AVAILABLE
    async_available = ASYNC_AVAILABLE
except ImportError:
    async_available = False
    AsyncNocoDBClient = None

pytestmark = pytest.mark.skipif(not async_available, reason="Async dependencies not available")


@pytest.mark.asyncio
class TestAsyncNocoDBClientInitialization:
    """Test AsyncNocoDBClient initialization."""

    async def test_async_client_initialization(self):
        """Test async client initialization."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token"
        )
        async_client = AsyncNocoDBClient(config)

        assert async_client.config.base_url == "https://app.nocodb.com"
        assert async_client.config.api_token == "test_token"

    async def test_async_client_with_access_protection(self):
        """Test async client initialization with access protection."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token",
            access_protection_auth="protection_value",
            access_protection_header="X-Custom-Auth"
        )
        async_client = AsyncNocoDBClient(config)

        assert async_client.config.api_token == "test_token"
        assert async_client.config.access_protection_auth == "protection_value"


@pytest.mark.asyncio
class TestAsyncRecordOperations:
    """Test async record operations."""

    @pytest.fixture
    def async_client(self):
        """Create async client for testing."""
        if not async_available:
            pytest.skip("Async dependencies not available")
        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token"
        )
        return AsyncNocoDBClient(config)

    async def test_get_records_async(self, async_client):
        """Test async get_records operation."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        expected_records = [
            {"Id": "1", "Name": "Record 1"},
            {"Id": "2", "Name": "Record 2"}
        ]
        expected_response = {
            "list": expected_records,
            "pageInfo": {"totalRows": 2}
        }

        with patch.object(async_client, '_get_async') as mock_get:
            mock_get.return_value = expected_response

            result = await async_client.get_records("table_123")

            assert result == expected_records
            mock_get.assert_called_once()

    async def test_insert_record_async(self, async_client):
        """Test async insert_record operation."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        record_data = {"Name": "New Record", "Status": "active"}
        expected_response = {"Id": "new_record_123"}

        with patch.object(async_client, '_post_async') as mock_post:
            mock_post.return_value = expected_response

            result = await async_client.insert_record("table_123", record_data)

            assert result == "new_record_123"
            mock_post.assert_called_once()

    async def test_update_record_async(self, async_client):
        """Test async update_record operation."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        update_data = {"Name": "Updated Record", "Status": "inactive"}
        expected_response = {"Id": "record_123"}

        with patch.object(async_client, '_patch_async') as mock_patch:
            mock_patch.return_value = expected_response

            result = await async_client.update_record("table_123", update_data, "record_123")

            assert result == "record_123"
            mock_patch.assert_called_once()


@pytest.mark.asyncio
class TestAsyncBulkOperations:
    """Test async bulk operations."""

    @pytest.fixture
    def async_client(self):
        """Create async client for testing."""
        if not async_available:
            pytest.skip("Async dependencies not available")
        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token"
        )
        return AsyncNocoDBClient(config)

    async def test_bulk_insert_records_async(self, async_client):
        """Test async bulk insert records."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        records = [
            {"Name": "Record 1", "Status": "active"},
            {"Name": "Record 2", "Status": "active"},
            {"Name": "Record 3", "Status": "inactive"}
        ]
        expected_response = [{"Id": "rec1"}, {"Id": "rec2"}, {"Id": "rec3"}]

        with patch.object(async_client, '_post_async') as mock_post:
            mock_post.return_value = expected_response

            result = await async_client.bulk_insert_records("table_123", records)

            assert result == ["rec1", "rec2", "rec3"]
            mock_post.assert_called_once()

    async def test_bulk_insert_empty_list_async(self, async_client):
        """Test bulk insert with empty list."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        result = await async_client.bulk_insert_records("table_123", [])
        assert result == []


@pytest.mark.asyncio
class TestAsyncClientErrorHandling:
    """Test async client error handling."""

    @pytest.fixture
    def async_client(self):
        """Create async client for testing."""
        if not async_available:
            pytest.skip("Async dependencies not available")
        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token"
        )
        return AsyncNocoDBClient(config)

    async def test_insert_record_validation_error_async(self, async_client):
        """Test async insert_record with validation error."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        with patch.object(async_client, '_post_async') as mock_post:
            mock_post.side_effect = ValidationException("Invalid data")

            with pytest.raises(ValidationException, match="Invalid data"):
                await async_client.insert_record("table_123", {"Name": ""})


class TestAsyncClientAvailability:
    """Test async client availability checks."""

    def test_async_dependencies_import(self):
        """Test that async dependencies are properly imported."""
        if async_available:
            assert AsyncNocoDBClient is not None
            assert hasattr(AsyncNocoDBClient, 'get_records')
            assert hasattr(AsyncNocoDBClient, 'bulk_insert_records')
        else:
            # Test should pass if async is not available
            assert AsyncNocoDBClient is None or not async_available

    def test_async_client_methods_are_async(self):
        """Test that client methods are properly async."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        from nocodb_simple_client.config import NocoDBConfig
        config = NocoDBConfig(
            base_url="https://app.nocodb.com",
            api_token="test_token"
        )
        async_client = AsyncNocoDBClient(config)

        # Check that key methods are coroutines
        assert asyncio.iscoroutinefunction(async_client.get_records)
        assert asyncio.iscoroutinefunction(async_client.insert_record)
        assert asyncio.iscoroutinefunction(async_client.bulk_insert_records)
        assert asyncio.iscoroutinefunction(async_client.close)
