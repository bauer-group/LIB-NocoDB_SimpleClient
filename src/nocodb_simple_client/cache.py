"""
MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import json
import pickle  # nosec B403
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any

"""Caching layer for NocoDB Simple Client."""

try:
    import diskcache as dc

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False
    dc = None

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore[assignment]


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get value from cache."""  # nosec - false positive
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if cache key exists."""  # nosec - false positive
        pass


class MemoryCache(CacheBackend):
    """In-memory cache implementation."""

    def __init__(self, max_size: int = 1000):
        """Initialize memory cache with maximum size.

        Args:
            max_size: Maximum number of items to store in cache
        """
        self.cache: dict[str, tuple[Any, float | None]] = {}  # key: (value, expiry_time)
        self.max_size = max_size

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items() if expiry and expiry < current_time
        ]
        for key in expired_keys:
            del self.cache[key]

    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        if len(self.cache) >= self.max_size:
            # Simple LRU eviction - remove oldest entries
            keys_to_remove = list(self.cache.keys())[: (len(self.cache) - self.max_size + 1)]
            for key in keys_to_remove:
                del self.cache[key]

    def get(self, key: str) -> Any | None:
        """Get value from cache."""  # nosec - false positive
        self._cleanup_expired()

        if key in self.cache:
            value, expiry = self.cache[key]
            if not expiry or expiry > time.time():
                return value
            else:
                del self.cache[key]

        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        self._cleanup_expired()
        self._evict_if_needed()

        expiry = time.time() + ttl if ttl else None
        self.cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()

    def exists(self, key: str) -> bool:
        """Check if cache key exists."""  # nosec - false positive
        return self.get(key) is not None


class DiskCache(CacheBackend):
    """Disk-based cache implementation using diskcache."""

    def __init__(self, directory: str = "./cache", size_limit: int = 100_000_000):
        """Initialize disk cache.

        Args:
            directory: Directory to store cache files
            size_limit: Maximum size of cache in bytes

        Raises:
            ImportError: If diskcache is not installed
        """
        if not DISKCACHE_AVAILABLE:
            raise ImportError(
                "DiskCache requires diskcache. "
                "Install with: pip install 'nocodb-simple-client[caching]'"
            )

        self.cache = dc.Cache(directory, size_limit=size_limit)

    def get(self, key: str) -> Any | None:
        """Get value from cache."""  # nosec - false positive
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        if ttl:
            self.cache.set(key, value, expire=ttl)
        else:
            self.cache.set(key, value)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.cache.delete(key)

    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()

    def exists(self, key: str) -> bool:
        """Check if cache key exists."""  # nosec - false positive
        return key in self.cache


class RedisCache(CacheBackend):
    """Redis-based cache implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        key_prefix: str = "nocodb:",
    ):
        """Initialize Redis cache.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password
            key_prefix: Prefix for all cache keys

        Raises:
            ImportError: If redis is not installed
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "RedisCache requires redis. "
                "Install with: pip install 'nocodb-simple-client[caching]'"
            )

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We'll handle encoding/decoding
        )
        self.key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Add prefix to cache key."""  # nosec - false positive
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Any | None:
        """Get value from cache."""  # nosec - false positive
        try:
            data = self.client.get(self._make_key(key))
            if data:
                try:
                    # Try JSON first for security
                    return json.loads(data.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fall back to pickle for complex objects
                    return pickle.loads(data)  # nosec B301
        except (redis.RedisError, pickle.PickleError):
            pass
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        try:
            # Try JSON first for security
            try:
                data = json.dumps(value, default=str).encode("utf-8")
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects  # nosec B301
                data = pickle.dumps(value)

            if ttl:
                self.client.setex(self._make_key(key), ttl, data)
            else:
                self.client.set(self._make_key(key), data)
        except (redis.RedisError, pickle.PickleError):
            pass  # Fail silently for cache operations

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.client.delete(self._make_key(key))
        except redis.RedisError:
            pass

    def clear(self) -> None:
        """Clear all cached values with prefix."""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except redis.RedisError:
            pass

    def exists(self, key: str) -> bool:
        """Check if cache key exists."""  # nosec - false positive
        try:
            return bool(self.client.exists(self._make_key(key)))
        except redis.RedisError:
            return False


class CacheManager:
    """Cache manager for handling different cache backends."""

    def __init__(self, backend: CacheBackend, default_ttl: int | None = 300):
        """Initialize cache manager.

        Args:
            backend: Cache backend implementation
            default_ttl: Default time-to-live in seconds
        """
        self.backend = backend
        self.default_ttl = default_ttl

    def _make_cache_key(self, table_id: str, operation: str, **kwargs: Any) -> str:
        """Generate cache key from parameters."""  # nosec - false positive
        # Create a deterministic hash of the parameters
        key_data = {"table_id": table_id, "operation": operation, **kwargs}

        # Sort keys for consistency
        sorted_data = json.dumps(key_data, sort_keys=True, default=str)

        # Create hash
        key_hash = hashlib.sha256(sorted_data.encode()).hexdigest()

        return f"{table_id}:{operation}:{key_hash}"

    def get_records_cache_key(
        self,
        table_id: str,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> str:
        """Generate cache key for get_records operation."""  # nosec - false positive
        return self._make_cache_key(
            table_id=table_id,
            operation="get_records",
            sort=sort,
            where=where,
            fields=fields,
            limit=limit,
            offset=offset,
        )

    def get_record_cache_key(
        self, table_id: str, record_id: int | str, fields: list[str] | None = None
    ) -> str:
        """Generate cache key for get_record operation."""  # nosec - false positive
        return self._make_cache_key(
            table_id=table_id, operation="get_record", record_id=str(record_id), fields=fields
        )

    def count_records_cache_key(self, table_id: str, where: str | None = None) -> str:
        """Generate cache key for count_records operation."""  # nosec - false positive
        return self._make_cache_key(table_id=table_id, operation="count_records", where=where)

    def get(self, key: str) -> Any | None:
        """Get value from cache."""  # nosec - false positive
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        cache_ttl = ttl if ttl is not None else self.default_ttl
        self.backend.set(key, value, cache_ttl)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.backend.delete(key)

    def clear(self) -> None:
        """Clear all cached values."""
        self.backend.clear()

    def invalidate_table_cache(self, table_id: str) -> None:
        """Invalidate all cached data for a specific table."""
        # For simple backends, we can't easily delete by pattern
        # So we'll clear the entire cache
        # TODO: Implement pattern-based deletion for supporting backends
        self.clear()


def cached_method(
    cache_manager: CacheManager,
    ttl: int | None = None,
    cache_key_func: Callable[..., str] | None = None,
) -> Callable[..., Any]:
    """Decorator for caching method results."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(self, *args, **kwargs)
            else:
                # Default key generation
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call original method
            result = func(self, *args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def create_cache_manager(backend_type: str = "memory", **backend_kwargs: Any) -> CacheManager:
    """Factory function to create cache manager with specified backend.

    Args:
        backend_type: Type of cache backend ('memory', 'disk', 'redis')
        **backend_kwargs: Arguments for the specific backend

    Returns:
        CacheManager instance
    """
    backend: CacheBackend
    if backend_type == "memory":
        backend = MemoryCache(**backend_kwargs)
    elif backend_type == "disk":
        backend = DiskCache(**backend_kwargs)
    elif backend_type == "redis":
        backend = RedisCache(**backend_kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")

    return CacheManager(backend)


class CacheStats:
    """Cache statistics tracker."""

    def __init__(self) -> None:
        """Initialize cache statistics tracker."""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def record_set(self) -> None:
        """Record a cache set operation."""
        self.sets += 1

    def record_delete(self) -> None:
        """Record a cache delete operation."""
        self.deletes += 1

    def reset(self) -> None:
        """Reset all statistics."""
        self.hits = self.misses = self.sets = self.deletes = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": self.hit_rate,
            "total_requests": self.hits + self.misses,
        }
