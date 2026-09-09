# Contributing to Violet Pool Controller Integration

Thank you for your interest in contributing to the Violet Pool Controller integration for Home Assistant! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

This project adheres to the [Home Assistant Code of Conduct](https://www.home-assistant.io/docs/policies/#code-of-conduct). By participating, you are expected to uphold this code. Please report unacceptable behavior to info@home-assistant.io.

---

## Getting Started

### Prerequisites

- Python 3.14 or later (`scripts/setup-test-env.sh` refuses anything older,
  because Home Assistant needs it)
- Home Assistant 2026.8.0 or later (the floor declared in `hacs.json`)
- Git
- A Violet Pool Controller device (or access to a simulator)

### Recommended Tools

- **VS Code** with Python and Home Assistant extensions
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/violet-hass.git
cd violet-hass
```

### 2. Set Up Development Environment

```bash
# The whole project uses one venv name: .venv
python3.14 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# requirements-dev.txt is the single source of truth for tool versions.
# It already includes requirements.txt, so this one line is the whole setup.
pip install -r requirements-dev.txt
```

Or let the script do it, which is what the devcontainer runs on create:

```bash
./scripts/setup-test-env.sh          # creates/reuses .venv
./scripts/setup-test-env.sh --recreate   # rebuild from scratch
```

### 3. Install in Home Assistant

#### Method A: HACS (Recommended for Testing)

1. Copy your local repository to HACS custom_components:
```bash
cp -r custom_components/violet_pool_controller ~/.homeassistant/custom_components/
```

2. Restart Home Assistant

#### Method B: Symbolic Link

```bash
ln -s /path/to/violet-hass/custom_components/violet_pool_controller ~/.homeassistant/custom_components/violet_pool_controller
```

### 4. Verify Installation

Check Home Assistant logs for successful integration load:
```
Setup completed successfully for 'Violet Pool Controller'
```

---

## Coding Standards

This project follows the [Home Assistant Development Guidelines](https://developers.home-assistant.io/docs/development_guidelines/).

### Python Style

We follow:
- **PEP 8** - Style Guide for Python Code
- **PEP 257** - Docstring Conventions
- **PEP 484** - Type Hints
- **Home Assistant specific guidelines**

#### Code Quality Requirements

| Metric | Tool | Gate |
|--------|------|------|
| Linting | Ruff | 0 errors - enforced by CI on Python 3.12, 3.13 and 3.14 |
| Types | mypy | 0 errors - enforced by CI on Python 3.14 |
| Test coverage | pytest-cov | Floor in `pyproject.toml` (`[tool.coverage.report] fail_under`). Raise it when you add tests; never lower it to make a build pass. |

`ruff format --check` is **not** in CI yet: the tree has never been formatted,
so enabling it would rewrite dozens of files. That needs its own commit.

### File Structure

```
custom_components/violet_pool_controller/
├── __init__.py              # Integration setup, platform loading
├── device.py                # Device & coordinator
├── entity.py                # Base entity class
├── const.py                 # Constants hub
├── config_flow.py           # Setup UI
├── config_flow_utils/       # Config flow helpers (a package, not a module)
├── safety_guard.py          # Cooldowns + restart-safe auto-stop
├── auth_guard.py            # Reports silent auth rejections as a repair
├── services.py              # Service registration
├── service_mixins/          # Service handlers, one mixin per subject area
├── sensor.py, switch.py, binary_sensor.py, climate.py, cover.py,
│   number.py, select.py, light.py, update.py, button.py   # the 10 platforms
├── sensor_modules/          # Modular sensor implementations
├── manifest.json            # Integration metadata (incl. the API dependency)
├── strings.json             # UI strings
└── translations/            # Localised strings (10 languages)
```

**There is no `api.py` here.** The HTTP client lives in the standalone
[`violet-poolController-api`](https://github.com/Xerolux/violet-poolController-api)
package; API fixes belong in that repository and ship as a new PyPI release.
See [ARCHITECTURE.md](ARCHITECTURE.md) for the full module inventory.

### Naming Conventions

**Files:** `snake_case.py`
**Classes:** `PascalCase`
**Functions/Variables:** `snake_case`
**Constants:** `UPPER_SNAKE_CASE`
**Entities:** `VioletEntityType` (e.g., `VioletClimate`)

### Documentation

Every file must have a module docstring:

```python
"""Brief description of the module.

 Longer description if needed.

 Args:
     Detailed descriptions if applicable

 Returns:
     Description of return values if applicable

 Raises:
     Description of exceptions if applicable
"""
```

Every public function must have a docstring:

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if setup was successful.

    Raises:
        ConfigEntryNotReady: If the controller is not ready.
    """
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=custom_components/violet_pool_controller --cov-report=html

# Run a single test
pytest tests/test_api.py::test_rate_limiter_is_initialized
```

Home Assistant and the API package must be installed: `tests/conftest.py`
stops the run with an actionable message rather than falling back to stubs.

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api.py              # API client tests
├── test_cover.py            # Cover platform tests
├── test_type_hints.py       # Type hint validation tests
└── ... (platform-specific tests)
```

### Writing Tests

Follow these patterns:

```python
"""Tests for Cover platform."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

class TestVioletCover:
    """Test VioletCover entity."""

    @pytest.mark.asyncio
    async def test_cover_is_open(self, mock_coordinator, config_entry):
        """Test cover is_open property."""
        mock_coordinator.data["COVER_STATE"] = "OPEN"
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.is_open is True
        assert cover.is_closed is False
```

### Test Fixtures

Use `conftest.py` for shared fixtures:

```python
@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    class MockCoordinator:
        def __init__(self):
            self.data = {"COVER_STATE": "OPEN"}

    return MockCoordinator()
```

---

## Submitting Changes

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Follow coding standards
   - Add/update tests
   - Update documentation
   - Commit with clear messages

3. **Run quality checks**
   ```bash
   # Linting
   ruff check custom_components/

   # Type checking
   mypy custom_components/violet_pool_controller

   # Tests
   pytest
   ```

4. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

### Commit Message Format

**Conventional Commits.** The release notes are generated from merged pull
request titles, so the title is what users read.

```
<type>(<optional scope>): <short description>

Longer explanation if it is not obvious from the diff.

Refs: #issue_number
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`.

Examples:
```
feat(api): add timeout configuration support

Lets users configure a custom timeout for API requests, which fixes
connection failures against slow controllers.

Refs: #123
```

```
docs: add SSL certificate errors to the troubleshooting guide
```

Everything written into this repository is **English** - commit messages,
branch names, PR titles and bodies included. The two exceptions are
`translations/*.json` and the German half of the bilingual docs
(`README.de.md`, `docs/wiki/*.de.md`). `tests/test_language_policy.py`
enforces this.

### Pull Request Checklist

- [ ] Code follows PEP 8 and PEP 257
- [ ] Type hints added where appropriate
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`ruff check custom_components/violet_pool_controller tests`)
- [ ] No type errors (`mypy custom_components/violet_pool_controller`)
- [ ] Commit messages follow Conventional Commits
- [ ] Changelog entry added under a `## Version X.Y.Z (YYYY-MM-DD)` heading
      if the change ships in a release

**Releasing** (maintainer): bump the version in **all five** places -
`custom_components/violet_pool_controller/manifest.json`, `const.py`,
`custom_components/violet_pool_controller/.version`, `pyproject.toml` and the
"Current Integration Version" line in `CLAUDE.md` - and add the changelog
section. CI's "Version consistency" job fails if any of them disagree, and the
release fails without the changelog section.

---

## Reporting Issues

### Bug Reports

Include:
- Home Assistant version
- Integration version (check `manifest.json`)
- Controller firmware version
- Detailed error description
- Steps to reproduce
- Relevant logs (Settings > System > Logs)
- Configuration screenshots

### Feature Requests

Include:
- Use case description
- Proposed implementation (if known)
- Examples of similar features in other integrations
- Impact assessment (who would benefit)

---

## Quality Scale Progress

This integration is following the [Home Assistant Quality Scale](https://www.home-assistant.io/docs/quality_scale/).

The declared level is in `custom_components/violet_pool_controller/manifest.json`
(`"quality_scale"`), and the per-rule status is tracked in
`custom_components/violet_pool_controller/quality_scale.yaml`. Read those two
files rather than a prose summary - a summary of a checklist goes stale
faster than the checklist.

---

## Getting Help

- **Documentation:** Check the [README.md](README.md)
- **Issues:** Search [GitHub Issues](https://github.com/Xerolux/violet-hass/issues)
- **Discussions:** Use [GitHub Discussions](https://github.com/Xerolux/violet-hass/discussions)
- **Home Assistant Community:** [Forums](https://community.home-assistant.io/)

---

## Recognition

Contributors are credited automatically in the release notes: the release
workflow builds them from merged pull requests, with `@author` attribution.
That is why every change destined for a release goes in through a pull
request rather than a local merge.

Thank you for contributing! 🌊
