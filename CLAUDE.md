# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for the **Violet Pool Controller** by PoolDigital GmbH & Co. KG. It enables local polling-based control and monitoring of pool systems including pumps, heaters, solar, chemical dosing, lighting, and covers.

**Current Version**: `1.0.5-beta.3` (defined in `manifest.json` and `const.py`)

## Development Commands

### Code Quality & Linting

```bash
# Install dev tools (one-time)
pip install ruff mypy

# Run ruff linter
python -m ruff check custom_components/violet_pool_controller/

# Auto-fix all ruff issues (preferred method)
python -m ruff check custom_components/violet_pool_controller/ --fix

# Run with specific rule sets
python -m ruff check custom_components/violet_pool_controller/ --select=E,F,W,C4,UP,SIM

# Type checking with mypy
python -m mypy custom_components/violet_pool_controller/
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
pytest tests/test_config_flow.py -v
pytest tests/test_device.py -v
pytest tests/test_sanitizer.py -v
pytest tests/test_discovery.py -v
pytest tests/test_error_handler.py -v

# Run with coverage
pytest --cov=custom_components/violet_pool_controller --cov-report=html

# Run single test function
pytest tests/test_api.py::test_function_name -v
```

**Test Configuration** (`pytest.ini`):
- `asyncio_mode = auto` - Automatic async/await handling
- `asyncio_default_fixture_loop_scope = function` - Isolated event loops per test

**Important**: The test suite includes a thread-safety workaround in `conftest.py` that patches `threading.enumerate()` to filter out Home Assistant's `_run_safe_shutdown_loop` threads for compatibility with newer HA versions.

## Architecture

### Core Module Structure (`custom_components/violet_pool_controller/`)

#### Main Components

- **`__init__.py`** - Integration entry point. Handles setup, config entry migration, platform loading, and service registration. Loads these platforms: `sensor`, `binary_sensor`, `switch`, `climate`, `cover`, `number`, `select`.

- **External API package** (`violet-poolController-api==0.0.11` on PyPI) - The HTTP client and low-level utilities are **not** in this repo; they ship as an external package. Provides:
  - `VioletPoolAPI` class - rate-limited HTTP client with retry/backoff
  - `VioletPoolAPIError` exception hierarchy
  - `InputSanitizer` - XSS/injection/path-traversal protection
  - `VioletState` - device state constants
  - `const_api` module - endpoint paths, action constants, rate-limit params
  - `const_devices` module - switch definitions, control parameters, `DEVICE_STATE_MAPPING`

- **`device.py`** - Contains two main classes:
  - `VioletPoolControllerDevice`: Device representation with auto-recovery
  - `VioletPoolDataUpdateCoordinator`: Home Assistant's data update coordinator pattern
  - Smart failure logging with throttling (5-minute intervals)
  - Automatic connection recovery with exponential backoff
  - **Thread Safety**: Uses two locks with documented ordering:
    - `_api_lock`: Protects API calls and data updates
    - `_recovery_lock`: Protects recovery state and attempts
    - **Never acquire locks in nested order** - see device.py:42-58 for full documentation

- **`entity.py`** - Base entity class `VioletPoolControllerEntity` extending `CoordinatorEntity`. Provides helper methods:
  - `get_value()` - Safe data access with fallback
  - `get_float_value()` - Float conversion with error handling
  - `get_bool_value()` - Boolean conversion
  - `interpret_state_as_bool()` - Smart state interpretation

- **`config_flow.py`** - UI-based configuration flow supporting:
  - Initial setup wizard
  - Feature selection
  - Dynamic sensor discovery
  - Duplicate detection
  - Multi-controller support

#### Utility & Support Modules

- **`error_codes.py`** - Comprehensive error code mappings:
  - Maps controller error codes to human-readable messages
  - Severity classification (info, warning, critical)
  - Error type categorization (MESSAGE, ALERT, ERROR)

- **`error_handler.py`** - Centralized error handling with `VioletErrorCodes` class:
  - Network errors (TIMEOUT, CONNECTION, DNS, SSL)
  - API errors (TIMEOUT, RATE_LIMITED, INVALID_RESPONSE, JSON_DECODE)
  - Auth errors (INVALID_CREDENTIALS, WEAK_PASSWORD, SESSION_EXPIRED)
  - Config errors and circuit breaker errors

