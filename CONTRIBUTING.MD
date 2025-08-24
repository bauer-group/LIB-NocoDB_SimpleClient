# Contributing to NocoDB Simple Client

Thank you for your interest in contributing to NocoDB Simple Client! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [GitHub Issues](https://github.com/bauer-group/nocodb-simple-client/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Detailed description of the issue or suggestion
   - Steps to reproduce (for bugs)
   - Your environment details (Python version, OS, etc.)

### Contributing Code

1. **Fork the Repository**
   ```bash
   git clone https://github.com/bauer-group/nocodb-simple-client.git
   cd nocodb-simple-client
   ```

2. **Set up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

5. **Run Tests and Checks**
   ```bash
   # Run tests
   pytest

   # Check code formatting
   black --check .

   # Run linting
   ruff check .

   # Type checking
   mypy nocodb_simple_client
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

We use the following tools for code quality:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding or updating tests
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting
- Aim for high test coverage
- Use meaningful test names that describe what is being tested

### Documentation

- Update docstrings for new or modified functions/classes
- Update README.md if your changes affect the public API
- Add examples for new features

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue for discussion
- Contact the maintainers at karl.bauer@bauer-group.com

Thank you for contributing! 🎉
