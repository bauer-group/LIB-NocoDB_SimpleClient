#!/bin/bash

# ============================================
# NocoDB CI/CD All-in-One Setup Script
# ============================================
# Dieses Script automatisiert das komplette Setup
# für NocoDB Testing in CI/CD Pipelines
#
# Usage:
#   ./ci-setup.sh [command]
#
# Commands:
#   setup    - Komplettes Setup (default)
#   cleanup  - Räume auf
#   docker   - Nur Docker Setup
#   token    - Nur Token Generation
# ============================================

set -e

# Konfiguration
NOCODB_VERSION="${NOCODB_VERSION:-latest}"
NOCODB_PORT="${NOCODB_PORT:-8080}"
NOCODB_URL="${NOCODB_URL:-http://localhost:$NOCODB_PORT}"
NC_ADMIN_EMAIL="${NC_ADMIN_EMAIL:-admin@test.local}"
NC_ADMIN_PASSWORD="${NC_ADMIN_PASSWORD:-TestPassword123}"
CONTAINER_NAME="${CONTAINER_NAME:-nocodb-ci-test}"

AUTH_TOKEN=""
BASE_ID=""
API_TOKEN=""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check Dependencies
check_dependencies() {
    log "Prüfe Abhängigkeiten..."

    local missing_deps=()

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    if ! command -v jq &> /dev/null; then
        warning "jq nicht installiert (optional für JSON parsing)"
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Fehlende Abhängigkeiten: ${missing_deps[*]}"
    fi

    log "✅ Alle Abhängigkeiten vorhanden"
}

# Docker Setup
setup_docker() {
    log "🐳 Starte NocoDB Docker Container..."

    # Stoppe alten Container falls vorhanden
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true

    # Starte NocoDB Container (kein Network erforderlich)
    docker run -d \
        --name $CONTAINER_NAME \
        -p $NOCODB_PORT:8080 \
        -e NC_DISABLE_TELE="true" \
        -e NC_ADMIN_EMAIL="$NC_ADMIN_EMAIL" \
        -e NC_ADMIN_PASSWORD="$NC_ADMIN_PASSWORD" \
        nocodb/nocodb:$NOCODB_VERSION

    log "Container gestartet: $CONTAINER_NAME"

    # Gib dem Container Zeit zum Initialisieren
    info "Warte 3 Sekunden für Container-Initialisierung..."
    sleep 3
}

# Wait for NocoDB
wait_for_nocodb() {
    log "⏳ Warte auf NocoDB..."

    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        # Check if container is still running
        if ! docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
            error "Container $CONTAINER_NAME läuft nicht mehr!"
            echo "Container Logs:"
            docker logs $CONTAINER_NAME 2>&1 | tail -50
            exit 1
        fi

        # Check if NocoDB is responding
        if curl -s "$NOCODB_URL/api/v1/health" > /dev/null 2>&1; then
            log "✅ NocoDB ist bereit!"
            return 0
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    error "NocoDB konnte nicht gestartet werden (Timeout nach $max_attempts Versuchen)"
    echo "Container Logs:"
    docker logs $CONTAINER_NAME 2>&1 | tail -50
}

