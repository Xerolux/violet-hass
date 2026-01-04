# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for the **Violet Pool Controller** by PoolDigital GmbH & Co. KG. It enables local polling-based control and monitoring of pool systems including pumps, heaters, solar, chemical dosing, lighting, and covers.

**Current Version**: `1.0.7-alpha.2` (defined in `manifest.json` and `const.py`)

## Development Commands

### Test Environment Setup (One-Time)

```bash
# Automated setup using script
./scripts/setup-test-env.sh

# This creates a virtual environment and installs:
# - Home Assistant 2025.1.4
# - pytest and test dependencies
# - Development tools (ruff, mypy)
```

### Running Tests

```bash
# Option 1: Using the test runner script (recommended)
./scripts/run-tests.sh

# Option 2: Manual execution
source activate-test-env.sh
pytest tests/ -v

# Run specific test suites
pytest tests/test_api.py -v              # API tests
pytest tests/test_config_flow.py -v      # Config flow tests
pytest tests/test_device.py -v           # Device tests
pytest tests/test_integration.py -v      # Integration tests

# Run with coverage
pytest --cov=custom_components/violet_pool_controller --cov-report=html
```

### Code Quality

```bash
# Lint code (uses ruff)
ruff check custom_components/

# Auto-fix linting issues
ruff check --fix custom_components/

# Type checking
mypy custom_components/violet_pool_controller/
```

### Testing with VS Code Dev Container

The project supports VS Code Remote Containers for development:
1. Open in VS Code with Remote - Containers extension
2. Reopen in Container when prompted
3. Access Home Assistant at `http://localhost:8123`

## Architecture

### Core Module Structure (`custom_components/violet_pool_controller/`)

#### Main Components

- **`__init__.py`** - Integration entry point. Handles setup, config entry migration, platform loading, and service registration. Loads these platforms: `sensor`, `binary_sensor`, `switch`, `climate`, `cover`, `number`.

- **`api.py`** - HTTP client (`VioletPoolAPI`) for controller communication. Implements:
  - Token bucket rate limiting
  - Priority queue for API requests
  - Retry logic with exponential backoff
  - All API endpoints (`/getReadings`, `/setFunctionManually`, `/setConfig`, etc.)
  - Timeout handling and error recovery

- **`device.py`** - Contains two main classes:
  - `VioletPoolControllerDevice`: Device representation with auto-recovery
  - `VioletPoolDataUpdateCoordinator`: Home Assistant's data update coordinator pattern
  - Smart failure logging with throttling
  - Automatic connection recovery

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

#### Utility Modules

- **`utils_rate_limiter.py`** - Global rate limiter for API protection:
  - Token bucket algorithm
  - Priority queue implementation
  - Request throttling to prevent controller overload

- **`utils_sanitizer.py`** - Input sanitization utilities:
  - Protection against XSS, SQL injection, command injection
  - Path traversal prevention
  - Pattern-based validation (alphanumeric, numeric, etc.)
  - HTML escaping for user inputs

- **`error_codes.py`** - Comprehensive error code mappings:
  - Maps controller error codes to human-readable messages
  - Severity classification (info, warning, critical)
  - Error type categorization (MESSAGE, ALERT, ERROR)

#### Constants Organization (Modular)

- **`const.py`** - Central hub re-exporting all constants plus integration-level config:
  - `DOMAIN`, `INTEGRATION_VERSION`, `MANUFACTURER`
  - Configuration keys (`CONF_API_URL`, `CONF_USERNAME`, etc.)
  - Default values for all settings
  - Pool configuration (types, disinfection methods)

- **`const_api.py`** - API-related constants:
  - Endpoint paths
  - Action constants (`ACTION_ON`, `ACTION_OFF`, `ACTION_AUTO`)
  - Rate limiting parameters
  - Request/response keys

- **`const_devices.py`** - Device parameter templates:
  - Switch device definitions
  - Control parameters for pumps, heaters, etc.
  - Extension relay configurations

- **`const_sensors.py`** - Sensor definitions:
  - Sensor key mappings
  - Unit of measurement mappings
  - Feature-to-sensor mappings
  - Device class assignments

- **`const_features.py`** - Feature flags and feature groups:
  - Available features (pump, heater, solar, dosing, etc.)
  - Feature groupings for UI
  - Feature dependencies

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

2. **Rate Limiting**: API requests go through a global rate limiter (`utils_rate_limiter.py`) using token bucket algorithm to protect the controller from overload.

3. **Multi-State Switches**: Pool devices support multiple states:
   - `0` = AUTO - Standby (automatic control, currently off)
   - `1` = MANUAL ON (manual on)
   - `2` = AUTO - Active (automatic control, currently on)
   - `3` = AUTO - Active with Timer (automatic control with timing)
   - `4` = MANUAL ON - Forced (manual on, forced mode)
   - `5` = AUTO - Waiting (automatic control, waiting for conditions)
   - `6` = MANUAL OFF (manual off)

   Additionally, some states include descriptive suffixes (e.g., `"3|PUMP_ANTI_FREEZE"`) which are parsed to extract operational modes like frost protection.

4. **Multi-Controller Support**:
   - Unique identifiers use `{api_url}_{device_id}` format
   - Dynamic device info generation
   - Separate data coordinators per controller

5. **Auto-Recovery**:
   - Automatic reconnection on connection loss
   - Exponential backoff for retries
   - Smart error logging with throttling

6. **Input Sanitization**:
   - All user inputs validated through `InputSanitizer`
   - Protection against injection attacks
   - Safe handling of API parameters

## API Communication

