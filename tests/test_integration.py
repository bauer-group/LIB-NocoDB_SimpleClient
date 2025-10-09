""""""Integration tests for nocodb-simple-client."""Integration tests for nocodb-simple-client.

Integration tests for nocodb-simple-client.



Diese Tests erwarten einen extern verwalteten NocoDB-Container

(z.B. via ci-setup.sh im CI/CD-Workflow).Diese Tests erwarten einen extern verwalteten NocoDB-ContainerDiese Tests setzen und verwalten eine eigene NocoDB Container-Instanz



Container-Management erfolgt NICHT durch diese Tests!(z.B. via ci-setup.sh im CI/CD-Workflow).und testen alle verfügbaren Client-Operationen umfassend.

"""

"""

import json

import osContainer-Management erfolgt NICHT durch diese Tests!

import tempfile

from pathlib import Path"""import os

from uuid import uuid4

import tempfile

import pytest

import requestsimport jsonimport time



# Optional dependenciesimport osfrom pathlib import Path

try:

    from PIL import Imageimport tempfilefrom uuid import uuid4

    PILLOW_AVAILABLE = True

except ImportError:from pathlib import Path

    PILLOW_AVAILABLE = False

    Image = Nonefrom uuid import uuid4import pytest



from nocodb_simple_client import (import requests

    AsyncNocoDBClient,

    NocoDBClient,import pytest

    NocoDBException,

    NocoDBMetaClient,import requests# Optional dependencies for integration tests

    NocoDBTable,

    RecordNotFoundException,try:

)

# Optional dependencies    import docker

# Skip integration tests if environment variable is set

SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "1") == "1"try:    DOCKER_AVAILABLE = True



# Load configuration from environment or config file    from PIL import Imageexcept ImportError:

NOCODB_URL = os.getenv("NOCODB_URL", "http://localhost:8080")

NOCODB_TOKEN = os.getenv("NOCODB_API_TOKEN")    PILLOW_AVAILABLE = True    DOCKER_AVAILABLE = False

ADMIN_EMAIL = os.getenv("NC_ADMIN_EMAIL", "test@integration.local")

ADMIN_PASSWORD = os.getenv("NC_ADMIN_PASSWORD", "IntegrationTest123!")except ImportError:    docker = None



    PILLOW_AVAILABLE = False

def load_config_from_file() -> dict:

    """Lädt Konfiguration aus nocodb-config.json falls vorhanden."""    Image = Nonetry:

    config_file = Path("nocodb-config.json")

    if config_file.exists():    from PIL import Image

        try:

            with open(config_file) as f:from nocodb_simple_client import (    PILLOW_AVAILABLE = True

                config = json.load(f)

                print(f"✅ Konfiguration aus {config_file} geladen")    AsyncNocoDBClient,except ImportError:

                return config

        except Exception as e:    NocoDBClient,    PILLOW_AVAILABLE = False

            print(f"⚠️  Konnte config file nicht laden: {e}")

    return {}    NocoDBException,    Image = None



    NocoDBMetaClient,

# Load configuration from file if available

_config = load_config_from_file()    NocoDBTable,from nocodb_simple_client import (

if not NOCODB_TOKEN and "api_token" in _config:

    NOCODB_TOKEN = _config["api_token"]    RecordNotFoundException,    AsyncNocoDBClient,

if "base_url" in _config:

    NOCODB_URL = _config["base_url"])    NocoDBClient,

if "admin_email" in _config:

    ADMIN_EMAIL = _config["admin_email"]    NocoDBException,



# Skip integration tests if environment variable is set    NocoDBMetaClient,

def verify_nocodb_accessible() -> bool:

    """Prüft ob NocoDB erreichbar ist."""SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "1") == "1"    NocoDBTable,

    try:

        response = requests.get(f"{NOCODB_URL}/api/v1/health", timeout=5)    RecordNotFoundException,

        if response.status_code == 200:

            print(f"✅ NocoDB ist erreichbar unter {NOCODB_URL}")# Load configuration from environment or config file)

            return True

        print(f"❌ NocoDB Health Check fehlgeschlagen: HTTP {response.status_code}")NOCODB_URL = os.getenv("NOCODB_URL", "http://localhost:8080")

        return False

    except Exception as e:NOCODB_TOKEN = os.getenv("NOCODB_API_TOKEN")# Skip integration tests if environment variable is set OR if docker is not available

        print(f"❌ Kann NocoDB nicht erreichen: {e}")

        print(f"   URL: {NOCODB_URL}")ADMIN_EMAIL = os.getenv("NC_ADMIN_EMAIL", "test@integration.local")SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "1") == "1" or not DOCKER_AVAILABLE

        print(f"   Stelle sicher, dass der Container läuft (z.B. via ci-setup.sh)")

        return FalseADMIN_PASSWORD = os.getenv("NC_ADMIN_PASSWORD", "IntegrationTest123!")



# Test configuration

class NocoDBTestSetup:

    """Setup-Helfer für NocoDB-Tests."""NOCODB_IMAGE = "nocodb/nocodb:latest"



    def __init__(self, base_url: str):def load_config_from_file() -> dict:CONTAINER_NAME = "nocodb-integration-test"

        self.base_url = base_url

        self.token = None    """Lädt Konfiguration aus nocodb-config.json falls vorhanden."""HOST_PORT = 8080

        self.project_id = None

        self.test_table_id = None    config_file = Path("nocodb-config.json")CONTAINER_PORT = 8080

        self.meta_client = None

    if config_file.exists():ADMIN_EMAIL = "test@integration.local"

    def setup_admin_and_project(self) -> dict[str, str]:

        """Authentifiziert und erstellt Test-Projekt."""        try:ADMIN_PASSWORD = "IntegrationTest123!"

        # Step 1: User Registration (optional, falls noch nicht existiert)

        signup_data = {            with open(config_file) as f:PROJECT_NAME = "Integration_Test_Project"

            "email": ADMIN_EMAIL,

            "password": ADMIN_PASSWORD,                config = json.load(f)TEST_TIMEOUT = 300

            "firstname": "Integration",

            "lastname": "Test",                print(f"✅ Konfiguration aus {config_file} geladen")

        }

                return config

        try:

            requests.post(        except Exception as e:class NocoDBContainerManager:

                f"{self.base_url}/api/v2/auth/user/signup",

                json=signup_data,            print(f"⚠️  Konnte config file nicht laden: {e}")    """Verwaltet NocoDB Container für Integrationstests."""

                timeout=30

            )    return {}

        except Exception:

            pass  # User existiert möglicherweise bereits    def __init__(self, image: str = NOCODB_IMAGE, port: int = HOST_PORT):



        # Step 2: User Authentication        self.image = image

        auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}

        response = requests.post(# Load configuration from file if available        self.port = port

            f"{self.base_url}/api/v2/auth/user/signin",

            json=auth_data,_config = load_config_from_file()        self.container = None

            timeout=30

        )if not NOCODB_TOKEN and "api_token" in _config:        self.client = docker.from_env()



        if response.status_code != 200:    NOCODB_TOKEN = _config["api_token"]        self.base_url = f"http://localhost:{port}"

            raise RuntimeError(f"Authentifizierung fehlgeschlagen: {response.status_code}")

