"""Tests for NocoDB File Operations based on actual implementation."""

import hashlib
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from nocodb_simple_client.file_operations import FileManager, TableFileManager
from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.table import NocoDBTable
from nocodb_simple_client.exceptions import NocoDBException, ValidationException


class TestFileManager:
    """Test FileManager functionality."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        return Mock(spec=NocoDBClient)

    @pytest.fixture
    def file_manager(self, client):
        """Create file manager instance."""
        return FileManager(client)

    def test_file_manager_initialization(self, client):
        """Test file manager initialization."""
        file_manager = FileManager(client)

        assert file_manager.client == client
        assert file_manager.temp_dir is None

    def test_validate_file_success(self, file_manager):
        """Test successful file validation."""
        test_content = b"Test file content"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = len(test_content)
                with patch("mimetypes.guess_type", return_value=("text/plain", None)):
                    with patch("builtins.open", mock_open(read_data=test_content)):

                        result = file_manager.validate_file("/path/to/test.txt")

                        assert result["exists"] is True
                        assert result["size"] == len(test_content)
                        assert result["mime_type"] == "text/plain"
                        assert "hash" in result

    def test_validate_file_not_exists(self, file_manager):
        """Test file validation when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(ValidationException, match="File not found"):
                file_manager.validate_file("/path/to/nonexistent.txt")

    def test_calculate_file_hash(self, file_manager):
        """Test file hash calculation."""
        test_content = b"Test content for hashing"
        expected_hash = hashlib.sha256(test_content).hexdigest()

        with patch("builtins.open", mock_open(read_data=test_content)):
            result = file_manager.calculate_file_hash("/path/to/test.txt")

            assert result == expected_hash

    def test_calculate_file_hash_md5(self, file_manager):
        """Test file hash calculation with MD5."""
        test_content = b"Test content for MD5 hashing"
        expected_hash = hashlib.md5(test_content).hexdigest()

        with patch("builtins.open", mock_open(read_data=test_content)):
            result = file_manager.calculate_file_hash("/path/to/test.txt", algorithm="md5")

            assert result == expected_hash

    def test_upload_file(self, file_manager, client):
        """Test single file upload."""
        upload_response = {"url": "https://example.com/file.txt", "title": "test.txt"}
        client._upload_file.return_value = upload_response

        with patch.object(file_manager, 'validate_file') as mock_validate:
            mock_validate.return_value = {"exists": True, "size": 100, "mime_type": "text/plain"}

            result = file_manager.upload_file("table_123", "/path/to/test.txt")

            assert result == upload_response
            client._upload_file.assert_called_once_with("table_123", "/path/to/test.txt")
            mock_validate.assert_called_once_with("/path/to/test.txt")

    def test_upload_files_batch(self, file_manager, client):
        """Test batch file upload."""
        file_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
        upload_responses = [
            {"url": "https://example.com/file1.txt", "title": "file1.txt"},
            {"url": "https://example.com/file2.txt", "title": "file2.txt"}
        ]

        client._upload_file.side_effect = upload_responses

        with patch.object(file_manager, 'validate_file') as mock_validate:
            mock_validate.return_value = {"exists": True, "size": 100, "mime_type": "text/plain"}

            result = file_manager.upload_files_batch("table_123", file_paths)

            assert result == upload_responses
            assert client._upload_file.call_count == 2
            assert mock_validate.call_count == 2

    def test_upload_files_batch_empty_list(self, file_manager):
        """Test batch upload with empty file list."""
        result = file_manager.upload_files_batch("table_123", [])
        assert result == []

    def test_attach_files_to_record(self, file_manager, client):
        """Test attaching multiple files to a record."""
        file_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
        upload_responses = [
            {"url": "https://example.com/file1.txt", "title": "file1.txt"},
            {"url": "https://example.com/file2.txt", "title": "file2.txt"}
        ]

        with patch.object(file_manager, 'upload_files_batch') as mock_upload:
            mock_upload.return_value = upload_responses
            with patch.object(client, 'update_record') as mock_update:
                mock_update.return_value = "record_123"

                result = file_manager.attach_files_to_record(
                    "table_123", "record_123", "Documents", file_paths
                )

                assert result == "record_123"
                mock_upload.assert_called_once_with("table_123", file_paths)
                mock_update.assert_called_once()

    def test_download_file(self, file_manager, client):
        """Test file download."""
        file_content = b"Downloaded file content"
        client.download_file_from_record.return_value = file_content

        with patch("builtins.open", mock_open()) as mock_file:
            result = file_manager.download_file(
                "table_123", "record_123", "Documents", 0, "/download/path/file.txt"
            )

            assert result == "/download/path/file.txt"
            client.download_file_from_record.assert_called_once_with(
                "table_123", "record_123", "Documents", 0
            )
            mock_file.assert_called_once_with("/download/path/file.txt", "wb")

    def test_download_record_attachments(self, file_manager, client):
        """Test downloading all attachments from a record."""
        attachments = [
            {"url": "https://example.com/file1.txt", "title": "file1.txt"},
            {"url": "https://example.com/file2.txt", "title": "file2.txt"}
        ]

        with patch.object(file_manager, 'get_attachment_info') as mock_info:
            mock_info.return_value = attachments
            with patch.object(file_manager, 'download_file') as mock_download:
                mock_download.side_effect = ["/download/file1.txt", "/download/file2.txt"]

                result = file_manager.download_record_attachments(
                    "table_123", "record_123", "Documents", "/download/dir"
                )

                assert result == ["/download/file1.txt", "/download/file2.txt"]
                assert mock_download.call_count == 2

    def test_bulk_download_attachments(self, file_manager):
        """Test bulk download attachments from multiple records."""
        record_ids = ["record_1", "record_2"]

        with patch.object(file_manager, 'download_record_attachments') as mock_download:
            mock_download.side_effect = [
                ["/download/file1.txt"],
                ["/download/file2.txt", "/download/file3.txt"]
            ]

            result = file_manager.bulk_download_attachments(
                "table_123", record_ids, "Documents", "/download/dir"
            )

            expected = {
                "record_1": ["/download/file1.txt"],
                "record_2": ["/download/file2.txt", "/download/file3.txt"]
            }
            assert result == expected
            assert mock_download.call_count == 2

    def test_cleanup_temp_files(self, file_manager):
        """Test cleanup of temporary files."""
        with patch("shutil.rmtree") as mock_rmtree:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.iterdir") as mock_iterdir:
                    mock_iterdir.return_value = [Path("/temp/file1"), Path("/temp/file2")]

                    result = file_manager.cleanup_temp_files("/temp/dir")

                    assert result == 2  # Number of files cleaned
                    mock_rmtree.assert_called()

    def test_get_attachment_info(self, file_manager, client):
        """Test getting attachment information."""
        record_data = {
            "Documents": [
                {"url": "https://example.com/file1.txt", "title": "file1.txt"},
                {"url": "https://example.com/file2.txt", "title": "file2.txt"}
            ]
        }
        client.get_record.return_value = record_data

        result = file_manager.get_attachment_info("table_123", "record_123", "Documents")

        assert result == record_data["Documents"]
        client.get_record.assert_called_once_with("table_123", "record_123")

    def test_create_attachment_summary(self, file_manager):
        """Test creating attachment summary."""
        attachments = [
            {"url": "https://example.com/file1.txt", "title": "file1.txt", "size": 100},
            {"url": "https://example.com/file2.jpg", "title": "file2.jpg", "size": 200}
        ]

        with patch.object(file_manager, 'get_attachment_info') as mock_info:
            mock_info.return_value = attachments

            result = file_manager.create_attachment_summary("table_123", "record_123", "Documents")

            assert result["total_count"] == 2
            assert result["total_size"] == 300
            assert "txt" in result["file_types"]
            assert "jpg" in result["file_types"]


