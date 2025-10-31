# Release Checklist

Use this checklist before publishing a new version.

## Pre-Release

- [ ] All tests passing: `pytest tests/ -v`
- [ ] Code style checked: `black --check src/ tests/` and `isort --check src/ tests/`
- [ ] No sensitive data in repository (credentials, tokens, personal data)
- [ ] No hardcoded paths or user-specific content
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated
- [ ] Version number updated in `pyproject.toml`

## Code Review

- [ ] All TODO comments documented or removed
- [ ] No debug print statements left in code
- [ ] Error messages are user-friendly
- [ ] Logging levels appropriate (no sensitive data in logs)
- [ ] Type hints added where applicable

## Documentation

- [ ] README.md is complete and accurate
- [ ] Installation instructions tested on clean system
- [ ] All examples in docs work correctly
- [ ] Troubleshooting guides are up to date
- [ ] API/CLI documentation is complete

## Testing

- [ ] Tested on multiple platforms (Windows, macOS, Linux)
- [ ] Tested with various image formats
- [ ] Tested Google Sheets integration (if applicable)
- [ ] Tested with edge cases (empty images, corrupted files, etc.)

## Repository Cleanup

- [ ] `.gitignore` includes all generated files
- [ ] No personal images in `examples/inbox/`
- [ ] No credentials or secrets in repository
- [ ] Build artifacts cleaned: `rm -rf src/itbl.egg-info/ build/ dist/`
- [ ] `__pycache__` directories removed: `find . -type d -name __pycache__ -exec rm -r {} +`

## Release

- [ ] Git tag created: `git tag -a v0.1.0 -m "Release v0.1.0"`
- [ ] Tag pushed: `git push origin v0.1.0`
- [ ] Release notes prepared (if using GitHub releases)
- [ ] PyPI package built: `python -m build`
- [ ] PyPI package uploaded: `twine upload dist/*` (if publishing to PyPI)

## Post-Release

- [ ] Verify installation from source works
- [ ] Verify installation from PyPI works (if published)
- [ ] Update any downstream dependencies
- [ ] Announce release (if applicable)

