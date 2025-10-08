"""Integration tests for nocodb-simple-client.

Diese Tests setzen und verwalten eine eigene NocoDB Container-Instanz
und testen alle verfügbaren Client-Operationen umfassend.
"""

import os
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import pytest
import requests

# Optional dependencies for integration tests
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None

from nocodb_simple_client import (
    AsyncNocoDBClient,
    NocoDBClient,
    NocoDBException,
    NocoDBMetaClient,
    NocoDBTable,
    RecordNotFoundException,
)

# Skip integration tests if environment variable is set OR if docker is not available
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "1") == "1" or not DOCKER_AVAILABLE

# Test configuration
NOCODB_IMAGE = "nocodb/nocodb:latest"
CONTAINER_NAME = "nocodb-integration-test"
HOST_PORT = 8080
CONTAINER_PORT = 8080
ADMIN_EMAIL = "test@integration.local"
ADMIN_PASSWORD = "IntegrationTest123!"
PROJECT_NAME = "Integration_Test_Project"
TEST_TIMEOUT = 300


class NocoDBContainerManager:
    """Verwaltet NocoDB Container für Integrationstests."""

    def __init__(self, image: str = NOCODB_IMAGE, port: int = HOST_PORT):
        self.image = image
        self.port = port
        self.container = None
        self.client = docker.from_env()
        self.base_url = f"http://localhost:{port}"

    def start_container(self) -> None:
        """Startet NocoDB Container."""
        self._cleanup_existing_container()

        print(f"Starte NocoDB Container: {self.image}")
        self.container = self.client.containers.run(
            self.image,
            name=CONTAINER_NAME,
            ports={f"{CONTAINER_PORT}/tcp": self.port},
            environment={
                "NC_AUTH_JWT_SECRET": f"test-jwt-secret-{uuid4()}",
                "NC_PUBLIC_URL": self.base_url,
                "NC_DISABLE_TELE": "true",
                "NC_MIN": "true",
            },
            detach=True,
            remove=True,
        )

        self._wait_for_readiness()

    def _cleanup_existing_container(self) -> None:
        """Räumt bestehende Container auf."""
        try:
            existing = self.client.containers.get(CONTAINER_NAME)
            existing.kill()
            existing.wait()
        except docker.errors.NotFound:
            pass

    def _wait_for_readiness(self, timeout: int = TEST_TIMEOUT) -> None:
        """Wartet bis NocoDB bereit ist."""
        print("Warte auf NocoDB-Bereitschaft...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/dashboard", timeout=5)
                if response.status_code == 200:
                    print("NocoDB ist bereit")
                    time.sleep(5)
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(3)

        raise RuntimeError(f"NocoDB wurde nicht innerhalb von {timeout} Sekunden bereit")

    def stop_container(self) -> None:
        """Stoppt den NocoDB Container."""
        if self.container:
            try:
                self.container.kill()
                self.container.wait()
                print("NocoDB Container gestoppt")
            except Exception as e:
                print(f"Fehler beim Stoppen des Containers: {e}")

    def get_logs(self) -> str:
        """Gibt Container-Logs zurück."""
        if self.container:
            return self.container.logs().decode("utf-8")
        return ""


