#!/bin/bash
# Unix wrapper for setup.py
set -e

echo "Running NocoDB Simple Client setup..."
cd "$(dirname "$0")/.."
python3 scripts/setup.py "$@"

echo ""
echo "Setup completed successfully!"