# Contributing to SamFWTool

Thank you for your interest in contributing to SamFWTool!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/samfwtool/samfwtool/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Firmware file format (if applicable)

### Suggesting Features

1. Check existing feature requests in Issues
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure code follows PEP 8 style guide
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints where applicable
- Write docstrings for all public functions/classes
- Keep functions focused and modular
- Add comments for complex logic

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Test on multiple platforms if possible

### Documentation

- Update README.md if adding user-facing features
- Add docstrings to new code
- Update docs/ if applicable

## Development Setup

```bash
# Clone repository
git clone https://github.com/samfwtool/samfwtool.git
cd samfwtool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black samfwtool/

# Lint code
flake8 samfwtool/
```

## Questions?

Feel free to ask questions in:
- GitHub Issues
- Discussions tab
- Discord (link in README)

Thank you for contributing!
