"""Tests for bulk operations functionality."""

from unittest.mock import Mock, patch

import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.exceptions import NocoDBException, ValidationException
from nocodb_simple_client.table import NocoDBTable


class TestBulkOperations:
    """Test bulk operations for records."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def table(self, mock_client):
        """Create a table instance for testing."""
        return NocoDBTable(mock_client, "test_table_id")

    def test_bulk_insert_records_success(self, mock_client, table):
        """Test successful bulk insert operation."""
        # Arrange
        test_records = [
            {"Name": "Record 1", "Value": 100},
            {"Name": "Record 2", "Value": 200},
            {"Name": "Record 3", "Value": 300},
        ]
        expected_ids = ["id1", "id2", "id3"]
        mock_client.bulk_insert_records.return_value = expected_ids

        # Act
        result = table.bulk_insert_records(test_records)

        # Assert
        assert result == expected_ids
        mock_client.bulk_insert_records.assert_called_once_with("test_table_id", test_records)

    def test_bulk_insert_records_empty_list(self, mock_client, table):
        """Test bulk insert with empty list."""
        # Arrange
        test_records = []
        mock_client.bulk_insert_records.return_value = []

        # Act
        result = table.bulk_insert_records(test_records)

        # Assert
        assert result == []
        mock_client.bulk_insert_records.assert_called_once_with("test_table_id", test_records)

    def test_bulk_update_records_success(self, mock_client, table):
        """Test successful bulk update operation."""
        # Arrange
        test_records = [
            {"Id": "id1", "Name": "Updated Record 1", "Value": 150},
            {"Id": "id2", "Name": "Updated Record 2", "Value": 250},
            {"Id": "id3", "Name": "Updated Record 3", "Value": 350},
        ]
        expected_ids = ["id1", "id2", "id3"]
        mock_client.bulk_update_records.return_value = expected_ids

        # Act
        result = table.bulk_update_records(test_records)

        # Assert
        assert result == expected_ids
        mock_client.bulk_update_records.assert_called_once_with("test_table_id", test_records)

    def test_bulk_update_records_missing_ids(self, mock_client, table):
        """Test bulk update with records missing IDs."""
        # Arrange
        test_records = [{"Name": "Record without ID", "Value": 100}]
        mock_client.bulk_update_records.side_effect = ValidationException(
            "Record must include Id for bulk update"
        )

        # Act & Assert
        with pytest.raises(ValidationException, match="Record must include Id"):
            table.bulk_update_records(test_records)

    def test_bulk_delete_records_success(self, mock_client, table):
        """Test successful bulk delete operation."""
        # Arrange
        test_ids = ["id1", "id2", "id3"]
        mock_client.bulk_delete_records.return_value = test_ids

        # Act
        result = table.bulk_delete_records(test_ids)

        # Assert
        assert result == test_ids
        mock_client.bulk_delete_records.assert_called_once_with("test_table_id", test_ids)

    def test_bulk_delete_records_empty_list(self, mock_client, table):
        """Test bulk delete with empty list."""
        # Arrange
        test_ids = []
        mock_client.bulk_delete_records.return_value = []

        # Act
        result = table.bulk_delete_records(test_ids)

        # Assert
        assert result == []
        mock_client.bulk_delete_records.assert_called_once_with("test_table_id", test_ids)


class TestClientBulkOperations:
    """Test bulk operations at client level."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return NocoDBClient(base_url="http://test.com", db_auth_token="test_token")

    @patch("nocodb_simple_client.client.requests.post")
    def test_client_bulk_insert_success(self, mock_post, client):
        """Test client bulk insert operation."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Id": "id1"}, {"Id": "id2"}, {"Id": "id3"}]
        mock_post.return_value = mock_response

        test_records = [{"Name": "Record 1"}, {"Name": "Record 2"}, {"Name": "Record 3"}]

        # Act
        result = client.bulk_insert_records("test_table", test_records)

        # Assert
        assert result == ["id1", "id2", "id3"]
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "api/v2/tables/test_table/records" in call_args[0][0]
        assert call_args[1]["json"] == test_records

    @patch("nocodb_simple_client.client.requests.patch")
    def test_client_bulk_update_success(self, mock_patch, client):
        """Test client bulk update operation."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Id": "id1"}, {"Id": "id2"}, {"Id": "id3"}]
        mock_patch.return_value = mock_response

        test_records = [
            {"Id": "id1", "Name": "Updated Record 1"},
            {"Id": "id2", "Name": "Updated Record 2"},
            {"Id": "id3", "Name": "Updated Record 3"},
        ]

        # Act
        result = client.bulk_update_records("test_table", test_records)

        # Assert
        assert result == ["id1", "id2", "id3"]
        mock_patch.assert_called_once()
        call_args = mock_patch.call_args
        assert "api/v2/tables/test_table/records" in call_args[0][0]
        assert call_args[1]["json"] == test_records

    @patch("nocodb_simple_client.client.requests.delete")
    def test_client_bulk_delete_success(self, mock_delete, client):
        """Test client bulk delete operation."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Id": "id1"}, {"Id": "id2"}, {"Id": "id3"}]
        mock_delete.return_value = mock_response

        test_ids = ["id1", "id2", "id3"]

        # Act
        result = client.bulk_delete_records("test_table", test_ids)

        # Assert
        assert result == ["id1", "id2", "id3"]
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args
        assert "api/v2/tables/test_table/records" in call_args[0][0]
        expected_data = [{"Id": "id1"}, {"Id": "id2"}, {"Id": "id3"}]
        assert call_args[1]["json"] == expected_data

    @patch("nocodb_simple_client.client.requests.post")
    def test_client_bulk_insert_api_error(self, mock_post, client):
        """Test client bulk insert with API error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid data"}
        mock_post.return_value = mock_response

        test_records = [{"Name": "Test"}]

        # Act & Assert
        with pytest.raises(NocoDBException, match="Invalid data"):
            client.bulk_insert_records("test_table", test_records)

    @patch("nocodb_simple_client.client.requests.patch")
    def test_client_bulk_update_validation_error(self, mock_patch, client):
        """Test client bulk update with validation error."""
        # Arrange
        test_records = [{"Name": "Missing ID"}]  # Missing required Id field

        # Act & Assert
        with pytest.raises(ValidationException, match="Record must include 'Id'"):
            client.bulk_update_records("test_table", test_records)

    def test_bulk_operations_large_dataset(self, client):
        """Test bulk operations with large dataset to verify batching."""
        # This test would verify that large datasets are properly batched
        # In a real implementation, you might want to test batching logic
        pass