if "base_url" in _config:

        auth_result = response.json()

        self.token = auth_result.get("token")    NOCODB_URL = _config["base_url"]    def start_container(self) -> None:



        if not self.token:if "admin_email" in _config:        """Startet NocoDB Container."""

            raise RuntimeError("Token nicht in Auth-Response gefunden")

    ADMIN_EMAIL = _config["admin_email"]        self._cleanup_existing_container()

        print("✅ Authentifizierung erfolgreich")



        # Step 3: Initialize Meta Client

        self.meta_client = NocoDBMetaClient(        print(f"Starte NocoDB Container: {self.image}")

            base_url=self.base_url,

            db_auth_token=self.token,def verify_nocodb_accessible() -> bool:        print(f"Port mapping: {self.port}:{CONTAINER_PORT}")

            timeout=30

        )    """Prüft ob NocoDB erreichbar ist."""



        # Step 4: Discover base    try:        try:

        self.project_id = self._discover_base()

        response = requests.get(f"{NOCODB_URL}/api/v1/health", timeout=5)            self.container = self.client.containers.run(

        # Step 5: Create test table

        self._create_test_table()        if response.status_code == 200:                self.image,



        return {            print(f"✅ NocoDB ist erreichbar unter {NOCODB_URL}")                name=CONTAINER_NAME,

            "token": self.token,

            "project_id": self.project_id,            return True                ports={f"{CONTAINER_PORT}/tcp": self.port},

            "table_id": self.test_table_id,

        }        print(f"❌ NocoDB Health Check fehlgeschlagen: HTTP {response.status_code}")                environment={



    def _discover_base(self) -> str:        return False                    "NC_AUTH_JWT_SECRET": f"test-jwt-secret-{uuid4()}",

        """Findet und gibt Base ID zurück."""

        print("Lade Bases...")    except Exception as e:                    "NC_PUBLIC_URL": self.base_url,

        bases = self.meta_client.list_bases()

        print(f"❌ Kann NocoDB nicht erreichen: {e}")                    "NC_DISABLE_TELE": "true",

        if not bases or len(bases) == 0:

            raise RuntimeError("Keine Bases gefunden")        print(f"   URL: {NOCODB_URL}")                    "NC_MIN": "true",



        first_base = bases[0]        print(f"   Stelle sicher, dass der Container läuft (z.B. via ci-setup.sh)")                },

        base_id = first_base.get("id")

        base_title = first_base.get("title", "Unknown")        return False                detach=True,

        print(f"✅ Verwende Base: {base_title} (ID: {base_id})")

                remove=False,  # Don't auto-remove to allow log inspection

        return base_id

                auto_remove=False,

    def _create_test_table(self) -> None:

        """Erstellt Test-Tabelle."""class NocoDBTestSetup:            )

        table_data = {

            "title": "integration_test_table",    """Setup-Helfer für NocoDB-Tests."""            print(f"Container started with ID: {self.container.id}")

            "table_name": "integration_test_table",

            "columns": [

                {"title": "id", "column_name": "id", "uidt": "ID", "dt": "int", "pk": True, "ai": True, "rqd": True, "un": True},

                {"title": "Name", "column_name": "Name", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},    def __init__(self, base_url: str):            # Give container a moment to initialize

                {"title": "Description", "column_name": "Description", "uidt": "LongText", "dt": "text", "rqd": False},

                {"title": "TestField", "column_name": "TestField", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},        self.base_url = base_url            time.sleep(3)

                {"title": "email", "column_name": "email", "uidt": "Email", "dt": "varchar", "rqd": False},

                {"title": "age", "column_name": "age", "uidt": "Number", "dt": "int", "rqd": False},        self.token = None

                {"title": "status", "column_name": "status", "uidt": "SingleSelect", "dt": "varchar", "dtxp": "active,inactive,pending", "rqd": False},

                {"title": "created_at", "column_name": "created_at", "uidt": "DateTime", "dt": "datetime", "rqd": False},        self.project_id = None            # Check if container is still running

                {"title": "is_active", "column_name": "is_active", "uidt": "Checkbox", "dt": "boolean", "rqd": False},

                {"title": "attachment", "column_name": "attachment", "uidt": "Attachment", "dt": "text", "rqd": False},        self.test_table_id = None            self.container.reload()

            ],

        }        self.meta_client = None            if self.container.status != "running":



        print("Erstelle Test-Tabelle...")                logs = self.container.logs().decode("utf-8")

        table_result = self.meta_client.create_table(self.project_id, table_data)

        self.test_table_id = table_result.get("id")    def setup_admin_and_project(self) -> dict[str, str]:                print(f"Container status: {self.container.status}")



        if not self.test_table_id:        """Authentifiziert und erstellt Test-Projekt."""                print(f"Container logs:\n{logs}")

            raise RuntimeError("Table ID nicht in Response gefunden")

        # Step 1: User Registration (optional, falls noch nicht existiert)                raise RuntimeError(f"Container failed to start. Status: {self.container.status}")

        print(f"✅ Tabelle erstellt: {self.test_table_id}")

        signup_data = {



def generate_test_file(content: str = "Test file content", suffix: str = ".txt") -> Path:            "email": ADMIN_EMAIL,            print(f"Container is running. Status: {self.container.status}")

    """Generiert eine temporäre Test-Datei."""

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)            "password": ADMIN_PASSWORD,            self._wait_for_readiness()

    temp_file.write(content)

    temp_file.close()            "firstname": "Integration",

    return Path(temp_file.name)

            "lastname": "Test",        except Exception as e:



def generate_test_image() -> Path:        }            print(f"Failed to start container: {e}")

    """Generiert ein Test-Bild."""

    if not PILLOW_AVAILABLE:            if self.container:

        return generate_test_file("fake image content", ".png")

        try:                try:

    image = Image.new("RGB", (100, 100), color="red")

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)            requests.post(                    logs = self.container.logs().decode("utf-8")

    image.save(temp_file.name)

    return Path(temp_file.name)                f"{self.base_url}/api/v2/auth/user/signup",                    print(f"Container logs:\n{logs}")



                json=signup_data,                except Exception:

# ============================================================================

# PYTEST FIXTURES                timeout=30                    pass

# ============================================================================

            )            raise

@pytest.fixture(scope="session", autouse=True)

def verify_nocodb_running():        except Exception:

    """Prüft vor allen Tests ob NocoDB erreichbar ist."""

    if SKIP_INTEGRATION:            pass  # User existiert möglicherweise bereits    def _cleanup_existing_container(self) -> None:

        pytest.skip("Integration tests disabled (SKIP_INTEGRATION=1)")

        """Räumt bestehende Container auf."""

    if not verify_nocodb_accessible():

        pytest.fail(        # Step 2: User Authentication        try:

            f"NocoDB ist nicht erreichbar unter {NOCODB_URL}.\n"

            "Stelle sicher, dass der Container läuft:\n"        auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}            existing = self.client.containers.get(CONTAINER_NAME)

            "  ./scripts/ci-setup.sh setup"

        )        response = requests.post(            existing.kill()



            f"{self.base_url}/api/v2/auth/user/signin",            existing.wait()

@pytest.fixture(scope="session")

def nocodb_base_url():            json=auth_data,        except docker.errors.NotFound:

    """Gibt NocoDB Base URL zurück."""

    return NOCODB_URL            timeout=30            pass



        )

@pytest.fixture(scope="session")

