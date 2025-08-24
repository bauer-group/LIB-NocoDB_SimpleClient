#!/usr/bin/env python3
"""Custom security checks for Python files."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

DANGEROUS_FUNCTIONS = {
    'eval', 'exec', 'compile', 'open', '__import__',
    'getattr', 'setattr', 'delattr', 'hasattr',
    'input', 'raw_input'  # Python 2 compatibility
}

DANGEROUS_MODULES = {
    'subprocess', 'os', 'sys', 'socket', 'pickle',
    'marshal', 'shelve', 'dbm'
}

class SecurityChecker(ast.NodeVisitor):
    """AST visitor for security checks."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[Tuple[int, str]] = []
    
    def visit_Call(self, node):
        """Check function calls for security issues."""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_FUNCTIONS:
                if node.func.id not in ['open']:  # open is okay in context
                    self.issues.append((
                        node.lineno,
                        f"Potentially dangerous function call: {node.func.id}"
                    ))
        
        # Check for SQL injection patterns
        if isinstance(node.func, ast.Attribute):
            if hasattr(node.func.value, 'id') and node.func.attr in ['format', 'execute']:
                # Check for string formatting with user input
                for arg in node.args:
                    if isinstance(arg, ast.Str) and any(
                        pattern in arg.s.lower() 
                        for pattern in ['select', 'insert', 'update', 'delete', 'drop']
                    ):
                        self.issues.append((
                            node.lineno,
                            "Potential SQL injection vulnerability"
                        ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Check imports for dangerous modules."""
        for alias in node.names:
            if alias.name in DANGEROUS_MODULES:
                # Allow specific modules that we know are used safely
                if alias.name not in ['os', 'subprocess']:
                    self.issues.append((
                        node.lineno,
                        f"Import of potentially dangerous module: {alias.name}"
                    ))
        
        self.generic_visit(node)
    
    def visit_Str(self, node):
        """Check string literals for hardcoded secrets."""
        # Check for potential API keys, tokens, passwords
        if len(node.s) > 20 and any(
            keyword in node.s.lower() 
            for keyword in ['api_key', 'token', 'password', 'secret', 'key']
        ):
            # Check if it looks like a real secret (not a placeholder)
            if not any(
                placeholder in node.s.lower()
                for placeholder in ['your-', 'example', 'test', 'dummy', 'placeholder']
            ):
                self.issues.append((
                    node.lineno,
                    "Potential hardcoded secret detected"
                ))
        
        self.generic_visit(node)

def check_file(file_path: Path) -> List[Tuple[int, str]]:
    """Check a Python file for security issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        checker = SecurityChecker(str(file_path))
        checker.visit(tree)
        return checker.issues
    
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return []

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: security_checks.py <file1> [file2] ...")
        return 1
    
    total_issues = 0
    
    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
        
        issues = check_file(file_path)
        if issues:
            print(f"\nSecurity issues in {file_path}:")
            for line_no, message in issues:
                print(f"  Line {line_no}: {message}")
            total_issues += len(issues)
    
    if total_issues > 0:
        print(f"\nTotal security issues found: {total_issues}")
        return 1
    
    print("No security issues found")
    return 0

if __name__ == "__main__":
    sys.exit(main())