class TestTableFileManager:
    """Test TableFileManager functionality."""

    @pytest.fixture
    def mock_table(self):
        """Create mock table."""
        table = Mock(spec=NocoDBTable)
        table.table_id = "test_table_123"
        return table

    @pytest.fixture
    def table_file_manager(self, mock_table):
        """Create table file manager instance."""
        return TableFileManager(mock_table)

    def test_table_file_manager_initialization(self, mock_table):
        """Test table file manager initialization."""
        table_file_manager = TableFileManager(mock_table)

        assert table_file_manager.table == mock_table
        assert table_file_manager.table_id == "test_table_123"

    def test_upload_file_table_delegation(self, table_file_manager, mock_table):
        """Test upload_file delegation to table's client."""
        upload_response = {"url": "https://example.com/file.txt", "title": "test.txt"}

        # Mock the client's file_manager property
        mock_file_manager = Mock()
        mock_file_manager.upload_file.return_value = upload_response
        mock_table.client.file_manager = mock_file_manager

        result = table_file_manager.upload_file("/path/to/test.txt")

        assert result == upload_response
        mock_file_manager.upload_file.assert_called_once_with("test_table_123", "/path/to/test.txt")

    def test_attach_files_to_record_table_delegation(self, table_file_manager, mock_table):
        """Test attach_files_to_record delegation to table's client."""
        file_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]

        mock_file_manager = Mock()
        mock_file_manager.attach_files_to_record.return_value = "record_123"
        mock_table.client.file_manager = mock_file_manager

        result = table_file_manager.attach_files_to_record("record_123", "Documents", file_paths)

        assert result == "record_123"
        mock_file_manager.attach_files_to_record.assert_called_once_with(
            "test_table_123", "record_123", "Documents", file_paths
        )

    def test_download_record_attachments_table_delegation(self, table_file_manager, mock_table):
        """Test download_record_attachments delegation to table's client."""
        expected_files = ["/download/file1.txt", "/download/file2.txt"]

        mock_file_manager = Mock()
        mock_file_manager.download_record_attachments.return_value = expected_files
        mock_table.client.file_manager = mock_file_manager

        result = table_file_manager.download_record_attachments("record_123", "Documents", "/download")

        assert result == expected_files
        mock_file_manager.download_record_attachments.assert_called_once_with(
            "test_table_123", "record_123", "Documents", "/download"
        )

    def test_get_attachment_info_table_delegation(self, table_file_manager, mock_table):
        """Test get_attachment_info delegation to table's client."""
        expected_info = [{"url": "https://example.com/file.txt", "title": "file.txt"}]

        mock_file_manager = Mock()
        mock_file_manager.get_attachment_info.return_value = expected_info
        mock_table.client.file_manager = mock_file_manager

        result = table_file_manager.get_attachment_info("record_123", "Documents")

        assert result == expected_info
        mock_file_manager.get_attachment_info.assert_called_once_with(
            "test_table_123", "record_123", "Documents"
        )

    def test_create_attachment_summary_table_delegation(self, table_file_manager, mock_table):
        """Test create_attachment_summary delegation to table's client."""
        expected_summary = {"total_count": 2, "total_size": 300, "file_types": ["txt", "jpg"]}

        mock_file_manager = Mock()
        mock_file_manager.create_attachment_summary.return_value = expected_summary
        mock_table.client.file_manager = mock_file_manager

        result = table_file_manager.create_attachment_summary("record_123", "Documents")

        assert result == expected_summary
        mock_file_manager.create_attachment_summary.assert_called_once_with(
            "test_table_123", "record_123", "Documents"
        )


