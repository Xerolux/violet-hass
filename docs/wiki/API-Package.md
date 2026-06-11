# Python API Package (`violet-poolController-api`)

**[🇩🇪 Deutsch](API-Package.de)**

[![PyPI](https://img.shields.io/pypi/v/violet-poolController-api?logo=pypi)](https://pypi.org/project/violet-poolController-api/)

The HTTP client used by the Home Assistant integration is developed in the
[violet-hass monorepo](https://github.com/Xerolux/violet-hass) under
`violet_poolcontroller_api/` and published to PyPI as
[`violet-poolController-api`](https://pypi.org/project/violet-poolController-api/).
It has **no Home Assistant dependencies** and can be used in any Python project.

---

## Installation

```bash
pip install violet-poolController-api
```

Requires Python **3.12+** and `aiohttp`.

## Quick Start

```python
import asyncio
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.50",
            session=session,
            username="user",
            password="secret",
        )

        # Read all ~400 values
        readings = await api.get_readings()
        print(readings["pH_value"], readings["orp_value"])

        # Switch outputs (pump, heater, solar, ...)
        await api.set_switch_state("PUMP", "ON", duration=3600, last_value=2)

        # Manual dosing (runtime in seconds, via POST /triggerManualDosing)
        await api.manual_dosing("Chlor", 60)
        await api.set_switch_state("DOS_1_CL", "OFF")   # stop -> back to auto

        # Enable/disable a dosing channel persistently (controller config)
        await api.set_dosage_enabled("Flockmittel", True)

asyncio.run(main())
```

## Features

| Feature | Description |
|---------|-------------|
| **Rate Limiting** | Token-bucket limiter protects the controller from overload |
| **Circuit Breaker** | Stops hammering an unreachable controller; 4xx errors fail fast |
| **Retry & Backoff** | Automatic retries for transient network/server errors |
| **Input Sanitization** | `InputSanitizer` guards against injection in all parameters |
| **SSL/TLS** | Certificate verification on by default, self-signed supported |
| **Standalone Dosing** | `dosing_standalone=True` for dosing modules without base unit |
| **State Constants** | `VioletState`, `DEVICE_STATE_MAPPING` (states 0–6), translations |

## Dosing: Important Behavior

- Dosing outputs (`DOS_*`) **cannot** be switched via `/setFunctionManually` —
  the controller only accepts `POST /triggerManualDosing` (confirmed by PoolDigital).
  The client routes this automatically.
- A manual dosing run **requires a runtime**; stopping (`OFF`/`AUTO`) returns the
  channel to automatic mode.
- Flocculant (`DOS_6_FLOC`) has no auto mode — it is enabled/disabled via the
  config flag `DOSAGE_floc_use` (`set_dosage_enabled("Flockmittel", ...)`).

## Versioning & Releases

- Source of truth: `violet_poolcontroller_api/pyproject.toml` in the monorepo
- A git tag `api-v<version>` triggers the automated PyPI publish and GitHub release
- The HA integration pins its minimum version in `manifest.json`
  (kept in sync automatically by the *Sync API Version* workflow)

## Links

- 📦 [PyPI](https://pypi.org/project/violet-poolController-api/)
- 📚 [Full API Reference](https://github.com/Xerolux/violet-hass/blob/main/violet_poolcontroller_api/docs/API_REFERENCE.md)
- 📝 [Changelog](https://github.com/Xerolux/violet-hass/blob/main/violet_poolcontroller_api/CHANGELOG.md)
- 🧪 [Test Suite](https://github.com/Xerolux/violet-hass/tree/main/violet_poolcontroller_api/tests)

See also: [API Reference (HTTP endpoints)](API-Reference)
