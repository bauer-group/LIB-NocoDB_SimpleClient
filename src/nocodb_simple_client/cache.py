"""Caching layer for NocoDB Simple Client."""

import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from functools import wraps

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
    redis = None


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
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
        """Check if key exists in cache."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, tuple] = {}  # key: (value, expiry_time)
        self.max_size = max_size
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items()
            if expiry and expiry < current_time
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        if len(self.cache) >= self.max_size:
            # Simple LRU eviction - remove oldest entries
            keys_to_remove = list(self.cache.keys())[:(len(self.cache) - self.max_size + 1)]
            for key in keys_to_remove:
                del self.cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        self._cleanup_expired()
        
        if key in self.cache:
            value, expiry = self.cache[key]
            if not expiry or expiry > time.time():
                return value
            else:
                del self.cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
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
        """Check if key exists in cache."""
        return self.get(key) is not None


class DiskCache(CacheBackend):
    """Disk-based cache implementation using diskcache."""
    
    def __init__(self, directory: str = "./cache", size_limit: int = 100_000_000):
        if not DISKCACHE_AVAILABLE:
            raise ImportError(
                "DiskCache requires diskcache. Install with: pip install 'nocodb-simple-client[caching]'"
            )
        
        self.cache = dc.Cache(directory, size_limit=size_limit)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
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
        """Check if key exists in cache."""
        return key in self.cache


class RedisCache(CacheBackend):
    """Redis-based cache implementation."""
    
    def __init__(
        self, 
        host: str = 'localhost', 
        port: int = 6379, 
        db: int = 0, 
        password: Optional[str] = None,
        key_prefix: str = 'nocodb:'
    ):
        if not REDIS_AVAILABLE:
            raise ImportError(
                "RedisCache requires redis. Install with: pip install 'nocodb-simple-client[caching]'"
            )
        
        self.client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
            decode_responses=False  # We'll handle encoding/decoding
        )
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.client.get(self._make_key(key))
            if data:
                return pickle.loads(data)
        except (redis.RedisError, pickle.PickleError):
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        try:
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
        """Check if key exists in cache."""
        try:
            return bool(self.client.exists(self._make_key(key)))
        except redis.RedisError:
            return False


class CacheManager:
    """Cache manager for handling different cache backends."""
    
    def __init__(self, backend: CacheBackend, default_ttl: Optional[int] = 300):
        self.backend = backend
        self.default_ttl = default_ttl
    
    def _make_cache_key(
        self, 
        table_id: str, 
        operation: str, 
        **kwargs
    ) -> str:
        """Generate cache key from parameters."""
        # Create a deterministic hash of the parameters
        key_data = {
            'table_id': table_id,
            'operation': operation,
            **kwargs
        }
        
        # Sort keys for consistency
        sorted_data = json.dumps(key_data, sort_keys=True, default=str)
        
        # Create hash
        key_hash = hashlib.md5(sorted_data.encode()).hexdigest()
        
        return f"{table_id}:{operation}:{key_hash}"
    
    def get_records_cache_key(
        self, 
        table_id: str, 
        sort: Optional[str] = None,
        where: Optional[str] = None,
        fields: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> str:
        """Generate cache key for get_records operation."""
        return self._make_cache_key(
            table_id=table_id,
            operation='get_records',
            sort=sort,
            where=where,
            fields=fields,
            limit=limit,
            offset=offset
        )
    
    def get_record_cache_key(
        self, 
        table_id: str, 
        record_id: Union[int, str],
        fields: Optional[List[str]] = None
    ) -> str:
        """Generate cache key for get_record operation."""
        return self._make_cache_key(
            table_id=table_id,
            operation='get_record',
            record_id=str(record_id),
            fields=fields
        )
    
    def count_records_cache_key(
        self, 
        table_id: str, 
        where: Optional[str] = None
    ) -> str:
        """Generate cache key for count_records operation."""
        return self._make_cache_key(
            table_id=table_id,
            operation='count_records',
            where=where
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.backend.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
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
    ttl: Optional[int] = None,
    cache_key_func: Optional[callable] = None
):
    """Decorator for caching method results."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
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


def create_cache_manager(
    backend_type: str = 'memory',
    **backend_kwargs
) -> CacheManager:
    """Factory function to create cache manager with specified backend.
    
    Args:
        backend_type: Type of cache backend ('memory', 'disk', 'redis')
        **backend_kwargs: Arguments for the specific backend
        
    Returns:
        CacheManager instance
    """
    if backend_type == 'memory':
        backend = MemoryCache(**backend_kwargs)
    elif backend_type == 'disk':
        backend = DiskCache(**backend_kwargs)
    elif backend_type == 'redis':
        backend = RedisCache(**backend_kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
    
    return CacheManager(backend)


class CacheStats:
    """Cache statistics tracker."""
    
    def __init__(self):
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'hit_rate': self.hit_rate,
            'total_requests': self.hits + self.misses
        }