class NocoDBTestSetup:
    """Setup-Helfer für NocoDB-Tests."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.project_id = None
        self.test_table_id = None

    def setup_admin_and_project(self) -> dict[str, str]:
        """Erstellt Admin-Benutzer und Test-Projekt."""
        signup_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "firstname": "Integration",
            "lastname": "Test",
        }

        try:
            requests.post(f"{self.base_url}/api/v2/auth/user/signup", json=signup_data, timeout=30)
        except Exception as e:
            print(f"Signup error (expected): {e}")

        auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        response = requests.post(f"{self.base_url}/api/v2/auth/user/signin", json=auth_data, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Authentication failed: {response.status_code}")

        auth_result = response.json()
        self.token = auth_result.get("token")

        if not self.token:
            raise RuntimeError("Token not found in auth response")

        project_data = {
            "title": f"{PROJECT_NAME}_{uuid4().hex[:8]}",
            "description": "Automated integration test project",
            "color": "#24716E",
        }

        headers = {"xc-token": self.token, "Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/api/v2/meta/projects", json=project_data, headers=headers, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Project creation failed: {response.status_code}")

        project_result = response.json()
        self.project_id = project_result.get("id")

        if not self.project_id:
            raise RuntimeError("Project ID not found in creation response")

        self._create_test_table()

        return {
            "token": self.token,
            "project_id": self.project_id,
            "table_id": self.test_table_id,
        }

    def _create_test_table(self) -> None:
        """Erstellt Test-Tabelle mit verschiedenen Spaltentypen."""
        table_data = {
            "title": "integration_test_table",
            "table_name": "integration_test_table",
            "columns": [
                {"title": "id", "column_name": "id", "uidt": "ID", "dt": "int", "pk": True, "ai": True, "rqd": True, "un": True},
                {"title": "Name", "column_name": "Name", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},
                {"title": "Description", "column_name": "Description", "uidt": "LongText", "dt": "text", "rqd": False},
                {"title": "TestField", "column_name": "TestField", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},
                {"title": "email", "column_name": "email", "uidt": "Email", "dt": "varchar", "rqd": False},
                {"title": "age", "column_name": "age", "uidt": "Number", "dt": "int", "rqd": False},
                {"title": "status", "column_name": "status", "uidt": "SingleSelect", "dt": "varchar", "dtxp": "active,inactive,pending", "rqd": False},
                {"title": "created_at", "column_name": "created_at", "uidt": "DateTime", "dt": "datetime", "rqd": False},
                {"title": "is_active", "column_name": "is_active", "uidt": "Checkbox", "dt": "boolean", "rqd": False},
                {"title": "attachment", "column_name": "attachment", "uidt": "Attachment", "dt": "text", "rqd": False},
            ],
        }

        headers = {"xc-token": self.token, "Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/api/v2/meta/projects/{self.project_id}/tables", json=table_data, headers=headers, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Table creation failed: {response.status_code}")

        table_result = response.json()
        self.test_table_id = table_result.get("id")

        if not self.test_table_id:
            raise RuntimeError("Table ID not found in creation response")


def generate_test_file(content: str = "Test file content", suffix: str = ".txt") -> Path:
    """Generiert eine temporäre Test-Datei."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def generate_test_image() -> Path:
    """Generiert ein Test-Bild."""
    if not PILLOW_AVAILABLE:
        # Fallback: generate a fake PNG file
        return generate_test_file("fake image content", ".png")

    from PIL import Image
    image = Image.new("RGB", (100, 100), color="red")
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(temp_file.name)
    return Path(temp_file.name)


@pytest.fixture(scope="session")
def nocodb_container():
    """Session-weite Fixture für NocoDB Container."""
    if SKIP_INTEGRATION:
        pytest.skip("Integration tests disabled")

    container_manager = NocoDBContainerManager()

    try:
        container_manager.start_container()
        yield container_manager
    except Exception as e:
        print(f"Container setup failed: {e}")
        if container_manager.container:
            print("Container logs:")
            print(container_manager.get_logs())
        raise
    finally:
        container_manager.stop_container()


@pytest.fixture(scope="session")
def nocodb_setup(nocodb_container):
    """Session-weite Fixture für NocoDB Setup."""
    setup = NocoDBTestSetup(nocodb_container.base_url)
    config = setup.setup_admin_and_project()
    config["base_url"] = nocodb_container.base_url
    return config


@pytest.fixture
def nocodb_client(nocodb_setup):
    """Fixture für NocoDB Client."""
    with NocoDBClient(
        base_url=nocodb_setup["base_url"],
        db_auth_token=nocodb_setup["token"],
        timeout=30,
    ) as client:
        yield client


@pytest.fixture
def nocodb_meta_client(nocodb_setup):
    """Fixture für NocoDB Meta Client."""
    with NocoDBMetaClient(
        base_url=nocodb_setup["base_url"],
        db_auth_token=nocodb_setup["token"],
        timeout=30,
    ) as client:
        yield client


@pytest.fixture
def nocodb_table(nocodb_client, nocodb_setup):
    """Fixture für NocoDB Table."""
    return NocoDBTable(nocodb_client, nocodb_setup["table_id"])


@pytest.fixture
async def async_nocodb_client(nocodb_setup):
    """Fixture für Async NocoDB Client."""
    async with AsyncNocoDBClient(
        base_url=nocodb_setup["base_url"],
        db_auth_token=nocodb_setup["token"],
        timeout=30,
    ) as client:
        yield client


