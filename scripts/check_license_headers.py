#!/usr/bin/env python3
"""Check license headers in Python files."""

import os
import sys
from pathlib import Path

LICENSE_HEADER = '''"""
MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""'''

def check_license_header(file_path: Path) -> bool:
    """Check if a Python file has the correct license header."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Skip files that are too short to have a license header
        if len(content) < 100:
            return True
            
        # Check if license header is present
        return LICENSE_HEADER.strip() in content
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def main():
    """Main function."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("src directory not found")
        return 0
    
    missing_headers = []
    
    for py_file in src_dir.rglob("*.py"):
        if not check_license_header(py_file):
            missing_headers.append(py_file)
    
    if missing_headers:
        print("Files missing license headers:")
        for file_path in missing_headers:
            print(f"  - {file_path}")
        return 1
    
    print("All files have correct license headers")
    return 0

if __name__ == "__main__":
    sys.exit(main())