- **`diagnostics.py`** - Home Assistant diagnostics support:
  - `async_get_config_entry_diagnostics()` — exposes poll history, connection metrics (latency, request rate, system health)
  - Automatically redacts sensitive fields (username, password)

- **`discovery.py`** - ZeroConf/mDNS auto-discovery:
  - `VioletPoolControllerDiscovery` class
  - Service types: `_http._tcp.local.` and `_violet-controller._tcp.local.`
  - Triggers config flow when a controller is found on the network

#### Constants Organization (Modular)

- **`const.py`** - Central hub re-exporting all constants plus integration-level config:
  - `DOMAIN`, `INTEGRATION_VERSION`, `MANUFACTURER`
  - Configuration keys including `CONF_VERIFY_SSL` for SSL certificate verification
  - Default values for all settings
  - Pool configuration (types, disinfection methods)
  - Re-exports constants from `const_api` and `const_devices` (external package)

- **`const_sensors.py`** - Sensor definitions (local):
  - Sensor key mappings
  - Unit of measurement mappings
  - Feature-to-sensor mappings
  - Device class assignments

- **`const_features.py`** - Feature flags and feature groups (local):
  - Available features (pump, heater, solar, dosing, etc.)
  - Feature groupings for UI
  - Feature dependencies

**Note**: `const_api.py` and `const_devices.py` are now part of the external `violet-poolController-api` package, not local files.

#### Subdirectories

- **`config_flow_utils/`** - Config flow helper modules:
  - `constants.py` - Config flow constants
  - `validators.py` - Input validation (IP address, credential strength, sensor labels)
  - `sensor_helper.py` - Sensor grouping helpers
  - `__init__.py` - Re-exports all utilities

- **`sensor_modules/`** - Modular sensor implementations:
  - `base.py` - Base sensor functionality
  - `generic.py` - `VioletSensor` and `VioletStatusSensor` classes
  - `monitoring.py` - Monitoring sensors (latency, system health, request rate)
  - `specialized.py` - Specialized sensors (dosing, error codes, flow rate)
  - `__init__.py` - Module exports

#### Entity Platforms

- **`sensor.py`** - Sensor entities:
  - Temperature sensors (pool, solar, ambient)
  - Water chemistry (pH, ORP, chlorine, conductivity)
  - Analog inputs (AI1-AI8)
  - System diagnostics (runtime, error codes)
  - Calibration history

- **`binary_sensor.py`** - Binary sensor entities:
  - Digital input states (DI1-DI8)
  - System alarms
  - Connection status

- **`switch.py`** - 3-state switch entities (ON/OFF/AUTO):
  - Pump control
  - Heater control
  - Solar control
  - Dosing systems (pH-, pH+, Chlorine, Flocculant)
  - DMX scenes (1-8)
  - Extension relays (1-8)
  - Multi-state support (0-6) with automatic mode detection

- **`climate.py`** - Thermostat entities:
  - Pool heater control with temperature setpoints
  - Solar heater control
  - HVAC mode support (off, heat, auto)

- **`cover.py`** - Cover entities:
  - Pool cover control with string-state handling
  - Open/close/stop commands
  - Position tracking

- **`number.py`** - Number input entities:
  - Temperature setpoints (pool, solar)
  - pH target values
  - ORP target values
  - Dosing parameters

- **`select.py`** - Select entities for mode selection:
  - Dropdown controls using `SELECT_CONTROLS` constant
  - Mode selection for devices that expose enumerated options

#### Services

Services defined in `services.yaml` and registered in `services.py`:

- **`control_pump`** - Advanced pump control:
  - Speed control (0-3) - Controller supports 4 speed levels: PUMP_RPM_0 to PUMP_RPM_3
  - Force off mode
  - Eco mode
  - Boost mode
  - Auto mode
  - Duration settings

- **`smart_dosing`** - Chemical dosing control:
  - Manual dosing (pH-, pH+, Chlorine, Flocculant)
  - Automatic mode
  - Duration control