def nocodb_setup(nocodb_base_url):    def _wait_for_readiness(self, timeout: int = TEST_TIMEOUT) -> None:

    """Session-weite Fixture für NocoDB Setup."""

    setup = NocoDBTestSetup(nocodb_base_url)        if response.status_code != 200:        """Wartet bis NocoDB bereit ist."""

    config = setup.setup_admin_and_project()

    config["base_url"] = nocodb_base_url            raise RuntimeError(f"Authentifizierung fehlgeschlagen: {response.status_code}")        print("Warte auf NocoDB-Bereitschaft...")

    return config

        start_time = time.time()



@pytest.fixture        auth_result = response.json()        last_error = None

def nocodb_client(nocodb_setup):

    """Fixture für NocoDB Client."""        self.token = auth_result.get("token")

    with NocoDBClient(

        base_url=nocodb_setup["base_url"],        while time.time() - start_time < timeout:

        db_auth_token=nocodb_setup["token"],

        timeout=30,        if not self.token:            # Check if container is still running

    ) as client:

        yield client            raise RuntimeError("Token nicht in Auth-Response gefunden")            try:



                self.container.reload()

@pytest.fixture

def nocodb_meta_client(nocodb_setup):        print("✅ Authentifizierung erfolgreich")                if self.container.status != "running":

    """Fixture für NocoDB Meta Client."""

    with NocoDBMetaClient(                    logs = self.container.logs().decode("utf-8")

        base_url=nocodb_setup["base_url"],

        db_auth_token=nocodb_setup["token"],        # Step 3: Initialize Meta Client                    print(f"Container stopped unexpectedly. Status: {self.container.status}")

        timeout=30,

    ) as client:        self.meta_client = NocoDBMetaClient(                    print(f"Container logs:\n{logs}")

        yield client

            base_url=self.base_url,                    raise RuntimeError(f"Container stopped with status: {self.container.status}")



@pytest.fixture            db_auth_token=self.token,            except Exception as e:

def nocodb_table(nocodb_client, nocodb_setup):

    """Fixture für NocoDB Table."""            timeout=30                print(f"Error checking container status: {e}")

    return NocoDBTable(nocodb_client, nocodb_setup["table_id"])

        )



@pytest.fixture            # Try to connect to NocoDB

async def async_nocodb_client(nocodb_setup):

    """Fixture für Async NocoDB Client."""        # Step 4: Discover base            try:

    async with AsyncNocoDBClient(

        base_url=nocodb_setup["base_url"],        self.project_id = self._discover_base()                response = requests.get(f"{self.base_url}/dashboard", timeout=5)

        db_auth_token=nocodb_setup["token"],

        timeout=30,                if response.status_code == 200:

    ) as client:

        yield client        # Step 5: Create test table                    print("NocoDB ist bereit")



        self._create_test_table()                    time.sleep(2)  # Small delay to ensure full initialization

# ============================================================================

# INTEGRATION TESTS                    return

# ============================================================================

        return {                else:

class TestIntegration:

    """Integration tests für NocoDB Client."""            "token": self.token,                    last_error = f"HTTP {response.status_code}"



    def test_basic_crud_operations(self, nocodb_table):            "project_id": self.project_id,            except requests.exceptions.RequestException as e:

        """Test basic CRUD operations."""

        test_record = {            "table_id": self.test_table_id,                last_error = str(e)

            "Name": f"Integration Test Record {uuid4().hex[:8]}",

            "Description": "Created by integration tests",        }

            "TestField": "test_value",

            "email": "test@integration.com",            elapsed = int(time.time() - start_time)

            "age": 25,

            "status": "active",    def _discover_base(self) -> str:            if elapsed % 10 == 0:  # Log every 10 seconds

            "is_active": True,

        }        """Findet und gibt Base ID zurück."""                print(f"Waiting for NocoDB... ({elapsed}s elapsed, last error: {last_error})")



        record_id = nocodb_table.insert_record(test_record)        print("Lade Bases...")

        assert record_id is not None

        bases = self.meta_client.list_bases()            time.sleep(3)

        try:

            retrieved_record = nocodb_table.get_record(record_id)

            assert retrieved_record["Name"] == test_record["Name"]

            assert retrieved_record["email"] == test_record["email"]        if not bases or len(bases) == 0:        # Timeout reached - get final logs



            update_data = {"Name": "Updated Integration Test Record", "age": 30}            raise RuntimeError("Keine Bases gefunden")        try:

            updated_id = nocodb_table.update_record(update_data, record_id)

            assert updated_id == record_id            logs = self.container.logs().decode("utf-8")



            updated_record = nocodb_table.get_record(record_id)        first_base = bases[0]            print(f"Container logs after timeout:\n{logs}")

            assert updated_record["Name"] == "Updated Integration Test Record"

            assert updated_record["age"] == 30        base_id = first_base.get("id")        except Exception:



        finally:        base_title = first_base.get("title", "Unknown")            pass

            try:

                nocodb_table.delete_record(record_id)        print(f"✅ Verwende Base: {base_title} (ID: {base_id})")

            except Exception as e:

                print(f"Cleanup failed: {e}")        raise RuntimeError(



    def test_query_operations(self, nocodb_table):        return base_id            f"NocoDB wurde nicht innerhalb von {timeout} Sekunden bereit. "

        """Test querying operations."""

        total_count = nocodb_table.count_records()            f"Last error: {last_error}"

        assert isinstance(total_count, int)

        assert total_count >= 0    def _create_test_table(self) -> None:        )



        records = nocodb_table.get_records(limit=5)        """Erstellt Test-Tabelle."""

        assert isinstance(records, list)

        assert len(records) <= 5        table_data = {    def stop_container(self) -> None:



        try:            "title": "integration_test_table",        """Stoppt und entfernt den NocoDB Container."""

            filtered_records = nocodb_table.get_records(where="(Name,isnotblank)", limit=3)

            assert isinstance(filtered_records, list)            "table_name": "integration_test_table",        if self.container:

        except NocoDBException:

            pass            "columns": [            try:



    def test_error_handling(self, nocodb_table):                {"title": "id", "column_name": "id", "uidt": "ID", "dt": "int", "pk": True, "ai": True, "rqd": True, "un": True},                print("Stoppe NocoDB Container...")

        """Test error handling."""

        with pytest.raises((RecordNotFoundException, NocoDBException)):                {"title": "Name", "column_name": "Name", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},                self.container.reload()

            nocodb_table.get_record(99999999)

                {"title": "Description", "column_name": "Description", "uidt": "LongText", "dt": "text", "rqd": False},

        with pytest.raises((RecordNotFoundException, NocoDBException)):

            nocodb_table.delete_record(99999999)                {"title": "TestField", "column_name": "TestField", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},                # Stop container if running



    def test_bulk_operations(self, nocodb_client, nocodb_setup):                {"title": "email", "column_name": "email", "uidt": "Email", "dt": "varchar", "rqd": False},                if self.container.status == "running":

        """Test bulk operations."""

        table_id = nocodb_setup["table_id"]                {"title": "age", "column_name": "age", "uidt": "Number", "dt": "int", "rqd": False},                    self.container.stop(timeout=10)



        test_records = [                {"title": "status", "column_name": "status", "uidt": "SingleSelect", "dt": "varchar", "dtxp": "active,inactive,pending", "rqd": False},                    print("Container gestoppt")

            {

                "Name": f"Bulk Test {i}",                {"title": "created_at", "column_name": "created_at", "uidt": "DateTime", "dt": "datetime", "rqd": False},

                "email": f"bulk{i}@example.com",

                "age": 20 + i,                {"title": "is_active", "column_name": "is_active", "uidt": "Checkbox", "dt": "boolean", "rqd": False},                # Always try to remove the container

                "status": "active" if i % 2 == 0 else "inactive",

            }                {"title": "attachment", "column_name": "attachment", "uidt": "Attachment", "dt": "text", "rqd": False},                self.container.remove(force=True)

            for i in range(5)

        ]            ],                print("NocoDB Container entfernt")



        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)        }

        assert len(inserted_ids) == 5

            except Exception as e:

        try:

            update_records = []        print("Erstelle Test-Tabelle...")                print(f"Fehler beim Stoppen/Entfernen des Containers: {e}")

            for i, record_id in enumerate(inserted_ids):

                update_records.append({"id": record_id, "Name": f"Bulk Updated {i}"})        table_result = self.meta_client.create_table(self.project_id, table_data)                # Try force removal as last resort



            updated_ids = nocodb_client.bulk_update_records(table_id, update_records)        self.test_table_id = table_result.get("id")                try:

            assert len(updated_ids) == 5

                    if self.container:

            for i, record_id in enumerate(updated_ids):

                record = nocodb_client.get_record(table_id, record_id)        if not self.test_table_id:                        self.container.remove(force=True)

                assert record["Name"] == f"Bulk Updated {i}"

            raise RuntimeError("Table ID nicht in Response gefunden")                        print("Container mit force=True entfernt")

        finally:

            deleted_ids = nocodb_client.bulk_delete_records(table_id, inserted_ids)                except Exception as e2:

            assert len(deleted_ids) == 5

        print(f"✅ Tabelle erstellt: {self.test_table_id}")                    print(f"Force-Removal fehlgeschlagen: {e2}")

    def test_file_operations(self, nocodb_client, nocodb_setup):

        """Test file upload and download operations."""

        table_id = nocodb_setup["table_id"]

    def get_logs(self) -> str:

        test_record = {"Name": "File Test Record", "Description": "Testing file operations"}

        record_id = nocodb_client.insert_record(table_id, test_record)def generate_test_file(content: str = "Test file content", suffix: str = ".txt") -> Path:        """Gibt Container-Logs zurück."""



        test_file = generate_test_file("Integration test file content")    """Generiert eine temporäre Test-Datei."""        if self.container:

        test_image = generate_test_image()

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)            return self.container.logs().decode("utf-8")

        try:

            nocodb_client.attach_file_to_record(    temp_file.write(content)        return ""

                table_id=table_id,

                record_id=record_id,    temp_file.close()

                field_name="attachment",

                file_path=str(test_file),    return Path(temp_file.name)

            )

