# Testing Guide for Violet Pool Controller

## 🧪 Overview

This project contains comprehensive tests that must be run before each release.

## 📋 Quick Start

### 1. Set Up Test Environment (one-time)

```bash
# From the project root directory:
./scripts/setup-test-env.sh
```

The script:
- ✅ Checks Python 3.14
- ✅ Creates virtual environment (`.venv-ha-test/`)
- ✅ Installs dependencies from `requirements-dev.txt`
- ✅ Installs pytest and test dependencies
- ✅ Creates `activate-test-env.sh` helper

### 2. Run Tests

```bash
# Option 1: With the run script (recommended)
./scripts/run-tests.sh

# Option 2: Manually
source activate-test-env.sh
pytest tests/ -v
```

## 🎯 Test Categories

### API Tests (`tests/test_api.py`)
Tests for API communication with the pool controller:
- ✅ Rate limiting (token bucket)
- ✅ Priority queue
- ✅ Timeout handling
- ✅ Error handling
- ✅ JSON parsing

```bash
pytest tests/test_api.py -v
```

### Config Flow Tests (`tests/test_config_flow.py`)
Tests for the configuration UI:
- ✅ Duplicate detection
- ✅ Controller name handling
- ✅ IP validation

```bash
pytest tests/test_config_flow.py -v
```

### Device Tests (`tests/test_device.py`)
Tests for device management and recovery:
- ✅ Recovery lock against race conditions
- ✅ Exponential backoff
- ✅ Device info updates

```bash
pytest tests/test_device.py -v
```

### Integration Tests (`tests/test_integration.py`)
End-to-end tests for integration setup:
- ✅ Domain initialization
- ✅ Entry setup/unload
- ✅ Service registration
- ✅ Config migration

```bash
pytest tests/test_integration.py -v
```

### Entity State Tests (`tests/test_entity_state.py`)
Tests for state interpretation:
- ✅ 3-state switches (ON/OFF/AUTO)
- ✅ Numeric prefix handling
- ✅ String state parsing

```bash
pytest tests/test_entity_state.py -v
```

### Sanitizer Tests (`tests/test_sanitizer.py`)
Security and input validation tests:
- ✅ XSS prevention
- ✅ Path traversal prevention
- ✅ Range validation (pH, ORP, Chlorine)
- ✅ SQL injection prevention

```bash
pytest tests/test_sanitizer.py -v
```

## 📊 Test Coverage

Generate coverage report:

```bash
source activate-test-env.sh
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=html
```

Open HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🔧 Advanced Test Options

### Run a Single Test

```bash
pytest tests/test_api.py::TestVioletPoolAPI::test_rate_limiting_active -v
```

### Run Tests with Specific Marker

```bash
pytest -m thread_safe -v
```

### Run Tests in Parallel (faster)

```bash
pip install pytest-xdist
pytest tests/ -n auto -v
```

### Detailed Failure Output

```bash
pytest tests/ -vv --tb=long
```

### Repeat Only Failed Tests

```bash
pytest tests/ --lf -v
```

## 🐛 Debugging Tests

### With pdb (Python Debugger)

```bash
pytest tests/ --pdb
```

The debugger starts automatically on failure.

### Show Test Output (print statements)

```bash
pytest tests/ -v -s
```

### Enable Logging

```bash
pytest tests/ -v --log-cli-level=DEBUG
```

## ⚙️ pytest.ini Configuration

The `pytest.ini` contains:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

These settings are important for async tests with Home Assistant.

## 🔍 conftest.py - Thread-Check Workaround

The `tests/conftest.py` contains an important patch:
- Filters Home Assistant's `_run_safe_shutdown_loop` threads
- Prevents false-positive thread leaks
- Required for compatibility with HA 2025.1+

## 📝 Before Each Release

### Pre-Release Checklist

```bash
# 1. Check code quality
ruff check custom_components/
mypy custom_components/violet_pool_controller/

# 2. Run all tests
./scripts/run-tests.sh

# 3. Check coverage (should be > 80%)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# 4. Test integration in real HA instance (see TESTING_CHECKLIST.md)
```

### Expected Test Results

```
======================== Test Summary ========================
✓ 53 Tests PASSED
══════════════════════════════════════════════════════════════
Success rate: 100%
```

All tests must pass before a release is created!

## 🏗️ Test Structure

```
tests/
├── conftest.py              # Pytest configuration & fixtures
├── test_api.py              # API tests (7 tests)
├── test_config_flow.py      # Config flow tests (5 tests)
├── test_device.py           # Device tests (7 tests)
├── test_entity_state.py     # State tests (4 tests)
├── test_integration.py      # Integration tests (10 tests)
└── test_sanitizer.py        # Security tests (13 tests)
```

## 🔄 CI/CD Integration

For GitHub Actions / GitLab CI:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Setup Test Environment
        run: ./scripts/setup-test-env.sh
      - name: Run Tests
        run: ./scripts/run-tests.sh
```

## 🆘 Troubleshooting

### Problem: Import Errors

**Solution:**
```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

### Problem: "No module named custom_components"

**Solution:** Run tests from project root, not from the `tests/` directory.

### Problem: Thread Name Assertion Error

**Solution:** `conftest.py` already contains the fix. If problem persists:
```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Problem: Old Home Assistant Version

**Solution:**
```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Problem: pytest not found

**Solution:**
```bash
source .venv-ha-test/bin/activate
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Home Assistant Testing Best Practices](https://developers.home-assistant.io/docs/development_testing)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

## ✅ Test Success Criteria

Before a merge/release, the following must be met:

- [ ] **100% of unit tests pass**
- [ ] **Ruff Linting: 0 errors**
- [ ] **MyPy Type Check: 0 errors (except import-not-found)**
- [ ] **Test Coverage: > 80%**
- [ ] **Manual tests in real HA instance** (see TESTING_CHECKLIST.md)
- [ ] **No regression in existing features**

## 🚀 Continuous Testing

It is recommended to run tests automatically on every commit:

```bash
# Create git pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/run-tests.sh
EOF
chmod +x .git/hooks/pre-commit
```

Tests will then run automatically before every commit.
