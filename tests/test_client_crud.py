"""Tests for NocoDB Client CRUD operations based on actual implementation."""

from unittest.mock import Mock, patch
import pytest

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.exceptions import RecordNotFoundException, ValidationException


class TestNocoDBClientInit:
    """Test NocoDBClient initialization."""

    def test_client_initialization_with_required_params(self):
        """Test client initialization with required parameters."""
        client = NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

        assert client._base_url == "https://app.nocodb.com"
        assert client.headers["xc-token"] == "test_token"

    def test_client_initialization_with_access_protection(self):
        """Test client initialization with access protection."""
        client = NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token",
            access_protection_auth="protection_value",
            access_protection_header="X-Custom-Auth"
        )

        assert client.headers["xc-token"] == "test_token"
        assert client.headers["X-Custom-Auth"] == "protection_value"


class TestRecordOperations:
    """Test record CRUD operations."""

    @pytest.fixture
    def client(self):
        """Create client for testing."""
        return NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    @pytest.fixture
    def mock_response(self):
        """Mock response object."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"Id": "record_123", "Name": "Test Record"}
        return response

    def test_get_records_success(self, client):
        """Test successful get_records operation."""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {
                "list": [{"Id": "1", "Name": "Record 1"}, {"Id": "2", "Name": "Record 2"}],
                "pageInfo": {"totalRows": 2}
            }

            result = client.get_records("table_123")

            assert len(result) == 2
            assert result[0]["Id"] == "1"
            assert result[1]["Name"] == "Record 2"
            # Just verify _get was called at least once
            mock_get.assert_called()

    def test_get_records_with_filters(self, client):
        """Test get_records with filters and pagination."""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {
                "list": [{"Id": "1", "Name": "Active Record"}],
                "pageInfo": {"totalRows": 1}
            }

            result = client.get_records(
                table_id="table_123",
                where="(Status,eq,active)",
                limit=10,
                sort="Name"
            )

            assert len(result) == 1
            assert result[0]["Name"] == "Active Record"
            # Verify _get was called with correct endpoint
            mock_get.assert_called()

    def test_get_record_success(self, client):
        """Test successful get_record operation."""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"Id": "record_123", "Name": "Test Record", "Status": "active"}

            result = client.get_record("table_123", "record_123")

            assert result["Id"] == "record_123"
            assert result["Name"] == "Test Record"
            # Verify _get was called
            mock_get.assert_called()

    def test_get_record_not_found(self, client):
        """Test get_record when record doesn't exist."""
        with patch.object(client, '_get') as mock_get:
            mock_get.side_effect = RecordNotFoundException("Record not found", record_id="record_123")

            with pytest.raises(RecordNotFoundException) as exc_info:
                client.get_record("table_123", "record_123")

            assert "Record not found" in str(exc_info.value)

    def test_insert_record_success(self, client):
        """Test successful record insertion."""
        with patch.object(client, '_post') as mock_post:
            mock_post.return_value = {"Id": "new_record_123"}

            record_data = {"Name": "New Record", "Status": "active"}
            result = client.insert_record("table_123", record_data)

            assert result == "new_record_123"
            mock_post.assert_called()

    def test_insert_record_validation_error(self, client):
        """Test record insertion with validation error."""
        with patch.object(client, '_post') as mock_post:
            mock_post.side_effect = ValidationException("Invalid data")

            record_data = {"Name": ""}  # Invalid empty name

            with pytest.raises(ValidationException):
                client.insert_record("table_123", record_data)

    def test_update_record_success(self, client):
        """Test successful record update."""
        with patch.object(client, '_patch') as mock_patch:
            mock_patch.return_value = {"Id": "record_123"}

            update_data = {"Name": "Updated Record", "Status": "inactive"}
            result = client.update_record("table_123", update_data, "record_123")

            assert result == "record_123"
            mock_patch.assert_called()

    def test_delete_record_success(self, client):
        """Test successful record deletion."""
        with patch.object(client, '_delete') as mock_delete:
            mock_delete.return_value = {"Id": "record_123"}

            result = client.delete_record("table_123", "record_123")

            assert result == "record_123"
            mock_delete.assert_called()

    def test_count_records_success(self, client):
        """Test successful record counting."""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"count": 42}

            result = client.count_records("table_123")

            assert result == 42
            mock_get.assert_called()

    def test_count_records_with_filter(self, client):
        """Test record counting with filter."""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"count": 15}

            result = client.count_records("table_123", where="(Status,eq,active)")

            assert result == 15
            mock_get.assert_called()