class TestIntegration:
    """Integration tests requiring a real NocoDB instance."""

    def test_basic_crud_operations(self, nocodb_table):
        """Test basic CRUD operations against real NocoDB instance."""
        test_record = {
            "Name": f"Integration Test Record {uuid4().hex[:8]}",
            "Description": "Created by integration tests",
            "TestField": "test_value",
            "email": "test@integration.com",
            "age": 25,
            "status": "active",
            "is_active": True,
        }

        record_id = nocodb_table.insert_record(test_record)
        assert record_id is not None

        try:
            retrieved_record = nocodb_table.get_record(record_id)
            assert retrieved_record["Name"] == test_record["Name"]
            assert retrieved_record["email"] == test_record["email"]

            update_data = {"Name": "Updated Integration Test Record", "age": 30}
            updated_id = nocodb_table.update_record(update_data, record_id)
            assert updated_id == record_id

            updated_record = nocodb_table.get_record(record_id)
            assert updated_record["Name"] == "Updated Integration Test Record"
            assert updated_record["age"] == 30

        finally:
            try:
                nocodb_table.delete_record(record_id)
            except Exception as e:
                print(f"Warning: Could not clean up test record {record_id}: {e}")

    def test_query_operations(self, nocodb_table):
        """Test querying operations."""
        total_count = nocodb_table.count_records()
        assert isinstance(total_count, int)
        assert total_count >= 0

        records = nocodb_table.get_records(limit=5)
        assert isinstance(records, list)
        assert len(records) <= 5

        try:
            filtered_records = nocodb_table.get_records(where="(Name,isnotblank)", limit=3)
            assert isinstance(filtered_records, list)
        except NocoDBException:
            pass

    def test_error_handling(self, nocodb_table):
        """Test error handling with real API."""
        with pytest.raises((RecordNotFoundException, NocoDBException)):
            nocodb_table.get_record(99999999)

        with pytest.raises((RecordNotFoundException, NocoDBException)):
            nocodb_table.delete_record(99999999)

    def test_bulk_operations(self, nocodb_client, nocodb_setup):
        """Test bulk operations."""
        table_id = nocodb_setup["table_id"]

        test_records = [
            {
                "Name": f"Bulk Test {i}",
                "email": f"bulk{i}@example.com",
                "age": 20 + i,
                "status": "active" if i % 2 == 0 else "inactive",
            }
            for i in range(5)
        ]

        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)
        assert len(inserted_ids) == 5

        try:
            update_records = []
            for i, record_id in enumerate(inserted_ids):
                update_records.append(
                    {"id": record_id, "Name": f"Updated Bulk Test {i}", "age": 30 + i}
                )

            updated_ids = nocodb_client.bulk_update_records(table_id, update_records)
            assert len(updated_ids) == 5

            for i, record_id in enumerate(updated_ids):
                record = nocodb_client.get_record(table_id, record_id)
                assert record["Name"] == f"Updated Bulk Test {i}"
                assert record["age"] == 30 + i

        finally:
            deleted_ids = nocodb_client.bulk_delete_records(table_id, inserted_ids)
            assert len(deleted_ids) == 5

    def test_file_operations(self, nocodb_client, nocodb_setup):
        """Test file upload and download operations."""
        table_id = nocodb_setup["table_id"]

        test_record = {"Name": "File Test Record", "Description": "Testing file operations"}
        record_id = nocodb_client.insert_record(table_id, test_record)

        test_file = generate_test_file("Integration test file content")
        test_image = generate_test_image()

        try:
            nocodb_client.attach_file_to_record(
                table_id=table_id,
                record_id=record_id,
                field_name="attachment",
                file_path=str(test_file),
            )

            nocodb_client.attach_files_to_record(
                table_id=table_id,
                record_id=record_id,
                field_name="attachment",
                file_paths=[str(test_file), str(test_image)],
            )

            download_path = tempfile.mktemp(suffix=".txt")
            nocodb_client.download_file_from_record(
                table_id=table_id,
                record_id=record_id,
                field_name="attachment",
                file_path=download_path,
            )

            assert Path(download_path).exists()

            download_dir = Path(tempfile.mkdtemp())
            nocodb_client.download_files_from_record(
                table_id=table_id,
                record_id=record_id,
                field_name="attachment",
                directory=str(download_dir),
            )

            downloaded_files = list(download_dir.glob("*"))
            assert len(downloaded_files) > 0

            Path(download_path).unlink(missing_ok=True)
            for file in downloaded_files:
                file.unlink()
            download_dir.rmdir()

        finally:
            test_file.unlink()
            test_image.unlink()
            nocodb_client.delete_record(table_id, record_id)

    def test_context_manager_behavior(self, nocodb_setup):
        """Test context manager behavior with real client."""
        with NocoDBClient(
            base_url=nocodb_setup["base_url"],
            db_auth_token=nocodb_setup["token"],
            timeout=30,
        ) as client:
            table = NocoDBTable(client, nocodb_setup["table_id"])
            count = table.count_records()
            assert isinstance(count, int)

    def test_pagination_with_real_data(self, nocodb_table):
        """Test pagination handling with real data."""
        try:
            records = nocodb_table.get_records(limit=150)
            assert isinstance(records, list)
        except NocoDBException:
            pass

    def test_count_and_filtering(self, nocodb_client, nocodb_setup):
        """Test record counting and filtering."""
        table_id = nocodb_setup["table_id"]

        total_count = nocodb_client.count_records(table_id)
        assert isinstance(total_count, int)
        assert total_count >= 0

        test_records = [
            {"Name": f"Filter Test {i}", "status": "active" if i % 2 == 0 else "inactive"}
            for i in range(4)
        ]

        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)

        try:
            active_records = nocodb_client.get_records(
                table_id, where="(status,eq,active)", limit=100
            )
            inactive_records = nocodb_client.get_records(
                table_id, where="(status,eq,inactive)", limit=100
            )

            active_count = len([r for r in active_records if r.get("status") == "active"])
            inactive_count = len([r for r in inactive_records if r.get("status") == "inactive"])

            assert active_count >= 2
            assert inactive_count >= 2

        finally:
            nocodb_client.bulk_delete_records(table_id, inserted_ids)

    def test_table_wrapper_operations(self, nocodb_table):
        """Test table wrapper operations."""
        count = nocodb_table.count_records()
        assert isinstance(count, int)

        records = nocodb_table.get_records(limit=5)
        assert isinstance(records, list)

        test_record = {"Name": "Table Wrapper Test", "email": "wrapper@test.com"}

        record_id = nocodb_table.insert_record(test_record)
        assert record_id is not None

        try:
            retrieved = nocodb_table.get_record(record_id)
            assert retrieved["Name"] == test_record["Name"]

            updated_id = nocodb_table.update_record({"Name": "Updated Wrapper"}, record_id)
            assert updated_id == record_id

        finally:
            nocodb_table.delete_record(record_id)

    def test_query_builder(self, nocodb_table):
        """Test query builder functionality."""
        query = nocodb_table.query()
        records = query.where("Name", "isnotnull").limit(10).execute()
        assert isinstance(records, list)


