> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Testing.de)**

---

# Testing – Running and Writing Tests

> Complete guide for the Violet Pool Controller integration test system.

---

## Quick Start

```bash
# One-time: Set up test environment
./scripts/setup-test-env.sh

# Run tests
./scripts/run-tests.sh

# Expected result: all tests passing ✓
```

---

## Setting Up the Test Environment

### Automatic (Recommended)

```bash
./scripts/setup-test-env.sh
```

The script handles:
- Checking the configured Home Assistant/Python test environment
- Creating virtual environment `.venv-ha-test/`
- Installing dependencies from `requirements-dev.txt`
- Installing pytest and dependencies
- Creating `activate-test-env.sh` helper

### Manual

```bash
python3.14 -m venv .venv-ha-test
source .venv-ha-test/bin/activate
pip install -r requirements-dev.txt
```

---

## Running Tests

### All Tests

```bash
./scripts/run-tests.sh
# or
source .venv-ha-test/bin/activate
pytest tests/ -v
```

### Individual Test Files

```bash
pytest tests/test_api.py -v
pytest tests/test_config_flow.py -v
pytest tests/test_device.py -v
pytest tests/test_entity_state.py -v
pytest tests/test_integration.py -v
pytest tests/test_sanitizer.py -v
```

### Individual Test Function

```bash
pytest tests/test_api.py::TestVioletPoolAPI::test_rate_limiting -v
```

---

## Test Categories

### API Tests (`test_api.py`) – 7 Tests

Tests HTTP communication with the controller:

| Test | Description |
|------|-------------|
| `test_rate_limiting` | Token bucket limits requests |
| `test_priority_queue` | High-priority requests first |
| `test_timeout_handling` | Timeouts handled correctly |
| `test_retry_logic` | Retry attempts on errors |
| `test_error_responses` | HTTP errors forwarded correctly |
| `test_json_parsing` | JSON responses parsed correctly |
| `test_ssl_config` | SSL settings applied |

```bash
pytest tests/test_api.py -v
```

---

### Config Flow Tests (`test_config_flow.py`) – 5 Tests

Tests the setup wizard:

| Test | Description |
|------|-------------|
| `test_duplicate_detection` | Two identical controllers detected |
| `test_controller_name_handling` | Controller names saved correctly |
| `test_ip_validation` | Invalid IPs rejected |
| `test_feature_selection` | Feature selection saved |
| `test_successful_setup` | Complete setup flow |

```bash
pytest tests/test_config_flow.py -v
```

---

### Device Tests (`test_device.py`) – 7 Tests

Tests device management and recovery:

| Test | Description |
|------|-------------|
| `test_recovery_lock` | No race conditions |
| `test_exponential_backoff` | Wait times double |
| `test_max_recovery_attempts` | Stops after 10 attempts |
| `test_device_info_update` | Device info updated correctly |
| `test_connection_loss` | Connection loss detected |
| `test_successful_recovery` | Connection restored |
| `test_coordinator_update` | Data update processed correctly |

```bash
pytest tests/test_device.py -v
```

---

### Integration Tests (`test_integration.py`) – 10 Tests

End-to-end tests:

| Test | Description |
|------|-------------|
| `test_domain_initialization` | Domain registered correctly |
| `test_entry_setup` | Config entry loaded |
| `test_entry_unload` | Integration cleanly unloaded |
| `test_service_registration` | All services registered |
| `test_config_migration` | Old configurations migrated |
| `test_sensor_creation` | Sensors created |
| `test_switch_creation` | Switches created |
| `test_climate_creation` | Climate entities created |
| `test_cover_creation` | Cover entity created |
| `test_number_creation` | Number entities created |

```bash
pytest tests/test_integration.py -v
```

---

### Entity State Tests (`test_entity_state.py`) – 4 Tests

Tests state interpretation:

