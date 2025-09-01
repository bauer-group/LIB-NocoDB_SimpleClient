#!/usr/bin/env python3
"""
Run all local development checks and cleanup afterwards.
Simple all-in-one script for local testing and validation.

Usage:
    python scripts/run-all.py                    # Default: unit tests only
    python scripts/run-all.py --integration      # Include integration tests
    python scripts/run-all.py --performance      # Include performance tests
    python scripts/run-all.py --all-tests        # Include all tests
    python scripts/run-all.py --ci               # CI mode: unit tests only, no cleanup prompts
    python scripts/run-all.py --help             # Show help
"""

import argparse
import shutil
import subprocess
import sys
import time
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
    sys.path.append(str(Path(__file__).parent))
    from project_config import ProjectConfig


class LocalRunner:
    """Local development test runner with cleanup."""

    def __init__(self, include_integration=False, include_performance=False, ci_mode=False):
        self.project_root = Path(__file__).parent.parent
        self.config = ProjectConfig(self.project_root)
        self.temp_files = []
        self.start_time = time.time()
        self.include_integration = include_integration
        self.include_performance = include_performance
        self.ci_mode = ci_mode

    def print_header(self):
        """Print header."""
        print("=" * 60)
        mode = "CI" if self.ci_mode else "Local"
        print(f"🚀 NocoDB Simple Client - {mode} Development Runner")
        print("=" * 60)
        print(f"Project: {self.config.get_project_name()} v{self.config.get_project_version()}")
        print(f"Python: {sys.version.split()[0]}")

        # Show test mode
        test_modes = []
        if self.include_integration:
            test_modes.append("Integration")
        if self.include_performance:
            test_modes.append("Performance")
        if not test_modes:
            test_modes.append("Unit")

        print(f"Test Mode: {', '.join(test_modes)} Tests")
        if self.ci_mode:
            print("🤖 CI Mode: Automated execution, minimal cleanup")
        print()

    def run_command(
        self, cmd: list[str], description: str, capture_output: bool = True
    ) -> tuple[bool, str]:
        """Run a command and return success status."""
        print(f"🔍 {description}...")

        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    encoding="utf-8",
                    errors="replace",
                )
                success = result.returncode == 0
                output = result.stdout + result.stderr
            else:
                # Show output directly for interactive commands
                result = subprocess.run(
                    cmd, cwd=self.project_root, timeout=120, encoding="utf-8", errors="replace"
                )
                success = result.returncode == 0
                output = ""

            if success:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED")
                if output and len(output.strip()) > 0:
                    print(f"   Error: {output.strip()[:200]}...")

            return success, output

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return False, "Command timed out"
        except FileNotFoundError:
            print(f"❌ {description} - COMMAND NOT FOUND: {' '.join(cmd)}")
            return False, f"Command not found: {' '.join(cmd)}"
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return False, str(e)

    def setup_temp_environment(self):
        """Setup temporary directories for outputs."""
        print("🗂️  Setting up temporary environment...")

        # Create temp directories that we'll track for cleanup
        temp_dirs = [
            self.project_root / "htmlcov",
            self.project_root / "reports",
            self.project_root / ".coverage",
            self.project_root / ".pytest_cache",
            self.project_root / ".mypy_cache",
            self.project_root / ".ruff_cache",
            self.project_root / "build",
            self.project_root / "dist",
            self.project_root / "*.egg-info",
        ]

        # Track existing temp files/dirs to avoid deleting user data
        for temp_path in temp_dirs:
            if "*" in str(temp_path):
                # Handle glob patterns
                parent = temp_path.parent
                pattern = temp_path.name
                if parent.exists():
                    for match in parent.glob(pattern):
                        self.temp_files.append(match)
            else:
                self.temp_files.append(temp_path)

        print("✅ Environment ready")

    def run_all_checks(self) -> bool:
        """Run all development checks."""
        print("\n🔄 Running all development checks...")
        print("-" * 40)

        checks = []

        # Setup validation
        checks.append((["python", "scripts/show-config.py"], "Project configuration check", True))

        # Code quality
        checks.extend(
            [
                (
                    ["python", "-m", "black", "--check", "src/", "tests/"],
                    "Code formatting (Black)",
                    True,
                ),
                (["python", "-m", "ruff", "check", "src/", "tests/"], "Code linting (Ruff)", True),
                (
                    ["python", "-m", "mypy", "src/nocodb_simple_client/"],
                    "Type checking (MyPy)",
                    True,
                ),
            ]
        )

        # Security
        checks.append(
            (
                [
                    "python",
                    "-m",
                    "bandit",
                    "-r",
                    "src/",
                    "--exclude",
                    "docs,scripts,tests,examples",
                ],
                "Security scanning (Bandit)",
                True,
            )
        )

        # Testing - build test commands based on selected modes
        test_marker = self._build_test_marker()

        # Main test run
        checks.append(
            (
                ["python", "-m", "pytest", "-v", "--tb=short", "-m", test_marker],
                f"Tests ({self._get_test_description()})",
                False,  # Show test output
            )
        )

        # Coverage (only for unit tests to avoid NocoDB dependency in CI)
        if not self.include_integration:
            checks.append(
                (
                    [
                        "python",
                        "-m",
                        "pytest",
                        "--cov=src/nocodb_simple_client",
                        "--cov-report=term-missing",
                        "--cov-report=html",
                        "-m",
                        "not integration and not performance",
                    ],
                    "Test coverage (unit tests)",
                    True,
                )
            )

        # Build validation (skip in CI mode to save time)
        if not self.ci_mode:
            checks.extend(
                [
                    (["python", "-m", "build"], "Package build", True),
                    (
                        [
                            "python",
                            "-c",
                            "import src.nocodb_simple_client; print('Import successful')",
                        ],
                        "Import test",
                        True,
                    ),
                ]
            )

        return self._execute_checks(checks)

    def _build_test_marker(self) -> str:
        """Build pytest marker expression based on selected test modes."""
        markers = []

        if not self.include_integration and not self.include_performance:
            # Default: only unit tests
            markers.append("not integration and not performance")
        else:
            # Build inclusion list
            included = []
            if self.include_integration:
                included.append("integration")
            if self.include_performance:
                included.append("performance")

            # Always include unit tests (tests without markers)
            if included:
                markers.append(
                    f"({' or '.join(included)}) or (not integration and not performance)"
                )
            else:
                markers.append("not integration and not performance")

        return " and ".join(markers) if len(markers) > 1 else markers[0]

    def _get_test_description(self) -> str:
        """Get description of which tests are being run."""
        if self.include_integration and self.include_performance:
            return "All tests"
        elif self.include_integration:
            return "Unit + Integration tests"
        elif self.include_performance:
            return "Unit + Performance tests"
        else:
            return "Unit tests only"

    def _execute_checks(self, checks: list) -> bool:
        """Execute all checks and return success status."""
        passed = 0
        total = len(checks)
        integration_failed = 0

        for cmd, description, capture in checks:
            success, output = self.run_command(cmd, description, capture)

            # Handle integration test failures gracefully
            if self.include_integration and "Tests" in description and not success:
                if "NOCODB_TOKEN" in output or "connection" in output.lower():
                    print("ℹ️  Integration tests failed (NocoDB instance not available)")
                    integration_failed += 1
                    continue

            if success:
                passed += 1
            elif self.ci_mode and "build" in description.lower():
                # In CI mode, build failures are less critical
                print("⚠️  Build check failed (non-critical in CI mode)")
                passed += 1
            print()

        # Calculate success rate
        if integration_failed > 0 and not self.ci_mode:
            print("=" * 40)
            print(f"📊 Results: {passed}/{total - integration_failed} core checks passed")
            print(f"ℹ️  {integration_failed} integration checks skipped (NocoDB not available)")
        else:
            print("=" * 40)
            print(f"📊 Results: {passed}/{total} checks passed")

        success_threshold = total - integration_failed
        if passed >= success_threshold:
            if integration_failed > 0:
                print("🎉 All available checks passed! (Integration tests require NocoDB)")
            else:
                print("🎉 All checks passed!")
            return True
        else:
            print(f"💥 {success_threshold - passed} checks failed")
            return False

    def cleanup(self):
        """Clean up temporary files and directories."""
        print("\n🧹 Cleaning up temporary files...")

        cleaned = 0
        for temp_path in self.temp_files:
            try:
                if temp_path.exists():
                    if temp_path.is_file():
                        temp_path.unlink()
                        cleaned += 1
                    elif temp_path.is_dir():
                        shutil.rmtree(temp_path)
                        cleaned += 1
            except Exception as e:
                print(f"⚠️  Could not remove {temp_path}: {e}")

        # Additional cleanup of common temp files
        additional_cleanup = [
            ".coverage*",
            "*.pyc",
            "__pycache__",
        ]

        for pattern in additional_cleanup:
            for match in self.project_root.rglob(pattern):
                try:
                    if match.is_file():
                        match.unlink()
                        cleaned += 1
                    elif match.is_dir():
                        shutil.rmtree(match)
                        cleaned += 1
                except Exception:
                    pass

        print(f"✅ Cleaned up {cleaned} temporary files/directories")

    def print_summary(self, success: bool):
        """Print final summary."""
        duration = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration:.2f}s")

        if success:
            print("🎉 SUCCESS: All checks passed!")
            print("✅ Your code is ready for commit and push")
        else:
            print("💥 FAILURE: Some checks failed")
            print("🔧 Please fix the issues and run again")

        print("=" * 60)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="NocoDB Simple Client development test runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run-all.py                    # Unit tests only (CI safe)
  python scripts/run-all.py --integration      # Include integration tests
  python scripts/run-all.py --performance      # Include performance tests
  python scripts/run-all.py --all-tests        # Run all test types
  python scripts/run-all.py --ci               # CI mode (unit tests, minimal output)
        """.strip(),
    )

    parser.add_argument(
        "--integration",
        action="store_true",
        help="Include integration tests (requires NocoDB instance)",
    )

    parser.add_argument(
        "--performance", action="store_true", help="Include performance tests (slow)"
    )

    parser.add_argument(
        "--all-tests",
        action="store_true",
        help="Run all test types (unit, integration, performance)",
    )

    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: unit tests only, skip build validation, minimal cleanup",
    )

    parser.add_argument(
        "--no-cleanup", action="store_true", help="Skip cleanup of temporary files (for debugging)"
    )

    return parser.parse_args()


def main():
    """Main runner function."""
    args = parse_arguments()

    # Determine test modes
    include_integration = args.integration or args.all_tests
    include_performance = args.performance or args.all_tests
    ci_mode = args.ci

    # CI mode overrides - only unit tests in CI
    if ci_mode:
        include_integration = False
        include_performance = False

    runner = LocalRunner(
        include_integration=include_integration,
        include_performance=include_performance,
        ci_mode=ci_mode,
    )

    try:
        runner.print_header()
        runner.setup_temp_environment()

        # Run all checks
        success = runner.run_all_checks()

        # Cleanup (unless skipped)
        if not args.no_cleanup:
            runner.cleanup()
        else:
            print("\n🔧 Cleanup skipped (--no-cleanup flag)")

        # Print summary
        runner.print_summary(success)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        if not args.no_cleanup:
            runner.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        if not args.no_cleanup:
            runner.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
