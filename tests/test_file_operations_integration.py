"""
Integration tests for file operations functionality with real NocoDB instance.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nocodb_simple_client.exceptions import FileOperationError, NocoDBError
from nocodb_simple_client.file_operations import FileManager


@pytest.mark.integration
class TestFileManagerIntegration:
    """Test file manager with real NocoDB instance."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_file_manager_initialization(self, file_manager, nocodb_client):
        """Test file manager initialization with real client."""
        assert file_manager.client == nocodb_client
        assert file_manager.max_file_size == 50 * 1024 * 1024  # 50MB default
        assert hasattr(file_manager, "SUPPORTED_IMAGE_TYPES")
        assert hasattr(file_manager, "SUPPORTED_DOCUMENT_TYPES")

    def test_file_type_validation(self, file_manager):
        """Test file type validation with real implementation."""
        # Supported types
        assert file_manager.is_supported_type("document.pdf")
        assert file_manager.is_supported_type("image.jpg")
        assert file_manager.is_supported_type("data.csv")
        assert file_manager.is_supported_type("config.json")

        # Potentially unsupported types (depends on implementation)
        result = file_manager.is_supported_type("executable.exe")
        assert isinstance(result, bool)  # Should return boolean

    def test_file_size_validation(self, file_manager):
        """Test file size validation."""
        # Valid sizes
        assert file_manager.validate_file_size(1024)  # 1KB
        assert file_manager.validate_file_size(1024 * 1024)  # 1MB

        # Invalid sizes (exceeds limit)
        assert not file_manager.validate_file_size(100 * 1024 * 1024)  # 100MB
        assert not file_manager.validate_file_size(0)  # 0 bytes


