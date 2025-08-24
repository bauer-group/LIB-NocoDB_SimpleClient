#!/bin/bash
# Unix wrapper for quick-test.py
set -e

cd "$(dirname "$0")/.."
python3 scripts/quick-test.py "$@"
