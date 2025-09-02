#!/usr/bin/env python3
"""
Docker test runner for NocoDB Simple Client.
Runs all tests and validations in isolated Docker containers.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")

    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run NocoDB Simple Client tests in Docker containers"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests (includes NocoDB service)"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up Docker containers and images after tests"
    )
    parser.add_argument(
        "--no-build", action="store_true", help="Skip building Docker images (use existing ones)"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    test_results_dir = project_root / "test-results"
    docker_dir = project_root / "tests" / "docker"

    # Ensure test results directory exists
    test_results_dir.mkdir(exist_ok=True)

    print("🐳 Docker Test Runner for NocoDB Simple Client")
    print("=" * 50)

    # Change to docker directory for docker-compose
    import os

    os.chdir(docker_dir)

    success = True

    try:
        if args.integration:
            print("🔗 Running integration tests (with NocoDB service)...")

            # Start NocoDB and run integration tests
            if not args.no_build:
                success &= run_command(
                    [
                        "docker-compose",
                        "-f",
                        "docker-compose.test.yml",
                        "build",
                        "test-runner-integration",
                    ],
                    "Building integration test image",
                )

            if success:
                success &= run_command(
                    [
                        "docker-compose",
                        "-f",
                        "docker-compose.test.yml",
                        "--profile",
                        "integration",
                        "up",
                        "--abort-on-container-exit",
                    ],
                    "Running integration tests",
                )

        else:
            print("🧪 Running unit tests and code quality checks...")

            # Build and run unit tests only
            if not args.no_build:
                success &= run_command(
                    ["docker-compose", "-f", "docker-compose.test.yml", "build", "test-runner"],
                    "Building test image",
                )

            if success:
                success &= run_command(
                    [
                        "docker-compose",
                        "-f",
                        "docker-compose.test.yml",
                        "--profile",
                        "testing",
                        "up",
                        "--abort-on-container-exit",
                    ],
                    "Running unit tests",
                )

        # Show test results
        log_file = test_results_dir / (
            "integration-test-output.log" if args.integration else "test-output.log"
        )
        if log_file.exists():
            print(f"\n📋 Test results saved to: {log_file}")
            print("📄 Last 20 lines of output:")
            print("-" * 40)
            with open(log_file, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.rstrip())
            print("-" * 40)

    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        success = False

    finally:
        # Cleanup containers
        print("\n🧹 Cleaning up containers...")
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down"], capture_output=True
        )

        if args.cleanup:
            print("🗑️  Cleaning up Docker images...")
            # Remove test images
            subprocess.run(
                [
                    "docker",
                    "rmi",
                    "nocodb_simpleclient_test-runner",
                    "nocodb_simpleclient_test-runner-integration",
                ],
                capture_output=True,
            )

    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All Docker tests completed successfully!")
        exit_code = 0
    else:
        print("💥 Some Docker tests failed!")
        exit_code = 1

    print(f"📁 Check {test_results_dir} for detailed logs")
    print("=" * 50)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
