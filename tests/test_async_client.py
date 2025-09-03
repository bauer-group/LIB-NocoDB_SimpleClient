"""Tests for NocoDB Async Client based on actual implementation."""

import asyncio
import pytest


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

    async def test_bulk_insert_empty_list_async(self, async_client):
        """Test bulk insert with empty list."""
        if not async_available:
            pytest.skip("Async dependencies not available")

        result = await async_client.bulk_insert_records("table_123", [])
        assert result == []


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