class TestFileManagerUtilities:
    """Test file manager utility functions."""

    @pytest.fixture
    def file_manager(self):
        """Create file manager for utility tests."""
        return FileManager(Mock(spec=NocoDBClient))

    def test_supported_hash_algorithms(self, file_manager):
        """Test that supported hash algorithms work."""
        test_content = b"Test content"

        with patch("builtins.open", mock_open(read_data=test_content)):
            # Test SHA256 (default)
            sha256_hash = file_manager.calculate_file_hash("/test.txt")
            assert len(sha256_hash) == 64  # SHA256 produces 64-character hex string

            # Test MD5
            md5_hash = file_manager.calculate_file_hash("/test.txt", algorithm="md5")
            assert len(md5_hash) == 32  # MD5 produces 32-character hex string

            # Test SHA1
            sha1_hash = file_manager.calculate_file_hash("/test.txt", algorithm="sha1")
            assert len(sha1_hash) == 40  # SHA1 produces 40-character hex string

    def test_mime_type_detection(self, file_manager):
        """Test MIME type detection for various file extensions."""
        test_cases = [
            ("/test.txt", "text/plain"),
            ("/test.jpg", "image/jpeg"),
            ("/test.png", "image/png"),
            ("/test.pdf", "application/pdf"),
            ("/test.json", "application/json")
        ]

        for file_path, expected_mime in test_cases:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch("mimetypes.guess_type", return_value=(expected_mime, None)):
                        with patch("builtins.open", mock_open(read_data=b"test")):

                            result = file_manager.validate_file(file_path)
                            assert result["mime_type"] == expected_mime

    def test_file_size_validation(self, file_manager):
        """Test file size reporting in validation."""
        test_sizes = [0, 100, 1024, 1048576]  # 0B, 100B, 1KB, 1MB

        for size in test_sizes:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = size
                    with patch("mimetypes.guess_type", return_value=("text/plain", None)):
                        with patch("builtins.open", mock_open(read_data=b"x" * size)):

                            result = file_manager.validate_file("/test.txt")
                            assert result["size"] == size


class TestFileManagerErrorHandling:
    """Test file manager error handling scenarios."""

    @pytest.fixture
    def file_manager(self):
        """Create file manager for error tests."""
        return FileManager(Mock(spec=NocoDBClient))

    def test_upload_file_validation_error(self, file_manager):
        """Test upload with validation error."""
        with patch.object(file_manager, 'validate_file') as mock_validate:
            mock_validate.side_effect = ValidationException("File too large")

            with pytest.raises(ValidationException, match="File too large"):
                file_manager.upload_file("table_123", "/path/to/large_file.txt")

    def test_download_file_client_error(self, file_manager):
        """Test download with client error."""
        file_manager.client.download_file_from_record.side_effect = NocoDBException(
            "DOWNLOAD_ERROR", "Failed to download file"
        )

        with pytest.raises(NocoDBException, match="Failed to download file"):
            file_manager.download_file("table_123", "record_123", "Documents", 0, "/download/file.txt")

    def test_batch_upload_partial_failure(self, file_manager):
        """Test batch upload with partial failure."""
        file_paths = ["/valid_file.txt", "/invalid_file.txt"]

        def mock_validate(path):
            if "invalid" in path:
                raise ValidationException("Invalid file")
            return {"exists": True, "size": 100, "mime_type": "text/plain"}

        with patch.object(file_manager, 'validate_file', side_effect=mock_validate):
            with pytest.raises(ValidationException, match="Invalid file"):
                file_manager.upload_files_batch("table_123", file_paths)
