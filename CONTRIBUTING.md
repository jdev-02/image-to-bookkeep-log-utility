# Contributing to Image-to-Bookkeeping-Log (itbl)

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing Issues to avoid duplicates
2. Create a new issue with:
   - Clear description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information (OS, Python version, Tesseract version)

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the code style
4. **Add tests** if applicable
5. **Update documentation** if needed
6. **Commit your changes**: `git commit -m "Add feature: description"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Open a Pull Request**

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Run `black` and `isort` before committing:
  ```bash
  black src/ tests/
  isort src/ tests/
  ```

### Testing

- Add unit tests for new features
- Ensure existing tests pass: `pytest tests/`
- Test on multiple platforms if possible (Windows, macOS, Linux)

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update relevant docs in `docs/` folder

### Development Setup

See the [README.md](README.md) Installation section for setup instructions.

## Areas for Contribution

- OCR accuracy improvements
- Additional vendor mappings
- New output formats
- Better date/amount extraction patterns
- Documentation improvements
- Performance optimizations

## Questions?

Open an issue for questions or discussions about the project.

