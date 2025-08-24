#!/usr/bin/env python3
"""
Local validation script for NocoDB Simple Client.
Runs all quality checks in the correct order.
"""

import subprocess
import sys
from pathlib import Path

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Import project configuration
try:
    from .project_config import ProjectConfig
except ImportError:
    # Direct execution fallback
    sys.path.append(str(Path(__file__).parent))
    from project_config import ProjectConfig


def run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(f"✅ {description} passed")
            return True, result.stdout
        else:
            print(f"❌ {description} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False, result.stderr

    except FileNotFoundError:
        print(f"❌ {description} failed - command not found: {' '.join(cmd)}")
        return False, "Command not found"
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False, str(e)


def main():
    """Run all validation checks."""
    print("🚀 NocoDB Simple Client - Local Validation")
    print("=" * 50)

    # Load project configuration
    config = ProjectConfig()
    print(f"Project: {config.get_project_name()} v{config.get_project_version()}")

    # Show configured tools
    if config.has_tool_config("pytest.ini_options"):
        print("✅ Using pytest configuration from pyproject.toml")
    if config.has_tool_config("black"):
        print("✅ Using black configuration from pyproject.toml")
    if config.has_tool_config("ruff"):
        print("✅ Using ruff configuration from pyproject.toml")
    if config.has_tool_config("mypy"):
        print("✅ Using mypy configuration from pyproject.toml")
    if config.has_tool_config("bandit"):
        print("✅ Using bandit configuration from pyproject.toml")
    print()

    checks = [
        # Code formatting (using pyproject.toml config)
        (["python", "-m", "black", "--check", "src/", "tests/"], "Black code formatting check"),
        # Linting (using pyproject.toml config)
        (["python", "-m", "ruff", "check", "src/", "tests/"], "Ruff linting"),
        # Type checking (using pyproject.toml config)
        (["python", "-m", "mypy", "src/nocodb_simple_client/"], "MyPy type checking"),
        # Security checks (using pyproject.toml config)
        (["python", "-m", "bandit", "-r", "src/"], "Bandit security scan"),
        # Tests (using pyproject.toml config)
        (["python", "-m", "pytest", "-v"], "Unit tests"),
        # Coverage (using pyproject.toml config)
        (
            [
                "python",
                "-m",
                "pytest",
                "--cov=src/nocodb_simple_client",
                "--cov-report=term-missing",
            ],
            "Test coverage",
        ),
        # Build test (using pyproject.toml)
        (["python", "-m", "build", "--sdist", "--wheel"], "Package build test"),
    ]

    failed_checks = []
    passed_checks = []

    for cmd, description in checks:
        success, output = run_command(cmd, description)
        if success:
            passed_checks.append(description)
        else:
            failed_checks.append((description, output))
        print()

    # Summary
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    print(f"✅ Passed: {len(passed_checks)}")
    for check in passed_checks:
        print(f"   - {check}")

    if failed_checks:
        print(f"\n❌ Failed: {len(failed_checks)}")
        for check, _error in failed_checks:
            print(f"   - {check}")

    print(f"\nTotal: {len(passed_checks) + len(failed_checks)} checks")

    if failed_checks:
        print("\n🔧 To fix issues:")
        print("   - Format code: black src/ tests/")
        print("   - Fix linting: ruff --fix src/ tests/")
        print("   - Run tests: pytest")
        sys.exit(1)
    else:
        print("\n🎉 All validation checks passed! Ready for commit.")
        sys.exit(0)


if __name__ == "__main__":
    main()