class NocoDBTestSetup:

            nocodb_client.attach_files_to_record(

                table_id=table_id,    """Setup-Helfer für NocoDB-Tests mit der nocodb_simple_client Library."""

                record_id=record_id,

                field_name="attachment",def generate_test_image() -> Path:

                file_paths=[str(test_file), str(test_image)],

            )    """Generiert ein Test-Bild."""    def __init__(self, base_url: str):



            download_path = tempfile.mktemp(suffix=".txt")    if not PILLOW_AVAILABLE:        self.base_url = base_url

            nocodb_client.download_file_from_record(

                table_id=table_id,        return generate_test_file("fake image content", ".png")        self.token = None

                record_id=record_id,

                field_name="attachment",        self.project_id = None

                file_path=download_path,

            )    image = Image.new("RGB", (100, 100), color="red")        self.test_table_id = None



            assert Path(download_path).exists()    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)        self.meta_client = None



            download_dir = Path(tempfile.mkdtemp())    image.save(temp_file.name)

            nocodb_client.download_files_from_record(

                table_id=table_id,    return Path(temp_file.name)    def setup_admin_and_project(self) -> dict[str, str]:

                record_id=record_id,

                field_name="attachment",        """Erstellt Admin-Benutzer und Test-Projekt."""

                directory=str(download_dir),

            )        # Step 1: User Registration



            downloaded_files = list(download_dir.glob("*"))# ============================================================================        signup_data = {

            assert len(downloaded_files) > 0

# PYTEST FIXTURES            "email": ADMIN_EMAIL,

            Path(download_path).unlink(missing_ok=True)

            for file in downloaded_files:# ============================================================================            "password": ADMIN_PASSWORD,

                file.unlink()

            download_dir.rmdir()            "firstname": "Integration",



        finally:@pytest.fixture(scope="session", autouse=True)            "lastname": "Test",

            test_file.unlink()

            test_image.unlink()def verify_nocodb_running():        }

            nocodb_client.delete_record(table_id, record_id)

    """Prüft vor allen Tests ob NocoDB erreichbar ist."""

    def test_context_manager_behavior(self, nocodb_setup):

        """Test context manager behavior."""    if SKIP_INTEGRATION:        try:

        with NocoDBClient(

            base_url=nocodb_setup["base_url"],        pytest.skip("Integration tests disabled (SKIP_INTEGRATION=1)")            signup_response = requests.post(

            db_auth_token=nocodb_setup["token"],

            timeout=30,                f"{self.base_url}/api/v2/auth/user/signup",

        ) as client:

            table = NocoDBTable(client, nocodb_setup["table_id"])    if not verify_nocodb_accessible():                json=signup_data,

            count = table.count_records()

            assert isinstance(count, int)        pytest.fail(                timeout=30



    def test_pagination_with_real_data(self, nocodb_table):            f"NocoDB ist nicht erreichbar unter {NOCODB_URL}.\n"            )

        """Test pagination handling."""

        try:            "Stelle sicher, dass der Container läuft:\n"            print(f"Signup response: {signup_response.status_code}")

            records = nocodb_table.get_records(limit=150)

            assert isinstance(records, list)            "  ./scripts/ci-setup.sh setup"        except Exception as e:

        except NocoDBException:

            pass        )            print(f"Signup error (expected if user exists): {e}")



    def test_count_and_filtering(self, nocodb_client, nocodb_setup):

        """Test record counting and filtering."""

        table_id = nocodb_setup["table_id"]        # Step 2: User Authentication



        total_count = nocodb_client.count_records(table_id)@pytest.fixture(scope="session")        auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}

        assert isinstance(total_count, int)

        assert total_count >= 0def nocodb_base_url():        response = requests.post(



        test_records = [    """Gibt NocoDB Base URL zurück."""            f"{self.base_url}/api/v2/auth/user/signin",

            {"Name": f"Filter Test {i}", "status": "active" if i % 2 == 0 else "inactive"}

            for i in range(4)    return NOCODB_URL            json=auth_data,

        ]

            timeout=30

        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)

        )

        try:

            active_records = nocodb_client.get_records(@pytest.fixture(scope="session")

                table_id, where="(status,eq,active)", limit=100

            )def nocodb_setup(nocodb_base_url):        if response.status_code != 200:

            inactive_records = nocodb_client.get_records(

                table_id, where="(status,eq,inactive)", limit=100    """Session-weite Fixture für NocoDB Setup."""            print(f"Auth response body: {response.text}")

            )

    setup = NocoDBTestSetup(nocodb_base_url)            raise RuntimeError(f"Authentication failed: {response.status_code}")

            active_count = len([r for r in active_records if r.get("status") == "active"])

            inactive_count = len([r for r in inactive_records if r.get("status") == "inactive"])    config = setup.setup_admin_and_project()



            assert active_count >= 2    config["base_url"] = nocodb_base_url        auth_result = response.json()

            assert inactive_count >= 2

    return config        self.token = auth_result.get("token")

        finally:

            nocodb_client.bulk_delete_records(table_id, inserted_ids)



    def test_table_wrapper_operations(self, nocodb_table):        if not self.token:

        """Test table wrapper operations."""

        count = nocodb_table.count_records()@pytest.fixture            print(f"Auth result: {auth_result}")

        assert isinstance(count, int)

