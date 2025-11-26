# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for the **Violet Pool Controller** by PoolDigital GmbH & Co. KG. It enables local polling-based control and monitoring of pool systems including pumps, heaters, solar, chemical dosing, lighting, and covers.

## Development Commands

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=custom_components/violet_pool_controller

# Lint code (uses ruff)
ruff check custom_components/

# Type checking
mypy custom_components/violet_pool_controller/
```

## Testing with VS Code Dev Container

The project supports VS Code Remote Containers for development:
1. Open in VS Code with Remote - Containers extension
2. Reopen in Container when prompted
3. Access Home Assistant at `http://localhost:8123`

## Architecture

### Core Module Structure (`custom_components/violet_pool_controller/`)

- **`__init__.py`** - Integration entry point. Handles setup, config entry migration, platform loading, and service registration. Loads these platforms: `sensor`, `binary_sensor`, `switch`, `climate`, `cover`, `number`.

- **`api.py`** - HTTP client (`VioletPoolAPI`) for controller communication. Implements rate limiting, retry logic with exponential backoff, and all API endpoints (`/getReadings`, `/setFunctionManually`, `/setConfig`, etc.).

- **`device.py`** - Contains `VioletPoolControllerDevice` (device representation with auto-recovery) and `VioletPoolDataUpdateCoordinator` (Home Assistant's data update coordinator pattern). Handles smart failure logging with throttling and automatic connection recovery.

- **`entity.py`** - Base entity class `VioletPoolControllerEntity` extending `CoordinatorEntity`. Provides helper methods for data access (`get_value`, `get_float_value`, `get_bool_value`) and state interpretation (`interpret_state_as_bool`).

- **`config_flow.py`** - UI-based configuration flow. Supports feature selection and dynamic sensor discovery.

### Constants Organization (Modular)

- **`const.py`** - Central hub re-exporting all constants plus integration-level config (DOMAIN, version, configuration keys)
- **`const_api.py`** - API endpoints, action constants (`ACTION_ON`, `ACTION_OFF`, etc.), rate limiting parameters
- **`const_devices.py`** - Device parameter templates for switches/controls
- **`const_sensors.py`** - Sensor definitions, unit mappings, feature-to-sensor mappings
- **`const_features.py`** - Feature flags and feature groups

### Entity Platforms

- **`sensor.py`** - Temperature, water chemistry (pH, ORP, chlorine), analog inputs, system diagnostics
- **`binary_sensor.py`** - Digital input states, system alarms
- **`switch.py`** - 3-state switches (ON/OFF/AUTO) for pump, heater, solar, dosing, DMX scenes, extension relays
- **`climate.py`** - Thermostat entities for heater and solar control
- **`cover.py`** - Pool cover control with string-state handling
- **`number.py`** - Target value entities (temperature setpoints, pH/ORP targets)

### Services

Services defined in `services.yaml` and registered in `services.py`:
- `control_pump` - Pump control with speed settings
- `smart_dosing` - Manual/automatic chemical dosing
- `manage_pv_surplus` - PV surplus mode control
- `control_dmx_scenes` - DMX lighting scenes
- `set_light_color_pulse` - Pool light color pulse
- `manage_digital_rules` - Digital input rules
- `test_output` - Output test mode for diagnostics

### Key Patterns

1. **Coordinator Pattern**: All entities use `VioletPoolDataUpdateCoordinator` for synchronized data updates
2. **Rate Limiting**: API requests go through a global rate limiter (`utils_rate_limiter.py`) to protect the controller
3. **3-State Switches**: Pool devices support ON (1), OFF (0), and AUTO (2) modes via `STATE_MAP`
4. **Multi-Controller Support**: Unique identifiers use `{api_url}_{device_id}` format

## API Communication

The controller exposes a JSON API at endpoints like:
- `GET /getReadings?ALL` - All sensor data
- `GET /setFunctionManually?{payload}` - Control outputs (pump, heater, etc.)
- `POST /setConfig` - Update configuration
- `GET /getConfig?{keys}` - Fetch configuration values

## Translation Files

Located in `translations/` - supports: de, en, es, fr, it, nl, pl, pt, ru, zh

## Version

Current version: 0.2.0-beta.3 (defined in `manifest.json` and `const.py`)