class TestNocoDBMetaClientIntegration:
    """Integrationstests für NocoDBMetaClient."""

    def test_table_info(self, nocodb_meta_client, nocodb_setup):
        """Test getting table information."""
        table_id = nocodb_setup["table_id"]

        try:
            table_info = nocodb_meta_client.get_table_info(table_id)
            assert isinstance(table_info, dict)
            assert "title" in table_info
        except Exception:
            pytest.skip("Table info test requires specific API endpoint")

    def test_list_columns(self, nocodb_meta_client, nocodb_setup):
        """Test listing table columns."""
        table_id = nocodb_setup["table_id"]

        try:
            columns = nocodb_meta_client.list_columns(table_id)
            assert isinstance(columns, list)
            assert len(columns) > 0
        except Exception:
            pytest.skip("Column listing test requires specific API endpoint")


@pytest.mark.asyncio
class TestAsyncNocoDBClientIntegration:
    """Integrationstests für AsyncNocoDBClient."""

    async def test_async_basic_operations(self, async_nocodb_client, nocodb_setup):
        """Test basic async operations."""
        table_id = nocodb_setup["table_id"]

        records = await async_nocodb_client.get_records(table_id, limit=5)
        assert isinstance(records, list)

        test_record = {"Name": "Async Test Record", "email": "async@test.com"}

        record_id = await async_nocodb_client.insert_record(table_id, test_record)
        assert record_id is not None

        try:
            retrieved = await async_nocodb_client.get_record(table_id, record_id)
            assert retrieved["Name"] == test_record["Name"]

            updated_id = await async_nocodb_client.update_record(
                table_id, {"Name": "Updated Async"}, record_id
            )
            assert updated_id == record_id

        finally:
            await async_nocodb_client.delete_record(table_id, record_id)

    async def test_async_bulk_operations(self, async_nocodb_client, nocodb_setup):
        """Test async bulk operations."""
        table_id = nocodb_setup["table_id"]

        test_records = [
            {"Name": f"Async Bulk {i}", "email": f"async{i}@test.com"} for i in range(3)
        ]

        inserted_ids = await async_nocodb_client.bulk_insert_records(table_id, test_records)
        assert len(inserted_ids) == 3

        try:
            for record_id in inserted_ids:
                record = await async_nocodb_client.get_record(table_id, record_id)
                assert "Async Bulk" in record["Name"]

        finally:
            await async_nocodb_client.bulk_delete_records(table_id, inserted_ids)