- **`manage_pv_surplus`** - PV surplus mode control:
  - Enable/disable photovoltaic surplus usage
  - Integration with solar systems

- **`control_dmx_scenes`** - DMX lighting control:
  - Scene selection (1-8)
  - Scene activation/deactivation

- **`set_light_color_pulse`** - Pool light control:
  - Color pulse commands

- **`manage_digital_rules`** - Digital input rule management:
  - Configure automation rules based on digital inputs

- **`test_output`** - Diagnostics:
  - Output test mode for troubleshooting

### Key Design Patterns

1. **Coordinator Pattern**: All entities use `VioletPoolDataUpdateCoordinator` for synchronized data updates, reducing API calls and improving efficiency.

2. **Rate Limiting**: API requests go through a global rate limiter (provided by the external `violet-poolController-api` package) using token bucket algorithm to protect the controller from overload.

3. **Multi-State Switches**: Pool devices support multiple states (0-6):
   - `0` = AUTO_OFF (automatic control, currently off)
   - `1` = AUTO_ON (automatic control, currently on)
   - `2` = AUTO_ACTIVE (automatic control with timing)
   - `3` = AUTO_ACTIVE_TIMER (automatic control with timer)
   - `4` = MANUAL_ON_FORCED (manual on, forced mode)
   - `5` = AUTO_WAITING (automatic control, waiting for conditions)
   - `6` = MANUAL_OFF (manual off)

   **Important**: States may include descriptive suffixes (e.g., `"3|PUMP_ANTI_FREEZE"`) parsed as operational modes like frost protection.

4. **Multi-Controller Support**:
   - Unique identifiers use `{api_url}_{device_id}` format
   - Dynamic device info generation
   - Separate data coordinators per controller

5. **Auto-Recovery**:
   - Automatic reconnection on connection loss
   - Exponential backoff for retries (10s base, max 300s delay)
   - Smart error logging with throttling (5-minute intervals)
   - Max 10 recovery attempts before manual intervention required

6. **Input Sanitization**:
   - All user inputs validated through `InputSanitizer`
   - Protection against injection attacks
   - Safe handling of API parameters

7. **SSL/TLS Security**:
   - SSL certificate verification enabled by default (`verify_ssl=True`)
   - Configurable for self-signed certificates (generates warning)
   - Proper SSL context handling in API requests

## API Communication

The Violet Pool Controller exposes a JSON-based HTTP API:

### Endpoints

- **`GET /getReadings?ALL`** - Retrieve all sensor data
- **`GET /setFunctionManually?{payload}`** - Control outputs (pump, heater, solar, dosing, etc.)
- **`POST /setConfig`** - Update configuration values
- **`GET /getConfig?{keys}`** - Fetch specific configuration values

### Request Patterns

- All requests are rate-limited using token bucket algorithm
- Retry logic with exponential backoff (configurable, 3 attempts by default)
- Timeout: 10 seconds total, with 8-second connection/socket timeouts (configurable)
- SSL certificate verification: enabled by default, configurable
- Responses are JSON-formatted
- All user inputs are sanitized through `InputSanitizer` before API calls

## Testing Infrastructure

### Test Suite Organization

Located in `tests/`:

**Core Tests:**
- **`conftest.py`** - Pytest fixtures, timezone patching, socket disabling for HA compatibility
- **`test_api.py`** - API communication tests (rate limiting, timeout, error handling)
- **`test_config_flow.py`** - Configuration flow tests (duplicate detection, validation)
- **`test_device.py`** - Device and coordinator tests
- **`test_entity_state.py`** - Entity state interpretation tests
- **`test_integration.py`** - Full integration tests
- **`test_sanitizer.py`** - Input sanitization tests

**Platform & Feature Tests:**
- **`test_cover.py`** - Cover platform tests
- **`test_services.py`** - Service handler tests
- **`test_diagnostic_services.py`** - Diagnostic service tests
- **`test_translations.py`** - Translation file validation
- **`test_type_hints.py`** - Type annotation validation
- **`test_sensor_generic.py`** - Generic sensor module tests