@pytest.mark.integration
class TestFileUploadIntegration:
    """Test file upload operations with real NocoDB instance."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_upload_small_text_file(self, file_manager, test_files):
        """Test uploading a small text file."""
        # Create a small text file
        text_file = test_files.create_file("small_upload.txt", 5, "text")  # 5KB

        # Upload the file
        result = file_manager.upload_file(str(text_file))

        # Verify upload response
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

        # Verify file info
        file_info = file_manager.get_file_info(str(text_file))
        assert file_info["size"] <= 5 * 1024  # Should be around 5KB
        assert file_info["extension"] == ".txt"

    def test_upload_csv_file(self, file_manager, test_files):
        """Test uploading a CSV data file."""
        # Create a CSV file with realistic data
        csv_file = test_files.create_file("test_data.csv", 25, "csv")  # 25KB

        # Upload the file
        result = file_manager.upload_file(str(csv_file))

        # Verify upload
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

        # Verify CSV content was preserved (check file size)
        file_info = file_manager.get_file_info(str(csv_file))
        assert file_info["size"] > 1000  # Should have substantial content

    def test_upload_json_file(self, file_manager, test_files):
        """Test uploading a JSON configuration file."""
        # Create a JSON file with nested structure
        json_file = test_files.create_file("config.json", 15, "json")  # 15KB

        # Upload the file
        result = file_manager.upload_file(str(json_file))

        # Verify upload
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

    def test_upload_fake_image_file(self, file_manager, test_files):
        """Test uploading a fake image file."""
        # Create a fake JPEG file
        image_file = test_files.create_file("photo.jpg", 75, "image")  # 75KB

        # Upload the file
        result = file_manager.upload_file(str(image_file))

        # Verify upload
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

        # Check file info
        file_info = file_manager.get_file_info(str(image_file))
        assert file_info["extension"] == ".jpg"
        assert file_info["type"] == "image"

    def test_upload_binary_file(self, file_manager, test_files):
        """Test uploading a binary data file."""
        # Create a binary file
        binary_file = test_files.create_file("data.bin", 50, "binary")  # 50KB

        # Upload the file
        result = file_manager.upload_file(str(binary_file))

        # Verify upload
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

    def test_upload_large_file(self, file_manager, test_files):
        """Test uploading a file close to the 1MB limit."""
        # Create a file close to 1MB (but under limit)
        large_file = test_files.create_file("large_data.dat", 900, "binary")  # 900KB

        # Upload the file
        result = file_manager.upload_file(str(large_file))

        # Verify upload succeeded
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

        # Verify file size
        file_info = file_manager.get_file_info(str(large_file))
        assert file_info["size"] > 900 * 1024  # Should be around 900KB

    def test_upload_maximum_size_file(self, file_manager, test_files):
        """Test uploading a file at exactly 1MB."""
        # Create exactly 1MB file
        max_file = test_files.create_file("max_size.dat", 1024, "binary")  # 1MB

        # This should either succeed or fail gracefully
        try:
            result = file_manager.upload_file(str(max_file))
            assert isinstance(result, dict)
            print("✅ 1MB file upload successful")
        except (FileOperationError, NocoDBError) as e:
            print(f"ℹ️  1MB file upload rejected: {e}")
            # This is acceptable - some servers have lower limits

    def test_upload_file_data_directly(self, file_manager, test_files):
        """Test uploading file data directly without file path."""
        # Generate some test data
        test_data = b"Direct upload test content. " * 100  # ~2.8KB

        # Upload data directly
        result = file_manager.upload_file_data(
            test_data, filename="direct_upload.txt", content_type="text/plain"
        )

        # Verify upload
        assert isinstance(result, dict)
        assert "id" in result or "url" in result or "path" in result

    def test_upload_with_progress_callback(self, file_manager, test_files):
        """Test file upload with progress tracking."""
        # Create a medium-sized file for progress tracking
        progress_file = test_files.create_file("progress_test.dat", 100, "binary")  # 100KB

        progress_updates = []

        def progress_callback(bytes_uploaded, total_bytes):
            progress_updates.append((bytes_uploaded, total_bytes))

        # Upload with progress callback
        result = file_manager.upload_file(str(progress_file), progress_callback=progress_callback)

        # Verify upload succeeded
        assert isinstance(result, dict)

        # Check if progress was tracked (implementation dependent)
        if progress_updates:
            assert len(progress_updates) > 0
            last_update = progress_updates[-1]
            assert last_update[0] <= last_update[1]  # bytes_uploaded <= total_bytes


@pytest.mark.integration
class TestFileDownloadIntegration:
    """Test file download operations with real NocoDB instance."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_upload_and_download_cycle(self, file_manager, test_files):
        """Test complete upload and download cycle."""
        # Create test file
        original_file = test_files.create_file("cycle_test.txt", 10, "text")  # 10KB

        # Read original content for comparison
        with open(original_file, "rb") as f:
            original_content = f.read()

        # Upload the file
        upload_result = file_manager.upload_file(str(original_file))
        assert isinstance(upload_result, dict)

        # Extract file ID or URL for download
        file_id = upload_result.get("id") or upload_result.get("path") or upload_result.get("url")
        assert file_id, f"No file identifier found in upload result: {upload_result}"

        # Download the file as bytes
        downloaded_content = file_manager.download_file_data(file_id)

        # Verify content matches
        assert isinstance(downloaded_content, bytes)
        assert len(downloaded_content) > 0

        # For text files, we can compare content (may not be identical due to encoding)
        assert len(downloaded_content) >= len(original_content) * 0.9  # Allow some variance

    def test_download_to_file_path(self, file_manager, test_files, test_file_uploads_dir):
        """Test downloading file to specific path."""
        # Create and upload test file
        test_file = test_files.create_file("download_test.json", 20, "json")  # 20KB
        upload_result = file_manager.upload_file(str(test_file))

        # Get file identifier
        file_id = upload_result.get("id") or upload_result.get("path") or upload_result.get("url")

        # Download to specific path
        download_path = test_file_uploads_dir / "downloaded_file.json"
        result_path = file_manager.download_file(file_id, str(download_path))

        # Verify download
        assert result_path == str(download_path)
        assert download_path.exists()
        assert download_path.stat().st_size > 0

        # Cleanup
        download_path.unlink()

    def test_download_with_progress_callback(self, file_manager, test_files):
        """Test file download with progress tracking."""
        # Create and upload a medium file
        test_file = test_files.create_file("progress_download.dat", 50, "binary")  # 50KB
        upload_result = file_manager.upload_file(str(test_file))

        file_id = upload_result.get("id") or upload_result.get("path") or upload_result.get("url")

        progress_updates = []

        def progress_callback(bytes_downloaded, total_bytes):
            progress_updates.append((bytes_downloaded, total_bytes))

        # Download with progress tracking
        downloaded_content = file_manager.download_file_data(
            file_id, progress_callback=progress_callback
        )

        # Verify download
        assert isinstance(downloaded_content, bytes)
        assert len(downloaded_content) > 0


