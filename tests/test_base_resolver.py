"""Tests for BaseIdResolver.

MIT License

Copyright (c) BAUER GROUP
"""

from unittest.mock import MagicMock

import pytest

from nocodb_simple_client.base_resolver import BaseIdResolver
from nocodb_simple_client.exceptions import TableNotFoundException


class TestBaseIdResolver:
    """Test BaseIdResolver for base ID resolution and caching."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock NocoDB client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def resolver(self, mock_client):
        """Create a BaseIdResolver instance."""
        return BaseIdResolver(mock_client)

    def test_initialization(self, mock_client):
        """Test BaseIdResolver initialization."""
        resolver = BaseIdResolver(mock_client)

        assert resolver._client == mock_client
        assert resolver._cache == {}
        assert resolver._enabled is True

    def test_get_base_id_with_base_id_in_response(self, resolver, mock_client):
        """Test getting base_id when it's in the response."""
        mock_client._get.return_value = {
            "id": "table_123",
            "title": "Test Table",
            "base_id": "base_abc",
        }

        base_id = resolver.get_base_id("table_123")

        assert base_id == "base_abc"
        assert resolver._cache["table_123"] == "base_abc"
        mock_client._get.assert_called_once_with("api/v2/meta/tables/table_123")

    def test_get_base_id_with_source_id(self, resolver, mock_client):
        """Test getting base_id when response uses source_id."""
        mock_client._get.return_value = {
            "id": "table_123",
            "title": "Test Table",
            "source_id": "base_xyz",
        }

        base_id = resolver.get_base_id("table_123")

        assert base_id == "base_xyz"
        assert resolver._cache["table_123"] == "base_xyz"

    def test_get_base_id_with_project_id(self, resolver, mock_client):
        """Test getting base_id when response uses project_id (legacy)."""
        mock_client._get.return_value = {
            "id": "table_123",
            "title": "Test Table",
            "project_id": "base_legacy",
        }

        base_id = resolver.get_base_id("table_123")

        assert base_id == "base_legacy"
        assert resolver._cache["table_123"] == "base_legacy"

    def test_get_base_id_from_cache(self, resolver, mock_client):
        """Test getting base_id from cache (no API call)."""
        # Pre-populate cache
        resolver._cache["table_123"] = "base_cached"

        base_id = resolver.get_base_id("table_123")

        assert base_id == "base_cached"
        # Should not make any API calls
        mock_client._get.assert_not_called()

    def test_get_base_id_force_refresh(self, resolver, mock_client):
        """Test force refresh bypasses cache."""
        # Pre-populate cache
        resolver._cache["table_123"] = "base_old"

        mock_client._get.return_value = {
            "id": "table_123",
            "base_id": "base_new",
        }

        base_id = resolver.get_base_id("table_123", force_refresh=True)

        assert base_id == "base_new"
        assert resolver._cache["table_123"] == "base_new"
        mock_client._get.assert_called_once()

    def test_get_base_id_not_found(self, resolver, mock_client):
        """Test handling when base_id cannot be found."""
        mock_client._get.return_value = {
            "id": "table_123",
            "title": "Test Table",
            # No base_id, source_id, or project_id
        }

        with pytest.raises(TableNotFoundException, match="Could not resolve base_id"):
            resolver.get_base_id("table_123")

    def test_set_base_id_manually(self, resolver):
        """Test manually setting base_id mapping."""
        resolver.set_base_id("table_123", "base_manual")

        assert resolver._cache["table_123"] == "base_manual"

        # Verify it's used when getting
        base_id = resolver.get_base_id("table_123")
        assert base_id == "base_manual"

    def test_clear_cache_specific_table(self, resolver):
        """Test clearing cache for specific table."""
        resolver._cache = {
            "table_1": "base_1",
            "table_2": "base_2",
            "table_3": "base_3",
        }

        resolver.clear_cache("table_2")

        assert "table_1" in resolver._cache
        assert "table_2" not in resolver._cache
        assert "table_3" in resolver._cache

    def test_clear_cache_all(self, resolver):
        """Test clearing entire cache."""
        resolver._cache = {
            "table_1": "base_1",
            "table_2": "base_2",
            "table_3": "base_3",
        }

        resolver.clear_cache()

        assert resolver._cache == {}

    def test_get_cache_size(self, resolver):
        """Test getting cache size."""
        assert resolver.get_cache_size() == 0

        resolver._cache = {
            "table_1": "base_1",
            "table_2": "base_2",
        }

        assert resolver.get_cache_size() == 2

    def test_disable_resolver(self, resolver):
        """Test disabling the resolver."""
        assert resolver.is_enabled() is True

        resolver.disable()

        assert resolver.is_enabled() is False

    def test_enable_resolver(self, resolver):
        """Test enabling the resolver."""
        resolver.disable()
        assert resolver.is_enabled() is False

        resolver.enable()

        assert resolver.is_enabled() is True

    def test_multiple_tables_caching(self, resolver, mock_client):
        """Test caching works for multiple tables."""
        mock_client._get.side_effect = [
            {"id": "table_1", "base_id": "base_a"},
            {"id": "table_2", "base_id": "base_b"},
            {"id": "table_3", "base_id": "base_c"},
        ]

        # First calls - should hit API
        base1 = resolver.get_base_id("table_1")
        base2 = resolver.get_base_id("table_2")
        base3 = resolver.get_base_id("table_3")

        assert base1 == "base_a"
        assert base2 == "base_b"
        assert base3 == "base_c"
        assert mock_client._get.call_count == 3

        # Second calls - should use cache
        mock_client._get.reset_mock()

        base1_cached = resolver.get_base_id("table_1")
        base2_cached = resolver.get_base_id("table_2")

        assert base1_cached == "base_a"
        assert base2_cached == "base_b"
        assert mock_client._get.call_count == 0  # No API calls

    def test_cache_persistence_across_operations(self, resolver, mock_client):
        """Test cache persists across different operations."""
        mock_client._get.return_value = {"id": "table_123", "base_id": "base_abc"}

        # First call
        base_id_1 = resolver.get_base_id("table_123")

        # Manual set for different table
        resolver.set_base_id("table_456", "base_xyz")

        # Get both
        base_id_1_again = resolver.get_base_id("table_123")
        base_id_2 = resolver.get_base_id("table_456")

        assert base_id_1 == "base_abc"
        assert base_id_1_again == "base_abc"
        assert base_id_2 == "base_xyz"

        # Should only have made one API call
        assert mock_client._get.call_count == 1