**Advanced Scenario Tests:**
- **`test_discovery.py`** - ZeroConf discovery tests
- **`test_reconfigure_flow.py`** - Reconfiguration flow tests
- **`test_error_handler.py`** - Error handler and `VioletErrorCodes` tests
- **`test_platform_errors.py`** - Platform-level error handling
- **`test_security_fixes.py`** - Security-related regression tests
- **`test_offline_scenarios.py`** - Offline/connectivity loss scenarios
- **`test_improvements.py`** - Feature improvement tests

**Test Data:**
- **`getReadings_spec.json`** - Sample API response for mock fixtures

### Test Configuration

**`pytest.ini`** settings:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### CI/CD Testing

GitHub workflow `.github/workflows/validate.yml` runs:
- Ruff linting
- Mypy type checking
- Full test suite with pytest
- Tests against Home Assistant 2026.3.1
- Python 3.14 environment

## Translation Files

Located in `custom_components/violet_pool_controller/translations/`:

- **Primary languages**: `de.json` (German), `en.json` (English)
- **Additional languages**: `es.json`, `fr.json`, `it.json`, `nl.json`, `pl.json`, `pt.json`, `ru.json`, `zh.json`

Translation files cover:
- Configuration flow UI
- Entity names and descriptions
- Service descriptions
- Error messages

## Project Structure

```
violet-hass/
├── custom_components/
│   └── violet_pool_controller/      # Main integration code
│       ├── __init__.py               # Entry point (loads 7 platforms)
│       ├── device.py                 # Device & coordinator
│       ├── entity.py                 # Base entity class
│       ├── config_flow.py            # Config flow
│       ├── const.py                  # Constants hub (re-exports external pkg constants)
│       ├── const_sensors.py          # Sensor definitions (local)
│       ├── const_features.py         # Feature flags (local)
│       ├── sensor.py                 # Sensor platform
│       ├── binary_sensor.py          # Binary sensor platform
│       ├── switch.py                 # Switch platform
│       ├── climate.py                # Climate platform
│       ├── cover.py                  # Cover platform
│       ├── number.py                 # Number platform
│       ├── select.py                 # Select platform (NEW)
│       ├── services.py               # Service handlers
│       ├── services.yaml             # Service definitions
│       ├── error_codes.py            # Error code mappings
│       ├── error_handler.py          # VioletErrorCodes & error utilities (NEW)
│       ├── diagnostics.py            # HA diagnostics support (NEW)
│       ├── discovery.py              # ZeroConf/mDNS discovery (NEW)
│       ├── manifest.json             # Integration manifest
│       ├── strings.json              # UI strings
│       ├── icons.json                # Icon mappings
│       ├── quality_scale.yaml        # Quality scale metadata
│       ├── config_flow_utils/        # Config flow helpers (NEW)
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   ├── validators.py
│       │   └── sensor_helper.py
│       ├── sensor_modules/           # Modular sensor implementations (NEW)
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── generic.py
│       │   ├── monitoring.py
│       │   └── specialized.py
│       └── translations/             # Translations (10 languages)
├── tests/                            # Test suite (21 files)
│   ├── conftest.py                   # Pytest configuration
│   ├── test_api.py                   # API tests
│   ├── test_config_flow.py           # Config flow tests
│   ├── test_device.py                # Device tests
│   ├── test_entity_state.py          # Entity tests
│   ├── test_integration.py           # Integration tests
│   ├── test_sanitizer.py             # Sanitizer tests
│   ├── test_cover.py                 # Cover platform tests
│   ├── test_services.py              # Service tests
│   ├── test_diagnostic_services.py   # Diagnostic tests
│   ├── test_discovery.py             # Discovery tests
│   ├── test_error_handler.py         # Error handler tests
│   ├── test_reconfigure_flow.py      # Reconfiguration tests
│   ├── test_platform_errors.py       # Platform error tests
│   ├── test_security_fixes.py        # Security regression tests
│   ├── test_offline_scenarios.py     # Offline scenario tests
│   ├── test_improvements.py          # Feature improvement tests
│   ├── test_sensor_generic.py        # Generic sensor tests
│   ├── test_translations.py          # Translation validation
│   ├── test_type_hints.py            # Type hint tests
│   └── getReadings_spec.json         # Sample API response fixture
├── scripts/                          # Development scripts
│   ├── setup-test-env.sh             # Test environment setup
│   ├── run-tests.sh                  # Test runner
│   ├── start-ha-test.sh              # HA test instance launcher
│   ├── check-ha-logs.sh              # Log checker
│   └── quick-import-test.py          # Quick import test
├── blueprints/                       # Home Assistant blueprints
│   └── automation/                   # 4 automation templates
├── Dashboard/                        # Dashboard YAML examples
├── docs/                             # Documentation (27+ files)
├── .github/                          # GitHub config
│   └── workflows/                    # 15 CI/CD pipelines
├── .devcontainer/                    # VS Code dev container
├── CLAUDE.md                         # This file
├── README.md                         # Project README
├── WIKI.md                           # Comprehensive wiki
├── CONTRIBUTING.md                   # Contribution guidelines
├── hacs.json                         # HACS integration config
├── requirements.txt                  # Runtime dependencies
├── requirements-dev.txt              # Development dependencies
└── pytest.ini                        # Pytest configuration
```