| Test | Description |
|------|-------------|
| `test_3state_switches` | ON/OFF/AUTO interpreted correctly |
| `test_numeric_prefix` | `"2\|SOLAR_ACTIVE"` parsed correctly |
| `test_string_state_parsing` | String states converted correctly |
| `test_boolean_conversion` | Boolean values correct |

```bash
pytest tests/test_entity_state.py -v
```

---

### Sanitizer Tests (`test_sanitizer.py`) – 13 Tests

Security and input validation:

| Test | Description |
|------|-------------|
| `test_xss_prevention` | `<script>` is blocked |
| `test_sql_injection` | SQL syntax is blocked |
| `test_command_injection` | Shell commands are blocked |
| `test_path_traversal` | `../` is blocked |
| `test_ph_range` | pH outside 6.0–8.0 blocked |
| `test_orp_range` | ORP outside 200–900 mV blocked |
| `test_temperature_range` | Temp outside 10–40°C blocked |
| `test_alphanumeric_validation` | Only allowed characters |
| `test_numeric_validation` | Only numbers |
| `test_html_escaping` | HTML special characters escaped |
| `test_empty_input` | Empty inputs handled |
| `test_null_input` | None values handled |
| `test_oversized_input` | Overly long inputs truncated |

```bash
pytest tests/test_sanitizer.py -v
```

---

## Advanced Options

### Coverage Report

```bash
# Terminal report
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# HTML report (detailed)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=html
# Open: htmlcov/index.html

# Target: > 80% coverage
```

### Run in Parallel (Faster)

```bash
pip install pytest-xdist
pytest tests/ -n auto -v
```

### Re-run Failed Tests

```bash
pytest tests/ --lf -v
```

### Verbose with Details

```bash
pytest tests/ -vv --tb=long
```

---

## Debugging

### Python Debugger

```bash
pytest tests/ --pdb
# On failure: debugger starts automatically
```

### Show Print Output

```bash
pytest tests/ -v -s
```

### Debug Logging

```bash
pytest tests/ -v --log-cli-level=DEBUG
```

---

## pytest.ini Configuration

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

These settings are required for:
- **asyncio_mode = auto**: Automatic async/await handling
- **asyncio_default_fixture_loop_scope = function**: Isolated event loops per test

---

## conftest.py – Thread Workaround

`tests/conftest.py` contains an important patch:

```python
# Filters Home Assistant's _run_safe_shutdown_loop threads
# Prevents false-positive thread leak warnings
# Required for HA 2025.1+
```

---

## Pre-Release Checklist

```bash
# 1. Linting (0 errors!)
python -m ruff check custom_components/violet_pool_controller/
python -m mypy custom_components/violet_pool_controller/

# 2. All tests passing
./scripts/run-tests.sh

# 3. Check coverage (> 80%)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# 4. Manual test in real HA instance
```

### Expected Result

```
======================== test session starts ========================
...
======================== 53 passed in 12.34s ========================
```

---

## CI/CD Integration

GitHub Actions runs automatically on push/PR:

```yaml
# .github/workflows/validate.yml
- Ruff Linting
- MyPy Type Checking
- pytest (HA 2026.5.x)
- Python runtime compatible with the configured Home Assistant test target
```

---

## Troubleshooting

### ImportError / ModuleNotFoundError

```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

### "No module named custom_components"

Run tests from the project root (not from `tests/`):

```bash
# Correct
pytest tests/ -v

# Wrong
cd tests && pytest
```

### Thread-Assertion Error

```bash
# Recreate virtual environment
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Old HA Version

```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

---

## Test Success Criteria

Before every merge/release, the following must be met:

- [ ] **100% of all unit tests pass**
- [ ] **Ruff linting: 0 errors**
- [ ] **MyPy: 0 errors** (except `import-not-found`)
- [ ] **Coverage: > 80%**
- [ ] **No regression in existing features**

---

*Back: [Contributing](Contributing) | Next: [API Reference](API-Reference)*