class TestBulkOperationsBatching:
    """Test batching functionality for bulk operations."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return NocoDBClient(base_url="http://test.com", db_auth_token="test_token")

    @patch("nocodb_simple_client.client.requests.post")
    def test_bulk_insert_batching(self, mock_post, client):
        """Test that bulk insert properly handles batching for large datasets."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Id": f"id{i}"} for i in range(100)]
        mock_post.return_value = mock_response

        # Create a large dataset that would require batching
        large_dataset = [{"Name": f"Record {i}"} for i in range(250)]

        # Act
        result = client.bulk_insert_records("test_table", large_dataset)

        # Assert
        # Should make multiple calls due to batching
        assert mock_post.call_count >= 2  # At least 2 batches for 250 records
        assert len(result) == 250  # All records should be processed


class TestTableBulkOperationsIntegration:
    """Integration tests for table-level bulk operations."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def table(self, mock_client):
        """Create a table instance."""
        return NocoDBTable(mock_client, "integration_test_table")

    def test_table_bulk_workflow(self, mock_client, table):
        """Test complete bulk workflow: insert, update, delete."""
        # Arrange
        insert_records = [{"Name": "Test 1", "Value": 100}, {"Name": "Test 2", "Value": 200}]
        insert_ids = ["new_id1", "new_id2"]

        update_records = [
            {"Id": "new_id1", "Name": "Updated Test 1", "Value": 150},
            {"Id": "new_id2", "Name": "Updated Test 2", "Value": 250},
        ]
        update_ids = ["new_id1", "new_id2"]

        delete_ids = ["new_id1", "new_id2"]

        mock_client.bulk_insert_records.return_value = insert_ids
        mock_client.bulk_update_records.return_value = update_ids
        mock_client.bulk_delete_records.return_value = delete_ids

        # Act
        inserted_ids = table.bulk_insert_records(insert_records)
        updated_ids = table.bulk_update_records(update_records)
        deleted_ids = table.bulk_delete_records(delete_ids)

        # Assert
        assert inserted_ids == insert_ids
        assert updated_ids == update_ids
        assert deleted_ids == delete_ids

        mock_client.bulk_insert_records.assert_called_once_with(
            "integration_test_table", insert_records
        )
        mock_client.bulk_update_records.assert_called_once_with(
            "integration_test_table", update_records
        )
        mock_client.bulk_delete_records.assert_called_once_with(
            "integration_test_table", delete_ids
        )


if __name__ == "__main__":
    pytest.main([__file__])
