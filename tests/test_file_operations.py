"""
Unit tests for file operations functionality with mocked dependencies.
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.client import NocoDBClient
from nocodb_simple_client.exceptions import FileOperationError, NocoDBError
from nocodb_simple_client.file_operations import FileManager


class TestFileManager:
    """Test the main file manager functionality."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_file_manager_initialization(self, file_manager):
        """Test file manager initialization."""
        assert file_manager.client is not None
        assert file_manager.max_file_size == 50 * 1024 * 1024  # 50MB
        assert ".jpg" in file_manager.SUPPORTED_IMAGE_TYPES
        assert ".pdf" in file_manager.SUPPORTED_DOCUMENT_TYPES

    def test_supported_file_types(self, file_manager):
        """Test supported file type validation."""
        # Image types
        assert file_manager.is_supported_type("image.jpg")
        assert file_manager.is_supported_type("photo.png")
        assert file_manager.is_supported_type("graphic.gif")

        # Document types
        assert file_manager.is_supported_type("document.pdf")
        assert file_manager.is_supported_type("spreadsheet.xlsx")
        assert file_manager.is_supported_type("presentation.pptx")

        # Unsupported types
        assert not file_manager.is_supported_type("executable.exe")
        assert not file_manager.is_supported_type("script.bat")

    def test_file_size_validation(self, file_manager):
        """Test file size validation."""
        # Valid size
        assert file_manager.validate_file_size(1024 * 1024)  # 1MB
        assert file_manager.validate_file_size(10 * 1024 * 1024)  # 10MB

        # Invalid size
        assert not file_manager.validate_file_size(100 * 1024 * 1024)  # 100MB
        assert not file_manager.validate_file_size(0)  # 0 bytes

    def test_get_file_info(self, file_manager):
        """Test file information extraction."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"test image data")
            temp_path = temp_file.name

        try:
            info = file_manager.get_file_info(temp_path)

            assert info["name"] == os.path.basename(temp_path)
            assert info["size"] == 15  # len('test image data')
            assert info["extension"] == ".jpg"
            assert info["type"] == "image"
            assert "mime_type" in info
        finally:
            os.unlink(temp_path)


class TestFileUpload:
    """Test file upload functionality."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_upload_file_from_path(self, file_manager):
        """Test uploading file from file path."""
        mock_response = {
            "id": "file_123",
            "title": "test.jpg",
            "mimetype": "image/jpeg",
            "size": 1024,
            "url": "http://localhost:8080/download/file_123",
        }

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"test image data")
            temp_path = temp_file.name

        try:
            with patch.object(file_manager.client, "_make_request") as mock_request:
                mock_request.return_value = mock_response

                result = file_manager.upload_file(temp_path)

                assert result == mock_response
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[0][0] == "POST"  # Method
                assert "/api/v2/storage/upload" in call_args[0][1]  # Endpoint
        finally:
            os.unlink(temp_path)

    def test_upload_file_from_bytes(self, file_manager):
        """Test uploading file from bytes data."""
        mock_response = {
            "id": "file_124",
            "title": "uploaded.png",
            "mimetype": "image/png",
            "size": 1024,
            "url": "http://localhost:8080/download/file_124",
        }

        file_data = b"PNG image data"

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.upload_file_data(
                file_data, filename="test.png", content_type="image/png"
            )

            assert result == mock_response
            mock_request.assert_called_once()

    def test_upload_file_validation_error(self, file_manager):
        """Test file upload validation errors."""
        # Test unsupported file type
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp_file:
            temp_file.write(b"executable data")
            temp_path = temp_file.name

        try:
            with pytest.raises(FileOperationError, match="Unsupported file type"):
                file_manager.upload_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_upload_large_file_error(self, file_manager):
        """Test upload error for large files."""
        # Mock large file
        large_data = b"x" * (100 * 1024 * 1024)  # 100MB

        with pytest.raises(FileOperationError, match="File size exceeds maximum"):
            file_manager.upload_file_data(
                large_data, filename="large.jpg", content_type="image/jpeg"
            )

    def test_upload_with_progress_callback(self, file_manager):
        """Test file upload with progress callback."""
        mock_response = {"id": "file_125", "url": "http://test.com/file_125"}
        progress_calls = []

        def progress_callback(bytes_uploaded, total_bytes):
            progress_calls.append((bytes_uploaded, total_bytes))

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"test data")
            temp_path = temp_file.name

        try:
            with patch.object(file_manager.client, "_make_request") as mock_request:
                mock_request.return_value = mock_response

                result = file_manager.upload_file(temp_path, progress_callback=progress_callback)

                assert result == mock_response
                assert len(progress_calls) > 0  # Progress should be reported
        finally:
            os.unlink(temp_path)


