"""
File operations examples for NocoDB Simple Client.

This example demonstrates how to work with file attachments in NocoDB,
including uploading, downloading, and managing files in records.
"""

import os
import tempfile
from pathlib import Path

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable, RecordNotFoundException

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"
TABLE_ID = "your-table-id-with-file-field"
FILE_FIELD_NAME = "Document"  # Name of your attachment field


def create_sample_file() -> Path:
    """Create a sample file for testing."""
    temp_dir = Path(tempfile.gettempdir())
    sample_file = temp_dir / "sample_document.txt"

    with sample_file.open("w", encoding="utf-8") as f:
        f.write("This is a sample document for NocoDB testing.\n")
        f.write("Created by the NocoDB Simple Client example.\n")
        f.write(f"Timestamp: {os.getctime}")

    return sample_file


def main():
    """Demonstrate file operations with NocoDB."""

    # Initialize client and table
    client = NocoDBClient(
        base_url=NOCODB_BASE_URL,
        db_auth_token=API_TOKEN,
        timeout=60,  # Longer timeout for file operations
    )

    table = NocoDBTable(client, table_id=TABLE_ID)

    # Create a sample file
    sample_file = create_sample_file()
    print(f"Created sample file: {sample_file}")

    try:
        # Example 1: Create a record with basic data
        print("\n1. Creating a record...")
        record_data = {
            "Name": "File Upload Example",
            "Description": "Testing file attachment functionality",
            "CreatedDate": "2024-01-01",
        }

        record_id = table.insert_record(record_data)
        print(f"   ✓ Created record with ID: {record_id}")

        # Example 2: Attach a file to the record
        print("\n2. Attaching file to record...")
        table.attach_file_to_record(
            record_id=record_id, field_name=FILE_FIELD_NAME, file_path=sample_file
        )
        print("   ✓ File attached successfully")

        # Example 3: Retrieve record with file information
        print("\n3. Retrieving record with file info...")
        record_with_file = table.get_record(
            record_id=record_id, fields=["Id", "Name", FILE_FIELD_NAME]
        )

        if FILE_FIELD_NAME in record_with_file and record_with_file[FILE_FIELD_NAME]:
            file_info = record_with_file[FILE_FIELD_NAME][0]
            print(f"   ✓ File attached: {file_info.get('title')}")
            print(f"   ✓ File size: {file_info.get('size')} bytes")
            print(f"   ✓ File type: {file_info.get('mimetype')}")

        # Example 4: Download the file
        print("\n4. Downloading file from record...")
        download_path = Path(tempfile.gettempdir()) / "downloaded_sample.txt"

        table.download_file_from_record(
            record_id=record_id, field_name=FILE_FIELD_NAME, file_path=download_path
        )
        print(f"   ✓ File downloaded to: {download_path}")

        # Verify download by reading the file
        with download_path.open("r", encoding="utf-8") as f:
            content = f.read()
            print(f"   ✓ Downloaded file content preview: {content[:50]}...")

        # Example 5: Attach multiple files (if you have more files)
        print("\n5. Demonstrating multiple file attachment...")

        # Create additional sample files
        additional_files = []
        for i in range(2):
            temp_file = Path(tempfile.gettempdir()) / f"additional_file_{i}.txt"
            with temp_file.open("w", encoding="utf-8") as f:
                f.write(f"This is additional file number {i+1}")
            additional_files.append(temp_file)

        # Attach multiple files (this will add to existing files, not replace)
        table.attach_files_to_record(
            record_id=record_id, field_name=FILE_FIELD_NAME, file_paths=additional_files
        )
        print(f"   ✓ Attached {len(additional_files)} additional files")

        # Example 6: Download all files from the record
        print("\n6. Downloading all files...")
        download_dir = Path(tempfile.gettempdir()) / "nocodb_downloads"

        table.download_files_from_record(
            record_id=record_id, field_name=FILE_FIELD_NAME, directory=download_dir
        )

        # List downloaded files
        if download_dir.exists():
            downloaded_files = list(download_dir.iterdir())
            print(f"   ✓ Downloaded {len(downloaded_files)} files to {download_dir}")
            for file in downloaded_files:
                print(f"      - {file.name}")

        # Example 7: Remove all files from the record
        print("\n7. Removing all files from record...")
        table.delete_file_from_record(record_id=record_id, field_name=FILE_FIELD_NAME)
        print("   ✓ All files removed from record")

        # Cleanup: Delete the test record
        print("\n8. Cleaning up...")
        table.delete_record(record_id)
        print("   ✓ Test record deleted")

    except RecordNotFoundException as e:
        print(f"❌ Record not found: {e.message}")

    except NocoDBException as e:
        print(f"❌ NocoDB error: {e.error} - {e.message}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        # Clean up temporary files
        try:
            if sample_file.exists():
                sample_file.unlink()

            if download_path.exists():
                download_path.unlink()

            for temp_file in additional_files:
                if temp_file.exists():
                    temp_file.unlink()

        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")

        # Close client
        client.close()
        print("\n✓ Client session closed and cleanup completed")


if __name__ == "__main__":
    main()