## Development Best Practices

### Dependency Management

**pytest-homeassistant-custom-component**
- **Repository:** https://github.com/MatthewFlamm/pytest-homeassistant-custom-component
- **Policy:** Always use the latest version when available
- **Reason:** Ensures compatibility with latest Home Assistant versions and Python versions
- **Update frequency:** Check for updates when:
  - New Home Assistant version is released
  - New Python version is released
  - CI/CD pipeline fails due to compatibility issues
- **Current version:** `>=0.13.109` (Python 3.14+ compatible)
- **Update command:** `pip install --upgrade pytest-homeassistant-custom-component`

### Code Style

1. **Follow PEP 8**: Use ruff for linting and auto-formatting
2. **Type Hints**: Use type hints throughout (checked with mypy)
3. **Docstrings**: Document all public classes and methods
4. **Constants**: Use the modular const_*.py files for new constants

### Error Handling

1. **Never fail silently**: Log all errors appropriately
2. **Use try-except**: Wrap API calls and data parsing in try-except blocks
3. **Graceful degradation**: Continue operation even if some features fail
4. **User feedback**: Provide clear error messages in the UI

### Testing

1. **Write tests first**: Follow TDD where possible
2. **Test coverage**: Aim for >80% coverage
3. **Mock external calls**: Use fixtures to mock API responses
4. **Test edge cases**: Include error conditions and boundary values

### Security

1. **Sanitize inputs**: Use `InputSanitizer` for all user inputs
2. **Validate data**: Check API responses before processing
3. **No hardcoded secrets**: Use configuration for credentials
4. **Rate limiting**: Respect API rate limits to prevent abuse

### Performance

1. **Batch requests**: Use coordinator pattern to batch data updates
2. **Cache wisely**: Cache configuration data, refresh sensor data
3. **Async operations**: Use asyncio for all I/O operations
4. **Minimize logging**: Use appropriate log levels

## GitHub Workflows

Located in `.github/workflows/`:

**Validation & CI:**
- **`validate.yml`** - Code validation on push/PR (ruff, mypy, pytest; HA 2026.3.x, Python 3.14)
- **`hassfest-validation.yml`** - Home Assistant manifest/quality validation
- **`hacs-validation.yml`** - HACS compatibility check

**Release & Security:**
- **`release.yml`** - Automated release creation
- **`security.yml`** - Security scanning
- **`update-api-dependency.yml`** - Automated `violet-poolController-api` dependency updates

**Code Quality & Automation:**
- **`claude.yml`** - Claude Code integration
- **`claude-code-review.yml`** - Automated code review
- **`pr-management.yml`** - PR workflow management
- **`automerge.yml`** - Automatic PR merging
- **`auto-label-pr.yml`** - PR auto-labeling
- **`status-check-labels.yml`** - Label-based status checks
- **`maintenance.yml`** - Repository maintenance
- **`stale.yml`** - Stale issue/PR management
- **`wiki-sync.yml`** - Wiki synchronization

## Common Tasks for AI Assistants

