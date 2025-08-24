#!/usr/bin/env python3
"""
Development environment setup script for NocoDB Simple Client.
Cross-platform setup for Windows, macOS, and Linux.
"""

import platform
import subprocess
import sys
import venv
from pathlib import Path

# Import project configuration
try:
    from .project_config import ProjectConfig
except ImportError:
    # Direct execution fallback
    sys.path.append(str(Path(__file__).parent))
    from project_config import ProjectConfig


def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 NocoDB Simple Client - Development Setup")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()


def check_python_version():
    """Check if Python version is supported."""
    print(f"✅ Python version: {sys.version.split()[0]}")
    # Note: Python 3.8+ required as per pyproject.toml


def create_virtual_environment(venv_path: Path):
    """Create virtual environment if it doesn't exist."""
    if venv_path.exists():
        print(f"📦 Virtual environment already exists at: {venv_path}")
        return

    print(f"📦 Creating virtual environment at: {venv_path}")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully")
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        sys.exit(1)


def get_activation_command(venv_path: Path) -> str:
    """Get virtual environment activation command for current platform."""
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "activate.bat")
    else:
        return f"source {venv_path}/bin/activate"


def get_python_executable(venv_path: Path) -> Path:
    """Get Python executable path in virtual environment."""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def run_command(cmd: list, description: str, venv_python: Path = None):
    """Run a command with proper error handling."""
    print(f"🔧 {description}...")

    # Use virtual environment Python if provided
    if venv_python and cmd[0] in ["python", "pip"]:
        cmd[0] = str(venv_python)
        if cmd[0].endswith("python.exe") or cmd[0].endswith("python"):
            if len(cmd) > 1 and cmd[1] == "pip":
                cmd = [str(venv_python), "-m", "pip"] + cmd[2:]

    try:
        subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Command: {' '.join(cmd)}")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} failed - command not found: {cmd[0]}")
        return False


def main():
    """Main setup function."""
    print_banner()

    # Load project configuration
    project_root = Path(__file__).parent.parent
    config = ProjectConfig(project_root)

    # Print project info
    print(f"Setting up: {config.get_project_name()} v{config.get_project_version()}")
    print(f"Required Python: {config.get_python_version()}+")
    print()

    # Check Python version
    check_python_version()

    venv_path = project_root / "venv"

    # Create virtual environment
    create_virtual_environment(venv_path)

    # Get virtual environment Python
    venv_python = get_python_executable(venv_path)

    if not venv_python.exists():
        print(f"❌ Virtual environment Python not found: {venv_python}")
        sys.exit(1)

    # Upgrade pip
    if not run_command(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip", venv_python
    ):
        sys.exit(1)

    # Install development dependencies from pyproject.toml
    if not run_command(
        [str(venv_python), "-m", "pip", "install", "-e", ".[dev,docs]"],
        "Installing development dependencies from pyproject.toml",
        venv_python,
    ):
        sys.exit(1)

    # Install pre-commit hooks
    if not run_command(
        [str(venv_python), "-m", "pre_commit", "install"],
        "Installing pre-commit hooks",
        venv_python,
    ):
        print("⚠️  Pre-commit hook installation failed, but continuing...")

    # Success message
    print()
    print("=" * 60)
    print("🎉 Development environment setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Activate virtual environment:")
    print(f"   {get_activation_command(venv_path)}")
    print()
    print("2. Run validation:")
    print("   python scripts/validate.py")
    print()
    print("3. Run quick tests:")
    print("   python scripts/quick-test.py")
    print()
    print("4. Start developing! 🚀")
    print()


if __name__ == "__main__":
    main()
