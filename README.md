# Violet Pool Controller API

[![PyPI version](https://img.shields.io/pypi/v/violet-poolController-api.svg?style=for-the-badge)](https://pypi.org/project/violet-poolController-api/)
[![PyPI downloads](https://img.shields.io/pypi/dm/violet-poolController-api.svg?style=for-the-badge)](https://pypistats.org/packages/violet-poolcontroller-api)
[![Python versions](https://img.shields.io/pypi/pyversions/violet-poolController-api.svg?style=for-the-badge)](https://pypi.org/project/violet-poolController-api/)
[![License: AGPL v3+](https://img.shields.io/badge/License-AGPL_v3%2B-blue?style=for-the-badge)](LICENSE)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)
[![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

An asynchronous Python client for interacting with the **Violet Pool Controller**.

This library is primarily designed to power the official [Violet Pool Controller Home Assistant Integration](https://github.com/Xerolux/violet-hass), but it can be used independently for any Python project that needs to fetch readings or control a Violet Pool system.

> **📖 Documentation:**
> - GitHub Pages: https://xerolux.github.io/violet-poolController-api/
> - GitHub Wiki: https://github.com/Xerolux/violet-poolController-api/wiki
>
> The `docs/` directory is the single source of truth and is used for both GitHub Pages and Wiki sync.

## Features
* **Asynchronous:** Fully async operations using `aiohttp`.
* **Resilient:** Built-in Circuit Breaker and Rate Limiter to protect both the client and the controller from overload.
* **Sanitization:** Strict payload input sanitization to prevent injection and invalid settings.

## Installation

```bash
pip install violet-poolController-api
```

## Basic Usage

```python
import asyncio
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError

async def main():
    # Create an aiohttp ClientSession
    async with aiohttp.ClientSession() as session:
        # Initialize the API
        # Note: In a standard setup, just enter the IP address without a port.
        # A port (e.g. "192.168.1.100:8080") can optionally be provided if you use a proxy or alternative setup.
        api = VioletPoolAPI(
            host="192.168.1.100",
            username="admin",
            password="your_password",
            session=session,
            dosing_standalone=False,  # True for Violet dosing standalone setups
        )

        try:
            # --- 1. Fetch current sensor readings ---
            readings = await api.get_readings()
            print("Current Pool Readings:")
            print(readings)

            # --- 2. Control the Filter Pump ---
            # Set pump speed to 2 (Normal) permanently (duration=0)
            await api.set_pump_speed(speed=2, duration=0)
            print("\nPump speed set to 2.")

            # --- 3. Set Target Temperature ---
            # Set the target temperature for the heater to 28.5 degrees
            await api.set_device_temperature("HEATER", 28.5)
            print("\nHeater target temperature set to 28.5°C.")

            # --- 4. Control Pool Lights ---
            # Trigger the color pulse animation for the pool light
            await api.set_light_color_pulse()
            print("\nLight color pulse triggered.")

        except VioletPoolAPIError as e:
            print(f"An error occurred while communicating with the Violet controller: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Operations

The API client includes many more functions tailored to the Violet Controller:
- `get_config(["PUMP_SPEED_1", "PUMP_SPEED_2"])`: Fetch specific configuration values.
- `set_ph_target(7.2)`: Change the pH target value.
- `set_orp_target(750)`: Change the ORP (Redox) target value.
- `set_pv_surplus(active=True)`: Enable the PV-Surplus mode.
- `manual_dosing(dosing_type="Chlor", duration=120)`: Trigger manual chemical dosing.

For a full list of available commands and more detailed examples, please refer to the [Wiki](https://github.com/Xerolux/violet-poolController-api/wiki) or the source code in `api.py`.

## Violet Dosing Standalone Mode

If your Violet setup runs as dosing standalone (without the base module), enable:

```python
api = VioletPoolAPI(
    host="192.168.1.100",
    username="admin",
    password="your_password",
    session=session,
    dosing_standalone=True,
)
```

In this mode, dosing functions (for example `manual_dosing` and dosing parameter/target updates) stay available, while base-module-only switch functions (for example pump/light/backwash) are blocked with a clear error message.

**Note on getReadings format:**
As of version `0.0.7`, the API client automatically detects and normalizes the payload output from the controller. Whether your Violet Controller returns the classic base-module `dict` structure (`{"PUMPSTATE": "2", "PH": 7.2}`) or the new standalone `list` structure, the `get_readings()` and `get_specific_readings()` functions will always return a seamless, flattened key-value dictionary. Your Home Assistant integration or downstream application will work uniformly with both formats without requiring any extra code!

**Hardware Profile Detection:**
As of the latest release, the API client provides a method to detect the specific hardware configuration of your Violet Controller.
The API automatically detects the connected modules and updates internal states based on the available readings.
```python
profile = await api.get_hardware_profile()
print(profile)
# Output example:
# {
#     "base_module": True,
#     "dosing_module": True,
#     "extension_module_1": True,
#     "extension_module_2": False,
# }
```
This detection parses `get_readings()` to check for the presence of certain internal status parameters (`SYSTEM_dosagemodule_cpu_temperature`, `EXT1_1`, `EXT2_1`), allowing your application to dynamically adapt to the connected modules (Base Module, Dosing Module, Relay Extension 1 and 2). By utilizing this detection, developers and integrations can accurately filter out features for missing hardware, ensuring that only supported options are exposed to the user.

## Mock Server (Testing Without Hardware)

The project includes a full mock server that simulates the Violet Pool Controller. This allows you to develop and test without needing the physical controller.

### Start the Mock Server

```bash
# Without authentication (default port 8480)
python tests/mock_server.py

# With Basic Auth (like the real controller)
python tests/mock_server.py --user admin --password secret

# With simulated network latency (300ms)
python tests/mock_server.py --user admin --password secret --delay 0.3

# Dosing-standalone mode (list format responses)
python tests/mock_server.py --standalone
```

### Connect Your Code

```python
import asyncio, aiohttp
from violet_poolcontroller_api import VioletPoolAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="localhost:8480",
            session=session,
            username="admin",
            password="secret",
        )
        readings = await api.get_readings()
        print(f"pH={readings['pH_value']}, PUMP={readings['PUMP']}")

asyncio.run(main())
```

### Run the Smoke Test

The smoke test automatically starts the mock server, tests every public API method, and prints a detailed report:

```bash
python tests/test_api_smoke.py --user admin --password secret
```

### Mock Server Control Endpoints

These endpoints exist only on the mock server (not the real controller):

| Endpoint | Description |
|---|---|
| `GET /mock/state` | View internal state (outputs, sensors, config) as JSON |
| `GET /mock/error?code=500&count=3` | Force next 3 requests to return HTTP 500 |
| `GET /mock/reset` | Reset all state to defaults |

### Mock Server Features

- **Stateful:** Switch/dosing changes are reflected in `getReadings` (e.g. PUMP ON -> PUMP=4)
- **Sensor drift:** pH, ORP, chlorine, and CPU temperature change slowly over time
- **Config persistence:** Values set via `setConfig` are returned by `getConfig`
- **Log history:** Actions are logged and returned by `getLog`
- **Error simulation:** Test your error handling with forced HTTP errors

## License
GNU Affero General Public License v3.0 or later (AGPLv3+)

---

## About the Violet Pool Controller

The **VIOLET Pool Controller** by [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) is a premium smart pool automation system developed in Germany, featuring a JSON API for seamless Home Assistant integration.

- **Offizieller Shop:** [pooldigital.de](https://www.pooldigital.de/)
- **Community:** [PoolDigital Forum](http://forum.pooldigital.de/)

**Disclaimer:**
*This is an unofficial, community-driven project. It is not affiliated with, endorsed by, or associated with PoolDigital GmbH & Co. KG in any way. "VIOLET" and any related trademarks are the property of their respective owners.*

⚠️ **WARNING - USE AT YOUR OWN RISK:**
*This software interacts with physical hardware and automation systems that control water chemistry (pH, Chlorine/ORP) and electrical equipment (pumps, heaters). A bug, network issue, or incorrect configuration could result in hardware damage, unsafe water conditions, or other hazards. By using this software, you acknowledge and agree that you are solely responsible for any damage, injury, or loss of property that may occur. Please always monitor your pool's chemistry and hardware independently.*