### Adding a New Sensor

1. Add sensor definition to `const_sensors.py`
2. Update `sensor.py` to create the entity
3. Add translation strings to `strings.json` and translation files
4. Write tests in `tests/test_integration.py`

### Adding a New Service

1. Define service in `services.yaml`
2. Implement handler in `services.py`
3. Register in `__init__.py` `async_setup_entry()`
4. Add translation strings
5. Write service tests

### Fixing API Issues

1. API client lives in the **external** `violet-poolController-api` PyPI package — check its source for endpoint definitions and rate limiting
2. Local error handling is in `error_handler.py` (`VioletErrorCodes`)
3. Test with `tests/test_api.py` and `tests/test_error_handler.py`
4. Check retry/backoff logic in `device.py`

### Updating Constants

1. Identify correct const_*.py file based on category
2. Add constant with clear naming
3. Update imports in `const.py` if needed
4. Document usage in docstrings

## Dependencies

**Runtime** (from `requirements.txt`):
- `homeassistant>=2026.3.0` - Minimum Home Assistant version
- `aiohttp>=3.11.0` - Async HTTP client
- `voluptuous>=0.15.0` - Data validation

**Integration requirement** (from `manifest.json`):
- `violet-poolController-api==0.0.11` - External API client package (installed by HA automatically)

**Development** (from `requirements-dev.txt`):
- `ruff>=0.15.0` - Linter and formatter
- `mypy>=1.15.0` - Static type checker
- `pytest>=9.0.0` - Test framework
- `pytest-cov>=6.0.0` - Coverage plugin
- `pytest-asyncio>=1.0.0` - Async test support
- `pytest-homeassistant-custom-component>=0.13.109` - HA test helpers

## Important Notes

1. **Thread Safety**: The integration uses two locks (`_api_lock`, `_recovery_lock`) with documented ordering. Always read device.py:42-58 before modifying concurrent code to prevent deadlocks.

2. **State Handling**: Switches support states 0-6 with specific meanings:
   - States 0, 5, 6 = Device OFF (different automatic/manual modes)
   - States 1, 2, 3, 4 = Device ON (different automatic/manual modes)
   - Composite states like `"3|PUMP_ANTI_FREEZE"` provide additional context about operational modes
   - All states are defined in `DEVICE_STATE_MAPPING` inside the external `violet-poolController-api` package (`const_devices` module)

3. **Multi-Controller**: The integration supports multiple pool controllers on the same Home Assistant instance. Each gets unique entity IDs based on the API URL.

4. **SSL/TLS Security**: SSL certificate verification is enabled by default (`verify_ssl=True`). Only disable for self-signed certificates in trusted networks.

5. **Fault Tolerance**: DMX scene updates and other non-critical operations are fault-tolerant and won't crash the integration if they fail.

6. **Calibration History**: The integration parses calibration history from the controller API, handling various date formats and edge cases.

7. **Version Consistency**: Keep version numbers in sync across `manifest.json`, `const.py`, and `docs/RELEASE_NOTES.md`.

8. **Code Quality**: Always run `ruff check --fix` before committing. The integration maintains 0 ruff errors.

9. **Home Assistant Compatibility**: Integration requires HA 2026.3.0+ and is tested against HA 2026.3.x. Use modern type annotations (`X | None` not `Optional[X]`) and `collections.abc` imports.

10. **Recovery Behavior**: When connection is lost, the integration attempts auto-recovery with exponential backoff (10s → 300s max) for up to 10 attempts. After max attempts, manual intervention is required.

11. **External API Package**: `api.py`, `utils_rate_limiter.py`, `utils_sanitizer.py`, `const_api.py`, and `const_devices.py` no longer exist as local files. All are provided by `violet-poolController-api` (PyPI). Import from `violet_poolcontroller_api.*`.

12. **Diagnostics**: The integration supports Home Assistant's built-in diagnostics download (`diagnostics.py`). Sensitive fields are redacted automatically. Access via HA UI → Devices → Download diagnostics.

13. **ZeroConf Discovery**: Controllers are auto-discovered on the local network via `discovery.py`. Manually adding a controller via the config flow remains supported.
