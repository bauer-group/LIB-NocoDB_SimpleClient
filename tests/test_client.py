"""Tests for NocoDBClient."""

from unittest.mock import Mock, patch

import pytest

from nocodb_simple_client import NocoDBClient, NocoDBException, RecordNotFoundException


class TestNocoDBClient:
    """Test cases for NocoDBClient."""

    def test_client_initialization(self):
        """Test client initialization with various parameters."""
        client = NocoDBClient(
            base_url="https://test.nocodb.com",
            db_auth_token="test-token",
            access_protection_auth="custom-auth",
            max_redirects=5,
            timeout=60,
        )

        assert client._base_url == "https://test.nocodb.com"
        assert client.headers["xc-token"] == "test-token"
        assert client.headers["X-BAUERGROUP-Auth"] == "custom-auth"
        assert client._request_timeout == 60
        assert client._session.max_redirects == 5

    def test_client_initialization_custom_header(self):
        """Test client initialization with custom protection header."""
        client = NocoDBClient(
            base_url="https://test.nocodb.com",
            db_auth_token="test-token",
            access_protection_auth="custom-auth-value",
            access_protection_header="X-Custom-Protection",
        )

        assert client._base_url == "https://test.nocodb.com"
        assert client.headers["xc-token"] == "test-token"
        assert client.headers["X-Custom-Protection"] == "custom-auth-value"
        # Default header should not be present
        assert "X-BAUERGROUP-Auth" not in client.headers

    def test_client_initialization_minimal(self):
        """Test client initialization with minimal parameters."""
        client = NocoDBClient(
            base_url="https://test.nocodb.com/",  # Test trailing slash removal
            db_auth_token="test-token",
        )

        assert client._base_url == "https://test.nocodb.com"
        assert client.headers["xc-token"] == "test-token"
        assert "X-BAUERGROUP-Auth" not in client.headers

    def test_client_initialization_no_auth_value(self):
        """Test client initialization without protection auth value."""
        client = NocoDBClient(
            base_url="https://test.nocodb.com",
            db_auth_token="test-token",
            access_protection_header="X-Custom-Header",  # Header name but no value
        )

        assert client._base_url == "https://test.nocodb.com"
        assert client.headers["xc-token"] == "test-token"
        # No protection header should be set without a value
        assert "X-Custom-Header" not in client.headers
        assert "X-BAUERGROUP-Auth" not in client.headers

    def test_context_manager(self):
        """Test client as context manager."""
        with NocoDBClient(base_url="https://test.nocodb.com", db_auth_token="test-token") as client:
            assert client._session is not None

        # Session should be closed after context exit
        # Note: In real implementation, you'd check if session is closed

    def test_get_records(self, client, mock_session, sample_records):
        """Test get_records method."""
        mock_session.get.return_value.json.return_value = {
            "list": sample_records,
            "pageInfo": {"isLastPage": True},
        }

        records = client.get_records("test-table", limit=10)

        assert len(records) == 2
        assert records[0]["Name"] == "Test Record"
        mock_session.get.assert_called_once()

    def test_get_records_with_filters(self, client, mock_session, sample_records):
        """Test get_records with filtering and sorting."""
        mock_session.get.return_value.json.return_value = {
            "list": sample_records,
            "pageInfo": {"isLastPage": True},
        }

        records = client.get_records(
            "test-table", sort="-Id", where="(Active,eq,true)", fields=["Id", "Name"], limit=5
        )

        # Verify the returned records
        assert len(records) == 2

        # Verify the request was made with correct parameters
        args, kwargs = mock_session.get.call_args
        assert "params" in kwargs
        params = kwargs["params"]
        assert params["sort"] == "-Id"
        assert params["where"] == "(Active,eq,true)"
        assert params["fields"] == "Id,Name"
        assert params["limit"] == 5

    def test_get_record(self, client, mock_session, sample_record):
        """Test get_record method."""
        mock_session.get.return_value.json.return_value = sample_record

        record = client.get_record("test-table", 1)

        assert record["Id"] == 1
        assert record["Name"] == "Test Record"
        mock_session.get.assert_called_once()

    def test_insert_record(self, client, mock_session):
        """Test insert_record method."""
        mock_session.post.return_value.json.return_value = {"Id": 123}

        new_record = {"Name": "New Record", "Email": "new@example.com"}
        record_id = client.insert_record("test-table", new_record)

        assert record_id == 123
        mock_session.post.assert_called_once()

    def test_update_record(self, client, mock_session):
        """Test update_record method."""
        mock_session.patch.return_value.json.return_value = {"Id": 123}

        update_data = {"Name": "Updated Record"}
        record_id = client.update_record("test-table", update_data, 123)

        assert record_id == 123
        mock_session.patch.assert_called_once()

    def test_delete_record(self, client, mock_session):
        """Test delete_record method."""
        mock_session.delete.return_value.json.return_value = {"Id": 123}

        record_id = client.delete_record("test-table", 123)

        assert record_id == 123
        mock_session.delete.assert_called_once()

    def test_count_records(self, client, mock_session):
        """Test count_records method."""
        mock_session.get.return_value.json.return_value = {"count": 42}

        count = client.count_records("test-table")

        assert count == 42
        mock_session.get.assert_called_once()

    def test_count_records_with_filter(self, client, mock_session):
        """Test count_records with where clause."""
        mock_session.get.return_value.json.return_value = {"count": 15}

        count = client.count_records("test-table", where="(Active,eq,true)")

        assert count == 15
        # Verify where parameter was passed
        args, kwargs = mock_session.get.call_args
        assert kwargs["params"]["where"] == "(Active,eq,true)"

    def test_error_handling_record_not_found(self, client, mock_session):
        """Test handling of RecordNotFoundException."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": "RECORD_NOT_FOUND",
            "message": "Record not found",
        }
        mock_session.get.return_value = mock_response

        with pytest.raises(RecordNotFoundException) as exc_info:
            client.get_record("test-table", 999)

        assert exc_info.value.error == "RECORD_NOT_FOUND"
        assert exc_info.value.message == "Record not found"

    def test_error_handling_general_nocodb_error(self, client, mock_session):
        """Test handling of general NocoDBException."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "VALIDATION_ERROR",
            "message": "Invalid data provided",
        }
        mock_session.get.return_value = mock_response

        with pytest.raises(NocoDBException) as exc_info:
            client.get_records("test-table")

        assert exc_info.value.error == "VALIDATION_ERROR"
        assert exc_info.value.message == "Invalid data provided"

    def test_error_handling_http_error_without_json(self, client, mock_session):
        """Test handling of HTTP errors without JSON response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_session.get.return_value = mock_response

        with pytest.raises(NocoDBException):
            client.get_records("test-table")

    def test_pagination_handling(self, client, mock_session):
        """Test automatic pagination handling."""
        # Mock multiple pages of data
        page1_data = {
            "list": [{"Id": i, "Name": f"Record {i}"} for i in range(1, 101)],
            "pageInfo": {"isLastPage": False},
        }
        page2_data = {
            "list": [{"Id": i, "Name": f"Record {i}"} for i in range(101, 151)],
            "pageInfo": {"isLastPage": True},
        }

        mock_session.get.side_effect = [
            Mock(status_code=200, json=lambda: page1_data),
            Mock(status_code=200, json=lambda: page2_data),
        ]

        records = client.get_records("test-table", limit=150)

        assert len(records) == 150
        assert mock_session.get.call_count == 2

    def test_close_session(self, client):
        """Test closing the client session."""
        client.close()
        client._session.close.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open")
    @patch("mimetypes.guess_type")
    def test_upload_file(self, mock_mime, mock_open, mock_exists, client, mock_session):
        """Test file upload functionality."""
        # Setup mocks
        from io import BytesIO

        mock_exists.return_value = True
        mock_mime.return_value = ("text/plain", None)
        # Create a real BytesIO object with test content
        mock_file = BytesIO(b"test file content")
        mock_open.return_value.__enter__.return_value = mock_file
        mock_session.post.return_value.json.return_value = [{"id": "file123"}]

        # Test file upload
        result = client._upload_file("test-table", "/path/to/file.txt")

        assert result == [{"id": "file123"}]
        mock_session.post.assert_called_once()

    def test_upload_file_not_found(self, client):
        """Test file upload with non-existent file."""
        with pytest.raises(NocoDBException) as exc_info:
            client._upload_file("test-table", "/nonexistent/file.txt")

        assert exc_info.value.error == "FILE_NOT_FOUND"

    def test_attach_file_to_record(self, client, mock_session):
        """Test attaching file to record."""
        # Mock file upload response
        mock_session.post.return_value.json.return_value = [{"id": "file123"}]
        # Mock record update response
        mock_session.patch.return_value.json.return_value = {"Id": 123}

        with patch.object(client, "_upload_file") as mock_upload:
            mock_upload.return_value = [{"id": "file123"}]

            result = client.attach_file_to_record("test-table", 123, "Document", "/path/file.txt")

            assert result == 123
            mock_upload.assert_called_once_with("test-table", "/path/file.txt")

    def test_download_file_from_record(self, client, mock_session):
        """Test downloading file from record."""
        # Mock get record response with file info
        record_with_file = {
            "Id": 123,
            "Document": [{"title": "test_file.txt", "signedPath": "download/path/file123"}],
        }

        # Mock file download response
        mock_file_response = Mock()
        mock_file_response.status_code = 200
        mock_file_response.iter_content = lambda chunk_size: [b"file content"]

        mock_session.get.side_effect = [
            Mock(status_code=200, json=lambda: record_with_file),  # get_record call
            mock_file_response,  # file download call
        ]

        with patch("pathlib.Path.open"), patch("pathlib.Path.mkdir"):
            client.download_file_from_record("test-table", 123, "Document", "/save/path/file.txt")

            assert mock_session.get.call_count == 2

    def test_download_file_no_file_found(self, client, mock_session):
        """Test download when no file is attached."""
        record_without_file = {"Id": 123, "Document": None}
        mock_session.get.return_value.json.return_value = record_without_file

        with pytest.raises(NocoDBException) as exc_info:
            client.download_file_from_record("test-table", 123, "Document", "/save/path/file.txt")

        assert exc_info.value.error == "FILE_NOT_FOUND"
