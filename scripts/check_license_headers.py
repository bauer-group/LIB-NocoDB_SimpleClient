#!/usr/bin/env python3
"""Check license headers in Python files."""

import sys
from pathlib import Path

# Key components that should be present in the license
LICENSE_COMPONENTS = [
    "MIT License",
    "Copyright (c) BAUER GROUP",
    "Permission is hereby granted, free of charge",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND',
]


def check_license_header(file_path: Path) -> bool:
    """Check if a Python file has the correct license header."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Skip files that are too short to have a license header
        if len(content) < 100:
            return True

        # Check if all license components are present
        for component in LICENSE_COMPONENTS:
            if component not in content:
                return False

        return True
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False


def main():
    """Main function."""
    # Check if files are passed as arguments (from pre-commit)
    if len(sys.argv) > 1:
        files_to_check = [Path(f) for f in sys.argv[1:]]
    else:
        # Fallback to scanning src directory
        src_dir = Path("src")
        if not src_dir.exists():
            print("src directory not found")
            return 0
        files_to_check = list(src_dir.rglob("*.py"))

    missing_headers = []

    for py_file in files_to_check:
        if py_file.exists() and not check_license_header(py_file):
            missing_headers.append(py_file)

    if missing_headers:
        print("Files missing license headers:")
        for file_path in missing_headers:
            print(f"  - {file_path}")
        return 1

    if files_to_check:
        print("All files have correct license headers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