# Generate API Token
generate_token() {
    log "🔑 Generiere API Token..."

    # Step 1: Sign in to retrieve auth token (xc-auth header)
    log "👤 Melde Admin-Benutzer an..."

    local signin_response=$(curl -s -X POST "$NOCODB_URL/api/v1/auth/user/signin" \
        -H "Content-Type: application/json" \
        -H "xc-gui: true" \
        -d "{\"email\":\"$NC_ADMIN_EMAIL\",\"password\":\"$NC_ADMIN_PASSWORD\"}")

    if command -v jq &> /dev/null; then
        AUTH_TOKEN=$(echo "$signin_response" | jq -r '.token // empty' 2>/dev/null)
    else
        AUTH_TOKEN=$(echo "$signin_response" | grep -o '"token":"[^"]*' | head -1 | sed 's/"token":"//;s/"//')
    fi

    if [ -z "$AUTH_TOKEN" ]; then
        error "Login fehlgeschlagen. Response: $signin_response"
    fi

    log "✅ Erfolgreich angemeldet"

    # Step 2: Check if base exists (should be empty initially)
    log "📋 Prüfe Base-Liste..."

    local bases_response=$(curl -s -X GET "$NOCODB_URL/api/v1/db/meta/projects/" \
        -H "xc-auth: $AUTH_TOKEN" \
        -H "xc-gui: true")

    # Debug output
    if ! echo "$bases_response" | grep -q '"list"'; then
        error "Konnte Bases nicht abrufen. Response: $bases_response"
    fi

    # Extract first base ID (if any)
    if command -v jq &> /dev/null; then
        BASE_ID=$(echo "$bases_response" | jq -r '.list[0].id // empty' 2>/dev/null)
    else
        BASE_ID=$(echo "$bases_response" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"//')
    fi

    # Step 3: Create base if none exists
    if [ -z "$BASE_ID" ]; then
        log "📦 Erstelle Test-Base..."
        local create_response=$(curl -s -X POST "$NOCODB_URL/api/v1/db/meta/projects/" \
            -H "xc-auth: $AUTH_TOKEN" \
            -H "xc-gui: true" \
            -H "Content-Type: application/json" \
            -d '{"title":"TestBase","meta":"{\"iconColor\":\"#FA8231\"}"}')

        if command -v jq &> /dev/null; then
            BASE_ID=$(echo "$create_response" | jq -r '.id // empty' 2>/dev/null)
        else
            BASE_ID=$(echo "$create_response" | grep -o '"id":"[^"]*' | head -1 | sed 's/"id":"//;s/"//')
        fi

        if [ -z "$BASE_ID" ]; then
            error "Base konnte nicht erstellt werden. Response: $create_response"
        fi

        log "✅ Base erstellt: $BASE_ID"
    else
        log "✅ Base gefunden: $BASE_ID"
    fi

    # Step 4: Create API Token (global token, not base-specific)
    log "🔐 Erstelle API Token..."
    local token_response=$(curl -s -X POST "$NOCODB_URL/api/v1/tokens" \
        -H "xc-auth: $AUTH_TOKEN" \
        -H "xc-gui: true" \
        -H "Content-Type: application/json" \
        -d '{"description":"CI/CD Tests"}')

    # Extract API token
    if command -v jq &> /dev/null; then
        API_TOKEN=$(echo "$token_response" | jq -r '.token // empty' 2>/dev/null)
    else
        API_TOKEN=$(echo "$token_response" | grep -o '"token":"[^"]*' | head -1 | sed 's/"token":"//;s/"//')
    fi

    if [ -z "$API_TOKEN" ]; then
        warning "API Token Erstellung fehlgeschlagen"
        warning "Response war: $token_response"
        error "Konnte keinen API Token generieren"
    fi

    log "✅ API Token erfolgreich erstellt"
    info "Base ID: $BASE_ID"
    info "API Token: $API_TOKEN"
}

# Save Credentials
save_credentials() {
    log "💾 Speichere Credentials..."

    # JSON config file (primary)
    cat > nocodb-config.json <<EOF
{
  "NOCODB_TOKEN": "$API_TOKEN",
  "NOCODB_BASE_URL": "$NOCODB_URL",
  "NOCODB_PROJECT_ID": "$BASE_ID"
}
EOF

    # Bash environment file for sourcing (same variable names)
    cat > .env.test <<EOF
export NOCODB_TOKEN="$API_TOKEN"
export NOCODB_BASE_URL="$NOCODB_URL"
export NOCODB_PROJECT_ID="$BASE_ID"
EOF

    # GitHub Actions format
    if [ -n "$GITHUB_ENV" ]; then
        echo "NOCODB_TOKEN=$API_TOKEN" >> $GITHUB_ENV
        echo "NOCODB_BASE_URL=$NOCODB_URL" >> $GITHUB_ENV
        echo "NOCODB_PROJECT_ID=$BASE_ID" >> $GITHUB_ENV
    fi

    # GitLab CI format
    if [ -n "$CI_PROJECT_DIR" ]; then
        echo "NOCODB_TOKEN=$API_TOKEN" > nocodb.env
        echo "NOCODB_BASE_URL=$NOCODB_URL" >> nocodb.env
        echo "NOCODB_PROJECT_ID=$BASE_ID" >> nocodb.env
    fi

    log "✅ Credentials gespeichert"
    info "Dateien erstellt:"
    echo "  - nocodb-config.json (JSON format - primary)"
    echo "  - .env.test (Bash source format)"
}

# Test Connection
test_connection() {
    log "🔌 Teste API Verbindung..."

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "xc-token: $API_TOKEN" \
        "$NOCODB_URL/api/v1/db/meta/projects/")

    local http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    local body=$(echo "$response" | sed '$d')  # Remove last line (HTTP_STATUS)

    if [ "$http_status" = "200" ]; then
        log "✅ API Verbindung erfolgreich"

        # Pretty print if jq available and body is valid JSON
        if command -v jq &> /dev/null && echo "$body" | jq empty 2>/dev/null; then
            info "Verfügbare Bases:"
            echo "$body" | jq '.list[] | {id: .id, title: .title}'
        else
            echo "$body"
        fi
        return 0
    else
        error "API Verbindung fehlgeschlagen (HTTP $http_status). Body: $body"
    fi
}

