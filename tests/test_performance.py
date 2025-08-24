"""Performance tests for NocoDB Simple Client."""

import pytest
import time
import statistics
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from nocodb_simple_client import NocoDBClient, NocoDBTable
from nocodb_simple_client.config import NocoDBConfig
from nocodb_simple_client.cache import CacheManager, MemoryCache


class TestPerformance:
    """Performance test suite."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for performance testing."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token"
        )
        client = NocoDBClient(config)
        return client
    
    @pytest.fixture
    def mock_table(self, mock_client):
        """Create a mock table for performance testing."""
        return NocoDBTable(mock_client, "test_table")
    
    @pytest.mark.benchmark
    def test_client_initialization_performance(self, benchmark):
        """Test client initialization performance."""
        
        def create_client():
            config = NocoDBConfig(
                base_url="https://test.nocodb.com",
                api_token="test-token"
            )
            return NocoDBClient(config)
        
        result = benchmark(create_client)
        assert result is not None
    
    @pytest.mark.benchmark
    def test_session_reuse_performance(self):
        """Test performance benefits of session reuse."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token"
        )
        
        # Test without session reuse (new client each time)
        times_without_reuse = []
        for _ in range(10):
            start_time = time.time()
            client = NocoDBClient(config)
            client.close()
            times_without_reuse.append(time.time() - start_time)
        
        # Test with session reuse
        times_with_reuse = []
        with NocoDBClient(config) as client:
            for _ in range(10):
                start_time = time.time()
                # Simulate some operation (just accessing the session)
                _ = client._session
                times_with_reuse.append(time.time() - start_time)
        
        avg_without_reuse = statistics.mean(times_without_reuse)
        avg_with_reuse = statistics.mean(times_with_reuse)
        
        # Session reuse should be faster
        assert avg_with_reuse < avg_without_reuse
    
    @pytest.mark.benchmark
    @patch('requests.Session.get')
    def test_get_records_performance(self, mock_get, benchmark):
        """Test get_records performance."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'list': [{'Id': i, 'Name': f'Record {i}'} for i in range(100)],
            'pageInfo': {'isLastPage': True}
        }
        mock_get.return_value = mock_response
        
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token"
        )
        
        def get_records():
            with NocoDBClient(config) as client:
                table = NocoDBTable(client, "test_table")
                return table.get_records(limit=100)
        
        result = benchmark(get_records)
        assert len(result) == 100
    
    @pytest.mark.benchmark
    def test_cache_performance(self):
        """Test caching performance benefits."""
        cache_manager = CacheManager(MemoryCache(), default_ttl=300)
        
        # Test cache write performance
        write_times = []
        for i in range(1000):
            start_time = time.time()
            cache_manager.set(f"key_{i}", {"data": f"value_{i}"})
            write_times.append(time.time() - start_time)
        
        # Test cache read performance
        read_times = []
        for i in range(1000):
            start_time = time.time()
            cache_manager.get(f"key_{i}")
            read_times.append(time.time() - start_time)
        
        avg_write_time = statistics.mean(write_times)
        avg_read_time = statistics.mean(read_times)
        
        # Reads should be faster than writes
        assert avg_read_time < avg_write_time
        
        # Operations should be fast (less than 1ms on average)
        assert avg_write_time < 0.001
        assert avg_read_time < 0.001
    
    @pytest.mark.benchmark
    @patch('requests.Session.get')
    def test_cached_vs_uncached_performance(self, mock_get):
        """Compare performance of cached vs uncached requests."""
        # Mock slow response (simulate network delay)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'list': [{'Id': 1, 'Name': 'Test Record'}],
            'pageInfo': {'isLastPage': True}
        }
        
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms network delay
            return mock_response
        
        mock_get.side_effect = slow_response
        
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token"
        )
        
        # Test without caching
        uncached_times = []
        for _ in range(3):
            start_time = time.time()
            with NocoDBClient(config) as client:
                table = NocoDBTable(client, "test_table")
                table.get_records(limit=1)
            uncached_times.append(time.time() - start_time)
        
        # Reset mock
        mock_get.reset_mock()
        mock_get.side_effect = slow_response
        
        # Test with caching (simulation - actual caching would be integrated)
        cache = MemoryCache()
        cached_times = []
        
        # First call (cache miss)
        start_time = time.time()
        key = "test_cache_key"
        result = cache.get(key)
        if result is None:
            # Simulate API call
            time.sleep(0.1)
            result = [{'Id': 1, 'Name': 'Test Record'}]
            cache.set(key, result)
        cached_times.append(time.time() - start_time)
        
        # Subsequent calls (cache hits)
        for _ in range(2):
            start_time = time.time()
            result = cache.get(key)
            cached_times.append(time.time() - start_time)
        
        avg_uncached_time = statistics.mean(uncached_times)
        avg_cached_time = statistics.mean(cached_times[1:])  # Exclude first call (cache miss)
        
        # Cached requests should be significantly faster
        assert avg_cached_time < avg_uncached_time / 10
    
    @pytest.mark.benchmark
    def test_memory_usage_limits(self):
        """Test memory usage stays within reasonable limits."""
        cache = MemoryCache(max_size=100)
        
        # Fill cache beyond limit
        for i in range(200):
            cache.set(f"key_{i}", {"data": "x" * 1000})  # 1KB per entry
        
        # Cache should not exceed max size
        assert len(cache.cache) <= 100
    
    @pytest.mark.benchmark
    def test_validation_performance(self):
        """Test input validation performance."""
        from nocodb_simple_client.validation import (
            validate_table_id,
            validate_record_id,
            validate_record_data,
            validate_where_clause,
            validate_sort_clause,
            validate_limit
        )
        
        # Test validation functions performance
        validation_times = []
        
        test_data = [
            ('table_123', validate_table_id),
            ('record_456', validate_record_id),
            ({'name': 'test', 'value': 123}, validate_record_data),
            ('(name,eq,test)', validate_where_clause),
            ('name,-created_at', validate_sort_clause),
            (100, validate_limit)
        ]
        
        for data, validator in test_data:
            start_time = time.time()
            for _ in range(1000):
                validator(data)
            validation_times.append(time.time() - start_time)
        
        # Validation should be fast
        max_time_per_1000_ops = 0.01  # 10ms for 1000 operations
        for validation_time in validation_times:
            assert validation_time < max_time_per_1000_ops
    
    @pytest.mark.benchmark
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        # Simulate large record set
        large_records = [
            {'Id': i, 'name': f'Record {i}', 'data': 'x' * 100}
            for i in range(10000)
        ]
        
        start_time = time.time()
        
        # Test JSON serialization/deserialization (common in API operations)
        import json
        serialized = json.dumps(large_records)
        deserialized = json.loads(serialized)
        
        processing_time = time.time() - start_time
        
        # Should handle 10k records in reasonable time (less than 1 second)
        assert processing_time < 1.0
        assert len(deserialized) == 10000
    
    @pytest.mark.benchmark
    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access."""
        import threading
        import queue
        
        cache = MemoryCache(max_size=1000)
        results = queue.Queue()
        
        def cache_worker(worker_id: int, num_operations: int):
            """Worker function for cache operations."""
            times = []
            for i in range(num_operations):
                start_time = time.time()
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                
                cache.set(key, value)
                retrieved = cache.get(key)
                
                times.append(time.time() - start_time)
                assert retrieved == value
            
            results.put(times)
        
        # Run multiple workers concurrently
        num_workers = 4
        operations_per_worker = 100
        threads = []
        
        start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=cache_worker,
                args=(worker_id, operations_per_worker)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all workers to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect all timing results
        all_times = []
        while not results.empty():
            worker_times = results.get()
            all_times.extend(worker_times)
        
        avg_operation_time = statistics.mean(all_times)
        
        # Operations should still be fast under concurrent access
        assert avg_operation_time < 0.001  # Less than 1ms per operation
        assert total_time < 2.0  # Total test should complete in under 2 seconds
    
    def test_connection_pool_efficiency(self):
        """Test connection pooling efficiency."""
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token",
            pool_connections=5,
            pool_maxsize=10
        )
        
        # This test would need actual HTTP mocking to be meaningful
        # For now, just verify configuration is applied
        client = NocoDBClient(config)
        assert client.config.pool_connections == 5
        assert client.config.pool_maxsize == 10
        client.close()


