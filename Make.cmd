@echo off
REM Windows alternative to Makefile for NocoDB Simple Client
REM Usage: make.cmd <command>

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-dev" goto install-dev
if "%1"=="format" goto format
if "%1"=="lint" goto lint
if "%1"=="type-check" goto type-check
if "%1"=="security" goto security
if "%1"=="test" goto test
if "%1"=="test-cov" goto test-cov
if "%1"=="test-fast" goto test-fast
if "%1"=="build" goto build
if "%1"=="clean" goto clean
if "%1"=="check" goto check
if "%1"=="run-all" goto run-all
if "%1"=="show-config" goto show-config
if "%1"=="pre-commit" goto pre-commit

echo Unknown command: %1
goto help

:help
echo NocoDB Simple Client Development Commands (Windows)
echo ==================================================
echo.
echo Setup:
echo   make install      Install package in development mode
echo   make install-dev  Install with all development dependencies
echo.
echo Code Quality:
echo   make lint         Run ruff linter
echo   make format       Format code with black and ruff
echo   make type-check   Run mypy type checker
echo   make security     Run bandit security checks
echo.
echo Testing:
echo   make test         Run all tests
echo   make test-cov     Run tests with coverage report
echo   make test-fast    Run tests without slow/integration tests
echo.
echo Build:
echo   make build        Build package
echo   make clean        Clean build artifacts
echo.
echo Development:
echo   make check        Quick development checks
echo   make run-all      Complete validation with cleanup
echo   make show-config  Show tool configuration
echo   make pre-commit   Run pre-commit hooks
echo.
goto end

:install
echo Installing package in development mode...
pip install -e .
goto end

:install-dev
echo Installing development dependencies...
pip install -e ".[dev,docs]"
pre-commit install
echo ✅ Development environment ready!
goto end

:format
echo 🎨 Formatting code...
python -m black src/ tests/
python -m ruff --fix src/ tests/
goto end

:lint
echo 🔍 Linting code...
python -m ruff check src/ tests/
python -m black --check src/ tests/
goto end

:type-check
echo 🔍 Type checking...
python -m mypy src/nocodb_simple_client/
goto end

:security
echo 🔒 Security scanning...
python -m bandit -r src/
goto end

:test
echo 🧪 Running tests...
python -m pytest
goto end

:test-cov
echo 📊 Running tests with coverage...
python -m pytest --cov=src/nocodb_simple_client --cov-report=html --cov-report=term-missing
goto end

:test-fast
echo ⚡ Running fast tests...
python -m pytest -m "not slow and not integration"
goto end

:build
echo 📦 Building package...
python -m build
goto end

:clean
echo 🧹 Cleaning build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist htmlcov rmdir /s /q htmlcov
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .mypy_cache rmdir /s /q .mypy_cache
if exist .ruff_cache rmdir /s /q .ruff_cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo ✅ Cleanup completed!
goto end

:check
echo ⚡ Running quick development checks...
python scripts/check.py
goto end

:run-all
echo 🚀 Running complete validation...
python scripts/run-all.py
goto end

:show-config
echo 📋 Showing configuration...
python scripts/show-config.py
goto end

:pre-commit
echo 🔧 Running pre-commit hooks...
pre-commit run --all-files
goto end

:end
