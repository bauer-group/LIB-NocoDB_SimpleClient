"""Tests for NocoDBTable."""

from unittest.mock import Mock

import pytest

from nocodb_simple_client import NocoDBException, NocoDBTable


class TestNocoDBTable:
    """Test cases for NocoDBTable."""

    def test_table_initialization(self, client):
        """Test table initialization."""
        table = NocoDBTable(client, "test-table-id")

        assert table.client == client
        assert table.table_id == "test-table-id"

    def test_get_records(self, table, sample_records):
        """Test get_records method."""
        table.client.get_records = Mock(return_value=sample_records)

        records = table.get_records(limit=10, sort="-Id")

        assert len(records) == 2
        table.client.get_records.assert_called_once_with("test-table-id", "-Id", None, None, 10)

    def test_get_records_with_parameters(self, table, sample_records):
        """Test get_records with all parameters."""
        table.client.get_records = Mock(return_value=sample_records)

        records = table.get_records(
            sort="-Id", where="(Active,eq,true)", fields=["Id", "Name"], limit=5
        )

        assert records == sample_records
        table.client.get_records.assert_called_once_with(
            "test-table-id", "-Id", "(Active,eq,true)", ["Id", "Name"], 5
        )

    def test_get_record(self, table, sample_record):
        """Test get_record method."""
        table.client.get_record = Mock(return_value=sample_record)

        record = table.get_record(123, fields=["Id", "Name"])

        assert record["Id"] == 1
        table.client.get_record.assert_called_once_with("test-table-id", 123, ["Id", "Name"])

    def test_insert_record(self, table):
        """Test insert_record method."""
        table.client.insert_record = Mock(return_value=123)

        new_record = {"Name": "Test", "Email": "test@example.com"}
        record_id = table.insert_record(new_record)

        assert record_id == 123
        table.client.insert_record.assert_called_once_with("test-table-id", new_record)

    def test_update_record(self, table):
        """Test update_record method."""
        table.client.update_record = Mock(return_value=123)

        update_data = {"Name": "Updated Name"}
        record_id = table.update_record(update_data, 123)

        assert record_id == 123
        table.client.update_record.assert_called_once_with("test-table-id", update_data, 123)

    def test_update_record_without_id(self, table):
        """Test update_record without explicit record_id."""
        table.client.update_record = Mock(return_value=123)

        update_data = {"Id": 123, "Name": "Updated Name"}
        record_id = table.update_record(update_data)

        assert record_id == 123
        table.client.update_record.assert_called_once_with("test-table-id", update_data, None)

    def test_delete_record(self, table):
        """Test delete_record method."""
        table.client.delete_record = Mock(return_value=123)

        record_id = table.delete_record(123)

        assert record_id == 123
        table.client.delete_record.assert_called_once_with("test-table-id", 123)

    def test_count_records(self, table):
        """Test count_records method."""
        table.client.count_records = Mock(return_value=42)

        count = table.count_records()

        assert count == 42
        table.client.count_records.assert_called_once_with("test-table-id", None)

    def test_count_records_with_filter(self, table):
        """Test count_records with where clause."""
        table.client.count_records = Mock(return_value=15)

        count = table.count_records(where="(Active,eq,true)")

        assert count == 15
        table.client.count_records.assert_called_once_with("test-table-id", "(Active,eq,true)")

    def test_attach_file_to_record(self, table):
        """Test attach_file_to_record method."""
        table.client.attach_file_to_record = Mock(return_value=123)

        result = table.attach_file_to_record(123, "Document", "/path/to/file.txt")

        assert result == 123
        table.client.attach_file_to_record.assert_called_once_with(
            "test-table-id", 123, "Document", "/path/to/file.txt"
        )

    def test_attach_files_to_record(self, table):
        """Test attach_files_to_record method."""
        table.client.attach_files_to_record = Mock(return_value=123)

        files = ["/path/file1.txt", "/path/file2.txt"]
        result = table.attach_files_to_record(123, "Documents", files)

        assert result == 123
        table.client.attach_files_to_record.assert_called_once_with(
            "test-table-id", 123, "Documents", files
        )

    def test_delete_file_from_record(self, table):
        """Test delete_file_from_record method."""
        table.client.delete_file_from_record = Mock(return_value=123)

        result = table.delete_file_from_record(123, "Document")

        assert result == 123
        table.client.delete_file_from_record.assert_called_once_with(
            "test-table-id", 123, "Document"
        )

    def test_download_file_from_record(self, table):
        """Test download_file_from_record method."""
        table.client.download_file_from_record = Mock()

        table.download_file_from_record(123, "Document", "/save/path/file.txt")

        table.client.download_file_from_record.assert_called_once_with(
            "test-table-id", 123, "Document", "/save/path/file.txt"
        )

    def test_download_files_from_record(self, table):
        """Test download_files_from_record method."""
        table.client.download_files_from_record = Mock()

        table.download_files_from_record(123, "Documents", "/save/directory")

        table.client.download_files_from_record.assert_called_once_with(
            "test-table-id", 123, "Documents", "/save/directory"
        )

    def test_method_delegation_preserves_exceptions(self, table):
        """Test that exceptions from client methods are properly propagated."""
        # Test that NocoDBException is properly propagated
        table.client.get_records = Mock(side_effect=NocoDBException("TEST_ERROR", "Test error"))

        with pytest.raises(NocoDBException) as exc_info:
            table.get_records()

        assert exc_info.value.error == "TEST_ERROR"
        assert exc_info.value.message == "Test error"

    def test_type_consistency(self, table):
        """Test that method signatures accept both string and int IDs."""
        table.client.get_record = Mock(return_value={"Id": 123})
        table.client.delete_record = Mock(return_value=123)

        # Test with integer ID
        table.get_record(123)
        table.delete_record(123)

        # Test with string ID
        table.get_record("123")
        table.delete_record("123")

        # Both should work without type errors
        assert table.client.get_record.call_count == 2
        assert table.client.delete_record.call_count == 2
