> 🇬🇧 **English** | 🇩🇪 **[Deutsch](API-Reference.de)**

---

# API Reference – Violet Pool Controller HTTP API

> Complete documentation of the controller API endpoints and the Python client class.

---

## Overview

The Violet Pool Controller provides a **JSON-based HTTP API**. The integration communicates exclusively locally – no cloud, no external network required.

```
Home Assistant
    └── VioletPoolAPI (aiohttp)
            ├── GET  /getReadings?ALL        → All sensor data
            ├── GET  /setFunctionManually    → Control outputs
            ├── POST /setConfig              → Set configuration
            ├── GET  /getConfig              → Read configuration
            └── GET  /getHistory             → Retrieve history
```

---

## Endpoints

### GET `/getReadings?ALL`

Reads all current measurements and system states.

**Request:**
```
GET http://192.168.1.55/getReadings?ALL
```

**Response (JSON):**
```json
{
  "PUMP": 2,
  "HEATER": 0,
  "SOLAR": 1,
  "WATER_TEMP": 26.5,
  "SOLAR_TEMP": 42.1,
  "PH_VALUE": 7.2,
  "ORP_VALUE": 720,
  "CHLORINE": 0.8,
  "AI1": 0.0,
  "DI1": 0,
  "ERROR_CODE": "0",
  ...
}
```

**Usage in HA:**
- Polled every `scan_interval` seconds
- All sensor and switch entities are updated from this response

---

### GET `/setFunctionManually`

Controls outputs and functions of the controller.

**Request:**
```
GET http://192.168.1.55/setFunctionManually?PUMP=1
GET http://192.168.1.55/setFunctionManually?HEATER=OFF
GET http://192.168.1.55/setFunctionManually?PH_MINUS=AUTO
```

**Parameters:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| `PUMP` | `0`–`3`, `ON`, `OFF`, `AUTO` | Pump speed or mode |
| `HEATER` | `ON`, `OFF`, `AUTO` | Heater |
| `SOLAR` | `ON`, `OFF`, `AUTO` | Solar |
| `PH_MINUS` | `ON`, `OFF`, `AUTO` | pH reducer |
| `PH_PLUS` | `ON`, `OFF`, `AUTO` | pH increaser |
| `CHLORINE` | `ON`, `OFF`, `AUTO` | Chlorine |
| `FLOCCULANT` | `ON`, `OFF`, `AUTO` | Flocculant |
| `DMX1`–`DMX8` | `ON`, `OFF`, `AUTO` | DMX scenes |
| `RELAY1`–`RELAY8` | `ON`, `OFF`, `AUTO` | Extension relays |

**Action Constants:**

| Constant | Value | Meaning |
|----------|-------|---------|
| `ACTION_ON` | `"1"` | Manually turn on |
| `ACTION_OFF` | `"6"` | Manually turn off |
| `ACTION_AUTO` | `"AUTO"` | Set to automatic |
| `ACTION_ALLON` | `"ALLON"` | All on |
| `ACTION_ALLOFF` | `"ALLOFF"` | All off |
| `ACTION_ALLAUTO` | `"ALLAUTO"` | All automatic |

---

### POST `/setConfig`

Sets configuration values on the controller.

**Request:**
```
POST http://192.168.1.55/setConfig
Content-Type: application/x-www-form-urlencoded

TARGET_PH=7.2&TARGET_ORP=720
```

**Configurable Parameters:**
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `TARGET_PH` | float | 6.0–8.0 | pH setpoint |
| `TARGET_ORP` | int | 200–900 | ORP setpoint in mV |
| `TARGET_MIN_CHLORINE` | float | 0.1–5.0 | Minimum chlorine level mg/l |
| `TARGET_POOL_TEMP` | float | 10–40 | Pool target temperature °C |
| `TARGET_SOLAR_TEMP` | float | 20–60 | Solar maximum temperature °C |

---

### GET `/getConfig`

Reads configuration values.

**Request:**
```
GET http://192.168.1.55/getConfig?TARGET_PH,TARGET_ORP
```

**Response:**
```json
{
  "TARGET_PH": 7.2,
  "TARGET_ORP": 720
}
```

---

### GET `/getHistory`

Retrieves history data.

**Request:**
```
GET http://192.168.1.55/getHistory
```

---

### GET `/getCalibHistory`

Retrieves calibration history.

**Request:**
```
GET http://192.168.1.55/getCalibHistory
```

**Response:** JSON array with calibration entries including date, sensor type, and calibration values.

---

### GET `/setOutputTestmode`

Diagnostic mode for outputs.