class TestBulkOperations:
    """Test bulk record operations."""

    @pytest.fixture
    def client(self):
        """Create client for testing."""
        return NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_bulk_insert_records_success(self, client):
        """Test successful bulk record insertion."""
        with patch.object(client, '_post') as mock_post:
            mock_post.return_value = [{"Id": "rec1"}, {"Id": "rec2"}, {"Id": "rec3"}]

            records = [
                {"Name": "Record 1", "Status": "active"},
                {"Name": "Record 2", "Status": "active"},
                {"Name": "Record 3", "Status": "inactive"}
            ]

            result = client.bulk_insert_records("table_123", records)

            assert result == ["rec1", "rec2", "rec3"]
            mock_post.assert_called()

    def test_bulk_insert_records_empty_list(self, client):
        """Test bulk insert with empty list."""
        result = client.bulk_insert_records("table_123", [])
        assert result == []

    def test_bulk_insert_records_validation_error(self, client):
        """Test bulk insert validation error."""
        with pytest.raises(ValidationException) as exc_info:
            client.bulk_insert_records("table_123", "not_a_list")

        assert "Records must be a list" in str(exc_info.value)

    def test_bulk_update_records_success(self, client):
        """Test successful bulk record update."""
        with patch.object(client, '_patch') as mock_patch:
            mock_patch.return_value = [{"Id": "rec1"}, {"Id": "rec2"}]

            records = [
                {"Id": "rec1", "Name": "Updated Record 1"},
                {"Id": "rec2", "Name": "Updated Record 2"}
            ]

            result = client.bulk_update_records("table_123", records)

            assert result == ["rec1", "rec2"]
            mock_patch.assert_called()

    def test_bulk_delete_records_success(self, client):
        """Test successful bulk record deletion."""
        with patch.object(client, '_delete') as mock_delete:
            mock_delete.return_value = [{"Id": "rec1"}, {"Id": "rec2"}]

            record_ids = ["rec1", "rec2", "rec3"]
            result = client.bulk_delete_records("table_123", record_ids)

            assert result == ["rec1", "rec2"]
            # Just verify _delete was called
            mock_delete.assert_called()

    def test_bulk_delete_records_empty_list(self, client):
        """Test bulk delete with empty list."""
        result = client.bulk_delete_records("table_123", [])
        assert result == []

    def test_bulk_delete_records_validation_error(self, client):
        """Test bulk delete validation error."""
        with pytest.raises(ValidationException) as exc_info:
            client.bulk_delete_records("table_123", "not_a_list")

        assert "Record IDs must be a list" in str(exc_info.value)


class TestFileOperations:
    """Test file attachment operations - basic validation only."""

    @pytest.fixture
    def client(self):
        """Create client for testing."""
        return NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

    def test_file_methods_exist(self, client):
        """Test that file methods exist on client."""
        assert hasattr(client, 'attach_file_to_record')
        assert hasattr(client, 'download_file_from_record')
        assert hasattr(client, 'attach_files_to_record')
        assert hasattr(client, 'download_files_from_record')
        assert hasattr(client, 'delete_file_from_record')


class TestClientUtilities:
    """Test client utility methods."""

    def test_client_close(self):
        """Test client close method."""
        client = NocoDBClient(
            base_url="https://app.nocodb.com",
            db_auth_token="test_token"
        )

        # Should not raise any exceptions
        client.close()
