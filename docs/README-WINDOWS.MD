# NocoDB Simple Client - Windows Development Guide

Since the Makefile doesn't work natively on Windows, here are the Windows alternatives:

## Available Scripts

### Initial Setup (Virtual Environment)

**Automated setup with virtual environment:**
```cmd
# Run the setup script (recommended for first-time setup)
python scripts/setup.py
# Or use the Windows wrapper:
scripts\setup.cmd
```

This will:
- Create a virtual environment in `venv/`
- Install all development dependencies
- Set up pre-commit hooks
- Show activation instructions

**Manual virtual environment setup:**
```cmd
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate.bat

# Install development dependencies
pip install -e ".[dev,docs]"
pre-commit install
```

### Package Installation
```cmd
# Install in development mode
pip install -e .

# Full development environment
pip install -e ".[dev,docs]"
pre-commit install
```

### Quick Checks
```cmd
# Quick development checks (~10s)
python scripts/check.py

# Or use the Windows wrapper:
scripts\quick-test.cmd

# Full validation (~60s)
python scripts/run-all.py
# Or:
scripts\run-all.cmd
```

### Code Quality
```cmd
# Format code
python -m black src/ tests/
python -m ruff --fix src/ tests/

# Check code
python -m ruff check src/ tests/
python -m black --check src/ tests/

# Type checking
python -m mypy src/nocodb_simple_client/

# Security scan
python -m bandit -r src/
```

### Testing
```cmd
# All tests
python -m pytest

# Tests with coverage
python -m pytest --cov=src/nocodb_simple_client --cov-report=html --cov-report=term-missing

# Fast tests only
python -m pytest -m "not slow and not integration"
```

### Build
```cmd
# Build package
python -m build

# Clean up
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
for /d /r . %d in (*.egg-info) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc 2>nul
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist htmlcov rmdir /s /q htmlcov
```

### Show Configuration
```cmd
python scripts/show-config.py
```

### Git & Pre-Commit
```cmd
# Pre-commit hooks
pre-commit run --all-files

# Smart commit (automatically restages after pre-commit fixes)
scripts\smart-commit.cmd "Your commit message"
```

## Windows Make Alternative

I've also created a `MMake.cmd` script that works similarly to the Unix Makefile:

```cmd
# Available commands:
Make.cmd help         # Show all available commands
Make.cmd install      # Install package
Make.cmd install-dev  # Install dev dependencies
Make.cmd format       # Format code
Make.cmd lint         # Lint code
Make.cmd type-check   # Type check
Make.cmd security     # Security scan
Make.cmd test         # Run tests
Make.cmd test-cov     # Run tests with coverage
Make.cmd test-fast    # Run fast tests
Make.cmd build        # Build package
Make.cmd clean        # Clean artifacts
Make.cmd check        # Quick checks
Make.cmd run-all      # Full validation
Make.cmd show-config  # Show configuration
Make.cmd pre-commit   # Run pre-commit hooks
```

## Recommended Workflow

1. **First-time setup:**
   ```cmd
   # Automated setup (recommended)
   python scripts/setup.py

   # Activate virtual environment
   venv\Scripts\activate.bat
   ```

2. **Start development session:**
   ```cmd
   # Always activate virtual environment first
   venv\Scripts\activate.bat

   # Or if using make.cmd:
   Make.cmd install-dev
   ```

3. **During development:**
   ```cmd
   Make.cmd check     # Quick checks
   ```

4. **Before commit:**
   ```cmd
   Make.cmd run-all   # Full validation
   ```

5. **Commit:**
   ```cmd
   git add .
   scripts\smart-commit.cmd "Your commit message"
   ```

## Important Notes

- **Always activate the virtual environment** before running any development commands
- The setup script (`scripts\setup.cmd` or `python scripts/setup.py`) handles everything automatically
- All scripts use the configuration from `pyproject.toml` and are fully compatible with the Unix version of the project
- Virtual environment activation: `venv\Scripts\activate.bat`
- To deactivate: simply run `deactivate`
