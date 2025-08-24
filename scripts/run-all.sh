#!/bin/bash
# Unix wrapper for run-all.py
set -e

echo "Running complete development validation..."
echo ""

cd "$(dirname "$0")/.."
python3 scripts/run-all.py "$@"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All checks completed successfully!"
else
    echo "❌ Some checks failed. Please review the output above."
fi

exit $EXIT_CODE
