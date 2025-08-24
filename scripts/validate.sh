#!/bin/bash
# Unix wrapper for validate.py
set -e

cd "$(dirname "$0")/.."
python3 scripts/validate.py "$@"
