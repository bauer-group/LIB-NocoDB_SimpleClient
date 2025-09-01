"""
Integration tests for bulk operations functionality with real NocoDB instance.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.exceptions import NocoDBError
from nocodb_simple_client.table import NocoDBTable


@pytest.mark.integration
class TestBulkInsertIntegration:
    """Test bulk insert operations with real NocoDB instance."""

    def test_bulk_insert_single_batch(self, nocodb_client, test_table, test_data_manager):
        """Test bulk insert with single batch."""
        table_id = test_table["id"]

        test_records = [
            {"name": "John Doe", "email": "john@example.com", "age": 30, "status": "active"},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25, "status": "active"},
        ]

        # Execute bulk insert
        result = nocodb_client.bulk_insert_records(table_id, test_records)

        # Verify response
        assert isinstance(result, list)
        assert len(result) == 2

        # Check that records were created with IDs
        for i, record in enumerate(result):
            assert "id" in record
            assert record["name"] == test_records[i]["name"]
            assert record["email"] == test_records[i]["email"]

        # Track for cleanup
        for record in result:
            test_data_manager.created_records.append(record)

    def test_bulk_insert_multiple_batches(
        self, nocodb_client, test_table, test_data_manager, test_config
    ):
        """Test bulk insert with multiple batches."""
        table_id = test_table["id"]
        batch_size = test_config.bulk_batch_size

        # Create more records than batch size to test batching
        test_records = []
        for i in range(batch_size + 10):  # Exceed batch size
            test_records.append(
                {
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 40),
                    "status": "active",
                }
            )

        # Execute bulk insert
        result = nocodb_client.bulk_insert_records(table_id, test_records)

        # Verify all records were created
        assert isinstance(result, list)
        assert len(result) == len(test_records)

        # Verify each record has an ID and correct data
        for i, record in enumerate(result):
            assert "id" in record
            assert record["name"] == f"User {i}"
            assert record["email"] == f"user{i}@example.com"

        # Track for cleanup
        for record in result:
            test_data_manager.created_records.append(record)

    def test_bulk_insert_empty_list(self, nocodb_client, test_table):
        """Test bulk insert with empty list."""
        table_id = test_table["id"]

        result = nocodb_client.bulk_insert_records(table_id, [])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_bulk_insert_validation_error(self, nocodb_client, test_table):
        """Test bulk insert with invalid data."""
        table_id = test_table["id"]

        # Invalid records (missing required fields or wrong data types)
        invalid_records = [
            {"name": "Valid User", "email": "valid@example.com"},
            {"name": "", "email": "invalid-email"},  # Invalid email
            {"name": "Another User", "age": "not-a-number"},  # Invalid age
        ]

        # This should either succeed (NocoDB handles validation) or raise an error
        try:
            result = nocodb_client.bulk_insert_records(table_id, invalid_records)
            # If it succeeds, verify the valid records were created
            assert isinstance(result, list)
        except NocoDBError:
            # If it fails, that's also acceptable for invalid data
            pass


@pytest.mark.integration
class TestBulkUpdateIntegration:
    """Test bulk update operations with real NocoDB instance."""

    def test_bulk_update_records(self, nocodb_client, test_table_with_data, test_data_manager):
        """Test bulk update of existing records."""
        table_id = test_table_with_data["id"]
        sample_records = test_table_with_data["sample_records"]

        # Prepare update data
        update_records = []
        for record in sample_records[:2]:  # Update first 2 records
            update_records.append(
                {"id": record["id"], "status": "inactive", "notes": f"Updated: {record['notes']}"}
            )

        # Execute bulk update
        result = nocodb_client.bulk_update_records(table_id, update_records)

        # Verify updates
        assert isinstance(result, list)
        assert len(result) == 2

        # Check updated fields
        for i, updated_record in enumerate(result):
            assert updated_record["id"] == update_records[i]["id"]
            assert updated_record["status"] == "inactive"
            assert "Updated:" in updated_record["notes"]

    def test_bulk_update_nonexistent_records(self, nocodb_client, test_table):
        """Test bulk update with non-existent record IDs."""
        table_id = test_table["id"]

        update_records = [
            {"id": 99999, "name": "Non-existent User"},
            {"id": 99998, "name": "Another Non-existent User"},
        ]

        # This should either handle gracefully or raise an appropriate error
        try:
            result = nocodb_client.bulk_update_records(table_id, update_records)
            # If successful, result might be empty or contain error information
            assert isinstance(result, list)
        except NocoDBError as e:
            # Expected behavior for non-existent records
            assert "404" in str(e) or "not found" in str(e).lower()


@pytest.mark.integration
class TestBulkDeleteIntegration:
    """Test bulk delete operations with real NocoDB instance."""

    def test_bulk_delete_records(self, nocodb_client, test_table_with_data):
        """Test bulk delete of existing records."""
        table_id = test_table_with_data["id"]
        sample_records = test_table_with_data["sample_records"]

        # Get record IDs to delete (delete first 2 records)
        record_ids = [record["id"] for record in sample_records[:2]]

        # Execute bulk delete
        result = nocodb_client.bulk_delete_records(table_id, record_ids)

        # Verify deletion result
        assert isinstance(result, list | dict)

        # Verify records were actually deleted by trying to fetch them
        for record_id in record_ids:
            try:
                nocodb_client.get_record(table_id, record_id)
                # If we can still fetch it, it wasn't deleted
                pytest.fail(f"Record {record_id} was not deleted")
            except NocoDBError:
                # Expected - record should not be found
                pass

    def test_bulk_delete_nonexistent_records(self, nocodb_client, test_table):
        """Test bulk delete with non-existent record IDs."""
        table_id = test_table["id"]

        non_existent_ids = [99999, 99998, 99997]

        # This should either handle gracefully or raise an appropriate error
        try:
            result = nocodb_client.bulk_delete_records(table_id, non_existent_ids)
            assert isinstance(result, list | dict)
        except NocoDBError:
            # Expected behavior for non-existent records
            pass

    def test_bulk_delete_empty_list(self, nocodb_client, test_table):
        """Test bulk delete with empty list."""
        table_id = test_table["id"]

        result = nocodb_client.bulk_delete_records(table_id, [])

        # Should handle empty list gracefully
        assert isinstance(result, list | dict)


@pytest.mark.integration
@pytest.mark.slow
class TestBulkOperationsPerformance:
    """Test performance characteristics of bulk operations."""

    @pytest.mark.performance
    def test_large_bulk_insert_performance(
        self, nocodb_client, test_table, test_data_manager, test_config, skip_if_slow
    ):
        """Test performance of large bulk insert operations."""
        table_id = test_table["id"]
        record_count = test_config.performance_records

        # Generate large dataset
        large_dataset = []
        for i in range(record_count):
            large_dataset.append(
                {
                    "name": f"Performance User {i}",
                    "email": f"perf_user_{i}@example.com",
                    "age": 20 + (i % 50),
                    "status": "active",
                    "notes": f"Performance test record {i}",
                }
            )

        # Measure bulk insert performance
        start_time = time.time()
        result = nocodb_client.bulk_insert_records(table_id, large_dataset)
        end_time = time.time()

        # Verify all records were created
        assert len(result) == record_count

        # Performance assertions
        duration = end_time - start_time
        records_per_second = record_count / duration

        print(f"Bulk insert performance: {records_per_second:.2f} records/second")
        print(f"Total time for {record_count} records: {duration:.2f} seconds")

        # Performance should be reasonable (adjust threshold as needed)
        assert records_per_second > 10, f"Performance too slow: {records_per_second} records/second"

        # Track for cleanup
        for record in result:
            test_data_manager.created_records.append(record)

    @pytest.mark.performance
    def test_bulk_vs_individual_insert_performance(
        self, nocodb_client, test_table, test_data_manager, skip_if_slow
    ):
        """Compare bulk insert vs individual insert performance."""
        table_id = test_table["id"]
        test_count = 50  # Small test for comparison

        # Test data
        test_records = []
        for i in range(test_count):
            test_records.append(
                {
                    "name": f"Comparison User {i}",
                    "email": f"comp_user_{i}@example.com",
                    "age": 25,
                    "status": "active",
                }
            )

        # Test individual inserts
        start_time = time.time()
        individual_results = []
        for record in test_records:
            result = nocodb_client.create_record(table_id, record)
            individual_results.append(result)
        individual_time = time.time() - start_time

        # Test bulk insert
        start_time = time.time()
        bulk_results = nocodb_client.bulk_insert_records(table_id, test_records)
        bulk_time = time.time() - start_time

        # Verify results
        assert len(individual_results) == test_count
        assert len(bulk_results) == test_count

        # Performance comparison
        individual_rate = test_count / individual_time
        bulk_rate = test_count / bulk_time

        print(f"Individual insert rate: {individual_rate:.2f} records/second")
        print(f"Bulk insert rate: {bulk_rate:.2f} records/second")
        print(f"Bulk is {bulk_rate / individual_rate:.2f}x faster")

        # Bulk should be significantly faster
        assert bulk_rate > individual_rate, "Bulk insert should be faster than individual inserts"

        # Track all for cleanup
        for record in individual_results + bulk_results:
            test_data_manager.created_records.append(record)


@pytest.mark.integration
class TestBulkOperationsErrorHandling:
    """Test error handling in bulk operations."""

    def test_bulk_insert_network_error(self, nocodb_client, test_table, monkeypatch):
        """Test handling of network errors during bulk insert."""
        table_id = test_table["id"]

        test_records = [{"name": "Test User", "email": "test@example.com"}]

        # Mock a network error
        def mock_request_error(*args, **kwargs):
            raise ConnectionError("Network connection failed")

        monkeypatch.setattr(nocodb_client, "_make_request", mock_request_error)

        with pytest.raises((NocoDBError, ConnectionError)):
            nocodb_client.bulk_insert_records(table_id, test_records)

    def test_bulk_operations_with_invalid_table_id(self, nocodb_client):
        """Test bulk operations with invalid table ID."""
        invalid_table_id = "invalid_table_id"

        test_records = [{"name": "Test User", "email": "test@example.com"}]

        with pytest.raises(NocoDBError):
            nocodb_client.bulk_insert_records(invalid_table_id, test_records)

    def test_bulk_operations_with_large_payload(
        self, nocodb_client, test_table, test_data_manager, skip_if_slow
    ):
        """Test bulk operations with very large payloads."""
        table_id = test_table["id"]

        # Create records with large text content
        large_text = "x" * 10000  # 10KB of text per record
        large_records = []
        for i in range(10):
            large_records.append(
                {
                    "name": f"Large Content User {i}",
                    "email": f"large_{i}@example.com",
                    "notes": large_text,
                }
            )

        # This should either succeed or fail gracefully
        try:
            result = nocodb_client.bulk_insert_records(table_id, large_records)
            assert len(result) == 10

            # Track for cleanup
            for record in result:
                test_data_manager.created_records.append(record)

        except NocoDBError as e:
            # Acceptable if payload is too large
            assert "payload" in str(e).lower() or "size" in str(e).lower()


@pytest.mark.integration
class TestBulkOperationsWithTable:
    """Test bulk operations using NocoDBTable wrapper."""

    def test_table_bulk_insert(self, nocodb_client, test_table, test_data_manager):
        """Test bulk insert using NocoDBTable instance."""
        table = NocoDBTable(nocodb_client, test_table["id"])

        test_records = [
            {"name": "Table User 1", "email": "table1@example.com", "age": 30},
            {"name": "Table User 2", "email": "table2@example.com", "age": 25},
        ]

        # Execute bulk insert through table wrapper
        result = table.bulk_insert_records(test_records)

        # Verify response
        assert isinstance(result, list)
        assert len(result) == 2

        # Track for cleanup
        for record in result:
            test_data_manager.created_records.append(record)

    def test_table_bulk_update(self, nocodb_client, test_table_with_data):
        """Test bulk update using NocoDBTable instance."""
        table = NocoDBTable(nocodb_client, test_table_with_data["id"])
        sample_records = test_table_with_data["sample_records"]

        # Prepare updates
        updates = []
        for record in sample_records[:2]:
            updates.append({"id": record["id"], "status": "inactive"})

        # Execute bulk update
        result = table.bulk_update_records(updates)

        # Verify updates
        assert isinstance(result, list)
        assert len(result) == 2

    def test_table_bulk_delete(self, nocodb_client, test_table_with_data):
        """Test bulk delete using NocoDBTable instance."""
        table = NocoDBTable(nocodb_client, test_table_with_data["id"])
        sample_records = test_table_with_data["sample_records"]

        # Get IDs to delete
        record_ids = [record["id"] for record in sample_records[:2]]

        # Execute bulk delete
        result = table.bulk_delete_records(record_ids)

        # Verify deletion
        assert isinstance(result, list | dict)
