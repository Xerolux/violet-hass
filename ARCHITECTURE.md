# Architecture Overview

**Violet Pool Controller** – Home Assistant Integration + API Client (Monorepo)

---

## High-Level Structure

```
violet-hass/
├── violet_poolcontroller_api/          # API Package (published to PyPI)
│   └── violet_poolcontroller_api/
│       ├── api.py                      # VioletPoolAPI HTTP client
│       ├── circuit_breaker.py          # Fault tolerance pattern
│       ├── exceptions.py               # VioletPoolAPIError hierarchy
│       ├── parsers.py                  # Data parsing utilities
│       ├── readings.py                 # VioletReadings data class
│       ├── const_api.py                # API endpoints, actions
│       ├── const_devices.py            # Device state mappings
│       ├── utils_rate_limiter.py       # Token bucket rate limiter
│       ├── utils_sanitizer.py          # Input sanitization
│       └── pyproject.toml              # API package build config
│
├── custom_components/violet_pool_controller/    # HA Integration
│   ├── __init__.py                     # Integration entry point
│   ├── device.py                       # Device + Coordinator
│   ├── entity.py                       # Base entity class
│   ├── config_flow.py                  # Config/options UI
│   ├── const.py                        # Constants hub
│   ├── const_sensors.py                # Sensor definitions
│   ├── const_features.py               # Feature flags
│   ├── [entity platforms]/             # sensor, binary_sensor, switch, climate, cover, number, select, light, update, button
│   ├── [services]/                     # service_*.py + service_schemas.py
│   ├── [helpers]/                      # error_handler, diagnostics, discovery, etc.
│   ├── [utilities]/                    # config_flow_utils/, sensor_modules/
│   ├── manifest.json                   # HA integration metadata
│   ├── strings.json                    # UI strings
│   └── translations/                   # Multi-language support (10 languages)
│
├── tests/                              # Test suite
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_*.py                       # 20+ test files
│   └── getReadings_spec.json           # API mock data
│
├── docs/                               # Documentation
│   ├── RELEASE_NOTES.md               # Release changelog
│   └── [other docs]
│
├── CLAUDE.md                           # Developer instructions (you are here)
├── ARCHITECTURE.md                     # This file
├── CONTRIBUTING.md                     # Contribution guidelines
├── README.md                           # Project overview
├── BACKLOG_PROGRESS.md                 # Implementation progress
└── [CI/CD, config files]
```

---

## Core Architecture Patterns

### 1. **Coordinator Pattern** (Data Updates)

```
VioletPoolDataUpdateCoordinator (HomeAssistant's DataUpdateCoordinator)
  ├── _async_update_data()              # Polls device every N seconds
  ├── data: VioletReadings              # Latest device state
  ├── _setpoint_cache: dict             # Optimistic write cache (invalidated on poll)
  └── async_update_listeners()          # Notifies all subscribed entities
```

- **Single source of truth** for device data
- **Reduces API calls** – all entities read from shared data
- **Smart caching** – setpoint writes show immediately, polls restore live data

### 2. **Device Class** (Hardware Abstraction)

```
VioletPoolControllerDevice
  ├── api: VioletPoolAPI                # HTTP client (public)
  ├── async_update()                    # Fetch readings from controller
  ├── available: bool                   # Connection status
  ├── device_info: dict                 # HA device metadata
  ├── auto_recovery logic               # Exponential backoff on failures
  └── diagnostics                       # Health metrics, latency, request rate
```

- **Encapsulates hardware communication**
- **Auto-recovery** with exponential backoff (10s → 300s)
- **Thread-safe** (uses locks for API access)
- **Smart logging** with throttling (5-minute intervals)

### 3. **Entity Architecture** (10 Platforms)

Each entity type extends `CoordinatorEntity` + `VioletPoolControllerEntity`:

| Platform | Purpose | Count |
|----------|---------|-------|
| **sensor** | Numeric readings (temp, pH, ORP, etc.) | 40+ |
| **binary_sensor** | Digital inputs, alarms, status | 20+ |
| **switch** | Multi-state device control (pump, heater, dosing) | 30+ |
| **climate** | Thermostat (pool heater) | 2 |
| **cover** | Pool cover control | 1 |
| **number** | Setpoint inputs | 10+ |
| **select** | Mode selection | 5+ |
| **light** | RGB/DMX lighting | 5+ |
| **update** | Firmware updates | 1 |
| **button** | Manual actions | 5+ |