The Violet Pool Controller exposes a JSON-based HTTP API:

### Endpoints

- **`GET /getReadings?ALL`** - Retrieve all sensor data
- **`GET /setFunctionManually?{payload}`** - Control outputs (pump, heater, solar, dosing, etc.)
- **`POST /setConfig`** - Update configuration values
- **`GET /getConfig?{keys}`** - Fetch specific configuration values

### Request Patterns

- All requests are rate-limited using token bucket algorithm
- Retry logic with exponential backoff (3 attempts by default)
- Timeout: 10 seconds (configurable)
- Responses are JSON-formatted

## Testing Infrastructure

### Test Suite Organization

Located in `tests/`:

- **`conftest.py`** - Pytest fixtures and test configuration
- **`test_api.py`** - API communication tests (rate limiting, timeout, error handling)
- **`test_config_flow.py`** - Configuration flow tests (duplicate detection, validation)
- **`test_device.py`** - Device and coordinator tests
- **`test_entity_state.py`** - Entity state interpretation tests
- **`test_integration.py`** - Full integration tests
- **`test_sanitizer.py`** - Input sanitization tests

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
- Tests against Home Assistant 2024.12.0 and 2025.1.0
- Python 3.12 environment

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
│       ├── __init__.py               # Entry point
│       ├── api.py                    # API client
│       ├── device.py                 # Device & coordinator
│       ├── entity.py                 # Base entity class
│       ├── config_flow.py            # Config flow
│       ├── const*.py                 # Constants (modular)
│       ├── sensor.py                 # Sensor platform
│       ├── binary_sensor.py          # Binary sensor platform
│       ├── switch.py                 # Switch platform
│       ├── climate.py                # Climate platform
│       ├── cover.py                  # Cover platform
│       ├── number.py                 # Number platform
│       ├── services.py               # Service handlers
│       ├── services.yaml             # Service definitions
│       ├── utils_rate_limiter.py     # Rate limiting
│       ├── utils_sanitizer.py        # Input sanitization
│       ├── error_codes.py            # Error code mappings
│       ├── manifest.json             # Integration manifest
│       ├── strings.json              # UI strings
│       └── translations/             # Translations
├── tests/                            # Test suite
│   ├── conftest.py                   # Pytest configuration
│   ├── test_api.py                   # API tests
│   ├── test_config_flow.py           # Config flow tests
│   ├── test_device.py                # Device tests
│   ├── test_entity_state.py          # Entity tests
│   ├── test_integration.py           # Integration tests
│   └── test_sanitizer.py             # Sanitizer tests
├── scripts/                          # Development scripts
│   ├── setup-test-env.sh             # Test environment setup
│   └── run-tests.sh                  # Test runner
├── blueprints/                       # Home Assistant blueprints
│   └── automation/                   # Automation blueprints
├── Dashboard/                        # Dashboard examples
├── docs/                             # Documentation
├── .github/                          # GitHub workflows
│   └── workflows/                    # CI/CD pipelines
├── CLAUDE.md                         # This file
├── README.md                         # Project README
├── CONTRIBUTING.md                   # Contribution guidelines
├── TESTING.md                        # Testing guide
├── TESTING_CHECKLIST.md              # Manual testing checklist
├── CHANGELOG.md                      # Version history
├── RELEASE_NOTES.md                  # Release notes
├── requirements.txt                  # Runtime dependencies
├── requirements-dev.txt              # Development dependencies
└── pytest.ini                        # Pytest configuration
```

## Development Best Practices

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

- **`validate.yml`** - Code validation on push/PR (ruff, mypy, pytest)
- **`release.yml`** - Automated release creation
- **`claude.yml`** - Claude Code integration
- **`claude-code-review.yml`** - Automated code review
- **`security.yml`** - Security scanning
- **`pr-management.yml`** - PR automation
- **`automerge.yml`** - Automatic PR merging
- **`maintenance.yml`** - Repository maintenance
- **`labeler.yml`** - Automatic PR labeling

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

1. Check `api.py` for endpoint definitions
2. Review rate limiting in `utils_rate_limiter.py`
3. Test with `tests/test_api.py`
4. Check error handling and retries

### Updating Constants

1. Identify correct const_*.py file based on category
2. Add constant with clear naming
3. Update imports in `const.py` if needed
4. Document usage in docstrings

## Dependencies

**Runtime** (from `requirements.txt`):
- `aiohttp>=3.8.0` - Async HTTP client

**Development** (from `requirements-dev.txt`):
- `ruff>=0.1.0` - Linter and formatter
- `mypy>=1.7.0` - Static type checker
- `pytest>=7.4.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage plugin
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-homeassistant-custom-component>=0.13.0` - HA test helpers

## Important Notes

1. **State Handling**: Switches support states 0-6 with specific meanings:
   - States 0, 5, 6 = Device OFF (different automatic/manual modes)
   - States 1, 2, 3, 4 = Device ON (different automatic/manual modes)
   - Composite states like `"3|PUMP_ANTI_FREEZE"` provide additional context about operational modes
   - All states are defined in `const_devices.py:DEVICE_STATE_MAPPING`

2. **Multi-Controller**: The integration supports multiple pool controllers on the same Home Assistant instance. Each gets unique entity IDs based on the API URL.

3. **Fault Tolerance**: DMX scene updates and other non-critical operations are fault-tolerant and won't crash the integration if they fail.

4. **Calibration History**: The integration parses calibration history from the controller API, handling various date formats and edge cases.

5. **Version Consistency**: Keep version numbers in sync across `manifest.json`, `const.py`, and `RELEASE_NOTES.md`.