def nocodb_client(nocodb_setup):            raise RuntimeError("Token not found in auth response")

        records = nocodb_table.get_records(limit=5)

        assert isinstance(records, list)    """Fixture für NocoDB Client."""



        test_record = {"Name": "Table Wrapper Test", "email": "wrapper@test.com"}    with NocoDBClient(        print("Successfully authenticated, token obtained")



        record_id = nocodb_table.insert_record(test_record)        base_url=nocodb_setup["base_url"],

        assert record_id is not None

        db_auth_token=nocodb_setup["token"],        # Step 3: Initialize Meta Client early with token

        try:

            retrieved = nocodb_table.get_record(record_id)        timeout=30,        # This allows us to use Library methods wherever possible

            assert retrieved["Name"] == test_record["Name"]

    ) as client:        self.meta_client = NocoDBMetaClient(

            updated_id = nocodb_table.update_record({"Name": "Updated Wrapper"}, record_id)

            assert updated_id == record_id        yield client            base_url=self.base_url,



        finally:            db_auth_token=self.token,

            nocodb_table.delete_record(record_id)

            timeout=30

    def test_query_builder(self, nocodb_table):

        """Test query builder functionality."""@pytest.fixture        )

        query = nocodb_table.query()

        records = query.where("Name", "isnotnull").limit(10).execute()def nocodb_meta_client(nocodb_setup):

        assert isinstance(records, list)

    """Fixture für NocoDB Meta Client."""        # Step 4: Discover workspace and base using Library methods



class TestNocoDBMetaClientIntegration:    with NocoDBMetaClient(        self.project_id = self._discover_base()

    """Integrationstests für NocoDBMetaClient."""

        base_url=nocodb_setup["base_url"],

    def test_workspace_operations(self, nocodb_meta_client):

        """Test workspace listing and retrieval."""        db_auth_token=nocodb_setup["token"],        # Step 5: Create test table using the Library

        try:

            workspaces = nocodb_meta_client.list_workspaces()        timeout=30,        self._create_test_table()

            assert isinstance(workspaces, list)

            assert len(workspaces) > 0    ) as client:



            first_workspace = workspaces[0]        yield client        return {

            workspace_id = first_workspace.get("id")

            assert workspace_id is not None            "token": self.token,



            workspace = nocodb_meta_client.get_workspace(workspace_id)            "project_id": self.project_id,

            assert isinstance(workspace, dict)

            assert workspace.get("id") == workspace_id@pytest.fixture            "table_id": self.test_table_id,



        except Exception as e:def nocodb_table(nocodb_client, nocodb_setup):        }

            pytest.skip(f"Workspace operations not available: {e}")

    """Fixture für NocoDB Table."""

    def test_base_operations(self, nocodb_meta_client):

        """Test base listing and retrieval."""    return NocoDBTable(nocodb_client, nocodb_setup["table_id"])    def _discover_base(self) -> str:

        bases = nocodb_meta_client.list_bases()

        assert isinstance(bases, list)        """Discover and return a usable base ID using Library methods.

        assert len(bases) > 0



        first_base = bases[0]

        base_id = first_base.get("id")@pytest.fixture        Uses the nocodb_simple_client library's MetaClient method:

        assert base_id is not None

async def async_nocodb_client(nocodb_setup):        - list_bases() to get all available bases

        base = nocodb_meta_client.get_base(base_id)

        assert isinstance(base, dict)    """Fixture für Async NocoDB Client."""

        assert base.get("id") == base_id

    async with AsyncNocoDBClient(        Returns:

    def test_table_info(self, nocodb_meta_client, nocodb_setup):

        """Test getting table information."""        base_url=nocodb_setup["base_url"],            Base ID string

        table_id = nocodb_setup["table_id"]

        db_auth_token=nocodb_setup["token"],        """

        try:

            table_info = nocodb_meta_client.get_table_info(table_id)        timeout=30,        print("Fetching bases using meta_client.list_bases()...")

            assert isinstance(table_info, dict)

            assert "title" in table_info    ) as client:        try:

        except Exception:

            pytest.skip("Table info test requires specific API endpoint")        yield client            # Use Library API to list all bases



    def test_list_columns(self, nocodb_meta_client, nocodb_setup):            bases = self.meta_client.list_bases()

        """Test listing table columns."""

        table_id = nocodb_setup["table_id"]



        try:# ============================================================================            if not bases or len(bases) == 0:

            columns = nocodb_meta_client.list_columns(table_id)

            assert isinstance(columns, list)# INTEGRATION TESTS                raise RuntimeError("No bases found in NocoDB instance")

            assert len(columns) > 0

        except Exception:# ============================================================================

            pytest.skip("Column listing test requires specific API endpoint")

            # Use first base



@pytest.mark.asyncioclass TestIntegration:            first_base = bases[0]

