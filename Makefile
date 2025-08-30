# NocoDB Simple Client - Development Commands
.PHONY: help install install-dev test test-cov lint format type-check security build clean docs serve-docs pre-commit all-checks

# Default target (help)
help:
	@echo "NocoDB Simple Client Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install with all development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run ruff linter"
	@echo "  format       Format code with black and ruff"
	@echo "  type-check   Run mypy type checker"
	@echo "  security     Run bandit security checks"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  test-fast    Run tests without slow/integration tests"
	@echo ""
	@echo "Build:"
	@echo "  build        Build package"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build documentation"
	@echo "  serve-docs   Serve documentation locally"
	@echo ""
	@echo "Development:"
	@echo "  check        Quick development checks"
	@echo "  run-all      Complete validation with cleanup"
	@echo "  pre-commit   Run pre-commit hooks"
	@echo "  all-checks   Run all quality checks"

# Installation (using pyproject.toml)
install:
	pip install -e .

install-dev:
	@echo "Installing development dependencies from pyproject.toml..."
	pip install -e ".[dev,docs]"
	pre-commit install
	@echo "✅ Development environment ready!"

check-config:
	@echo "📋 Checking pyproject.toml configuration..."
	@python scripts/show-config.py

show-config: check-config

# Code formatting and linting (using pyproject.toml config)
format:
	@echo "🎨 Formatting code using pyproject.toml settings..."
	black src/ tests/
	ruff --fix src/ tests/

lint:
	@echo "🔍 Linting code using pyproject.toml settings..."
	ruff check src/ tests/
	black --check src/ tests/

type-check:
	@echo "🔍 Type checking using pyproject.toml settings..."
	mypy src/nocodb_simple_client/

security:
	@echo "🔒 Security scanning using pyproject.toml settings..."
	bandit -r src/

# Testing (using pyproject.toml config)
test:
	@echo "🧪 Running tests using pyproject.toml settings..."
	pytest

test-cov:
	@echo "📊 Running tests with coverage using pyproject.toml settings..."
	pytest --cov=src/nocodb_simple_client --cov-report=html --cov-report=term-missing

test-fast:
	@echo "⚡ Running fast tests using pyproject.toml settings..."
	pytest -m "not slow and not integration"

# Build
build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	mkdocs build

serve-docs:
	mkdocs serve

# Development workflow
pre-commit:
	pre-commit run --all-files

# Quick and complete validation
check:
	@echo "⚡ Running quick development checks..."
	@python scripts/check.py

run-all:
	@echo "🚀 Running complete validation with cleanup..."
	@python scripts/run-all.py

all-checks: format lint type-check security test
	@echo "All checks passed! ✅"