**Key Features**:
- **Safe data access** via `get_value()`, `get_float_value()`, etc.
- **Optimistic updates** for user feedback
- **State interpretation** (multi-state switches → boolean conversion)

### 4. **Multi-State Switch Logic**

Pool devices support states 0-6:
- `0, 2, 5, 6` = OFF (standby, rule-blocked, emergency, manual)
- `1, 3, 4` = ON (scheduled, emergency, manual forced)
- **Composite states** like `"3|PUMP_ANTI_FREEZE"` provide context (operational modes)

All mappings in `DEVICE_STATE_MAPPING` (API package).

### 5. **Service Architecture** (Control & Diagnostics)

```
VioletServiceManager
  ├── VioletServiceHandlers
  │   ├── VioletControlServiceHandlers     # Action services
  │   │   └── control_pump, smart_dosing, manage_pv_surplus, etc.
  │   │
  │   └── VioletDiagnosticServiceHandlers  # Diagnostic services
  │       └── export_diagnostic_logs, get_connection_status, etc.
  │
  └── Service schemas (Voluptuous validation)
```

- **Rate-limited** API calls (respects controller limits)
- **Serialized** by rate limiter (no concurrent conflicts)
- **Error handling** with user-friendly messages
- **Device targeting** – single or multi-device operations

---

## Data Flow

### Polling Cycle
```
Timer (every 10s default)
  ↓
VioletPoolDataUpdateCoordinator._async_update_data()
  ↓
VioletPoolControllerDevice.async_update()
  ↓
VioletPoolAPI.get_readings()  [HTTP GET /getReadings?ALL]
  ↓
VioletReadings(data)  [Typed data class]
  ↓
[Cache invalidation for setpoint keys present in new data]
  ↓
coordinator.data = new_readings
  ↓
async_update_listeners()  [Notify all entities]
  ↓
Entities update state in HA
```

### Write Flow (Example: Set Temperature)
```
User sets pool heater to 28°C
  ↓
climate.async_set_target_temperature(28.0)
  ↓
VioletPoolAPI.set_device_temperature(...)  [HTTP GET /setFunctionManually?...]
  ↓
Response: {"success": true}
  ↓
coordinator.update_setpoint_cache("POOL_TEMP_SETPOINT", 28.0)
  ↓
async_update_listeners()  [Immediate feedback]
  ↓
User sees 28°C immediately (optimistic)
  ↓
[Delayed refresh triggered]
  ↓
Next poll returns 28°C (cache invalidated, live data wins)
```

---

## API Package (Monorepo Dependency)

### Design
- **Published to PyPI** as `violet-poolController-api`
- **Installed by HA** from PyPI (see `manifest.json`)
- **Source** in this repo under `violet_poolcontroller_api/`
- **Development**: Use `pip install -e ./violet_poolcontroller_api`

### Key Components

**VioletPoolAPI** – HTTP Client
```python
api = VioletPoolAPI(
    host="192.168.1.100",
    use_ssl=False,
    username="admin",
    password="password",
    verify_ssl=True,
    timeout=10,
    max_retries=3
)
readings = await api.get_readings()  # dict[str, Any]
response = await api.set_switch_state("PUMP", "ON")  # {"success": bool}
```

**Rate Limiter** – Token Bucket Algorithm
- Prevents API flooding
- Configurable rate (default: 10 req/sec)
- Handles retries + backoff

**Circuit Breaker** – Fault Tolerance
- States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (recovery) → CLOSED
- Prevents cascade failures
- Configurable thresholds

**Input Sanitizer** – Security
- XSS prevention
- Injection protection
- Path traversal blocking
- Safe parameter handling

---

## Configuration Flow

```
User triggers config flow
  ↓
config_flow.py (async_step_user, async_step_zeroconf)
  ↓
[Validation: IP, credentials, SSL, timeout, retry attempts]
  ↓
_test_connection()  [Verifies controller is reachable]
  ↓
get_grouped_sensors()  [Auto-discover available sensors]
  ↓
Auto-detect active features  [Which pool features are enabled]
  ↓
async_create_entry()  [Store config]
  ↓
__init__.py: async_setup_entry()  [Load coordinator + platforms]
```

### Features Detected
- Filter (pump, runtime)
- Heating (heater, solar, runtime)
- LED lighting (DMX, RGB)
- pH/chlorine dosing
- Flocculation
- Covers
- Backwash
- PV surplus
- Digital inputs/rules

---

## Error Handling