class TestAsyncNocoDBClientIntegration:

    """Integrationstests für AsyncNocoDBClient."""    """Integration tests für NocoDB Client."""            base_id = first_base.get("id")



    async def test_async_basic_operations(self, async_nocodb_client, nocodb_setup):            base_title = first_base.get("title", "Unknown")

        """Test basic async operations."""

        table_id = nocodb_setup["table_id"]    def test_basic_crud_operations(self, nocodb_table):            print(f"Using base: {base_title} (ID: {base_id})")



        records = await async_nocodb_client.get_records(table_id, limit=5)        """Test basic CRUD operations."""

        assert isinstance(records, list)

        test_record = {            return base_id

        test_record = {"Name": "Async Test Record", "email": "async@test.com"}

            "Name": f"Integration Test Record {uuid4().hex[:8]}",

        record_id = await async_nocodb_client.insert_record(table_id, test_record)

        assert record_id is not None            "Description": "Created by integration tests",        except Exception as e:



        try:            "TestField": "test_value",            raise RuntimeError(f"Error discovering base: {e}") from e

            retrieved_record = await async_nocodb_client.get_record(table_id, record_id)

            assert retrieved_record["Name"] == test_record["Name"]            "email": "test@integration.com",



            update_data = {"Name": "Updated Async Record"}            "age": 25,    def _create_test_table(self) -> None:

            updated_id = await async_nocodb_client.update_record(table_id, update_data, record_id)

            assert updated_id == record_id            "status": "active",        """Erstellt Test-Tabelle mit der nocodb_simple_client Library."""



        finally:            "is_active": True,        table_data = {

            await async_nocodb_client.delete_record(table_id, record_id)

        }            "title": "integration_test_table",

    async def test_async_bulk_operations(self, async_nocodb_client, nocodb_setup):

        """Test async bulk operations."""            "table_name": "integration_test_table",

        table_id = nocodb_setup["table_id"]

        record_id = nocodb_table.insert_record(test_record)            "columns": [

        test_records = [

            {"Name": f"Async Bulk {i}", "email": f"async{i}@test.com"} for i in range(3)        assert record_id is not None                {"title": "id", "column_name": "id", "uidt": "ID", "dt": "int", "pk": True, "ai": True, "rqd": True, "un": True},

        ]

                {"title": "Name", "column_name": "Name", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},

        inserted_ids = await async_nocodb_client.bulk_insert_records(table_id, test_records)

        assert len(inserted_ids) == 3        try:                {"title": "Description", "column_name": "Description", "uidt": "LongText", "dt": "text", "rqd": False},



        try:            retrieved_record = nocodb_table.get_record(record_id)                {"title": "TestField", "column_name": "TestField", "uidt": "SingleLineText", "dt": "varchar", "rqd": False},

            update_records = [

                {"id": record_id, "Name": f"Async Updated {i}"}            assert retrieved_record["Name"] == test_record["Name"]                {"title": "email", "column_name": "email", "uidt": "Email", "dt": "varchar", "rqd": False},

                for i, record_id in enumerate(inserted_ids)

            ]            assert retrieved_record["email"] == test_record["email"]                {"title": "age", "column_name": "age", "uidt": "Number", "dt": "int", "rqd": False},

            updated_ids = await async_nocodb_client.bulk_update_records(table_id, update_records)

            assert len(updated_ids) == 3                {"title": "status", "column_name": "status", "uidt": "SingleSelect", "dt": "varchar", "dtxp": "active,inactive,pending", "rqd": False},



        finally:            update_data = {"Name": "Updated Integration Test Record", "age": 30}                {"title": "created_at", "column_name": "created_at", "uidt": "DateTime", "dt": "datetime", "rqd": False},

            deleted_ids = await async_nocodb_client.bulk_delete_records(table_id, inserted_ids)

            assert len(deleted_ids) == 3            updated_id = nocodb_table.update_record(update_data, record_id)                {"title": "is_active", "column_name": "is_active", "uidt": "Checkbox", "dt": "boolean", "rqd": False},


            assert updated_id == record_id                {"title": "attachment", "column_name": "attachment", "uidt": "Attachment", "dt": "text", "rqd": False},

            ],

            updated_record = nocodb_table.get_record(record_id)        }

            assert updated_record["Name"] == "Updated Integration Test Record"

            assert updated_record["age"] == 30        try:

            # Use the Library's create_table method

        finally:            print("Creating table using NocoDBMetaClient...")

            try:            table_result = self.meta_client.create_table(self.project_id, table_data)

                nocodb_table.delete_record(record_id)            self.test_table_id = table_result.get("id")

            except Exception as e:

                print(f"Cleanup failed: {e}")            if not self.test_table_id:

                print(f"Table result: {table_result}")

    def test_query_operations(self, nocodb_table):                raise RuntimeError("Table ID not found in creation response")

        """Test querying operations."""

        total_count = nocodb_table.count_records()            print(f"Table created successfully with ID: {self.test_table_id}")

        assert isinstance(total_count, int)

        assert total_count >= 0        except Exception as e:

            print(f"Table creation failed: {e}")

        records = nocodb_table.get_records(limit=5)            raise

        assert isinstance(records, list)

        assert len(records) <= 5

def generate_test_file(content: str = "Test file content", suffix: str = ".txt") -> Path:

        try:    """Generiert eine temporäre Test-Datei."""

            filtered_records = nocodb_table.get_records(where="(Name,isnotblank)", limit=3)    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)

            assert isinstance(filtered_records, list)    temp_file.write(content)

        except NocoDBException:    temp_file.close()

            pass    return Path(temp_file.name)



    def test_error_handling(self, nocodb_table):

        """Test error handling."""def generate_test_image() -> Path:

        with pytest.raises((RecordNotFoundException, NocoDBException)):    """Generiert ein Test-Bild."""

            nocodb_table.get_record(99999999)    if not PILLOW_AVAILABLE:

        # Fallback: generate a fake PNG file

        with pytest.raises((RecordNotFoundException, NocoDBException)):        return generate_test_file("fake image content", ".png")

            nocodb_table.delete_record(99999999)

    from PIL import Image

    def test_bulk_operations(self, nocodb_client, nocodb_setup):    image = Image.new("RGB", (100, 100), color="red")

        """Test bulk operations."""    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)

        table_id = nocodb_setup["table_id"]    image.save(temp_file.name)

    return Path(temp_file.name)

        test_records = [

            {

                "Name": f"Bulk Test {i}",@pytest.fixture(scope="session")

                "email": f"bulk{i}@example.com",def nocodb_container():

                "age": 20 + i,    """Session-weite Fixture für NocoDB Container."""

                "status": "active" if i % 2 == 0 else "inactive",    if SKIP_INTEGRATION:

            }        pytest.skip("Integration tests disabled")

            for i in range(5)

        ]    container_manager = NocoDBContainerManager()



        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)    try:

        assert len(inserted_ids) == 5        container_manager.start_container()

        yield container_manager

        try:    except Exception as e:

            update_records = []        print(f"Container setup failed: {e}")

            for i, record_id in enumerate(inserted_ids):        if container_manager.container:

                update_records.append({"id": record_id, "Name": f"Bulk Updated {i}"})            print("Container logs:")

            print(container_manager.get_logs())

            updated_ids = nocodb_client.bulk_update_records(table_id, update_records)        raise

            assert len(updated_ids) == 5    finally:

        container_manager.stop_container()

            for i, record_id in enumerate(updated_ids):

                record = nocodb_client.get_record(table_id, record_id)

                assert record["Name"] == f"Bulk Updated {i}"@pytest.fixture(scope="session")

def nocodb_setup(nocodb_container):

        finally:    """Session-weite Fixture für NocoDB Setup."""

            deleted_ids = nocodb_client.bulk_delete_records(table_id, inserted_ids)    setup = NocoDBTestSetup(nocodb_container.base_url)

            assert len(deleted_ids) == 5    config = setup.setup_admin_and_project()

    config["base_url"] = nocodb_container.base_url

    def test_file_operations(self, nocodb_client, nocodb_setup):    return config

        """Test file upload and download operations."""

        table_id = nocodb_setup["table_id"]

@pytest.fixture

        test_record = {"Name": "File Test Record", "Description": "Testing file operations"}def nocodb_client(nocodb_setup):

        record_id = nocodb_client.insert_record(table_id, test_record)    """Fixture für NocoDB Client."""

    with NocoDBClient(

        test_file = generate_test_file("Integration test file content")        base_url=nocodb_setup["base_url"],

        test_image = generate_test_image()        db_auth_token=nocodb_setup["token"],

        timeout=30,

        try:    ) as client:

            nocodb_client.attach_file_to_record(        yield client

                table_id=table_id,

                record_id=record_id,

                field_name="attachment",@pytest.fixture

                file_path=str(test_file),def nocodb_meta_client(nocodb_setup):

            )    """Fixture für NocoDB Meta Client."""

    with NocoDBMetaClient(

            nocodb_client.attach_files_to_record(        base_url=nocodb_setup["base_url"],

                table_id=table_id,        db_auth_token=nocodb_setup["token"],

                record_id=record_id,        timeout=30,

                field_name="attachment",    ) as client:

                file_paths=[str(test_file), str(test_image)],        yield client

            )



            download_path = tempfile.mktemp(suffix=".txt")@pytest.fixture

            nocodb_client.download_file_from_record(def nocodb_table(nocodb_client, nocodb_setup):

                table_id=table_id,    """Fixture für NocoDB Table."""

                record_id=record_id,    return NocoDBTable(nocodb_client, nocodb_setup["table_id"])

                field_name="attachment",

                file_path=download_path,

            )@pytest.fixture

