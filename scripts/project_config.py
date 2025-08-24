#!/usr/bin/env python3
"""
Project configuration utilities for NocoDB Simple Client.
Reads configuration from pyproject.toml and provides tool configurations.
"""

from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        print("Warning: Neither tomllib nor tomli available. Install tomli for Python < 3.11")
        tomllib = None


class ProjectConfig:
    """Project configuration manager."""

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent

        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from pyproject.toml."""
        if not self.pyproject_path.exists():
            print(f"Warning: {self.pyproject_path} not found")
            return {}

        if tomllib is None:
            print("Warning: Cannot parse pyproject.toml - tomli not available")
            return {}

        try:
            with open(self.pyproject_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse {self.pyproject_path}: {e}")
            return {}

    def get_dev_dependencies(self) -> list[str]:
        """Get development dependencies from pyproject.toml."""
        try:
            return self.config["project"]["optional-dependencies"]["dev"]
        except KeyError:
            print("Warning: No dev dependencies found in pyproject.toml")
            return []

    def get_docs_dependencies(self) -> list[str]:
        """Get documentation dependencies from pyproject.toml."""
        try:
            return self.config["project"]["optional-dependencies"]["docs"]
        except KeyError:
            return []

    def get_python_version(self) -> str:
        """Get required Python version from pyproject.toml."""
        try:
            requires_python = self.config["project"]["requires-python"]
            # Extract version from ">=3.8" format
            return requires_python.replace(">=", "").replace(">", "").strip()
        except KeyError:
            return "3.8"  # Default fallback

    def get_project_name(self) -> str:
        """Get project name from pyproject.toml."""
        try:
            return self.config["project"]["name"]
        except KeyError:
            return "nocodb-simple-client"

    def get_project_version(self) -> str:
        """Get project version from pyproject.toml."""
        try:
            return self.config["project"]["version"]
        except KeyError:
            # Try dynamic version
            try:
                version_path = self.config["tool"]["hatch"]["version"]["path"]
                init_file = self.project_root / version_path
                if init_file.exists():
                    content = init_file.read_text()
                    for line in content.split("\n"):
                        if line.startswith("__version__"):
                            return line.split("=")[1].strip().strip("\"'")
            except Exception:
                pass
            return "0.4.0"  # Default fallback

    def has_tool_config(self, tool: str) -> bool:
        """Check if tool configuration exists in pyproject.toml."""
        try:
            tools = self.config.get("tool", {})
            if "." in tool:
                # Handle nested tools like pytest.ini_options
                parts = tool.split(".")
                current = tools
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return False
                return True
            else:
                return tool in tools
        except Exception:
            return False

    def get_tool_config(self, tool: str) -> dict[str, Any]:
        """Get tool configuration from pyproject.toml."""
        try:
            return self.config["tool"][tool]
        except KeyError:
            return {}

    def _flatten_keys(self, d: dict, parent_key: str = "") -> dict[str, Any]:
        """Flatten nested dictionary keys."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_keys(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def get_test_config(self) -> dict[str, Any]:
        """Get pytest configuration."""
        return self.get_tool_config("pytest.ini_options")

    def get_coverage_config(self) -> dict[str, Any]:
        """Get coverage configuration."""
        return self.get_tool_config("coverage.run")

    def get_black_config(self) -> dict[str, Any]:
        """Get Black configuration."""
        return self.get_tool_config("black")

    def get_ruff_config(self) -> dict[str, Any]:
        """Get Ruff configuration."""
        return self.get_tool_config("ruff")

    def get_mypy_config(self) -> dict[str, Any]:
        """Get MyPy configuration."""
        return self.get_tool_config("mypy")

    def get_bandit_config(self) -> dict[str, Any]:
        """Get Bandit configuration."""
        return self.get_tool_config("bandit")

    def get_build_system(self) -> dict[str, Any]:
        """Get build system configuration."""
        return self.config.get("build-system", {})

    def print_summary(self):
        """Print configuration summary."""
        print("📋 Project Configuration Summary")
        print("=" * 40)
        print(f"Project: {self.get_project_name()}")
        print(f"Version: {self.get_project_version()}")
        print(f"Python: {self.get_python_version()}+")
        print(f"Build System: {self.get_build_system().get('build-backend', 'setuptools')}")
        print()

        # Tool configurations
        tools = ["black", "ruff", "mypy", "pytest.ini_options", "bandit", "coverage.run"]
        configured_tools = [tool for tool in tools if self.has_tool_config(tool)]

        if configured_tools:
            print(f"Configured Tools: {', '.join(configured_tools)}")
        else:
            print("No tool configurations found")
        print()


def get_project_config() -> ProjectConfig:
    """Get project configuration instance."""
    return ProjectConfig()


if __name__ == "__main__":
    # CLI usage
    config = get_project_config()
    config.print_summary()