class TestFileDownload:
    """Test file download functionality."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_download_file_to_path(self, file_manager):
        """Test downloading file to specific path."""
        mock_file_data = b"downloaded file content"

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_file_data

            with tempfile.TemporaryDirectory() as temp_dir:
                download_path = os.path.join(temp_dir, "downloaded.txt")

                result = file_manager.download_file("file_123", download_path)

                assert result == download_path
                assert os.path.exists(download_path)

                with open(download_path, "rb") as f:
                    assert f.read() == mock_file_data

                mock_request.assert_called_once_with("GET", "/api/v2/storage/download/file_123")

    def test_download_file_as_bytes(self, file_manager):
        """Test downloading file as bytes."""
        mock_file_data = b"file content as bytes"

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_file_data

            result = file_manager.download_file_data("file_124")

            assert result == mock_file_data
            mock_request.assert_called_once_with("GET", "/api/v2/storage/download/file_124")

    def test_download_file_with_progress(self, file_manager):
        """Test file download with progress callback."""
        mock_file_data = b"x" * 1024  # 1KB file
        progress_calls = []

        def progress_callback(bytes_downloaded, total_bytes):
            progress_calls.append((bytes_downloaded, total_bytes))

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_file_data

            result = file_manager.download_file_data(
                "file_125", progress_callback=progress_callback
            )

            assert result == mock_file_data
            assert len(progress_calls) > 0

    def test_download_nonexistent_file(self, file_manager):
        """Test downloading non-existent file."""
        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.side_effect = NocoDBError("File not found", status_code=404)

            with pytest.raises(FileOperationError, match="File not found"):
                file_manager.download_file_data("nonexistent_file")


class TestFileManagement:
    """Test file management operations."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_list_files(self, file_manager):
        """Test listing files."""
        mock_response = {
            "list": [
                {
                    "id": "file_1",
                    "title": "document.pdf",
                    "mimetype": "application/pdf",
                    "size": 1024000,
                    "created_at": "2023-01-01T10:00:00Z",
                },
                {
                    "id": "file_2",
                    "title": "image.jpg",
                    "mimetype": "image/jpeg",
                    "size": 512000,
                    "created_at": "2023-01-02T10:00:00Z",
                },
            ],
            "pageInfo": {"totalRows": 2},
        }

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.list_files()

            assert result == mock_response["list"]
            mock_request.assert_called_once_with("GET", "/api/v2/storage/files")

    def test_list_files_with_filters(self, file_manager):
        """Test listing files with type and size filters."""
        mock_response = {
            "list": [
                {"id": "file_3", "title": "photo.png", "mimetype": "image/png", "size": 256000}
            ]
        }

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.list_files(file_type="image", max_size=1024000)

            assert len(result) == 1
            assert result[0]["mimetype"].startswith("image/")
            mock_request.assert_called_once()

    def test_get_file_info_by_id(self, file_manager):
        """Test getting file information by ID."""
        mock_response = {
            "id": "file_123",
            "title": "test.jpg",
            "mimetype": "image/jpeg",
            "size": 1024,
            "url": "http://localhost:8080/download/file_123",
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:00:00Z",
        }

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.get_file_metadata("file_123")

            assert result == mock_response
            mock_request.assert_called_once_with("GET", "/api/v2/storage/files/file_123")

    def test_delete_file(self, file_manager):
        """Test deleting a file."""
        mock_response = {"deleted": True}

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.delete_file("file_123")

            assert result == mock_response
            mock_request.assert_called_once_with("DELETE", "/api/v2/storage/files/file_123")

    def test_batch_delete_files(self, file_manager):
        """Test batch deleting multiple files."""
        file_ids = ["file_1", "file_2", "file_3"]
        mock_response = {"deleted": 3}

        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = file_manager.batch_delete_files(file_ids)

            assert result == mock_response
            mock_request.assert_called_once_with(
                "DELETE", "/api/v2/storage/files/batch", json={"file_ids": file_ids}
            )


