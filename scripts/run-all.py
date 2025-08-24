#!/usr/bin/env python3
"""
Run all local development checks and cleanup afterwards.
Simple all-in-one script for local testing and validation.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

# Import project configuration
try:
    from .project_config import ProjectConfig
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from project_config import ProjectConfig


class LocalRunner:
    """Local development test runner with cleanup."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config = ProjectConfig(self.project_root)
        self.temp_files = []
        self.start_time = time.time()
        
    def print_header(self):
        """Print header."""
        print("=" * 60)
        print("🚀 NocoDB Simple Client - Local Development Runner")
        print("=" * 60)
        print(f"Project: {self.config.get_project_name()} v{self.config.get_project_version()}")
        print(f"Python: {sys.version.split()[0]}")
        print()
    
    def run_command(self, cmd: List[str], description: str, capture_output: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status."""
        print(f"🔍 {description}...")
        
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                success = result.returncode == 0
                output = result.stdout + result.stderr
            else:
                # Show output directly for interactive commands
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    timeout=120
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
            self.project_root / "*.egg-info"
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
        
        checks = [
            # Setup validation
            (["python", "scripts/show-config.py"], "Project configuration check", True),
            
            # Code quality
            (["black", "--check", "src/", "tests/"], "Code formatting (Black)", True),
            (["ruff", "check", "src/", "tests/"], "Code linting (Ruff)", True), 
            (["mypy", "src/nocodb_simple_client/"], "Type checking (MyPy)", True),
            
            # Security
            (["bandit", "-r", "src/"], "Security scanning (Bandit)", True),
            
            # Testing
            (["pytest", "-v", "--tb=short"], "Unit tests", False),  # Show output for tests
            (["pytest", "--cov=src/nocodb_simple_client", "--cov-report=term-missing", "--cov-report=html"], "Test coverage", True),
            
            # Build validation
            (["python", "-m", "build"], "Package build", True),
            (["python", "-c", "import src.nocodb_simple_client; print('✅ Import successful')"], "Import test", True),
        ]
        
        passed = 0
        total = len(checks)
        
        for cmd, description, capture in checks:
            success, _ = self.run_command(cmd, description, capture)
            if success:
                passed += 1
            print()
        
        print("=" * 40)
        print(f"📊 Results: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 All checks passed!")
            return True
        else:
            print(f"💥 {total - passed} checks failed")
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


def main():
    """Main runner function."""
    runner = LocalRunner()
    
    try:
        runner.print_header()
        runner.setup_temp_environment()
        
        # Run all checks
        success = runner.run_all_checks()
        
        # Always cleanup
        runner.cleanup()
        
        # Print summary
        runner.print_summary(success)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        runner.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        runner.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()