# Cleanup
cleanup() {
    log "🧹 Räume auf..."

    # Stop and remove container
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true

    # Remove files
    rm -f .env.test nocodb-config.json nocodb.env

    log "✅ Cleanup abgeschlossen"
}

# Main Setup
setup() {
    log "🚀 Starte NocoDB CI/CD Setup..."

    check_dependencies
    setup_docker
    wait_for_nocodb
    generate_token
    save_credentials
    test_connection

    echo ""
    log "✨ Setup erfolgreich abgeschlossen!"
    echo ""
    info "Base ID: $BASE_ID"
    info "API Token: $API_TOKEN"
    info "URL: $NOCODB_URL"
    echo ""
    info "Credentials wurden gespeichert in:"
    echo "  - nocodb-config.json (JSON - für Python/pytest)"
    echo "  - .env.test (Bash - für Shell scripts)"
    echo ""
    info "Führe jetzt deine Tests aus mit:"
    echo "  python -m pytest tests/"
    echo ""
    info "Für Cleanup:"
    echo "  $0 cleanup"
    echo ""
}

# Show Usage
usage() {
    cat <<EOF
NocoDB CI/CD Container Management Script

Usage: $0 [command]

Commands:
    setup    - Komplettes Setup: Container starten + Token generieren (default)
    cleanup  - Container stoppen und aufräumen
    docker   - Nur Docker Container starten und warten
    token    - Nur Token generieren (Container muss bereits laufen)
    help     - Zeige diese Hilfe

Environment Variables:
    NOCODB_VERSION     - Docker Image Version (default: latest)
    NOCODB_PORT        - Port für NocoDB (default: 8080)
    NC_ADMIN_EMAIL     - Admin Email (default: admin@test.local)
    NC_ADMIN_PASSWORD  - Admin Password (default: TestPassword123!)
    CONTAINER_NAME     - Docker Container Name (default: nocodb-ci-test)

Examples:
    # Standard Setup (Container + Token)
    $0 setup

    # Mit custom Port
    NOCODB_PORT=8090 $0 setup

    # Nur Container starten
    $0 docker

    # Nur Token generieren
    $0 token

    # Aufräumen
    $0 cleanup

Workflow:
    1. Setup: $0 setup
    2. Tests: pytest tests/test_integration.py
    3. Cleanup: $0 cleanup

EOF
}

# Parse Command
COMMAND=${1:-setup}

case $COMMAND in
    setup)
        setup
        ;;
    cleanup)
        cleanup
        ;;
    docker)
        check_dependencies
        setup_docker
        wait_for_nocodb
        ;;
    token)
        generate_token
        save_credentials
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unbekannter Command: $COMMAND"
        ;;
esac
