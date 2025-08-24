#!/bin/bash
# Smart commit script that handles pre-commit auto-fixes

if [ $# -eq 0 ]; then
    echo "Usage: scripts/smart-commit.sh \"commit message\""
    exit 1
fi

echo "Attempting commit..."
git commit -m "$1"
exit_code=$?

# Check if commit failed (exit code 1 means pre-commit made changes)
if [ $exit_code -eq 1 ]; then
    echo "Pre-commit made automatic fixes. Re-staging and committing..."
    git add .
    git commit -m "$1"

    if [ $? -eq 0 ]; then
        echo "✅ Commit successful after auto-fixes!"
    else
        echo "❌ Commit failed even after auto-fixes. Please check the errors above."
        exit 1
    fi
elif [ $exit_code -eq 0 ]; then
    echo "✅ Commit successful!"
else
    echo "❌ Commit failed with exit code $exit_code"
    exit $exit_code
fi