async def async_nocodb_client(nocodb_setup):

            assert Path(download_path).exists()    """Fixture für Async NocoDB Client."""

    async with AsyncNocoDBClient(

            download_dir = Path(tempfile.mkdtemp())        base_url=nocodb_setup["base_url"],

            nocodb_client.download_files_from_record(        db_auth_token=nocodb_setup["token"],

                table_id=table_id,        timeout=30,

                record_id=record_id,    ) as client:

                field_name="attachment",        yield client

                directory=str(download_dir),

            )

class TestIntegration:

            downloaded_files = list(download_dir.glob("*"))    """Integration tests requiring a real NocoDB instance."""

            assert len(downloaded_files) > 0

    def test_basic_crud_operations(self, nocodb_table):

            Path(download_path).unlink(missing_ok=True)        """Test basic CRUD operations against real NocoDB instance."""

            for file in downloaded_files:        test_record = {

                file.unlink()            "Name": f"Integration Test Record {uuid4().hex[:8]}",

            download_dir.rmdir()            "Description": "Created by integration tests",

            "TestField": "test_value",

        finally:            "email": "test@integration.com",

            test_file.unlink()            "age": 25,

            test_image.unlink()            "status": "active",

            nocodb_client.delete_record(table_id, record_id)            "is_active": True,

        }

    def test_context_manager_behavior(self, nocodb_setup):

        """Test context manager behavior."""        record_id = nocodb_table.insert_record(test_record)

        with NocoDBClient(        assert record_id is not None

            base_url=nocodb_setup["base_url"],

            db_auth_token=nocodb_setup["token"],        try:

            timeout=30,            retrieved_record = nocodb_table.get_record(record_id)

        ) as client:            assert retrieved_record["Name"] == test_record["Name"]

            table = NocoDBTable(client, nocodb_setup["table_id"])            assert retrieved_record["email"] == test_record["email"]

            count = table.count_records()

            assert isinstance(count, int)            update_data = {"Name": "Updated Integration Test Record", "age": 30}

            updated_id = nocodb_table.update_record(update_data, record_id)

    def test_pagination_with_real_data(self, nocodb_table):            assert updated_id == record_id

        """Test pagination handling."""

        try:            updated_record = nocodb_table.get_record(record_id)

            records = nocodb_table.get_records(limit=150)            assert updated_record["Name"] == "Updated Integration Test Record"

            assert isinstance(records, list)            assert updated_record["age"] == 30

        except NocoDBException:

            pass        finally:

            try:

    def test_count_and_filtering(self, nocodb_client, nocodb_setup):                nocodb_table.delete_record(record_id)

        """Test record counting and filtering."""            except Exception as e:

        table_id = nocodb_setup["table_id"]                print(f"Warning: Could not clean up test record {record_id}: {e}")



        total_count = nocodb_client.count_records(table_id)    def test_query_operations(self, nocodb_table):

        assert isinstance(total_count, int)        """Test querying operations."""

        assert total_count >= 0        total_count = nocodb_table.count_records()

        assert isinstance(total_count, int)

        test_records = [        assert total_count >= 0

            {"Name": f"Filter Test {i}", "status": "active" if i % 2 == 0 else "inactive"}

            for i in range(4)        records = nocodb_table.get_records(limit=5)

        ]        assert isinstance(records, list)

        assert len(records) <= 5

        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)

        try:

        try:            filtered_records = nocodb_table.get_records(where="(Name,isnotblank)", limit=3)

            active_records = nocodb_client.get_records(            assert isinstance(filtered_records, list)

                table_id, where="(status,eq,active)", limit=100        except NocoDBException:

            )            pass

            inactive_records = nocodb_client.get_records(

                table_id, where="(status,eq,inactive)", limit=100    def test_error_handling(self, nocodb_table):

            )        """Test error handling with real API."""

        with pytest.raises((RecordNotFoundException, NocoDBException)):

            active_count = len([r for r in active_records if r.get("status") == "active"])            nocodb_table.get_record(99999999)

            inactive_count = len([r for r in inactive_records if r.get("status") == "inactive"])

        with pytest.raises((RecordNotFoundException, NocoDBException)):

            assert active_count >= 2            nocodb_table.delete_record(99999999)

            assert inactive_count >= 2

    def test_bulk_operations(self, nocodb_client, nocodb_setup):

        finally:        """Test bulk operations."""

            nocodb_client.bulk_delete_records(table_id, inserted_ids)        table_id = nocodb_setup["table_id"]



    def test_table_wrapper_operations(self, nocodb_table):        test_records = [

        """Test table wrapper operations."""            {

        count = nocodb_table.count_records()                "Name": f"Bulk Test {i}",

        assert isinstance(count, int)                "email": f"bulk{i}@example.com",

                "age": 20 + i,

        records = nocodb_table.get_records(limit=5)                "status": "active" if i % 2 == 0 else "inactive",

        assert isinstance(records, list)            }

            for i in range(5)

        test_record = {"Name": "Table Wrapper Test", "email": "wrapper@test.com"}        ]



        record_id = nocodb_table.insert_record(test_record)        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)

        assert record_id is not None        assert len(inserted_ids) == 5



        try:        try:

            retrieved = nocodb_table.get_record(record_id)            update_records = []

            assert retrieved["Name"] == test_record["Name"]            for i, record_id in enumerate(inserted_ids):

                update_records.append(

            updated_id = nocodb_table.update_record({"Name": "Updated Wrapper"}, record_id)                    {"id": record_id, "Name": f"Updated Bulk Test {i}", "age": 30 + i}

            assert updated_id == record_id                )



        finally:            updated_ids = nocodb_client.bulk_update_records(table_id, update_records)

            nocodb_table.delete_record(record_id)            assert len(updated_ids) == 5



    def test_query_builder(self, nocodb_table):            for i, record_id in enumerate(updated_ids):

        """Test query builder functionality."""                record = nocodb_client.get_record(table_id, record_id)

        query = nocodb_table.query()                assert record["Name"] == f"Updated Bulk Test {i}"

        records = query.where("Name", "isnotnull").limit(10).execute()                assert record["age"] == 30 + i

        assert isinstance(records, list)

        finally:

            deleted_ids = nocodb_client.bulk_delete_records(table_id, inserted_ids)

