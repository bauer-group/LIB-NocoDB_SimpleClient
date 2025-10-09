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
NC_ADMIN_PASSWORD="${NC_ADMIN_PASSWORD:-TestPassword123!}"
CONTAINER_NAME="${CONTAINER_NAME:-nocodb-ci-test}"
NETWORK_NAME="${NETWORK_NAME:-nocodb-test-net}"

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

    # Erstelle Netzwerk falls nicht vorhanden
    docker network create $NETWORK_NAME 2>/dev/null || true

    # Stoppe alten Container falls vorhanden
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true

    # Starte NocoDB Container
    docker run -d \
        --name $CONTAINER_NAME \
        --network $NETWORK_NAME \
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

    # Step 1: Get list of bases (using Basic Auth with admin credentials)
    log "📋 Hole Base-Liste..."
    local auth_header="Authorization: Basic $(echo -n "$NC_ADMIN_EMAIL:$NC_ADMIN_PASSWORD" | base64)"

    local bases_response=$(curl -s -X GET "$NOCODB_URL/api/v2/meta/bases" \
        -H "$auth_header")

    # Debug output
    if ! echo "$bases_response" | grep -q '^{'; then
        error "Konnte Bases nicht abrufen. Response: $bases_response"
    fi

    # Extract first base ID
    local base_id=""
    if command -v jq &> /dev/null; then
        base_id=$(echo "$bases_response" | jq -r '.list[0].id // empty' 2>/dev/null)
    else
        base_id=$(echo "$bases_response" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"//')
    fi

    if [ -z "$base_id" ]; then
        error "Keine Base gefunden. Response: $bases_response"
    fi

    log "✅ Base gefunden: $base_id"

    # Step 2: Create API Token for this base
    log "🔐 Erstelle API Token für Base..."
    local token_response=$(curl -s -X POST "$NOCODB_URL/api/v2/meta/bases/$base_id/api-tokens" \
        -H "$auth_header" \
        -H "Content-Type: application/json" \
        -d '{"description":"CI/CD Integration Token"}')

    # Extract API token
    if command -v jq &> /dev/null; then
        API_TOKEN=$(echo "$token_response" | jq -r '.token // empty' 2>/dev/null)
    else
        API_TOKEN=$(echo "$token_response" | grep -o '"token":"[^"]*' | sed 's/"token":"//;s/"//')
    fi

    if [ -z "$API_TOKEN" ]; then
        warning "API Token Erstellung fehlgeschlagen, verwende Basic Auth"
        warning "Response war: $token_response"
        # Fallback: Use Basic Auth credentials
        API_TOKEN="$NC_ADMIN_EMAIL:$NC_ADMIN_PASSWORD"
    else
        log "✅ API Token erfolgreich erstellt"
    fi
}

    # Extract API token with error handling
    if command -v jq &> /dev/null; then
        API_TOKEN=$(echo "$api_token_response" | jq -r '.token // empty' 2>/dev/null)
    else
        API_TOKEN=$(echo "$api_token_response" | grep -o '"token":"[^"]*' | sed 's/"token":"//')
    fi

    # Fallback to auth token if API token generation failed
    if [ -z "$API_TOKEN" ] || [ "$API_TOKEN" = "null" ]; then
        warning "API Token konnte nicht generiert werden, nutze Auth Token als Fallback"
        warning "API Response war: $api_token_response"
        API_TOKEN=$AUTH_TOKEN
    else
        log "✅ API Token generiert"
    fi
}

# Save Credentials
save_credentials() {
    log "💾 Speichere Credentials..."

    # Bash environment file
    cat > .env.test <<EOF
export NOCODB_API_TOKEN="$API_TOKEN"
export NOCODB_URL="$NOCODB_URL"
export NC_ADMIN_EMAIL="$NC_ADMIN_EMAIL"
export NC_ADMIN_PASSWORD="$NC_ADMIN_PASSWORD"
EOF

    # JSON config file
    cat > nocodb-config.json <<EOF
{
  "api_token": "$API_TOKEN",
  "base_url": "$NOCODB_URL",
  "admin_email": "$NC_ADMIN_EMAIL",
  "container_name": "$CONTAINER_NAME"
}
EOF

    # GitHub Actions format
    if [ -n "$GITHUB_ENV" ]; then
        echo "NOCODB_API_TOKEN=$API_TOKEN" >> $GITHUB_ENV
        echo "NOCODB_URL=$NOCODB_URL" >> $GITHUB_ENV
    fi

    # GitLab CI format
    if [ -n "$CI_PROJECT_DIR" ]; then
        echo "NOCODB_API_TOKEN=$API_TOKEN" > nocodb.env
        echo "NOCODB_URL=$NOCODB_URL" >> nocodb.env
    fi

    log "✅ Credentials gespeichert"
}

# Test Connection
test_connection() {
    log "🔌 Teste API Verbindung..."

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "xc-token: $API_TOKEN" \
        "$NOCODB_URL/api/v1/db/meta/projects")

    local http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    local body=$(echo "$response" | sed '$d')  # Remove last line (HTTP_STATUS)

    if [ "$http_status" = "200" ]; then
        log "✅ API Verbindung erfolgreich"

        # Pretty print if jq available and body is valid JSON
        if command -v jq &> /dev/null && echo "$body" | jq empty 2>/dev/null; then
            echo "$body" | jq '.'
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

    # Remove network
    docker network rm $NETWORK_NAME 2>/dev/null || true

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
    info "API Token: $API_TOKEN"
    info "URL: $NOCODB_URL"
    echo ""
    info "Credentials wurden gespeichert in:"
    echo "  - .env.test (Bash format)"
    echo "  - nocodb-config.json (JSON format)"
    echo ""
    info "Führe jetzt deine Tests aus mit:"
    echo "  source .env.test"
    echo "  pytest tests/test_integration.py"
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