class TestAttachmentHandling:
    """Test attachment handling for table records."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_attach_file_to_record(self, file_manager):
        """Test attaching a file to a table record."""
        mock_upload_response = {
            "id": "file_123",
            "url": "http://localhost:8080/download/file_123",
            "title": "document.pdf",
        }

        mock_update_response = {"id": "rec_456", "attachments": [mock_upload_response]}

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"PDF content")
            temp_path = temp_file.name

        try:
            with patch.object(file_manager, "upload_file") as mock_upload, patch.object(
                file_manager.client, "update_record"
            ) as mock_update:

                mock_upload.return_value = mock_upload_response
                mock_update.return_value = mock_update_response

                result = file_manager.attach_file_to_record(
                    "table_123", "rec_456", "attachments", temp_path
                )

                assert result == mock_update_response
                mock_upload.assert_called_once_with(temp_path)
                mock_update.assert_called_once()
        finally:
            os.unlink(temp_path)

    def test_detach_file_from_record(self, file_manager):
        """Test detaching a file from a table record."""
        current_attachments = [
            {"id": "file_1", "title": "keep.jpg"},
            {"id": "file_2", "title": "remove.pdf"},
            {"id": "file_3", "title": "keep.docx"},
        ]

        expected_attachments = [
            {"id": "file_1", "title": "keep.jpg"},
            {"id": "file_3", "title": "keep.docx"},
        ]

        mock_record_response = {"attachments": current_attachments}
        mock_update_response = {"attachments": expected_attachments}

        with patch.object(file_manager.client, "get_record") as mock_get, patch.object(
            file_manager.client, "update_record"
        ) as mock_update:

            mock_get.return_value = mock_record_response
            mock_update.return_value = mock_update_response

            result = file_manager.detach_file_from_record(
                "table_123", "rec_456", "attachments", "file_2"
            )

            assert result == mock_update_response
            assert len(result["attachments"]) == 2

            mock_get.assert_called_once()
            mock_update.assert_called_once()

    def test_get_record_attachments(self, file_manager):
        """Test getting all attachments for a record."""
        mock_record = {
            "id": "rec_123",
            "name": "Test Record",
            "attachments": [
                {"id": "file_1", "title": "doc1.pdf", "size": 1024},
                {"id": "file_2", "title": "img1.jpg", "size": 2048},
            ],
        }

        with patch.object(file_manager.client, "get_record") as mock_get:
            mock_get.return_value = mock_record

            result = file_manager.get_record_attachments("table_123", "rec_123", "attachments")

            assert result == mock_record["attachments"]
            assert len(result) == 2
            mock_get.assert_called_once_with("table_123", "rec_123")


class TestImageProcessing:
    """Test image processing functionality."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_generate_image_thumbnail(self, file_manager):
        """Test generating image thumbnails."""
        mock_thumbnail_data = b"thumbnail image data"

        with patch.object(file_manager, "_process_image_thumbnail") as mock_process:
            mock_process.return_value = mock_thumbnail_data

            result = file_manager.generate_thumbnail("file_123", size=(150, 150))

            assert result == mock_thumbnail_data
            mock_process.assert_called_once_with("file_123", (150, 150))

    def test_get_image_metadata(self, file_manager):
        """Test extracting image metadata."""
        mock_metadata = {
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "mode": "RGB",
            "has_transparency": False,
        }

        with patch.object(file_manager, "_extract_image_metadata") as mock_extract:
            mock_extract.return_value = mock_metadata

            result = file_manager.get_image_metadata("file_123")

            assert result == mock_metadata
            mock_extract.assert_called_once_with("file_123")

    def test_validate_image_dimensions(self, file_manager):
        """Test validating image dimensions."""
        # Valid dimensions
        assert file_manager.validate_image_dimensions(800, 600, max_width=1920, max_height=1080)

        # Invalid dimensions
        assert not file_manager.validate_image_dimensions(
            2000, 1500, max_width=1920, max_height=1080
        )


class TestFileOperationErrorHandling:
    """Test error handling in file operations."""

    @pytest.fixture
    def file_manager(self):
        """Create a file manager instance for testing."""
        client = Mock(spec=NocoDBClient)
        client.base_url = "http://localhost:8080"
        client.token = "test-token"
        client.headers = {"xc-token": "test-token"}
        return FileManager(client)

    def test_upload_network_error(self, file_manager):
        """Test handling network errors during upload."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"test data")
            temp_path = temp_file.name

        try:
            with patch.object(file_manager.client, "_make_request") as mock_request:
                mock_request.side_effect = NocoDBError("Network error", status_code=500)

                with pytest.raises(FileOperationError, match="Upload failed"):
                    file_manager.upload_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_download_network_error(self, file_manager):
        """Test handling network errors during download."""
        with patch.object(file_manager.client, "_make_request") as mock_request:
            mock_request.side_effect = NocoDBError("Network error", status_code=500)

            with pytest.raises(FileOperationError, match="Download failed"):
                file_manager.download_file_data("file_123")

    def test_file_not_found_error(self, file_manager):
        """Test handling file not found errors."""
        with pytest.raises(FileOperationError, match="File not found"):
            file_manager.upload_file("nonexistent_file.jpg")

    def test_permission_error(self, file_manager):
        """Test handling permission errors."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(FileOperationError, match="Permission denied"):
                file_manager.upload_file("restricted_file.jpg")

    def test_disk_space_error(self, file_manager):
        """Test handling disk space errors."""
        with patch("builtins.open", side_effect=OSError("No space left on device")):
            with pytest.raises(FileOperationError, match="Storage error"):
                file_manager.download_file_data("large_file", "/tmp/download.bin")