class TestNocoDBMetaClientIntegration:            assert len(deleted_ids) == 5

    """Integrationstests für NocoDBMetaClient."""

    def test_file_operations(self, nocodb_client, nocodb_setup):

    def test_workspace_operations(self, nocodb_meta_client):        """Test file upload and download operations."""

        """Test workspace listing and retrieval."""        table_id = nocodb_setup["table_id"]

        try:

            workspaces = nocodb_meta_client.list_workspaces()        test_record = {"Name": "File Test Record", "Description": "Testing file operations"}

            assert isinstance(workspaces, list)        record_id = nocodb_client.insert_record(table_id, test_record)

            assert len(workspaces) > 0

        test_file = generate_test_file("Integration test file content")

            first_workspace = workspaces[0]        test_image = generate_test_image()

            workspace_id = first_workspace.get("id")

            assert workspace_id is not None        try:

            nocodb_client.attach_file_to_record(

            workspace = nocodb_meta_client.get_workspace(workspace_id)                table_id=table_id,

            assert isinstance(workspace, dict)                record_id=record_id,

            assert workspace.get("id") == workspace_id                field_name="attachment",

                file_path=str(test_file),

        except Exception as e:            )

            pytest.skip(f"Workspace operations not available: {e}")

            nocodb_client.attach_files_to_record(

    def test_base_operations(self, nocodb_meta_client):                table_id=table_id,

        """Test base listing and retrieval."""                record_id=record_id,

        bases = nocodb_meta_client.list_bases()                field_name="attachment",

        assert isinstance(bases, list)                file_paths=[str(test_file), str(test_image)],

        assert len(bases) > 0            )



        first_base = bases[0]            download_path = tempfile.mktemp(suffix=".txt")

        base_id = first_base.get("id")            nocodb_client.download_file_from_record(

        assert base_id is not None                table_id=table_id,

                record_id=record_id,

        base = nocodb_meta_client.get_base(base_id)                field_name="attachment",

        assert isinstance(base, dict)                file_path=download_path,

        assert base.get("id") == base_id            )



    def test_table_info(self, nocodb_meta_client, nocodb_setup):            assert Path(download_path).exists()

        """Test getting table information."""

        table_id = nocodb_setup["table_id"]            download_dir = Path(tempfile.mkdtemp())

            nocodb_client.download_files_from_record(

        try:                table_id=table_id,

            table_info = nocodb_meta_client.get_table_info(table_id)                record_id=record_id,

            assert isinstance(table_info, dict)                field_name="attachment",

            assert "title" in table_info                directory=str(download_dir),

        except Exception:            )

            pytest.skip("Table info test requires specific API endpoint")

            downloaded_files = list(download_dir.glob("*"))

    def test_list_columns(self, nocodb_meta_client, nocodb_setup):            assert len(downloaded_files) > 0

        """Test listing table columns."""

        table_id = nocodb_setup["table_id"]            Path(download_path).unlink(missing_ok=True)

            for file in downloaded_files:

        try:                file.unlink()

            columns = nocodb_meta_client.list_columns(table_id)            download_dir.rmdir()

            assert isinstance(columns, list)

            assert len(columns) > 0        finally:

        except Exception:            test_file.unlink()

            pytest.skip("Column listing test requires specific API endpoint")            test_image.unlink()

            nocodb_client.delete_record(table_id, record_id)



@pytest.mark.asyncio    def test_context_manager_behavior(self, nocodb_setup):

class TestAsyncNocoDBClientIntegration:        """Test context manager behavior with real client."""

    """Integrationstests für AsyncNocoDBClient."""        with NocoDBClient(

            base_url=nocodb_setup["base_url"],

    async def test_async_basic_operations(self, async_nocodb_client, nocodb_setup):            db_auth_token=nocodb_setup["token"],

        """Test basic async operations."""            timeout=30,

        table_id = nocodb_setup["table_id"]        ) as client:

            table = NocoDBTable(client, nocodb_setup["table_id"])

        records = await async_nocodb_client.get_records(table_id, limit=5)            count = table.count_records()

        assert isinstance(records, list)            assert isinstance(count, int)



        test_record = {"Name": "Async Test Record", "email": "async@test.com"}    def test_pagination_with_real_data(self, nocodb_table):

        """Test pagination handling with real data."""

        record_id = await async_nocodb_client.insert_record(table_id, test_record)        try:

        assert record_id is not None            records = nocodb_table.get_records(limit=150)

            assert isinstance(records, list)

        try:        except NocoDBException:

            retrieved_record = await async_nocodb_client.get_record(table_id, record_id)            pass

            assert retrieved_record["Name"] == test_record["Name"]

    def test_count_and_filtering(self, nocodb_client, nocodb_setup):

            update_data = {"Name": "Updated Async Record"}        """Test record counting and filtering."""

            updated_id = await async_nocodb_client.update_record(table_id, update_data, record_id)        table_id = nocodb_setup["table_id"]

            assert updated_id == record_id

        total_count = nocodb_client.count_records(table_id)

        finally:        assert isinstance(total_count, int)

            await async_nocodb_client.delete_record(table_id, record_id)        assert total_count >= 0



    async def test_async_bulk_operations(self, async_nocodb_client, nocodb_setup):        test_records = [

        """Test async bulk operations."""            {"Name": f"Filter Test {i}", "status": "active" if i % 2 == 0 else "inactive"}

        table_id = nocodb_setup["table_id"]            for i in range(4)

        ]

        test_records = [

            {"Name": f"Async Bulk {i}", "email": f"async{i}@test.com"} for i in range(3)        inserted_ids = nocodb_client.bulk_insert_records(table_id, test_records)

        ]

        try:

        inserted_ids = await async_nocodb_client.bulk_insert_records(table_id, test_records)            active_records = nocodb_client.get_records(

        assert len(inserted_ids) == 3                table_id, where="(status,eq,active)", limit=100

            )

        try:            inactive_records = nocodb_client.get_records(

            update_records = [                table_id, where="(status,eq,inactive)", limit=100

                {"id": record_id, "Name": f"Async Updated {i}"}            )

                for i, record_id in enumerate(inserted_ids)

            ]            active_count = len([r for r in active_records if r.get("status") == "active"])

            updated_ids = await async_nocodb_client.bulk_update_records(table_id, update_records)            inactive_count = len([r for r in inactive_records if r.get("status") == "inactive"])

            assert len(updated_ids) == 3

            assert active_count >= 2

        finally:            assert inactive_count >= 2

            deleted_ids = await async_nocodb_client.bulk_delete_records(table_id, inserted_ids)

            assert len(deleted_ids) == 3        finally:

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

    def test_workspace_operations(self, nocodb_meta_client):
        """Test workspace listing and retrieval.

        Note: Workspace operations may not be available in all NocoDB deployments.
        If the workspace endpoints are not available, this test will be skipped.
        """
        try:
            # Use Library API method
            workspaces = nocodb_meta_client.list_workspaces()
            assert isinstance(workspaces, list)
            assert len(workspaces) > 0

            # Get first workspace details using Library API
            first_workspace = workspaces[0]
            workspace_id = first_workspace.get("id")
            assert workspace_id is not None

            workspace = nocodb_meta_client.get_workspace(workspace_id)
            assert isinstance(workspace, dict)
            assert workspace.get("id") == workspace_id

        except Exception as e:
            pytest.skip(f"Workspace operations not available: {e}")

    def test_base_operations(self, nocodb_meta_client):
        """Test base listing and retrieval using Library API."""
        # Use Library API to list all bases
        bases = nocodb_meta_client.list_bases()
        assert isinstance(bases, list)
        assert len(bases) > 0

        # Get first base details using Library API
        first_base = bases[0]
        base_id = first_base.get("id")
        assert base_id is not None

        base = nocodb_meta_client.get_base(base_id)
        assert isinstance(base, dict)
        assert base.get("id") == base_id

    def test_table_info(self, nocodb_meta_client, nocodb_setup):
        """Test getting table information using Library API."""
        table_id = nocodb_setup["table_id"]

        try:
            # Use Library API method
            table_info = nocodb_meta_client.get_table_info(table_id)
            assert isinstance(table_info, dict)
            assert "title" in table_info
        except Exception:
            pytest.skip("Table info test requires specific API endpoint")

    def test_list_columns(self, nocodb_meta_client, nocodb_setup):
        """Test listing table columns using Library API."""
        table_id = nocodb_setup["table_id"]

        try:
            # Use Library API method
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
