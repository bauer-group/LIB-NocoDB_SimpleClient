"""Tests for NocoDBTable class based on actual implementation."""

from unittest.mock import Mock
import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.table import NocoDBTable


class TestNocoDBTable:
    """Test NocoDBTable functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        client = Mock(spec=NocoDBClient)
        return client

    @pytest.fixture
    def table(self, mock_client):
        """Create table instance."""
        return NocoDBTable(mock_client, "test_table_123")

    def test_table_initialization(self, mock_client):
        """Test table initialization."""
        table = NocoDBTable(mock_client, "test_table_123")

        assert table.client == mock_client
        assert table.table_id == "test_table_123"

    def test_get_records(self, table, mock_client):
        """Test get_records delegation to client."""
        expected_records = [{"Id": "1", "Name": "Test"}]
        mock_client.get_records.return_value = expected_records

        result = table.get_records(limit=10, where="(Status,eq,active)")

        assert result == expected_records
        mock_client.get_records.assert_called_once_with(
            "test_table_123", None, "(Status,eq,active)", None, 10
        )

    def test_get_record(self, table, mock_client):
        """Test get_record delegation to client."""
        expected_record = {"Id": "record_123", "Name": "Test Record"}
        mock_client.get_record.return_value = expected_record

        result = table.get_record("record_123")

        assert result == expected_record
        mock_client.get_record.assert_called_once_with("test_table_123", "record_123", None)

    def test_insert_record(self, table, mock_client):
        """Test insert_record delegation to client."""
        record_data = {"Name": "New Record", "Status": "active"}
        mock_client.insert_record.return_value = "new_record_123"

        result = table.insert_record(record_data)

        assert result == "new_record_123"
        mock_client.insert_record.assert_called_once_with("test_table_123", record_data)

    def test_update_record(self, table, mock_client):
        """Test update_record delegation to client."""
        update_data = {"Name": "Updated Record"}
        mock_client.update_record.return_value = "record_123"

        result = table.update_record(update_data, "record_123")

        assert result == "record_123"
        mock_client.update_record.assert_called_once_with(
            "test_table_123", update_data, "record_123"
        )

    def test_delete_record(self, table, mock_client):
        """Test delete_record delegation to client."""
        mock_client.delete_record.return_value = "record_123"

        result = table.delete_record("record_123")

        assert result == "record_123"
        mock_client.delete_record.assert_called_once_with("test_table_123", "record_123")

    def test_count_records(self, table, mock_client):
        """Test count_records delegation to client."""
        mock_client.count_records.return_value = 42

        result = table.count_records(where="(Status,eq,active)")

        assert result == 42
        mock_client.count_records.assert_called_once_with(
            "test_table_123", "(Status,eq,active)"
        )

    def test_bulk_insert_records(self, table, mock_client):
        """Test bulk_insert_records delegation to client."""
        records = [{"Name": "Record 1"}, {"Name": "Record 2"}]
        mock_client.bulk_insert_records.return_value = ["rec1", "rec2"]

        result = table.bulk_insert_records(records)

        assert result == ["rec1", "rec2"]
        mock_client.bulk_insert_records.assert_called_once_with("test_table_123", records)

    def test_bulk_update_records(self, table, mock_client):
        """Test bulk_update_records delegation to client."""
        records = [{"Id": "rec1", "Name": "Updated 1"}]
        mock_client.bulk_update_records.return_value = ["rec1"]

        result = table.bulk_update_records(records)

        assert result == ["rec1"]
        mock_client.bulk_update_records.assert_called_once_with("test_table_123", records)

    def test_bulk_delete_records(self, table, mock_client):
        """Test bulk_delete_records delegation to client."""
        record_ids = ["rec1", "rec2", "rec3"]
        mock_client.bulk_delete_records.return_value = ["rec1", "rec2", "rec3"]

        result = table.bulk_delete_records(record_ids)

        assert result == ["rec1", "rec2", "rec3"]
        mock_client.bulk_delete_records.assert_called_once_with("test_table_123", record_ids)

    def test_attach_file_to_record(self, table, mock_client):
        """Test file attachment delegation to client."""
        mock_client.attach_file_to_record.return_value = "record_123"

        result = table.attach_file_to_record("record_123", "Documents", "/path/to/test.txt")

        assert result == "record_123"
        mock_client.attach_file_to_record.assert_called_once_with(
            "test_table_123", "record_123", "Documents", "/path/to/test.txt"
        )

    def test_download_file_from_record(self, table, mock_client):
        """Test file download delegation to client."""
        expected_content = b"test file content"
        mock_client.download_file_from_record.return_value = expected_content

        result = table.download_file_from_record("record_123", "Documents", 0)

        assert result == expected_content
        mock_client.download_file_from_record.assert_called_once_with(
            "test_table_123", "record_123", "Documents", 0
        )