**Request:**
```
GET http://192.168.1.55/setOutputTestmode?output=PUMP&mode=ON&duration=120
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `output` | Output identifier (PUMP, HEATER, etc.) |
| `mode` | `SWITCH`, `ON`, or `OFF` |
| `duration` | Test duration in seconds (1–900) |

---

## Python Client: `VioletPoolAPI`

The Python client has been extracted into a standalone PyPI package:
- **PyPI:** [violet-poolController-api](https://pypi.org/project/violet-poolController-api/)
- **GitHub:** [Xerolux/violet-poolController-api](https://github.com/Xerolux/violet-poolController-api)

### Initialization

```python
from violet_poolcontroller_api.api import VioletPoolAPI
import aiohttp

async with aiohttp.ClientSession() as session:
    api = VioletPoolAPI(
        host="192.168.1.55",
        session=session,
        username="admin",        # Optional
        password="secret",       # Optional
        use_ssl=False,           # Use HTTPS
        verify_ssl=True,         # Verify certificate
        timeout=10,              # Seconds
        max_retries=3,           # Retry attempts
    )
```

### Methods

#### `get_readings()`

```python
data: dict = await api.get_readings()
# Returns all current measurements
```

#### `set_function_manually(key, value)`

```python
await api.set_function_manually("PUMP", "1")
await api.set_function_manually("HEATER", "OFF")
await api.set_function_manually("PH_MINUS", "AUTO")
```

#### `set_config(params)`

```python
await api.set_config({"TARGET_PH": 7.2, "TARGET_ORP": 720})
```

#### `get_config(keys)`

```python
config = await api.get_config(["TARGET_PH", "TARGET_ORP"])
```

#### `set_output_testmode(output, mode, duration)`

```python
await api.set_output_testmode(
    output="PUMP",
    mode="ON",
    duration=120
)
```

---

## Rate Limiting

All API calls go through the global rate limiter:

```python
from violet_poolcontroller_api.utils_rate_limiter import get_global_rate_limiter

limiter = get_global_rate_limiter()
# Token bucket algorithm
# Prevents controller overload
```

### Priority Levels

| Priority | Constant | Usage |
|----------|----------|-------|
| High | `API_PRIORITY_HIGH` | Manual control commands |
| Normal | `API_PRIORITY_NORMAL` | Regular polling |
| Low | `API_PRIORITY_LOW` | Background tasks |

---

## Error Handling

### Exceptions

| Exception | Description |
|-----------|-------------|
| `VioletPoolAPIError` | General API error |
| `aiohttp.ClientTimeout` | Timeout exceeded |
| `aiohttp.ClientConnectionError` | Connection failed |
| `json.JSONDecodeError` | Invalid JSON response |

### Retry Logic

```
Attempt 1:  Immediately
Attempt 2:  Exponential backoff
Attempt 3:  Exponential backoff
...
Max: DEFAULT_RETRY_ATTEMPTS (default: 3)
```

---

## Timeout Configuration

```
Total timeout:       DEFAULT_TIMEOUT_DURATION (default: 10s)
Connection timeout:  80% of total timeout (8s)
Socket timeout:      80% of total timeout (8s)
```

---

## Authentication

The controller supports HTTP Basic Authentication:

```
Authorization: Basic base64(username:password)
```

If no username/password is configured, no auth header is sent.

---

## SSL/TLS

```python
# Full verification (default)
api = VioletPoolAPI(host=..., use_ssl=True, verify_ssl=True)

# Self-signed certificate (home network)
api = VioletPoolAPI(host=..., use_ssl=True, verify_ssl=False)

# No SSL (HTTP)
api = VioletPoolAPI(host=..., use_ssl=False)
```

---

## Data Types in API Responses

| Data Type | Example Value | Description |
|-----------|--------------|-------------|
| Integer State | `2` | Device state 0–6 |
| Float | `26.5` | Temperature, pH, etc. |
| String State | `"3\|PUMP_ANTI_FREEZE"` | Composite state |
| String | `"RELEASED"` | Digital input status |
| Error Code | `"120"` | Error code as string |

---

## Sensor Key Reference

Important keys from `/getReadings?ALL`:

| Key | Unit | Description |
|-----|------|-------------|
| `WATER_TEMP` | °C | Pool water temperature |
| `SOLAR_TEMP` | °C | Solar collector temperature |
| `AIR_TEMP` | °C | Air temperature |
| `PH_VALUE` | pH | pH value |
| `ORP_VALUE` | mV | Redox potential |
| `CHLORINE` | mg/l | Chlorine level |
| `CONDUCTIVITY` | µS/cm | Conductivity |
| `PUMP` | 0–6 | Pump state |
| `HEATER` | 0–6 | Heater state |
| `SOLAR` | 0–6 | Solar state |
| `DI1`–`DI8` | 0/1 | Digital inputs |
| `AI1`–`AI8` | V/mA | Analog inputs |
| `ERROR_CODE` | string | Current error code |

---

*Back: [Testing](Testing) | Next: [Changelog](Changelog)*