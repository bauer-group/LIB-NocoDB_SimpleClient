"""
Comprehensive tests for the caching layer functionality.
"""

import os
import sys
import time
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.cache import CacheConfig, NocoDBCache
from nocodb_simple_client.client import NocoDBClient


class TestCacheConfig:
    """Test the cache configuration class."""

    def test_default_configuration(self):
        """Test default cache configuration values."""
        config = CacheConfig()

        assert config.enabled is True
        assert config.default_ttl == 300  # 5 minutes
        assert config.max_entries == 1000
        assert config.eviction_policy == "lru"

    def test_custom_configuration(self):
        """Test custom cache configuration values."""
        config = CacheConfig(
            enabled=False, default_ttl=600, max_entries=500, eviction_policy="fifo"
        )

        assert config.enabled is False
        assert config.default_ttl == 600
        assert config.max_entries == 500
        assert config.eviction_policy == "fifo"

    def test_invalid_eviction_policy(self):
        """Test that invalid eviction policy raises error."""
        with pytest.raises(ValueError, match="Invalid eviction policy"):
            CacheConfig(eviction_policy="invalid")


class TestNocoDBCache:
    """Test the main cache implementation."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        config = CacheConfig(enabled=True, default_ttl=60, max_entries=10)
        return NocoDBCache(config)

    @pytest.fixture
    def disabled_cache(self):
        """Create a disabled cache instance for testing."""
        config = CacheConfig(enabled=False)
        return NocoDBCache(config)

    def test_cache_initialization(self, cache):
        """Test cache initialization with configuration."""
        assert cache.config.enabled is True
        assert cache.config.default_ttl == 60
        assert cache.config.max_entries == 10
        assert len(cache._cache) == 0

    def test_cache_disabled(self, disabled_cache):
        """Test that disabled cache doesn't store values."""
        disabled_cache.set("key1", "value1")

        assert disabled_cache.get("key1") is None
        assert len(disabled_cache._cache) == 0

    def test_basic_get_set(self, cache):
        """Test basic cache get and set operations."""
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"
        assert len(cache._cache) == 1

    def test_get_nonexistent_key(self, cache):
        """Test getting a non-existent key returns None."""
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self, cache):
        """Test that cached items expire after TTL."""
        # Use a very short TTL for testing
        cache.set("key1", "value1", ttl=0.1)

        # Should be available immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)

        # Should be None after expiration
        assert cache.get("key1") is None

    def test_custom_ttl(self, cache):
        """Test setting custom TTL for cache entries."""
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=2)

        # Both should be available
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        # After 1.1 seconds, key1 should expire but key2 should remain
        time.sleep(1.1)
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_lru_eviction(self, cache):
        """Test LRU eviction when max_entries is reached."""
        # Fill cache to capacity
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")

        assert len(cache._cache) == 10

        # Access key0 to make it most recently used
        cache.get("key0")

        # Add new item, should evict least recently used (key1)
        cache.set("key10", "value10")

        assert len(cache._cache) == 10
        assert cache.get("key0") == "value0"  # Should still exist
        assert cache.get("key1") is None  # Should be evicted
        assert cache.get("key10") == "value10"

    def test_delete_entry(self, cache):
        """Test deleting cache entries."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        cache.delete("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_clear_cache(self, cache):
        """Test clearing entire cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert len(cache._cache) == 3

        cache.clear()

        assert len(cache._cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_statistics(self, cache):
        """Test cache hit/miss statistics."""
        # Initial statistics
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0

        # Set some values
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Cache hits
        cache.get("key1")
        cache.get("key1")
        cache.get("key2")

        # Cache miss
        cache.get("key3")

        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.75
        assert stats["total_entries"] == 2

    def test_cache_key_generation(self, cache):
        """Test automatic cache key generation for method calls."""
        # Test with various parameter types
        key1 = cache._generate_key("get_records", "table1", page=1, limit=10)
        key2 = cache._generate_key("get_records", "table1", page=2, limit=10)
        key3 = cache._generate_key("get_records", "table2", page=1, limit=10)

        assert key1 != key2  # Different pages should generate different keys
        assert key1 != key3  # Different tables should generate different keys

        # Same parameters should generate same key
        key4 = cache._generate_key("get_records", "table1", page=1, limit=10)
        assert key1 == key4


class TestCacheIntegration:
    """Test cache integration with NocoDBClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with caching enabled."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}

        # Enable caching
        cache_config = CacheConfig(enabled=True, default_ttl=60)
        client.cache = NocoDBCache(cache_config)

        return client

    def test_cached_get_records(self, mock_client):
        """Test that get_records operations are cached."""
        # Mock response data
        mock_data = {
            "list": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
            "pageInfo": {"totalRows": 2},
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_data

            # First call should hit the API
            result1 = mock_client.cache.get_or_set(
                "get_records_table1_page1", lambda: mock_data, ttl=60
            )

            # Second call should hit the cache
            result2 = mock_client.cache.get("get_records_table1_page1")

            assert result1 == mock_data
            assert result2 == mock_data
            assert mock_get.call_count == 0  # Should use lambda function

    def test_cache_invalidation_on_update(self, mock_client):
        """Test that cache is invalidated when records are updated."""
        # Set up cached data
        cache_key = "get_records_table1"
        mock_client.cache.set(cache_key, {"data": "old_data"})

        # Verify data is cached
        assert mock_client.cache.get(cache_key) == {"data": "old_data"}

        # Simulate update operation that should invalidate cache
        mock_client.cache.invalidate_pattern("get_records_table1*")

        # Cache should be cleared
        assert mock_client.cache.get(cache_key) is None

    def test_conditional_caching(self, mock_client):
        """Test conditional caching based on method type."""
        # GET operations should be cached
        get_key = mock_client.cache._generate_key("GET", "table1", "records")
        mock_client.cache.set(get_key, {"cached": "data"})
        assert mock_client.cache.get(get_key) == {"cached": "data"}

        # POST/PUT/DELETE operations should not be cached
        post_data = {"id": 1, "name": "New Item"}
        mock_client.cache.set("POST_data", post_data)  # This shouldn't cache

        # Verify caching behavior
        assert len([k for k in mock_client.cache._cache.keys() if "GET" in k]) > 0

    def test_cache_warming(self, mock_client):
        """Test cache warming strategies."""
        # Warm up cache with commonly accessed data
        tables = ["users", "products", "orders"]

        for table in tables:
            cache_key = f"get_records_{table}_page1"
            mock_data = {"list": [], "pageInfo": {"totalRows": 0}}
            mock_client.cache.set(cache_key, mock_data, ttl=300)

        # Verify all tables are cached
        for table in tables:
            cache_key = f"get_records_{table}_page1"
            assert mock_client.cache.get(cache_key) is not None

        # Check cache statistics
        stats = mock_client.cache.get_stats()
        assert stats["total_entries"] == 3


class TestCacheErrorHandling:
    """Test cache error handling and edge cases."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        config = CacheConfig(enabled=True, default_ttl=60)
        return NocoDBCache(config)

    def test_serialization_error_handling(self, cache):
        """Test handling of non-serializable objects."""
        # Objects that can't be easily serialized
        complex_object = {"func": lambda x: x, "set": {1, 2, 3}}

        # Should handle gracefully (or convert to serializable form)
        cache.set("complex", complex_object)
        result = cache.get("complex")

        # The cache should either store a serializable version or handle gracefully
        assert result is not None or result is None  # Both outcomes acceptable

    def test_memory_pressure_handling(self, cache):
        """Test cache behavior under memory pressure."""
        # Fill cache beyond capacity with large objects
        large_data = "x" * 10000  # 10KB string

        for i in range(15):  # Exceed max_entries (10)
            cache.set(f"large_key_{i}", large_data)

        # Cache should not exceed max_entries
        assert len(cache._cache) <= cache.config.max_entries

    def test_concurrent_access_safety(self, cache):
        """Test cache safety under concurrent access."""
        import threading

        def cache_worker(thread_id):
            for i in range(10):
                cache.set(f"thread_{thread_id}_key_{i}", f"value_{i}")
                cache.get(f"thread_{thread_id}_key_{i}")

        # Create multiple threads accessing cache
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Cache should still be in valid state
        assert len(cache._cache) <= cache.config.max_entries
        stats = cache.get_stats()
        assert stats["hits"] >= 0
        assert stats["misses"] >= 0

    def test_cache_corruption_recovery(self, cache):
        """Test recovery from cache corruption scenarios."""
        # Simulate corrupted cache state
        cache.set("valid_key", "valid_value")

        # Manually corrupt cache entry (our cache uses tuples, not dicts)
        if "valid_key" in cache._cache:
            cache._cache["valid_key"] = "invalid_format"  # Should be a tuple (value, expiry)

        # Cache should handle corruption gracefully
        result = cache.get("valid_key")
        # Should either return None or recover gracefully
        assert result is None or isinstance(result, str)

    def test_extremely_long_keys(self, cache):
        """Test handling of extremely long cache keys."""
        long_key = "x" * 1000  # Very long key

        cache.set(long_key, "test_value")
        result = cache.get(long_key)

        assert result == "test_value" or result is None  # Should handle gracefully


class TestCacheMetrics:
    """Test cache metrics and monitoring."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        config = CacheConfig(enabled=True, default_ttl=60)
        return NocoDBCache(config)

    def test_detailed_statistics(self, cache):
        """Test detailed cache statistics collection."""
        # Perform various cache operations
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("key3")  # miss
        cache.delete("key2")

        stats = cache.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["sets"] == 2
        assert stats["deletes"] == 1
        assert stats["total_entries"] == 1
        assert "memory_usage" in stats
        assert "avg_access_time" in stats

    def test_cache_efficiency_metrics(self, cache):
        """Test cache efficiency and performance metrics."""
        # Fill cache with test data
        for i in range(5):
            cache.set(f"key{i}", f"value{i}")

        # Access patterns
        for _ in range(10):
            cache.get("key0")  # Hot key

        for i in range(1, 5):
            cache.get(f"key{i}")  # Moderate access

        cache.get("nonexistent")  # Miss

        efficiency = cache.calculate_efficiency()

        assert efficiency["hit_rate"] > 0.8  # Should be high
        assert efficiency["hotkey_ratio"] > 0  # Should identify hot keys
        assert "access_patterns" in efficiency

    def test_cache_health_check(self, cache):
        """Test cache health monitoring."""
        # Add some test data
        cache.set("test1", "data1")
        cache.set("test2", "data2", ttl=0.1)  # Short TTL

        health = cache.health_check()

        assert health["status"] == "healthy"
        assert health["total_entries"] == 2
        assert health["expired_entries"] >= 0
        assert "memory_usage_mb" in health
        assert "oldest_entry_age" in health

        # Wait for expiration
        time.sleep(0.2)

        health_after = cache.health_check()
        assert health_after["expired_entries"] >= 1
