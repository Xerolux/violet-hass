# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for the **Violet Pool Controller** by PoolDigital GmbH & Co. KG. It enables local polling-based control and monitoring of pool systems including pumps, heaters, solar, chemical dosing, lighting, and covers.

**Current Version**: `1.0.3-beta.3` (defined in `manifest.json` and `const.py`)
**IoT Class**: `local_polling`
**Minimum HA Version**: `2025.12.0` (tested against HA 2026.x)
**ZeroConf Discovery**: Enabled for `violet*` device names and `_violet-controller._tcp.local.`

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
pytest tests/test_services.py -v
pytest tests/test_error_handler.py -v

# Run with coverage
pytest --cov=custom_components/violet_pool_controller --cov-report=html

# Run single test function
pytest tests/test_api.py::test_function_name -v
```

**Test Configuration** (`pytest.ini`):
- `asyncio_mode = auto` - Automatic async/await handling
- `addopts = -p no:socket` - Don't block sockets (required for Home Assistant)

**Important**: The test suite includes a thread-safety workaround in `conftest.py` that patches `threading.enumerate()` to filter out Home Assistant's `_run_safe_shutdown_loop` threads for compatibility with newer HA versions.

## Architecture

### Core Module Structure (`custom_components/violet_pool_controller/`)

#### Main Components

- **`__init__.py`** - Integration entry point. Handles setup, config entry migration, platform loading, and service registration. Loads these platforms: `sensor`, `binary_sensor`, `switch`, `climate`, `cover`, `number`, `select`.

- **`api.py`** - HTTP client (`VioletPoolAPI`) for controller communication. Implements:
  - Token bucket rate limiting with priority queue (4 priority levels)
  - Circuit breaker integration for resilient calls
  - Retry logic with exponential backoff
  - SSL/TLS certificate verification (configurable via `verify_ssl` parameter)
  - All API endpoints (`/getReadings`, `/setFunctionManually`, `/setConfig`, etc.)
  - Basic authentication support
  - Timeout handling with granular connection timeouts (80% of total timeout for connection/socket)

- **`device.py`** - Contains two main classes:
  - `VioletPoolControllerDevice`: Device representation with auto-recovery
  - `VioletPoolDataUpdateCoordinator`: Home Assistant's data update coordinator pattern
  - Smart failure logging with throttling (5-minute intervals)
  - Automatic connection recovery with exponential backoff
  - Connection health metrics tracking (latency history, rolling window of 60 samples)
  - **Thread Safety**: Uses two locks with documented ordering:
    - `_api_lock`: Protects API calls and data updates
    - `_recovery_lock`: Protects recovery state and attempts
    - **Never acquire locks in nested order** - see `device.py:42-58` for full documentation

- **`entity.py`** - Base entity class `VioletPoolControllerEntity` extending `CoordinatorEntity`. Provides helper methods:
  - `get_value()` - Safe data access with fallback
  - `get_float_value()` - Float conversion with error handling
  - `get_bool_value()` - Boolean conversion
  - `interpret_state_as_bool()` - Smart state interpretation (uses pre-compiled regex patterns)

- **`config_flow.py`** - UI-based configuration flow (1200+ lines) supporting:
  - Initial setup wizard
  - Feature selection
  - Dynamic sensor discovery
  - Duplicate detection
  - Multi-controller support
  - Reconfiguration flow

#### Resilience & Error Handling Modules

- **`circuit_breaker.py`** - Circuit breaker pattern for resilient API calls:
  - States: `CLOSED` (normal) → `OPEN` (failing) → `HALF_OPEN` (testing recovery)
  - Automatic state transitions based on failure/success thresholds
  - Prevents cascade failures when controller is unreachable

- **`error_handler.py`** - Comprehensive error classification and handling:
  - `VioletErrorCodes` - Categorized error code constants
  - Custom exception types for different failure modes
  - Consistent error classification across the integration

- **`diagnostics.py`** - Home Assistant diagnostics support:
  - Exposes integration state for HA diagnostics panel
  - Redacts sensitive information (credentials, IPs)

- **`discovery.py`** - ZeroConf discovery handler:
  - Discovers Violet controllers on the local network
  - Handles `_violet-controller._tcp.local.` service type

#### Utility Modules

- **`utils_rate_limiter.py`** - Global rate limiter for API protection:
  - Token bucket algorithm (10 max requests per 1.0s window, 3 burst)
  - Priority queue with 4 levels (critical, high, normal, low)
  - Request throttling to prevent controller overload
  - Cleanup of request history every 5 minutes

- **`utils_sanitizer.py`** - Input sanitization utilities:
  - Protection against XSS, SQL injection, command injection
  - Path traversal prevention
  - Pattern-based validation (alphanumeric, numeric, etc.)
  - HTML escaping for user inputs

- **`error_codes.py`** - Comprehensive error code mappings (23KB):
  - Maps controller error codes to human-readable messages
  - Severity classification (info, warning, critical)
  - Error type categorization (MESSAGE, ALERT, ERROR)

#### Constants Organization (Modular)

- **`const.py`** - Central hub (94 lines) re-exporting all constants plus integration-level config:
  - `DOMAIN`, `INTEGRATION_VERSION`, `MANUFACTURER`
  - Configuration keys including `CONF_VERIFY_SSL`, `CONF_ENABLE_DIAGNOSTIC_LOGGING`
  - Default values for all settings
  - Pool configuration (types, disinfection methods)

- **`const_api.py`** - API-related constants:
  - Endpoint paths (all `/get*` and `/set*` routes)
  - Action constants (`ACTION_ON`, `ACTION_OFF`, `ACTION_AUTO`)
  - Rate limiting parameters
  - Request/response keys

- **`const_devices.py`** - Device parameter templates (308 lines):
  - Switch device definitions with full state mappings
  - `VioletState` class for intelligent state interpretation
  - Control parameters for pumps, heaters, etc.
  - Extension relay configurations (2 banks × 8 relays)
  - `DEVICE_STATE_MAPPING` for all 7 states (0-6)

- **`const_sensors.py`** - Sensor definitions:
  - Sensor key mappings
  - Unit of measurement mappings
  - Feature-to-sensor mappings
  - Device class assignments

- **`const_features.py`** - Feature flags and feature groups (489 lines):
  - Available features (14 total): heating, solar, ph_control, chlorine_control, flocculation, cover_control, backwash, pv_surplus, filter_control, water_level, water_refill, led_lighting, digital_inputs, extension_outputs
  - Feature groupings for UI
  - Feature dependencies

#### Entity Platforms

- **`sensor.py`** - Sensor platform using modular `sensor_modules/` architecture:
  - Temperature sensors (pool, solar, ambient)
  - Water chemistry (pH, ORP, chlorine, conductivity)
  - Analog inputs (AI1-AI8)
  - System diagnostics (runtime, error codes)
  - Calibration history
  - **Diagnostic sensors**: connection latency, system health %, API request rate, last event age

- **`binary_sensor.py`** - Binary sensor entities:
  - Device states: PUMP, SOLAR, HEATER, LIGHT, BACKWASH, REFILL, ECO, PVSURPLUS
  - Digital inputs (INPUT1-12, INPUT_CE1-4)
  - Diagnostic problem sensors
  - System alarms and connection status

- **`switch.py`** - 3-state switch entities (ON/OFF/AUTO):
  - PUMP, HEATER, SOLAR, LIGHT controls
  - Dosing systems (pH-, pH+, Chlorine, Flocculant)
  - 12 DMX scenes
  - 16 extension relays (2 banks × 8)
  - 7 digital rules
  - Multi-state support (0-6) with composite state parsing

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
  - Dosing canister volumes (4 chemicals)
  - Dosing parameters

- **`select.py`** - **NEW**: Select entity platform for mode selection:
  - Mode control (ON/AUTO/OFF) for pump, heater, solar, light, dosing systems
  - Alternative to switch entities for cleaner HA UI integration

#### Sensor Submodules Package

Located at `sensor_modules/`:

- **`__init__.py`** - Exports all sensor classes
- **`base.py`** - `VioletSensor` base class with common functionality
- **`generic.py`** - Generic sensor implementation for standard readings
- **`monitoring.py`** - Monitoring sensors (connection latency, health %, request rates)
- **`specialized.py`** - Specialized sensors (error codes, status parsing)

#### Config Flow Utilities Package

Located at `config_flow_utils/`:

- **`__init__.py`** - Package exports
- **`constants.py`** - Config flow specific constants
- **`sensor_helper.py`** - Dynamic sensor discovery helpers
- **`validators.py`** - Input validation for config flow fields

#### Services

Services defined in `services.yaml` and registered in `services.py` (58KB):

**Device Control Services**:
- **`control_pump`** - Speed control (0-3), force off, eco, boost, auto, duration
- **`smart_dosing`** - Manual dosing (pH-, pH+, Chlorine, Flocculant), automatic mode, duration
- **`manage_pv_surplus`** - Enable/disable photovoltaic surplus usage
- **`control_dmx_scenes`** - Scenes (all_on, all_off, all_auto, sequence, party_mode)
- **`set_light_color_pulse`** - Pool light color pulse animation
- **`manage_digital_rules`** - Digital input rule management (trigger, lock, unlock)
- **`test_output`** - Output test mode for diagnostics

**Diagnostic Services**:
- **`export_diagnostic_logs`** - Export integration logs (configurable line count)
- **`get_connection_status`** - Detailed connection metrics (latency, health, request rate)
- **`get_error_summary`** - Error summary with recovery suggestions
- **`test_connection`** - Connection test with diagnostic info
- **`clear_error_history`** - Clear error history after recovery

### Key Design Patterns

1. **Coordinator Pattern**: All entities use `VioletPoolDataUpdateCoordinator` for synchronized data updates. `PARALLEL_UPDATES = 0` enables concurrent platform updates.

2. **Circuit Breaker**: `circuit_breaker.py` wraps API calls with automatic failure detection and recovery (CLOSED → OPEN → HALF_OPEN states), preventing cascade failures.

3. **Rate Limiting**: API requests go through `utils_rate_limiter.py` using token bucket algorithm (10 req/s, 3 burst, 4 priority levels).

4. **Multi-State Switches**: Pool devices support multiple states (0-6):
   - `0` = AUTO_OFF (automatic control, currently off)
   - `1` = AUTO_ON (automatic control, currently on)
   - `2` = AUTO_ACTIVE (automatic control with timing)
   - `3` = AUTO_ACTIVE_TIMER (automatic control with timer)
   - `4` = MANUAL_ON (manual forced on)
   - `5` = AUTO_WAITING (automatic control, waiting for conditions)
   - `6` = MANUAL_OFF (manual forced off)

   **Important**: States may include descriptive suffixes (e.g., `"3|PUMP_ANTI_FREEZE"`) which are pipe-separated composite states. The numeric part is the actual state; the suffix provides operational context (e.g., frost protection mode). The `VioletState` class in `const_devices.py` handles interpretation, including German translations.

5. **Modular Sensor Architecture**: Sensors are organized in `sensor_modules/` package with specialized subclasses for generic, monitoring, and specialized sensor types.

6. **Multi-Controller Support**:
   - Unique identifiers use `{entry_id}` format
   - Dynamic device info generation
   - Separate data coordinators per controller

7. **Auto-Recovery**:
   - Automatic reconnection on connection loss
   - Exponential backoff for retries (10s base, max 300s delay)
   - Smart error logging with throttling (5-minute intervals)
   - Max 10 recovery attempts before manual intervention required
   - Poll history tracking (deque, maxlen=1000) with consecutive failure counting

8. **Input Sanitization**:
   - All user inputs validated through `InputSanitizer`
   - Protection against XSS, SQL injection, command injection, path traversal
   - Safe handling of API parameters

9. **SSL/TLS Security**:
   - SSL certificate verification enabled by default (`verify_ssl=True`)
   - Configurable for self-signed certificates (generates warning)
   - Proper SSL context handling in API requests

10. **Diagnostic Logging**:
    - Configurable via `CONF_ENABLE_DIAGNOSTIC_LOGGING` without reloading the integration
    - Applied through module-level logger configuration
    - Connection health metrics: latency (rolling 60-sample window), system health %, API request rate, last event age

## API Communication

The Violet Pool Controller exposes a JSON-based HTTP API:

### Endpoints

- **`GET /getReadings?ALL`** - Retrieve all sensor data (primary polling endpoint)
- **`GET /setFunctionManually?{payload}`** - Control outputs (pump, heater, solar, dosing, etc.)
- **`POST /setConfig`** - Update configuration values
- **`GET /getConfig?{keys}`** - Fetch specific configuration values
- **`GET /getCalibRawValues`** - Raw calibration values
- **`GET /getCalibHistory`** - Calibration history (various date formats supported)
- **`GET /restoreOldCalib`** - Restore previous calibration
- **`GET /getHistory`** - Historical data
- **`GET /getWeatherdata`** - Weather information
- **`GET /getOverallDosing`** - Dosing statistics
- **`GET /getOutputstates`** - Output states
- **`POST /setTargetValues`** - Set target values
- **`POST /setDosingParameters`** - Dosing parameters
- **`GET /setOutputTestmode`** - Test mode activation

### Request Patterns

- All requests are rate-limited using token bucket algorithm (10 req/s, 3 burst)
- Circuit breaker wraps all API calls for resilience
- Retry logic with exponential backoff (3 attempts by default)
- Timeout: 10 seconds total, with 8-second connection/socket timeouts (configurable)
- SSL certificate verification: enabled by default, configurable
- Responses are JSON-formatted
- All user inputs are sanitized through `InputSanitizer` before API calls
- Basic authentication supported via `username`/`password` config options

## Testing Infrastructure

### Test Suite Organization

Located in `tests/` (20 test files):

- **`conftest.py`** - Pytest fixtures and test configuration (includes `getReadings_spec.json` spec)
- **`test_api.py`** - API communication tests (rate limiting, timeout, error handling)
- **`test_config_flow.py`** - Configuration flow tests (duplicate detection, validation)
- **`test_device.py`** - Device and coordinator tests
- **`test_entity_state.py`** - Entity state interpretation tests
- **`test_integration.py`** - Full integration tests
- **`test_sanitizer.py`** - Input sanitization tests
- **`test_services.py`** - Service handler tests
- **`test_cover.py`** - Cover entity tests
- **`test_discovery.py`** - ZeroConf discovery handler tests
- **`test_error_handler.py`** - Error handling and circuit breaker tests
- **`test_diagnostic_services.py`** - Diagnostic service tests
- **`test_offline_scenarios.py`** - Offline/connection loss handling
- **`test_platform_errors.py`** - Platform error handling tests
- **`test_reconfigure_flow.py`** - Reconfiguration flow tests
- **`test_security_fixes.py`** - Security validation tests
- **`test_sensor_generic.py`** - Generic sensor module tests
- **`test_improvements.py`** - Feature improvement tests
- **`test_translations.py`** - Translation validation tests
- **`test_type_hints.py`** - Type hint validation tests

### Test Configuration

**`pytest.ini`** settings:
```ini
[pytest]
asyncio_mode = auto
addopts = -p no:socket
```

### CI/CD Testing

GitHub workflow `.github/workflows/validate.yml` runs:
- Ruff linting
- Mypy type checking
- Full test suite with pytest
- Tests against Home Assistant 2025.12.0+
- Python 3.13 environment

## Translation Files

Located in `custom_components/violet_pool_controller/translations/`:

- **Primary languages**: `de.json` (German - primary), `en.json` (English)
- **Additional languages**: `es.json`, `fr.json`, `it.json`, `nl.json`, `pl.json`, `pt.json`, `ru.json`, `zh.json`

Translation files cover:
- Configuration flow UI
- Entity names and descriptions
- Service descriptions
- Error messages
- German state descriptions for switches and sensors (key feature as of 1.0.3-beta.3)

## Project Structure

```
violet-hass/
├── custom_components/
│   └── violet_pool_controller/      # Main integration code
│       ├── __init__.py               # Entry point (platforms: sensor, binary_sensor,
│       │                             #   switch, climate, cover, number, select)
│       ├── api.py                    # API client with circuit breaker integration
│       ├── circuit_breaker.py        # Circuit breaker pattern for resilience
│       ├── error_handler.py          # Error classification and custom exceptions
│       ├── diagnostics.py            # HA diagnostics panel support
│       ├── discovery.py              # ZeroConf discovery handler
│       ├── device.py                 # Device & coordinator (650+ lines)
│       ├── entity.py                 # Base entity class (330+ lines)
│       ├── config_flow.py            # Config flow (1200+ lines)
│       ├── const.py                  # Central constants hub (re-exports)
│       ├── const_api.py              # API endpoints and actions
│       ├── const_devices.py          # Device params, VioletState class, state mappings
│       ├── const_sensors.py          # Sensor definitions and units
│       ├── const_features.py         # Feature flags (14 features)
│       ├── sensor.py                 # Sensor platform (uses sensor_modules/)
│       ├── binary_sensor.py          # Binary sensor platform
│       ├── switch.py                 # 3-state switch platform
│       ├── climate.py                # Climate/thermostat platform
│       ├── cover.py                  # Cover platform
│       ├── number.py                 # Number input platform
│       ├── select.py                 # Mode selection platform (NEW)
│       ├── services.py               # Service handlers (58KB)
│       ├── services.yaml             # Service definitions (12 services)
│       ├── utils_rate_limiter.py     # Token bucket rate limiter
│       ├── utils_sanitizer.py        # Input sanitization
│       ├── error_codes.py            # Controller error code mappings
│       ├── quality_scale.yaml        # HA quality scale metrics
│       ├── icons.json                # Custom icons
│       ├── manifest.json             # Integration manifest
│       ├── strings.json              # UI strings
│       ├── sensor_modules/           # Modular sensor architecture
│       │   ├── __init__.py           # Exports all sensor classes
│       │   ├── base.py               # VioletSensor base class
│       │   ├── generic.py            # Generic sensor implementation
│       │   ├── monitoring.py         # Monitoring sensors (latency, health, rates)
│       │   └── specialized.py        # Specialized sensors (error codes, status)
│       ├── config_flow_utils/        # Config flow helpers
│       │   ├── __init__.py
│       │   ├── constants.py          # Config flow constants
│       │   ├── sensor_helper.py      # Dynamic sensor discovery
│       │   └── validators.py         # Input validators
│       └── translations/             # 10 language files
│           ├── de.json               # German (primary)
│           ├── en.json               # English
│           └── es/fr/it/nl/pl/pt/ru/zh.json
├── tests/                            # 20 test files
│   ├── conftest.py                   # Pytest configuration & fixtures
│   ├── getReadings_spec.json          # API response specification
│   ├── test_api.py                   # API tests
│   ├── test_config_flow.py           # Config flow tests
│   ├── test_device.py                # Device tests
│   ├── test_entity_state.py          # Entity state tests
│   ├── test_integration.py           # Integration tests
│   ├── test_sanitizer.py             # Sanitizer tests
│   ├── test_services.py              # Service handler tests
│   ├── test_cover.py                 # Cover entity tests
│   ├── test_discovery.py             # Discovery tests
│   ├── test_error_handler.py         # Error handler tests
│   ├── test_diagnostic_services.py   # Diagnostic service tests
│   ├── test_offline_scenarios.py     # Offline handling tests
│   ├── test_platform_errors.py       # Platform error tests
│   ├── test_reconfigure_flow.py      # Reconfiguration flow tests
│   ├── test_security_fixes.py        # Security tests
│   ├── test_sensor_generic.py        # Generic sensor tests
│   ├── test_improvements.py          # Feature improvement tests
│   ├── test_translations.py          # Translation validation tests
│   └── test_type_hints.py            # Type hint tests
├── scripts/                          # Development scripts
│   ├── setup-test-env.sh             # Test environment setup
│   └── run-tests.sh                  # Test runner
├── blueprints/                       # Home Assistant blueprints
│   └── automation/                   # Automation blueprints
├── Dashboard/                        # Dashboard examples and templates
├── docs/                             # Documentation
│   ├── archive/                      # Archived documentation
│   └── help/                         # Help documentation
├── .github/                          # GitHub workflows
│   └── workflows/                    # CI/CD pipelines (13 workflows)
├── CLAUDE.md                         # This file
├── README.md                         # Project README
├── requirements.txt                  # Runtime dependencies
├── requirements-dev.txt              # Development dependencies
└── pytest.ini                        # Pytest configuration
```

## Development Best Practices

### Code Style

1. **Follow PEP 8**: Use ruff for linting and auto-formatting. Always run `ruff check --fix` before committing. The integration maintains 0 ruff errors.
2. **Type Hints**: Use type hints throughout (checked with mypy). Use modern annotations (`X | None` not `Optional[X]`) and `collections.abc` imports.
3. **Docstrings**: Document all public classes and methods.
4. **Constants**: Use the correct modular `const_*.py` file based on category (API → `const_api.py`, sensors → `const_sensors.py`, etc.).

### Error Handling

1. **Never fail silently**: Log all errors appropriately using the integration's logging patterns.
2. **Use try-except**: Wrap API calls and data parsing in try-except blocks.
3. **Graceful degradation**: Non-critical operations (DMX, diagnostics) are fault-tolerant and won't crash the integration.
4. **Circuit breaker**: Use the circuit breaker pattern for resilient API calls.
5. **User feedback**: Provide clear error messages in the UI.

### Testing

1. **Write tests first**: Follow TDD where possible.
2. **Test coverage**: Aim for >80% coverage.
3. **Mock external calls**: Use fixtures from `conftest.py` to mock API responses.
4. **Test edge cases**: Include offline scenarios, error conditions, composite states, and boundary values.
5. **Use `getReadings_spec.json`**: Reference the API spec for realistic test data.

### Security

1. **Sanitize inputs**: Use `InputSanitizer` for all user inputs from config flow and services.
2. **Validate data**: Check API responses before processing.
3. **No hardcoded secrets**: Use configuration for credentials.
4. **Rate limiting**: Respect API rate limits to prevent controller overload.

### Performance

1. **Batch requests**: Use coordinator pattern to batch data updates.
2. **Parallel platform updates**: `PARALLEL_UPDATES = 0` for concurrent updates.
3. **Async operations**: Use asyncio for all I/O operations.
4. **Pre-compiled patterns**: Use pre-compiled regex patterns (see `entity.py`).
5. **Minimize logging**: Use appropriate log levels; diagnostic logging is configurable.

## GitHub Workflows

Located in `.github/workflows/` (13 workflows):

- **`validate.yml`** - Code validation on push/PR (ruff, mypy, pytest)
- **`release.yml`** - Automated release creation
- **`claude.yml`** - Claude Code integration
- **`claude-code-review.yml`** - Automated code review
- **`security.yml`** - Security scanning
- **`pr-management.yml`** - PR automation
- **`automerge.yml`** - Automatic PR merging
- **`maintenance.yml`** - Repository maintenance
- **`labeler.yml`** - Automatic PR labeling
- **`stale.yml`** - Stale issue/PR management
- **`status-check-labels.yml`** - Status check labeling
- **`auto-label-pr.yml`** - Auto PR labeling
- **`wiki-sync.yml`** - Wiki synchronization

## Common Tasks for AI Assistants

### Adding a New Sensor

1. Add sensor definition to `const_sensors.py`
2. Create entity class in the appropriate `sensor_modules/` submodule
3. Export from `sensor_modules/__init__.py`
4. Register in `sensor.py`
5. Add translation strings to `strings.json` and all `translations/*.json` files
6. Write tests in `tests/test_sensor_generic.py` or `tests/test_integration.py`

### Adding a New Service

1. Define service in `services.yaml`
2. Implement handler in `services.py`
3. Register in `__init__.py` `async_setup_entry()`
4. Add translation strings to `strings.json` and translation files
5. Write service tests in `tests/test_services.py` or `tests/test_diagnostic_services.py`

### Adding a New Platform

1. Create `platform_name.py` in `custom_components/violet_pool_controller/`
2. Add platform to `PLATFORMS` list in `__init__.py`
3. Create entity classes extending `VioletPoolControllerEntity`
4. Add translation strings
5. Write tests in a new `tests/test_platform_name.py`

### Fixing API Issues

1. Check `api.py` for endpoint definitions
2. Review circuit breaker in `circuit_breaker.py`
3. Review rate limiting in `utils_rate_limiter.py`
4. Test with `tests/test_api.py`
5. Check error handling in `error_handler.py`
6. Test offline scenarios with `tests/test_offline_scenarios.py`

### Updating Constants

1. Identify correct `const_*.py` file based on category
2. Add constant with clear naming
3. Update re-exports in `const.py` if needed
4. Document usage in docstrings

### Adding a New Feature Flag

1. Add feature constant to `const_features.py`
2. Associate relevant sensors/switches with the feature
3. Update `config_flow.py` and `config_flow_utils/` for UI presentation
4. Add translation strings

## Dependencies

**Runtime** (from `requirements.txt`):
- `homeassistant>=2025.12.0` - Minimum Home Assistant version (HA 2026 ready)
- `aiohttp>=3.10.0` - Async HTTP client
- `voluptuous>=0.14.2` - Data validation

**Development** (from `requirements-dev.txt`):
- `ruff>=0.1.0` - Linter and formatter
- `mypy>=1.7.0` - Static type checker
- `pytest>=7.4.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage plugin
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-homeassistant-custom-component>=0.13.0` - HA test helpers

## Important Notes

1. **Thread Safety**: The integration uses two locks (`_api_lock`, `_recovery_lock`) with documented ordering. Always read `device.py:42-58` before modifying concurrent code to prevent deadlocks. **Never acquire these locks in nested order.**

2. **State Handling**: Switches and selects support states 0-6 with specific meanings:
   - States `0`, `5`, `6` = Device OFF (different automatic/manual modes)
   - States `1`, `2`, `3`, `4` = Device ON (different automatic/manual modes)
   - Composite states like `"3|PUMP_ANTI_FREEZE"` — numeric part is state, suffix is operational detail
   - All states and their German translations are defined in `const_devices.py` via `VioletState` class

3. **VioletState Class**: The `VioletState` class in `const_devices.py` provides intelligent state interpretation with `mode`, `is_active`, `description`, `display_mode`, and `icon` properties. Use this for all switch/select state logic.

4. **Multi-Controller**: The integration supports multiple pool controllers on the same Home Assistant instance. Entity IDs use `{entry_id}` for unique identification.

5. **SSL/TLS Security**: SSL certificate verification is enabled by default (`verify_ssl=True`). Only disable for self-signed certificates in trusted networks.

6. **Circuit Breaker**: The circuit breaker in `circuit_breaker.py` automatically stops API calls when the controller is unreachable and resumes when it recovers. Do not bypass this pattern for resilience.

7. **Fault Tolerance**: DMX scene updates, diagnostic services, and other non-critical operations are fault-tolerant and won't crash the integration if they fail.

8. **Calibration History**: The integration parses calibration history from the controller API, handling various date formats and edge cases.

9. **Version Consistency**: Keep version numbers in sync across `manifest.json`, `const.py`, and `docs/RELEASE_NOTES.md`.

10. **Code Quality**: Always run `ruff check --fix` before committing. The integration maintains 0 ruff errors.

11. **Home Assistant Compatibility**: Integration requires HA 2025.12.0+ and is tested against HA 2026.x. Use modern type annotations (`X | None` not `Optional[X]`) and `collections.abc` imports.

12. **Recovery Behavior**: When connection is lost, the integration attempts auto-recovery with exponential backoff (10s → 300s max) for up to 10 attempts. After max attempts, manual intervention is required. Poll history is tracked in a deque (maxlen=1000).

13. **Select Platform**: The `select.py` platform was added to provide cleaner mode selection (ON/AUTO/OFF) as an alternative to the 3-state switch pattern. When adding new mode-selectable devices, prefer `select.py` for simple ON/AUTO/OFF controls.

14. **Diagnostic Sensors**: Connection latency, system health %, API request rate, and last event age are tracked as sensors via `sensor_modules/monitoring.py`. These use a rolling window of 60 latency samples for accurate reporting.

15. **Sensor Module Architecture**: When adding new sensors, place them in the appropriate `sensor_modules/` submodule:
    - **`generic.py`**: Standard readings (temperature, chemistry, analog inputs)
    - **`monitoring.py`**: Connection and performance metrics
    - **`specialized.py`**: Complex sensors requiring custom parsing (error codes, status)
