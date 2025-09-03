"""Tests for NocoDB File Operations based on actual implementation."""

from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from nocodb_simple_client.file_operations import FileManager
from nocodb_simple_client.client import NocoDBClient


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
        assert hasattr(file_manager, 'SUPPORTED_IMAGE_TYPES')
        assert hasattr(file_manager, 'SUPPORTED_DOCUMENT_TYPES')
        assert hasattr(file_manager, 'MAX_FILE_SIZE')

    def test_supported_file_types_constants(self, file_manager):
        """Test file type constants."""
        assert ".jpg" in file_manager.SUPPORTED_IMAGE_TYPES
        assert ".png" in file_manager.SUPPORTED_IMAGE_TYPES
        assert ".pdf" in file_manager.SUPPORTED_DOCUMENT_TYPES
        assert ".docx" in file_manager.SUPPORTED_DOCUMENT_TYPES
        assert ".zip" in file_manager.SUPPORTED_ARCHIVE_TYPES
        assert file_manager.MAX_FILE_SIZE == 100 * 1024 * 1024

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    @patch('mimetypes.guess_type')
    def test_validate_file_success(self, mock_guess_type, mock_stat, mock_is_file, mock_exists, file_manager):
        """Test successful file validation."""
        # Mock file exists and is a file
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock file size
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024  # 1KB
        mock_stat.return_value = mock_stat_result

        # Mock mime type
        mock_guess_type.return_value = ('image/jpeg', None)

        result = file_manager.validate_file("test.jpg")

        assert result["name"] == "test.jpg"
        assert result["size"] == 1024
        assert result["extension"] == ".jpg"
        assert result["mime_type"] == "image/jpeg"
        assert result["file_type"] == "image"
        assert result["is_supported"] is True

    @patch('pathlib.Path.exists')
    def test_validate_file_not_exists(self, mock_exists, file_manager):
        """Test file validation when file doesn't exist."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="File not found"):
            file_manager.validate_file("nonexistent.jpg")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_validate_file_not_file(self, mock_is_file, mock_exists, file_manager):
        """Test file validation when path is not a file."""
        mock_exists.return_value = True
        mock_is_file.return_value = False

        with pytest.raises(ValueError, match="Path is not a file"):
            file_manager.validate_file("directory")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    def test_validate_file_too_large(self, mock_stat, mock_is_file, mock_exists, file_manager):
        """Test file validation when file is too large."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock file size larger than MAX_FILE_SIZE
        mock_stat_result = Mock()
        mock_stat_result.st_size = file_manager.MAX_FILE_SIZE + 1
        mock_stat.return_value = mock_stat_result

        with pytest.raises(ValueError, match="File too large"):
            file_manager.validate_file("largefile.jpg")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    def test_validate_file_empty(self, mock_stat, mock_is_file, mock_exists, file_manager):
        """Test file validation when file is empty."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock empty file
        mock_stat_result = Mock()
        mock_stat_result.st_size = 0
        mock_stat.return_value = mock_stat_result

        with pytest.raises(ValueError, match="File is empty"):
            file_manager.validate_file("empty.jpg")

    def test_file_type_detection(self, file_manager):
        """Test file type detection based on extension."""
        with patch('pathlib.Path.exists', return_value=True), patch('pathlib.Path.is_file', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat_result = Mock()
                mock_stat_result.st_size = 1024
                mock_stat.return_value = mock_stat_result

                with patch('mimetypes.guess_type', return_value=('image/jpeg', None)):
                    # Test image file
                    result = file_manager.validate_file("test.jpg")
                    assert result["file_type"] == "image"

                with patch('mimetypes.guess_type', return_value=('application/pdf', None)):
                    # Test document file
                    result = file_manager.validate_file("test.pdf")
                    assert result["file_type"] == "document"

                with patch('mimetypes.guess_type', return_value=('application/zip', None)):
                    # Test archive file
                    result = file_manager.validate_file("test.zip")
                    assert result["file_type"] == "archive"

                with patch('mimetypes.guess_type', return_value=(None, None)):
                    # Test unknown file type
                    result = file_manager.validate_file("test.unknown")
                    assert result["file_type"] == "other"
                    assert result["is_supported"] is False

    @patch('builtins.open', new_callable=mock_open, read_data=b'test content')
    @patch('hashlib.new')
    def test_calculate_file_hash(self, mock_hashlib, mock_file, file_manager):
        """Test file hash calculation."""
        # Mock hash object
        mock_hash = Mock()
        mock_hash.hexdigest.return_value = "abcdef123456"
        mock_hashlib.return_value = mock_hash

        result = file_manager.calculate_file_hash("test.txt")

        assert result == "abcdef123456"
        mock_hashlib.assert_called_once_with("sha256")
        mock_hash.update.assert_called()
        mock_hash.hexdigest.assert_called_once()

    @patch('nocodb_simple_client.file_operations.FileManager.validate_file')
    def test_upload_file_with_validation(self, mock_validate, file_manager):
        """Test file upload with validation."""
        # Mock validation result
        mock_validate.return_value = {"path": Path("test.jpg")}

        # Mock client upload
        file_manager.client._upload_file.return_value = {"url": "http://example.com/file.jpg"}

        result = file_manager.upload_file("table123", "test.jpg", validate=True)

        assert result == {"url": "http://example.com/file.jpg"}
        mock_validate.assert_called_once_with("test.jpg")
        file_manager.client._upload_file.assert_called_once_with("table123", Path("test.jpg"))

    def test_upload_file_without_validation(self, file_manager):
        """Test file upload without validation."""
        # Mock client upload
        file_manager.client._upload_file.return_value = {"url": "http://example.com/file.jpg"}

        result = file_manager.upload_file("table123", "test.jpg", validate=False)

        assert result == {"url": "http://example.com/file.jpg"}
        file_manager.client._upload_file.assert_called_once_with("table123", Path("test.jpg"))

    def test_upload_file_invalid_response(self, file_manager):
        """Test file upload with invalid response."""
        # Mock client upload returning non-dict
        file_manager.client._upload_file.return_value = "invalid_response"

        result = file_manager.upload_file("table123", "test.jpg", validate=False)

        assert result == {}


class TestFileManagerUtilities:
    """Test file manager utility methods."""

    @pytest.fixture
    def file_manager(self):
        """Create file manager instance."""
        return FileManager(Mock())

    def test_mime_type_detection(self, file_manager):
        """Test MIME type detection."""
        with patch('mimetypes.guess_type') as mock_guess:
            with patch('pathlib.Path.exists', return_value=True), patch('pathlib.Path.is_file', return_value=True):
                with patch('pathlib.Path.stat') as mock_stat:
                    mock_stat_result = Mock()
                    mock_stat_result.st_size = 1024
                    mock_stat.return_value = mock_stat_result

                    # Test various mime types
                    test_cases = [
                        ("test.jpg", "image/jpeg"),
                        ("test.png", "image/png"),
                        ("test.pdf", "application/pdf"),
                        ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                        ("test.zip", "application/zip")
                    ]

                    for filename, expected_mime in test_cases:
                        mock_guess.return_value = (expected_mime, None)
                        result = file_manager.validate_file(filename)
                        assert result["mime_type"] == expected_mime

    def test_file_size_validation(self, file_manager):
        """Test file size validation."""
        with patch('pathlib.Path.exists', return_value=True), patch('pathlib.Path.is_file', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat_result = Mock()

                # Test valid file size
                mock_stat_result.st_size = 50 * 1024 * 1024  # 50MB
                mock_stat.return_value = mock_stat_result

                with patch('mimetypes.guess_type', return_value=('image/jpeg', None)):
                    result = file_manager.validate_file("test.jpg")
                    assert result["size"] == 50 * 1024 * 1024

                # Test file too large
                mock_stat_result.st_size = file_manager.MAX_FILE_SIZE + 1
                mock_stat.return_value = mock_stat_result

                with pytest.raises(ValueError, match="File too large"):
                    file_manager.validate_file("large.jpg")


class TestFileManagerErrorHandling:
    """Test file manager error handling."""

    @pytest.fixture
    def file_manager(self):
        """Create file manager instance."""
        client = Mock()
        return FileManager(client)

    def test_upload_file_client_error(self, file_manager):
        """Test file upload with client error."""
        # Mock client raising exception
        file_manager.client._upload_file.side_effect = Exception("Upload failed")

        with pytest.raises(Exception, match="Upload failed"):
            file_manager.upload_file("table123", "test.jpg", validate=False)

    @patch('hashlib.new')
    def test_hash_calculation_with_different_algorithms(self, mock_hashlib, file_manager):
        """Test hash calculation with different algorithms."""
        mock_hash = Mock()
        mock_hash.hexdigest.return_value = "hash_result"
        mock_hashlib.return_value = mock_hash

        with patch('builtins.open', mock_open(read_data=b'test')):
            # Test different algorithms
            algorithms = ["md5", "sha1", "sha256", "sha512"]

            for algorithm in algorithms:
                result = file_manager.calculate_file_hash("test.txt", algorithm)
                assert result == "hash_result"

                # Verify correct algorithm was used
                mock_hashlib.assert_called_with(algorithm)


class TestFileManagerIntegration:
    """Test file manager integration scenarios."""

    @pytest.fixture
    def file_manager(self):
        """Create file manager with mock client."""
        client = Mock()
        return FileManager(client)

    def test_complete_file_workflow(self, file_manager):
        """Test complete file workflow: validate, hash, upload."""
        with patch('pathlib.Path.exists', return_value=True), patch('pathlib.Path.is_file', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat_result = Mock()
                mock_stat_result.st_size = 1024
                mock_stat.return_value = mock_stat_result

                with patch('mimetypes.guess_type', return_value=('image/jpeg', None)):
                    with patch('builtins.open', mock_open(read_data=b'test')):
                        with patch('hashlib.new') as mock_hashlib:
                            mock_hash = Mock()
                            mock_hash.hexdigest.return_value = "filehash123"
                            mock_hashlib.return_value = mock_hash

                            # Mock client upload
                            file_manager.client._upload_file.return_value = {"url": "uploaded_url"}

                            # Validate file
                            validation_result = file_manager.validate_file("test.jpg")
                            assert validation_result["file_type"] == "image"

                            # Calculate hash
                            file_hash = file_manager.calculate_file_hash("test.jpg")
                            assert file_hash == "filehash123"

                            # Upload file
                            upload_result = file_manager.upload_file("table123", "test.jpg")
                            assert upload_result["url"] == "uploaded_url"
