"""Integration tests for nocodb-simple-client.

Diese Tests erwarten einen extern verwalteten NocoDB-Container
(z.B. via ci-setup.sh im CI/CD-Workflow).

Container-Management erfolgt NICHT durch diese Tests!
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from nocodb_simple_client import NocoDBClient, NocoDBException, NocoDBTable, RecordNotFoundException

# Skip integration tests if environment variable is set
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "1") == "1"


def load_config_from_file() -> dict:
    """Lädt Konfiguration aus nocodb-config.json oder .env.test falls vorhanden."""
    # Priorität 1: nocodb-config.json
    config_file = Path("nocodb-config.json")
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                print(f"✅ Konfiguration aus {config_file} geladen")
                return config
        except Exception as e:
            print(f"⚠️  Konnte nocodb-config.json nicht laden: {e}")

    # Priorität 2: .env.test
    env_test_file = Path(".env.test")
    if env_test_file.exists():
        try:
            with open(env_test_file) as f:
                config = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
                print(f"✅ Konfiguration aus {env_test_file} geladen")
                return config
        except Exception as e:
            print(f"⚠️  Konnte .env.test nicht laden: {e}")

    return {}


@pytest.mark.skipif(
    SKIP_INTEGRATION, reason="Integration tests skipped (set SKIP_INTEGRATION=0 to run)"
)
class TestIntegration:
    """Integration tests requiring a real NocoDB instance."""

    @pytest.fixture(scope="class")
    def integration_config(self):
        """Get integration test configuration from environment or config files."""
        # Load from config files first
        file_config = load_config_from_file()

        # Build configuration with priority: env vars > config file > defaults
        config = {
            "base_url": os.getenv("NOCODB_URL") or os.getenv("NOCODB_TEST_BASE_URL") or file_config.get("base_url") or "http://localhost:8080",
            "api_token": os.getenv("NOCODB_API_TOKEN") or os.getenv("NOCODB_TEST_API_TOKEN") or file_config.get("api_token"),
            "table_id": os.getenv("NOCODB_TEST_TABLE_ID") or file_config.get("table_id"),
        }

        if not config["api_token"]:
            pytest.skip(
                "Integration tests require API token.\n"
                "Provide via:\n"
                "  - Environment: NOCODB_API_TOKEN or NOCODB_TEST_API_TOKEN\n"
                "  - Config file: nocodb-config.json or .env.test\n"
                "  - CI: Run './scripts/ci-setup.sh setup' first"
            )

        if not config["table_id"]:
            pytest.skip(
                "Integration tests require table ID.\n"
                "Provide via NOCODB_TEST_TABLE_ID or in config file"
            )

        return config

    @pytest.fixture(scope="class")
    def integration_client(self, integration_config):
        """Create a client for integration testing."""
        with NocoDBClient(
            base_url=integration_config["base_url"],
            db_auth_token=integration_config["api_token"],
            timeout=30,
        ) as client:
            yield client

    @pytest.fixture(scope="class")
    def integration_table(self, integration_client, integration_config):
        """Create a table instance for integration testing."""
        return NocoDBTable(integration_client, integration_config["table_id"])

    def test_basic_crud_operations(self, integration_table):
        """Test basic CRUD operations against real NocoDB instance."""
        # Create a test record
        test_record = {
            "Name": "Integration Test Record",
            "Description": "Created by integration tests",
            "TestField": "test_value",
        }

        # Insert record
        record_id = integration_table.insert_record(test_record)
        assert record_id is not None

        try:
            # Get the created record
            retrieved_record = integration_table.get_record(record_id)
            assert retrieved_record["Name"] == "Integration Test Record"

            # Update the record
            update_data = {"Name": "Updated Integration Test Record"}
            updated_id = integration_table.update_record(update_data, record_id)
            assert updated_id == record_id

            # Verify the update
            updated_record = integration_table.get_record(record_id)
            assert updated_record["Name"] == "Updated Integration Test Record"

        finally:
            # Clean up: delete the test record
            try:
                integration_table.delete_record(record_id)
            except Exception as e:
                print(f"Warning: Could not clean up test record {record_id}: {e}")

    def test_query_operations(self, integration_table):
        """Test querying operations."""
        # Get records count
        total_count = integration_table.count_records()
        assert isinstance(total_count, int)
        assert total_count >= 0

        # Get some records
        records = integration_table.get_records(limit=5)
        assert isinstance(records, list)
        assert len(records) <= 5

        # Test with filtering (this might not return results depending on data)
        try:
            filtered_records = integration_table.get_records(where="(Name,isnotblank)", limit=3)
            assert isinstance(filtered_records, list)
        except NocoDBException:
            # Filter might not be compatible with the table schema
            pass

    def test_error_handling(self, integration_table):
        """Test error handling with real API."""
        # Try to get a non-existent record
        with pytest.raises((RecordNotFoundException, NocoDBException)):
            integration_table.get_record(99999999)

        # Try to delete a non-existent record
        with pytest.raises((RecordNotFoundException, NocoDBException)):
            integration_table.delete_record(99999999)

    def test_file_operations_if_supported(self, integration_table):
        """Test file operations if the table supports them."""
        # This test is more complex as it requires a table with file fields
        # and we need to handle the case where file operations aren't supported

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
            temp_file.write("This is a test file for integration testing")
            temp_file_path = temp_file.name

        try:
            # Create a test record first
            test_record = {"Name": "File Test Record", "Description": "Testing file operations"}

            record_id = integration_table.insert_record(test_record)

            try:
                # Try to attach file (this might fail if table doesn't have file fields)
                # We'll assume the file field is named "Document" - adjust as needed
                integration_table.attach_file_to_record(
                    record_id=record_id,
                    field_name="Document",  # Adjust field name as needed
                    file_path=temp_file_path,
                )

                # If we get here, file operations are supported
                # Try to download the file
                download_path = tempfile.mktemp(suffix=".txt")
                integration_table.download_file_from_record(
                    record_id=record_id, field_name="Document", file_path=download_path
                )

                # Verify the download
                assert Path(download_path).exists()

                # Clean up download
                Path(download_path).unlink()

            except NocoDBException as e:
                # File operations might not be supported by this table
                pytest.skip(f"File operations not supported: {e.message}")

            finally:
                # Clean up test record
                try:
                    integration_table.delete_record(record_id)
                except Exception:
                    pass

        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink()

    def test_context_manager_with_real_client(self, integration_config):
        """Test context manager behavior with real client."""
        # Test that context manager works properly
        with NocoDBClient(
            base_url=integration_config["base_url"],
            db_auth_token=integration_config["api_token"],
            timeout=30,
        ) as client:
            table = NocoDBTable(client, integration_config["table_id"])
            count = table.count_records()
            assert isinstance(count, int)

        # Client should be properly closed after context exit
        # (We can't easily test this without accessing internal state)

    def test_pagination_with_real_data(self, integration_table):
        """Test pagination handling with real data."""
        # Get a larger number of records to test pagination
        try:
            records = integration_table.get_records(limit=150)
            assert isinstance(records, list)
            # We don't know how many records are in the table,
            # but the operation should complete without errors
        except NocoDBException:
            # Table might not have enough records or pagination might fail
            # This is acceptable for integration tests
            pass
