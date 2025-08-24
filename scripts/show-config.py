#!/usr/bin/env python3
"""
Show active pyproject.toml configuration for development tools.
"""

import sys
from pathlib import Path

# Import project configuration
try:
    from .project_config import ProjectConfig
except ImportError:
    # Direct execution fallback
    sys.path.append(str(Path(__file__).parent))
    from project_config import ProjectConfig


def print_tool_config(config: ProjectConfig, tool_name: str, display_name: str):
    """Print configuration for a specific tool."""
    if config.has_tool_config(tool_name):
        print(f"✅ {display_name}")
        tool_config = config.get_tool_config(tool_name)
        
        if tool_config:
            print("   Configuration:")
            for key, value in tool_config.items():
                if isinstance(value, list) and len(value) > 3:
                    # Truncate long lists
                    value_str = f"[{', '.join(map(str, value[:3]))}, ... +{len(value)-3} more]"
                elif isinstance(value, str) and len(value) > 50:
                    # Truncate long strings
                    value_str = f"{value[:47]}..."
                else:
                    value_str = str(value)
                print(f"   - {key}: {value_str}")
        print()
    else:
        print(f"❌ {display_name} - No configuration found")


def main():
    """Show all tool configurations."""
    print("📋 NocoDB Simple Client - Tool Configuration Status")
    print("=" * 60)
    
    config = ProjectConfig()
    
    # Project info
    print("📦 Project Information")
    print(f"Name: {config.get_project_name()}")
    print(f"Version: {config.get_project_version()}")
    print(f"Python: {config.get_python_version()}+")
    
    build_system = config.get_build_system()
    if build_system:
        print(f"Build Backend: {build_system.get('build-backend', 'Unknown')}")
    print()
    
    # Dependencies
    print("📚 Dependencies")
    dev_deps = config.get_dev_dependencies()
    docs_deps = config.get_docs_dependencies()
    
    if dev_deps:
        print(f"Dev Dependencies: {len(dev_deps)} packages")
        for dep in dev_deps[:3]:  # Show first 3
            print(f"  - {dep}")
        if len(dev_deps) > 3:
            print(f"  ... and {len(dev_deps) - 3} more")
    
    if docs_deps:
        print(f"Docs Dependencies: {len(docs_deps)} packages")
    print()
    
    # Tool configurations
    print("🔧 Tool Configurations")
    print_tool_config(config, "black", "Black (Code Formatter)")
    print_tool_config(config, "ruff", "Ruff (Linter)")
    print_tool_config(config, "mypy", "MyPy (Type Checker)")
    print_tool_config(config, "pytest.ini_options", "Pytest (Test Runner)")
    print_tool_config(config, "coverage.run", "Coverage (Test Coverage)")
    print_tool_config(config, "bandit", "Bandit (Security Scanner)")
    
    # Summary
    tools = ["black", "ruff", "mypy", "pytest.ini_options", "coverage.run", "bandit"]
    configured = sum(1 for tool in tools if config.has_tool_config(tool))
    
    print("📊 Summary")
    print(f"Tools configured: {configured}/{len(tools)}")
    
    if configured == len(tools):
        print("🎉 All development tools are configured via pyproject.toml!")
    elif configured > 0:
        print("⚠️  Some tools are configured. Consider configuring all tools in pyproject.toml.")
    else:
        print("❌ No tool configurations found in pyproject.toml")


if __name__ == "__main__":
    main()