@pytest.mark.benchmark(group="api_operations")
class TestAPIPerformance:
    """API operation performance tests."""
    
    @pytest.mark.benchmark
    @patch('requests.Session.get')
    def test_batch_get_records_performance(self, mock_get):
        """Test performance of batch record retrieval."""
        # Mock paginated response
        def mock_paginated_response(url, **kwargs):
            params = kwargs.get('params', {})
            offset = params.get('offset', 0)
            limit = params.get('limit', 25)
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            # Generate records for this page
            records = [
                {'Id': i, 'Name': f'Record {i}'}
                for i in range(offset, min(offset + limit, 1000))
            ]
            
            is_last = offset + limit >= 1000
            
            mock_response.json.return_value = {
                'list': records,
                'pageInfo': {'isLastPage': is_last}
            }
            return mock_response
        
        mock_get.side_effect = mock_paginated_response
        
        config = NocoDBConfig(
            base_url="https://test.nocodb.com",
            api_token="test-token"
        )
        
        def get_large_dataset():
            with NocoDBClient(config) as client:
                table = NocoDBTable(client, "test_table")
                return table.get_records(limit=1000)
        
        start_time = time.time()
        records = get_large_dataset()
        total_time = time.time() - start_time
        
        assert len(records) == 1000
        # Should complete in reasonable time
        assert total_time < 5.0  # 5 seconds max for 1000 records


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])