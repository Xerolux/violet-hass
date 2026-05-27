> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Contributing.de)**

---

# Contributing – Participate & Contribute

> How you can contribute to the Violet Pool Controller project.

---

## Welcome!

Contributions are warmly welcome – whether bug reports, feature requests, documentation, or code. Every contribution counts!

---

## Types of Contributions

| Type | Description | How? |
|------|-------------|------|
| **Bug Report** | Found a bug | GitHub Issue |
| **Feature Request** | Want a new feature | GitHub Issue |
| **Pull Request** | Improved code or docs | Fork → PR |
| **Translation** | Add a new language | Fork → PR |
| **Wiki** | Improve documentation | Fork → PR |
| **Testing** | Test the integration | Feedback via Issue |

---

## Creating a Bug Report

### Open a GitHub Issue

[Create New Issue](https://github.com/Xerolux/violet-hass/issues/new)

### A Good Bug Report Contains

```
1. SUMMARY
   What is the problem? (1-2 sentences)

2. ENVIRONMENT
   - Home Assistant Version: 2026.x.x (Minimum: 2026.5.0)
   - Integration Version: 1.0.5
   - Controller Firmware: x.x.x
   - Python Version: 3.14.2+

3. STEPS TO REPRODUCE
   1. Add integration with ...
   2. Click on ...
   3. Error occurs

4. EXPECTED BEHAVIOR
   What should happen?

5. ACTUAL BEHAVIOR
   What happens instead?

6. LOGS
   Settings → System → Logs → Filter by "violet"
```

---

## Creating a Pull Request

### Step by Step

```bash
# 1. Fork the repository (GitHub UI)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/violet-hass.git
cd violet-hass

# 3. Create a branch
git checkout -b feat/new-feature
# or: fix/bug-description

# 4. Make changes
# Edit code...

# 5. Check code quality
pip install ruff mypy
python -m ruff check custom_components/violet_pool_controller/ --fix
python -m mypy custom_components/violet_pool_controller/

# 6. Run tests
./scripts/setup-test-env.sh  # One-time
./scripts/run-tests.sh

# 7. Commit (Conventional Commits)
git add custom_components/violet_pool_controller/file.py
git commit -m "feat: Added new feature XYZ"

# 8. Push
git push origin feat/new-feature

# 9. Create Pull Request on GitHub
```

### Branch Naming

| Type | Example |
|------|---------|
| Feature | `feat/dmx-color-control` |
| Bugfix | `fix/pump-state-parsing` |
| Documentation | `docs/wiki-update` |
| Refactoring | `refactor/api-cleanup` |
| Tests | `test/sensor-coverage` |

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

[optional body]

[optional footer]
```

### Types

| Type | Usage |
|------|--------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Add/modify tests |
| `chore` | Build, dependencies, CI |
| `perf` | Performance improvement |

### Examples

```bash
git commit -m "feat: Added support for AI1-AI8 analog inputs"
git commit -m "fix: pH sensor shows wrong value for negative numbers"
git commit -m "docs: Extended error codes table"
git commit -m "test: Added tests for rate limiter edge cases"
```

---

## Code Style

### Linting with Ruff

```bash
# Check
python -m ruff check custom_components/violet_pool_controller/

# Auto-fix
python -m ruff check custom_components/violet_pool_controller/ --fix
```

### Type Checking with MyPy

```bash
python -m mypy custom_components/violet_pool_controller/
```

### Style Rules

```python
# Yes: Modern type annotations
def get_value(key: str) -> float | None:
    ...

# No: Old Optional syntax
from typing import Optional
def get_value(key: str) -> Optional[float]:
    ...

# Yes: collections.abc
from collections.abc import Callable

# No: typing.Callable (deprecated)
from typing import Callable
```

### Important Principles

1. **No silent errors:** Log all exceptions
2. **Type Hints:** Type all public methods
3. **Docstrings:** Document public classes and methods
4. **Constants:** Define in `const_*.py` files
5. **Tests:** Cover new features with tests

---

## Writing Tests

### Adding New Tests

```python
# tests/test_my_feature.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.violet_pool_controller.api import VioletPoolAPI


class TestMyFeature:
    """Tests for my new feature."""

    @pytest.fixture
    def api(self):
        """API fixture."""
        session = AsyncMock()
        return VioletPoolAPI(
            host="192.168.1.55",
            session=session,
        )

    async def test_basic_functionality(self, api):
        """Test basic functionality."""
        # Arrange
        expected = 7.2

        # Act
        result = api.parse_ph_value("7.2")

        # Assert
        assert result == expected

    async def test_error_handling(self, api):
        """Test error handling."""
        with pytest.raises(ValueError):
            api.parse_ph_value("invalid")
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Single test
pytest tests/test_my_feature.py -v

# With coverage
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# Details
pytest tests/ -vv --tb=long
```

### Test Criteria for PR Merge

- [ ] All 53+ existing tests pass
- [ ] New features have tests
- [ ] Coverage > 80%
- [ ] Ruff: 0 errors
- [ ] MyPy: 0 errors

---

## Adding a New Language

### Create Translation File

1. Copy `custom_components/violet_pool_controller/translations/en.json` as a template
2. Save as `xx.json` (language code)
3. Translate all strings
4. Create a PR

### Supported Languages

Currently: `de`, `en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ru`, `zh`

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Set up Violet Pool Controller",
        "description": "Enter connection details"
      }
    }
  }
}
```

---

## Setting Up the Development Environment

### Local HA Development Instance

```bash
# Virtual environment for tests
./scripts/setup-test-env.sh

# VS Code Dev Container (recommended)
# Open .devcontainer/ → "Reopen in Container"
# → http://localhost:8123
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pre-Commit Hook (Optional)

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python -m ruff check custom_components/violet_pool_controller/ --fix
./scripts/run-tests.sh
EOF
chmod +x .git/hooks/pre-commit
```

---

## Review Process

1. **Open PR** with clear description
2. **CI checks** automatically: Ruff, MyPy, pytest
3. **Maintainer reviews** the code
4. **Address feedback** if needed
5. **Merge** after approval

### PR Checklist

- [ ] Branch created from `main`
- [ ] Description explains what and why
- [ ] Tests added/updated
- [ ] Ruff and MyPy error-free
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added

---

## License

By contributing, you agree that your code will be published under the **MIT License**.

```
MIT License – Copyright (c) 2024 Xerolux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## Questions?

- **GitHub Discussions:** For general questions
- **GitHub Issues:** For specific bugs/features
- **Email:** git@xerolux.de

---

*Back: [Home](Home) | Next: [Testing](Testing)*
