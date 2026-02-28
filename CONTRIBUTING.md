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

- Python 3.12 or later
- Home Assistant 2025.1 or later
- Git
- A Violet Pool Controller device (or access to simulator)

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
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install ruff mypy pytest pytest-asyncio pytest-homeassistant-custom-component
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

| Metric | Tool | Target (Bronze) | Target (Silver) | Target (Gold) |
|--------|------|-----------------|-----------------|---------------|
| Linting | Ruff | ✅ 0 errors | ✅ 0 errors | ✅ 0 errors |
| Type Hints | mypy | ✅ 50% | ⚠️ 80% | ❌ 90% |
| Test Coverage | pytest | ⚠️ 80% | ⚠️ 85% | ❌ 95% |

### File Structure

```
custom_components/violet_pool_controller/
├── __init__.py              # Integration setup
├── api.py                   # HTTP client
├── device.py                # Device & coordinator
├── error_handler.py         # Error handling
├── manifest.json            # Integration metadata
├── services.py              # Service handlers
├── const.py                 # Constants
├── config_flow.py           # Setup UI
├── config_flow_utils.py     # Config flow helpers
├── sensor.py                # Sensor platform
├── switch.py                # Switch platform
├── binary_sensor.py         # Binary sensor platform
├── climate.py               # Climate platform
├── cover.py                 # Cover platform
├── number.py                # Number platform
├── select.py                # Select platform
├── strings.json             # UI translations
└── translations/            # Localized strings (future)
```

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

# Run specific test
pytest tests/test_api.py::test_get_readings
```

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

Use clear, descriptive commit messages:

```
[Scope] Brief description

More detailed explanatory text if needed.

Refs: #issue_number
```

Examples:
```
[API] Add timeout configuration support

Allows users to configure custom timeout values for API requests.
Fixes connection issues with slow controllers.

Refs: #123
```

```
[Docs] Update troubleshooting guide

Added section for SSL certificate errors and resolution steps.
```

### Pull Request Checklist

- [ ] Code follows PEP 8 and PEP 257
- [ ] Type hints added where appropriate
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`ruff check`)
- [ ] No type errors (`mypy`)
- [ ] Commit messages follow format

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

**Current Level:** 🥉 **Bronze** (100% complete)
**Next Target:** 🥈 **Silver** (in progress)

See [HA_QUALITY_SCALE_PROGRESS.md](docs/HA_QUALITY_SCALE_PROGRESS.md) for detailed status.

---

## Getting Help

- **Documentation:** Check the [README.md](README.md)
- **Issues:** Search [GitHub Issues](https://github.com/Xerolux/violet-hass/issues)
- **Discussions:** Use [GitHub Discussions](https://github.com/Xerolux/violet-hass/discussions)
- **Home Assistant Community:** [Forums](https://community.home-assistant.io/)

---

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Integration documentation

Thank you for contributing! 🌊
