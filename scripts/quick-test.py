#!/usr/bin/env python3
"""
Quick test script for NocoDB Simple Client.
Runs essential checks for rapid development feedback.
"""

import subprocess
import sys
from pathlib import Path

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def print_banner():
    """Print test banner."""
    print("=" * 50)
    print("🚀 NocoDB Simple Client - Quick Tests")
    print("=" * 50)
    print()


def run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).parent.parent,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0:
            print(f"✅ {description} passed")
            return True, result.stdout
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False, result.stderr

    except FileNotFoundError:
        print(f"❌ {description} failed - command not found: {' '.join(cmd)}")
        return False, "Command not found"
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False, str(e)


def check_virtual_env():
    """Check if virtual environment is active."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected")
        print(
            "   Consider activating venv: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
        )
    print()


def main():
    """Run quick tests."""
    print_banner()

    # Check virtual environment
    check_virtual_env()

    # Quick checks in order of importance
    quick_checks = [
        # Fast linting
        (
            ["python", "-m", "ruff", "check", "src/", "tests/", "--select=F,E"],
            "Fast linting (syntax errors)",
        ),
        # Type checking (most important files only)
        (["python", "-m", "mypy", "src/nocodb_simple_client/__init__.py"], "Quick type check"),
        # Fast tests only (exclude slow, integration, performance, and benchmark tests)
        (
            [
                "python",
                "-m",
                "pytest",
                "-m",
                "not slow and not integration and not performance and not benchmark",
                "-x",
                "--tb=short",
            ],
            "Fast unit tests",
        ),
        # Basic import test
        (["python", "-c", "import src.nocodb_simple_client; print('Import OK')"], "Import test"),
    ]

    failed_checks = []
    passed_checks = []

    for cmd, description in quick_checks:
        success, output = run_command(cmd, description)
        if success:
            passed_checks.append(description)
        else:
            failed_checks.append((description, output))
        print()

    # Summary
    print("=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)

    print(f"✅ Passed: {len(passed_checks)}")
    for check in passed_checks:
        print(f"   - {check}")

    if failed_checks:
        print(f"\n❌ Failed: {len(failed_checks)}")
        for check, _error in failed_checks:
            print(f"   - {check}")

    print(f"\nTotal: {len(passed_checks) + len(failed_checks)} quick checks")

    if failed_checks:
        print("\n🔧 Quick fixes:")
        print("   - Format: black src/ tests/")
        print("   - Fix imports: ruff --fix src/ tests/")
        print("   - Full validation: python scripts/validate.py")
        sys.exit(1)
    else:
        print("\n🎉 All quick checks passed!")
        print("💡 Run full validation with: python scripts/validate.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