### Error Codes (`error_handler.py`)
```python
VioletErrorCodes
  ├── Network Errors (TIMEOUT, CONNECTION, DNS, SSL)
  ├── API Errors (TIMEOUT, RATE_LIMITED, INVALID_RESPONSE, JSON_DECODE)
  ├── Auth Errors (INVALID_CREDENTIALS, WEAK_PASSWORD, SESSION_EXPIRED)
  ├── Config Errors (INVALID_INPUT, DUPLICATE_ENTRY)
  └── Circuit Breaker (OPEN, HALF_OPEN)
```

### Recovery Strategy
- **Smart logging** with throttling (5-min intervals for repeated errors)
- **Auto-recovery** with exponential backoff
- **Max 10 attempts** before requiring manual intervention
- **User-friendly messages** in UI (translated)

---

## Security Model

See [SECURITY.md](./SECURITY.md) for full architecture.

**Key Principles**:
1. **Passive-first** – Never assume device state, always read actual state
2. **No state restoration** – Don't restore "on" state after restart
3. **Explicit user actions only** – No automations that change state without user command
4. **Input validation** – All user inputs sanitized
5. **Rate limiting** – Prevent API abuse
6. **SSL/TLS** – Certificate verification enabled by default

---

## Testing Infrastructure

### Test Suites
- **Unit tests** – Device, API, config flow, services
- **Integration tests** – Full setup + entity creation
- **Platform tests** – Individual entity types
- **Security tests** – Input sanitization, state handling

### Test Configuration
- `asyncio_mode = auto` (automatic async handling)
- `asyncio_default_fixture_loop_scope = function` (isolated event loops)
- **Mock data** – `getReadings_spec.json` (real API response example)

### Continuous Integration
- Python 3.12-3.14 matrix
- Ruff linting + Mypy type checking
- Home Assistant 2026.5.x compatibility
- Security scanning (CodeQL, TruffleHog)

---

## Diagnostics & Observability

### Built-in Sensors
- **Connection latency** (ms)
- **System health** (0-100%)
- **API request rate** (req/min)
- **Error codes** (controller-reported issues)
- **Calibration history** (sensor calibration timestamps)

### Diagnostic Export
- HA → Download diagnostics
- Includes: poll history, connection metrics, error logs
- Automatically redacts: passwords, usernames

### Debug Logging
- `CONF_ENABLE_DIAGNOSTIC_LOGGING` (config option)
- Per-device logging toggle
- Useful for troubleshooting connection issues

---

## Performance Considerations

### Polling Interval
- Default: 10 seconds
- Configurable: 5-300 seconds
- Trades off freshness vs. API load

### Data Structures
- **Poll history**: Fixed-size deque (maxlen=1000)
- **Latency tracking**: Deque (maxlen=360) for 1-hour rolling average
- **Cache**: Setpoint cache (invalidated per poll)

### Concurrency
- **API lock** (`_api_lock`) – Serializes API calls
- **No race conditions** – Coordinator ensures single update at a time
- **Thread-safe** – Safe for multi-threaded HA environments

---

## Deployment

### Home Assistant Integration
- **Minimum HA**: 2026.5.0 (Python 3.14.2)
- **Distribution**: HACS + GitHub releases
- **Installation**: Custom Components → Add repository → Install

### API Package
- **Published to PyPI**: `violet-poolController-api`
- **Versioned independently** from integration
- **Supports**: Python 3.12+

### Updates
- **Release workflow** (`.github/workflows/release.yml`)
  - Tag `v*` → creates GH release
  - Auto-updates manifest.json version
- **Dev releases** (`v*-dev.*`) on every main push
- **API releases** (tag `api-v*`)
  - Published to PyPI
  - Version must match `pyproject.toml`

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `device.py` | Device + Coordinator (core) |
| `entity.py` | Base entity class |
| `config_flow.py` | UI configuration |
| `error_handler.py` | Error code mappings |
| `service_*.py` | Service implementations |
| `sensor.py`, `switch.py`, etc. | Entity platforms |
| `manifest.json` | HA metadata + dependencies |
| `CLAUDE.md` | Developer instructions |
| `SECURITY.md` | Security architecture |

---

## Development Workflow

### Setup
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Quality Assurance
```bash
python -m ruff check custom_components/ --fix
python -m mypy custom_components/
pytest -v
```

### Before Commit
- Ruff: 0 errors
- Mypy: type checking passes
- Tests: all green
- Git: conventional commits

---

**Last Updated**: 2026-06-16  
**Version**: 2.0.0 (Integration) + 0.0.32 (API)