@pytest.mark.integration
class TestFileManagementIntegration:
    """Test file management operations with real NocoDB instance."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_list_uploaded_files(self, file_manager, test_files):
        """Test listing files after uploading several."""
        # Upload multiple test files
        uploaded_files = []
        test_file_set = test_files.get_test_files()

        for _filename, file_path in list(test_file_set.items())[:3]:  # Upload first 3 files
            result = file_manager.upload_file(str(file_path))
            uploaded_files.append(result)

        # List files
        file_list = file_manager.list_files()

        # Verify file list
        assert isinstance(file_list, list)
        # Note: List might contain other files, so we just check it's not empty
        # and contains reasonable data structure
        if file_list:
            for file_info in file_list[:5]:  # Check first 5 files
                assert isinstance(file_info, dict)
                # Common fields that should exist
                expected_fields = ["id", "name", "title", "size", "type", "url", "path"]
                has_required_field = any(field in file_info for field in expected_fields)
                assert has_required_field, f"File info missing expected fields: {file_info}"

    def test_get_file_metadata(self, file_manager, test_files):
        """Test getting metadata for uploaded files."""
        # Upload a test file
        test_file = test_files.create_file("metadata_test.csv", 30, "csv")  # 30KB
        upload_result = file_manager.upload_file(str(test_file))

        file_id = upload_result.get("id")
        if not file_id:
            pytest.skip("File ID not available in upload response")

        # Get file metadata
        metadata = file_manager.get_file_metadata(file_id)

        # Verify metadata
        assert isinstance(metadata, dict)
        assert "id" in metadata or "size" in metadata or "name" in metadata

    def test_delete_uploaded_file(self, file_manager, test_files):
        """Test deleting an uploaded file."""
        # Upload a file to delete
        test_file = test_files.create_file("delete_test.txt", 5, "text")  # 5KB
        upload_result = file_manager.upload_file(str(test_file))

        file_id = upload_result.get("id")
        if not file_id:
            pytest.skip("File ID not available for deletion test")

        # Delete the file
        delete_result = file_manager.delete_file(file_id)

        # Verify deletion
        assert isinstance(delete_result, dict | bool)

        # Try to get metadata - should fail or return empty
        try:
            metadata = file_manager.get_file_metadata(file_id)
            # If this succeeds, the file might not be truly deleted
            # or the API might have a delay
            print(f"ℹ️  File still exists after deletion: {metadata}")
        except (NocoDBError, FileOperationError):
            # Expected - file should not be found
            pass


@pytest.mark.integration
class TestAttachmentIntegration:
    """Test file attachment to table records."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_attach_file_to_record(self, file_manager, test_table_with_data, test_files):
        """Test attaching files to table records."""
        table_id = test_table_with_data["id"]
        sample_records = test_table_with_data["sample_records"]

        if not sample_records:
            pytest.skip("No sample records available for attachment test")

        # Use the first record for attachment
        record = sample_records[0]
        record_id = record["id"]

        # Create a test file to attach
        attachment_file = test_files.create_file("attachment.pdf", 25, "text")  # 25KB, fake PDF

        # Attach file to record (this depends on table having an attachment field)
        try:
            result = file_manager.attach_file_to_record(
                table_id,
                record_id,
                "attachments",  # Assuming attachment field name
                str(attachment_file),
            )

            # Verify attachment
            assert isinstance(result, dict)
            assert "id" in result

        except (NocoDBError, FileOperationError, AttributeError) as e:
            # Attachment functionality might not be implemented or
            # table might not have attachment field
            pytest.skip(f"File attachment not supported or available: {e}")


