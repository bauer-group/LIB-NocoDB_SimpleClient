"""Enhanced file operations for NocoDB attachments.

MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import mimetypes
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

if TYPE_CHECKING:
    from .client import NocoDBClient


class FileManager:
    """Advanced file operations manager for NocoDB attachments."""

    SUPPORTED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
    SUPPORTED_DOCUMENT_TYPES = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}
    SUPPORTED_ARCHIVE_TYPES = {".zip", ".rar", ".7z", ".tar", ".gz"}

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self, client: "NocoDBClient") -> None:
        """Initialize the file manager.

        Args:
            client: NocoDBClient instance
        """
        self.client = client

    def validate_file(self, file_path: str | Path) -> dict[str, Any]:
        """Validate file before upload.

        Args:
            file_path: Path to the file to validate

        Returns:
            Dictionary with file information

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})")

        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        # Get file info
        mime_type, _ = mimetypes.guess_type(str(file_path))
        extension = file_path.suffix.lower()

        file_type = "other"
        if extension in self.SUPPORTED_IMAGE_TYPES:
            file_type = "image"
        elif extension in self.SUPPORTED_DOCUMENT_TYPES:
            file_type = "document"
        elif extension in self.SUPPORTED_ARCHIVE_TYPES:
            file_type = "archive"

        return {
            "path": file_path,
            "name": file_path.name,
            "size": file_size,
            "extension": extension,
            "mime_type": mime_type,
            "file_type": file_type,
            "is_supported": file_type != "other",
        }

    def calculate_file_hash(self, file_path: str | Path, algorithm: str = "sha256") -> str:
        """Calculate hash of a file.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use

        Returns:
            Hex digest of the file hash
        """
        file_path = Path(file_path)
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def upload_file(
        self, table_id: str, file_path: str | Path, validate: bool = True
    ) -> dict[str, Any]:
        """Upload file to NocoDB.

        Args:
            table_id: ID of the table
            file_path: Path to the file to upload
            validate: Whether to validate the file before upload

        Returns:
            Upload response from NocoDB

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
            NocoDBException: For API errors
        """
        if validate:
            file_info = self.validate_file(file_path)
            file_path = file_info["path"]
        else:
            file_path = Path(file_path)

        result = self.client._upload_file(table_id, file_path)
        return result if isinstance(result, dict) else {}

    def upload_files_batch(
        self,
        table_id: str,
        file_paths: list[str | Path],
        validate: bool = True,
        skip_errors: bool = False,
    ) -> list[dict[str, Any]]:
        """Upload multiple files in batch.

        Args:
            table_id: ID of the table
            file_paths: List of file paths to upload
            validate: Whether to validate files before upload
            skip_errors: Whether to skip files that fail validation/upload

        Returns:
            List of upload responses

        Raises:
            ValueError: If validation fails and skip_errors is False
        """
        results = []

        for file_path in file_paths:
            try:
                result = self.upload_file(table_id, file_path, validate)
                results.append(result)
            except Exception as e:
                if skip_errors:
                    results.append({"error": str(e), "file_path": str(file_path)})
                else:
                    raise

        return results

    def attach_files_to_record(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        file_paths: list[str | Path],
        append: bool = True,
        validate: bool = True,
    ) -> int | str:
        """Attach multiple files to a record.

        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_name: Name of the attachment field
            file_paths: List of file paths to attach
            append: Whether to append to existing attachments or replace
            validate: Whether to validate files before upload

        Returns:
            The ID of the updated record
        """
        # Upload all files first
        uploaded_files = []
        for file_path in file_paths:
            try:
                upload_response = self.upload_file(table_id, file_path, validate)
                uploaded_files.append(upload_response)
            except Exception:
                if not validate:
                    raise
                # Skip invalid files if validation is disabled
                continue

        if not uploaded_files:
            raise ValueError("No valid files to attach")

        # Get existing attachments if appending
        existing_attachments = []
        if append:
            try:
                record = self.client.get_record(table_id, record_id, fields=[field_name])
                existing_attachments = record.get(field_name, [])
                if not isinstance(existing_attachments, list):
                    existing_attachments = []
            except Exception:
                # If we can't get existing attachments, just use new ones
                existing_attachments = []

        # Combine existing and new attachments
        all_attachments = existing_attachments + uploaded_files

        # Update the record
        record_update = {field_name: all_attachments}
        return self.client.update_record(table_id, record_update, record_id)

    def download_file(
        self,
        file_url: str,
        save_path: str | Path,
        create_dirs: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """Download file from URL.

        Args:
            file_url: URL of the file to download
            save_path: Path where to save the file
            create_dirs: Whether to create parent directories
            overwrite: Whether to overwrite existing file

        Returns:
            Path to the downloaded file

        Raises:
            FileExistsError: If file exists and overwrite is False
            OSError: For file system errors
        """
        save_path = Path(save_path)

        if save_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {save_path}")

        if create_dirs:
            save_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the client's existing download functionality
        # Note: This method doesn't exist directly, we need to implement it
        response = self.client._session.get(file_url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return save_path

    def download_record_attachments(
        self,
        table_id: str,
        record_id: int | str,
        field_name: str,
        download_dir: str | Path,
        create_dirs: bool = True,
        organize_by_record: bool = True,
    ) -> list[Path]:
        """Download all attachments from a record field.

        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_name: Name of the attachment field
            download_dir: Directory to save files
            create_dirs: Whether to create directories
            organize_by_record: Whether to create subdirectory for this record

        Returns:
            List of paths to downloaded files
        """
        download_dir = Path(download_dir)

        if organize_by_record:
            download_dir = download_dir / f"record_{record_id}"

        if create_dirs:
            download_dir.mkdir(parents=True, exist_ok=True)

        # Get record attachments
        record = self.client.get_record(table_id, record_id, fields=[field_name])
        attachments = record.get(field_name, [])

        if not isinstance(attachments, list):
            attachments = []

        downloaded_files = []

        for i, attachment in enumerate(attachments):
            if isinstance(attachment, dict) and "url" in attachment:
                file_name = attachment.get("title") or f"attachment_{i}"
                # Ensure unique filename
                save_path = download_dir / file_name
                counter = 1
                while save_path.exists():
                    name_parts = file_name.rsplit(".", 1)
                    if len(name_parts) == 2:
                        new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                    else:
                        new_name = f"{file_name}_{counter}"
                    save_path = download_dir / new_name
                    counter += 1

                try:
                    downloaded_path = self.download_file(
                        attachment["url"], save_path, create_dirs=False, overwrite=True
                    )
                    downloaded_files.append(downloaded_path)
                except Exception:
                    # Skip failed downloads  # nosec B112
                    continue

        return downloaded_files

    def bulk_download_attachments(
        self,
        table_id: str,
        record_ids: list[int | str],
        field_name: str,
        download_dir: str | Path,
        max_concurrent: int = 5,
    ) -> dict[int | str, list[Path]]:
        """Download attachments from multiple records.

        Args:
            table_id: ID of the table
            record_ids: List of record IDs
            field_name: Name of the attachment field
            download_dir: Directory to save files
            max_concurrent: Maximum concurrent downloads

        Returns:
            Dictionary mapping record IDs to lists of downloaded file paths
        """
        results = {}

        for record_id in record_ids:
            try:
                downloaded_files = self.download_record_attachments(
                    table_id, record_id, field_name, download_dir, organize_by_record=True
                )
                results[record_id] = downloaded_files
            except Exception:
                results[record_id] = []

        return results

    def cleanup_temp_files(self, temp_dir: str | Path | None = None) -> int:
        """Clean up temporary files.

        Args:
            temp_dir: Temporary directory to clean (uses system temp if None)

        Returns:
            Number of files cleaned up
        """
        if temp_dir is None:
            temp_dir = Path(tempfile.gettempdir()) / "nocodb_simple_client"
        else:
            temp_dir = Path(temp_dir)

        if not temp_dir.exists():
            return 0

        files_cleaned = 0

        try:
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        files_cleaned += 1
                    except OSError:
                        continue
                elif file_path.is_dir():
                    try:
                        shutil.rmtree(file_path)
                        files_cleaned += 1
                    except OSError:
                        continue
        except OSError:
            pass

        return files_cleaned

    def get_attachment_info(
        self, table_id: str, record_id: int | str, field_name: str
    ) -> list[dict[str, Any]]:
        """Get detailed information about record attachments.

        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_name: Name of the attachment field

        Returns:
            List of attachment info dictionaries
        """
        record = self.client.get_record(table_id, record_id, fields=[field_name])
        attachments = record.get(field_name, [])

        if not isinstance(attachments, list):
            return []

        attachment_info = []

        for attachment in attachments:
            if isinstance(attachment, dict):
                url = attachment.get("url", "")
                title = attachment.get("title", "")

                info = {
                    "title": title,
                    "url": url,
                    "size": attachment.get("size"),
                    "mimetype": attachment.get("mimetype"),
                }

                # Extract file extension from title or URL
                if title:
                    info["extension"] = Path(title).suffix.lower()
                elif url:
                    parsed_url = urlparse(url)
                    info["extension"] = Path(parsed_url.path).suffix.lower()
                else:
                    info["extension"] = ""

                # Determine file type
                extension = info["extension"]
                if extension in self.SUPPORTED_IMAGE_TYPES:
                    info["file_type"] = "image"
                elif extension in self.SUPPORTED_DOCUMENT_TYPES:
                    info["file_type"] = "document"
                elif extension in self.SUPPORTED_ARCHIVE_TYPES:
                    info["file_type"] = "archive"
                else:
                    info["file_type"] = "other"

                attachment_info.append(info)

        return attachment_info

    def create_attachment_summary(
        self, table_id: str, field_name: str, where: str | None = None
    ) -> dict[str, Any]:
        """Create summary of attachments across records.

        Args:
            table_id: ID of the table
            field_name: Name of the attachment field
            where: Filter condition for records

        Returns:
            Summary dictionary with attachment statistics
        """
        # Get all records with attachments
        records = self.client.get_records(
            table_id, fields=[field_name, "Id"], where=where, limit=1000
        )

        summary: dict[str, Any] = {
            "total_records": len(records),
            "records_with_attachments": 0,
            "total_attachments": 0,
            "file_types": {},
            "total_size": 0,
            "largest_file": None,
            "most_attachments_record": None,
            "max_attachments_count": 0,
        }

        for record_data in records:
            if not isinstance(record_data, dict):
                continue
            attachments = record_data.get(field_name, [])
            if not isinstance(attachments, list):
                continue

            if attachments:
                summary["records_with_attachments"] += 1
                attachment_count = len(attachments)
                summary["total_attachments"] += attachment_count

                if attachment_count > summary["max_attachments_count"]:
                    summary["max_attachments_count"] = attachment_count
                    summary["most_attachments_record"] = record_data.get("Id")

                for attachment in attachments:
                    if isinstance(attachment, dict):
                        # Track file types
                        title = attachment.get("title", "")
                        if title:
                            extension = Path(title).suffix.lower()
                            if extension in self.SUPPORTED_IMAGE_TYPES:
                                file_type = "image"
                            elif extension in self.SUPPORTED_DOCUMENT_TYPES:
                                file_type = "document"
                            elif extension in self.SUPPORTED_ARCHIVE_TYPES:
                                file_type = "archive"
                            else:
                                file_type = "other"

                            summary["file_types"][file_type] = (
                                summary["file_types"].get(file_type, 0) + 1
                            )

                        # Track file sizes
                        size = attachment.get("size")
                        if size and isinstance(size, int | float):
                            summary["total_size"] += size
                            if (
                                summary["largest_file"] is None
                                or size > summary["largest_file"]["size"]
                            ):
                                summary["largest_file"] = {
                                    "title": title,
                                    "size": size,
                                    "record_id": record_data.get("Id"),
                                }

        return summary


class TableFileManager:
    """Helper class for managing files on a specific table."""

    def __init__(self, file_manager: FileManager, table_id: str) -> None:
        """Initialize table-specific file manager.

        Args:
            file_manager: FileManager instance
            table_id: ID of the table
        """
        self._file_manager = file_manager
        self._table_id = table_id

    def upload_file(self, file_path: str | Path, **kwargs: Any) -> dict[str, Any]:
        """Upload file to this table."""
        return self._file_manager.upload_file(self._table_id, file_path, **kwargs)

    def attach_files_to_record(
        self,
        record_id: int | str,
        field_name: str,
        file_paths: list[str | Path],
        **kwargs: Any,
    ) -> int | str:
        """Attach files to a record in this table."""
        return self._file_manager.attach_files_to_record(
            self._table_id, record_id, field_name, file_paths, **kwargs
        )

    def download_record_attachments(
        self, record_id: int | str, field_name: str, download_dir: str | Path, **kwargs: Any
    ) -> list[Path]:
        """Download attachments from a record in this table."""
        return self._file_manager.download_record_attachments(
            self._table_id, record_id, field_name, download_dir, **kwargs
        )

    def get_attachment_info(self, record_id: int | str, field_name: str) -> list[dict[str, Any]]:
        """Get attachment info for a record in this table."""
        return self._file_manager.get_attachment_info(self._table_id, record_id, field_name)

    def create_attachment_summary(
        self, field_name: str, where: str | None = None
    ) -> dict[str, Any]:
        """Create attachment summary for this table."""
        return self._file_manager.create_attachment_summary(self._table_id, field_name, where)
