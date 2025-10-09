# NocoDB CI/CD Container Management

Dieses Script automatisiert das Docker-Container-Management für NocoDB-Integrationstests.

## 📁 Script

### `ci-setup.sh` (Bash)
Bash-Script für Linux/macOS CI/CD-Umgebungen zur Verwaltung von NocoDB-Containern.

**Zweck:** Container-Lifecycle-Management (starten, stoppen, aufräumen)
**Tests:** Werden separat über pytest ausgeführt

## 🚀 Verwendung

### Komplettes Setup (empfohlen für CI/CD)

```bash
./scripts/ci-setup.sh setup
```

Dies führt automatisch aus:

1. ✅ Prüfung der Abhängigkeiten (Docker, curl)
2. 🐳 Start des NocoDB-Containers mit Health-Checks
3. ⏳ Warten auf Container-Bereitschaft
4. 🔑 Generierung eines API-Tokens
5. 💾 Speicherung der Credentials
6. 🔌 Test der API-Verbindung

**Danach:** Tests mit pytest ausführen

### Einzelne Befehle

```bash
# Nur Docker-Container starten
./scripts/ci-setup.sh docker

# Nur Token generieren (Container muss laufen)
./scripts/ci-setup.sh token

# Aufräumen
./scripts/ci-setup.sh cleanup

# Hilfe anzeigen
./scripts/ci-setup.sh help
```

## ⚙️ Konfiguration

Über Umgebungsvariablen:

```bash
# Container-Konfiguration
export NOCODB_VERSION="latest"           # Docker Image Version
export NOCODB_PORT="8080"                # Port für NocoDB
export CONTAINER_NAME="nocodb-ci-test"   # Container Name
export NETWORK_NAME="nocodb-test-net"    # Docker Network

# Authentifizierung
export NC_ADMIN_EMAIL="admin@test.local"
export NC_ADMIN_PASSWORD="TestPassword123!"

# Beispiel: Custom Setup
NOCODB_PORT=9090 CONTAINER_NAME=my-nocodb ./scripts/ci-setup.sh setup
```

## 📝 Ausgabe-Dateien

Nach erfolgreichem Setup werden folgende Dateien erstellt:

### `.env.test` (Bash-Format)
```bash
export NOCODB_API_TOKEN="your-token-here"
export NOCODB_URL="http://localhost:8080"
export NC_ADMIN_EMAIL="admin@test.local"
export NC_ADMIN_PASSWORD="TestPassword123!"
```

Verwendung:
```bash
source .env.test
curl -H "xc-token: $NOCODB_API_TOKEN" $NOCODB_URL/api/v1/db/meta/projects
```

### `nocodb-config.json` (JSON-Format)
```json
{
  "api_token": "your-token-here",
  "base_url": "http://localhost:8080",
  "admin_email": "admin@test.local",
  "container_name": "nocodb-ci-test"
}
```

Verwendung:
```python
import json

with open('nocodb-config.json') as f:
    config = json.load(f)
    token = config['api_token']
    base_url = config['base_url']
```

## 🔧 Integration mit Tests

### GitHub Actions (Empfohlen)

```yaml
- name: 🐳 Setup NocoDB Container
  run: |
    chmod +x scripts/ci-setup.sh
    CONTAINER_NAME=nocodb-integration-test \
    NOCODB_PORT=8080 \
    ./scripts/ci-setup.sh setup

- name: 🧪 Run Integration Tests
  run: |
    python -m pytest tests/test_integration.py -v
  env:
    SKIP_INTEGRATION: 0
    USE_EXTERNAL_CONTAINER: 1

- name: 🧹 Cleanup
  if: always()
  run: |
    CONTAINER_NAME=nocodb-integration-test ./scripts/ci-setup.sh cleanup
```

**Wichtig:** `USE_EXTERNAL_CONTAINER=1` teilt den Tests mit, dass ein externes Container-Management verwendet wird.

### GitLab CI

```yaml
integration_tests:
  script:
    - chmod +x scripts/ci-setup.sh
    - ./scripts/ci-setup.sh setup
    - pytest tests/test_integration.py -v
  after_script:
    - ./scripts/ci-setup.sh cleanup
  variables:
    SKIP_INTEGRATION: 0
    USE_EXTERNAL_CONTAINER: 1
```

### Lokale Entwicklung

**Option 1: Externes Container-Management (wie CI/CD)**

```bash
# Container starten
./scripts/ci-setup.sh setup

# Tests ausführen mit externem Container
SKIP_INTEGRATION=0 USE_EXTERNAL_CONTAINER=1 pytest tests/test_integration.py -v

# Aufräumen
./scripts/ci-setup.sh cleanup
```

**Option 2: Automatisches Management (default)**

```bash
# Tests verwalten Container selbst
SKIP_INTEGRATION=0 pytest tests/test_integration.py -v
```

## 🐍 Python-Tests (test_integration.py)

Die Integration-Tests in `tests/test_integration.py` haben zwei Modi:

### Modus 1: Automatisches Container-Management (Default)
```bash
# Tests starten ihren eigenen Container
SKIP_INTEGRATION=0 pytest tests/test_integration.py
```

### Modus 2: Externe Container-Verwaltung (CI/CD)
```bash
# Container wird extern (z.B. durch ci-setup.sh) verwaltet
./scripts/ci-setup.sh setup
source .env.test
SKIP_INTEGRATION=0 pytest tests/test_integration.py
```

Die Tests erkennen automatisch:
- ✅ Ob Docker verfügbar ist
- ✅ Ob bereits ein Container läuft
- ✅ Ob Credentials vorhanden sind

## 🔍 Troubleshooting

### Container startet nicht

```bash
# Logs anzeigen
docker logs nocodb-ci-test

# Container-Status prüfen
docker ps -a | grep nocodb

# Manual cleanup
docker stop nocodb-ci-test
docker rm nocodb-ci-test
```

### Port bereits belegt

```bash
# Nutze anderen Port
NOCODB_PORT=9090 ./scripts/ci-setup.sh setup
```

### API-Verbindung fehlschlägt

```bash
# Prüfe Container-Status
docker ps

# Teste Health-Endpoint
curl http://localhost:8080/api/v1/health

# Container neu starten
./scripts/ci-setup.sh cleanup
./scripts/ci-setup.sh setup
```

### Alte Container aufräumen

```bash
# Alle NocoDB-Container stoppen
docker ps -a | grep nocodb | awk '{print $1}' | xargs docker stop

# Aufräumen
docker system prune -f
```

## 📋 Voraussetzungen

- Docker
- curl
- jq (optional, aber empfohlen für bessere JSON-Ausgabe)

Installation auf Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y docker.io curl jq
```

## 🎯 Best Practices

1. **CI/CD**: Nutze das Setup-Script für konsistente Container-Verwaltung
2. **Lokale Entwicklung**: Wähle zwischen externem oder automatischem Container-Management
3. **Cleanup**: Führe immer Cleanup durch (auch bei Fehlern via `if: always()`)
4. **Credentials**: `.env.test` nie in Git committen (ist in `.gitignore`)
5. **Timeout**: Erhöhe `TEST_TIMEOUT` bei langsamen Systemen
6. **Tests**: Lasse pytest die Tests ausführen, nicht das Setup-Script

## 🤝 Beitragen

Verbesserungen an den CI-Scripts sind willkommen! Bitte:

1. Teste auf verschiedenen Plattformen (Linux, macOS)
2. Dokumentiere Änderungen in dieser README
3. Halte den Fokus auf Container-Management (keine Test-Logik)