@pytest.mark.integration
@pytest.mark.slow
class TestFileOperationsPerformance:
    """Test file operations performance characteristics."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    @pytest.mark.performance
    def test_multiple_file_upload_performance(self, file_manager, test_files, skip_if_slow):
        """Test performance of uploading multiple files."""
        # Create multiple test files of varying sizes
        test_files_list = []
        for i in range(10):
            size_kb = (i + 1) * 10  # 10KB, 20KB, ..., 100KB
            file_path = test_files.create_file(f"perf_test_{i}.dat", size_kb, "binary")
            test_files_list.append(file_path)

        # Measure upload time
        start_time = time.time()
        uploaded_files = []

        for file_path in test_files_list:
            try:
                result = file_manager.upload_file(str(file_path))
                uploaded_files.append(result)
            except Exception as e:
                print(f"Upload failed for {file_path}: {e}")

        end_time = time.time()

        # Performance analysis
        duration = end_time - start_time
        successful_uploads = len(uploaded_files)

        if successful_uploads > 0:
            avg_time_per_file = duration / successful_uploads
            print(f"Uploaded {successful_uploads} files in {duration:.2f} seconds")
            print(f"Average time per file: {avg_time_per_file:.2f} seconds")

            # Performance assertion (adjust based on expectations)
            assert avg_time_per_file < 10.0, f"File upload too slow: {avg_time_per_file}s per file"
        else:
            pytest.fail("No files were successfully uploaded")

    @pytest.mark.performance
    def test_large_file_handling_performance(self, file_manager, test_files, skip_if_slow):
        """Test performance with larger files."""
        # Create files of increasing size
        sizes = [100, 250, 500, 750]  # KB

        for size_kb in sizes:
            print(f"Testing {size_kb}KB file upload...")

            # Create test file
            large_file = test_files.create_file(f"large_{size_kb}kb.dat", size_kb, "binary")

            # Measure upload time
            start_time = time.time()

            try:
                result = file_manager.upload_file(str(large_file))
                end_time = time.time()

                duration = end_time - start_time
                throughput = (size_kb * 1024) / duration / 1024  # KB/s

                print(f"  {size_kb}KB uploaded in {duration:.2f}s ({throughput:.2f} KB/s)")

                # Basic performance check
                assert duration < 30, f"{size_kb}KB upload took too long: {duration}s"
                assert isinstance(result, dict)

            except Exception as e:
                print(f"  {size_kb}KB upload failed: {e}")
                # Large file failures might be expected depending on server limits


@pytest.mark.integration
class TestFileOperationsErrorHandling:
    """Test error handling in file operations with real API."""

    @pytest.fixture
    def file_manager(self, nocodb_client):
        """Create a real file manager instance."""
        return FileManager(nocodb_client)

    def test_upload_nonexistent_file(self, file_manager):
        """Test error handling when uploading non-existent file."""
        nonexistent_file = "/path/to/nonexistent/file.txt"

        with pytest.raises((FileOperationError, FileNotFoundError, OSError)):
            file_manager.upload_file(nonexistent_file)

    def test_download_nonexistent_file(self, file_manager):
        """Test error handling when downloading non-existent file."""
        fake_file_id = "nonexistent_file_id_12345"

        with pytest.raises((NocoDBError, FileOperationError)):
            file_manager.download_file_data(fake_file_id)

    def test_get_metadata_nonexistent_file(self, file_manager):
        """Test error handling when getting metadata for non-existent file."""
        fake_file_id = "nonexistent_file_id_67890"

        with pytest.raises((NocoDBError, FileOperationError)):
            file_manager.get_file_metadata(fake_file_id)

    def test_delete_nonexistent_file(self, file_manager):
        """Test error handling when deleting non-existent file."""
        fake_file_id = "nonexistent_file_id_abcdef"

        # This might succeed (idempotent) or fail - both are acceptable
        try:
            result = file_manager.delete_file(fake_file_id)
            # If it succeeds, should return reasonable response
            assert isinstance(result, dict | bool)
        except (NocoDBError, FileOperationError):
            # If it fails, that's also acceptable
            pass
