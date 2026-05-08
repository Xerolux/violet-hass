# ZeroConf Discovery: Correct Implementation

## The Problem

In my original implementation in `discovery.py`:

```python
# ❌ WRONG - ConfigFlowHandler does not exist!
def async_discover_service(self, hass, service_info):
    return config_entries.ConfigFlowHandler(  # ← Error!
        DOMAIN,
        context={...}
    )
```

**Error**: `ConfigFlowHandler` does not exist in Home Assistant!

---

## The Correct Solution

### What ZeroConf Discovery REALLY Does:

In Home Assistant, ZeroConf discoveries are **NOT** handled via `return` statements!

Instead, discovery happens automatically:

1. **Home Assistant discovers service** (automatically via mDNS)
2. **HA calls `async_zeroconf_get_service_info`**
3. **This function stores the info** (does not return it!)
4. **User clicks "Configure"** in the UI
5. **Config Flow is started** with the discovered info

---

## Correct Implementation

### File: `discovery.py`

```python
"""ZeroConf discovery for Violet Pool Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult  # Not ConfigFlowHandler!

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Service types for discovery
SERVICE_TYPES = ["_http._tcp.local.", "_violet-controller._tcp.local."]


class VioletPoolControllerDiscovery:
    """Discovery handler for Violet Pool Controller."""

    def __init__(self) -> None:
        """Initialize discovery handler."""
        self._discovered_devices: dict[str, dict[str, Any]] = {}

    @callback
    def async_discover_service(
        self,
        hass: HomeAssistant,
        service_info: ZeroconfServiceInfo,
    ) -> None:  # ← Return NOTHING!
        """Discover a Violet Pool Controller device.

        This method is called by HA when a device is discovered.
        It stores the info for later use.

        Args:
            hass: The Home Assistant instance.
            service_info: The ZeroConf service info.
        """
        _LOGGER.info(
            "Discovered Violet Pool Controller: %s at %s:%s",
            service_info.name,
            service_info.host,
            service_info.port,
        )

        # Store the discovered device info
        self._discovered_devices[service_info.name] = {
            "host": service_info.host,
            "port": service_info.port,
            "hostname": service_info.hostname,
            "name": service_info.name,
            "type": service_info.type,
        }

        # ❌ NO RETURN! We only store the info!
        # The UI automatically shows discovered devices


def get_discovery_handler() -> VioletPoolControllerDiscovery:
    """Get the global discovery handler instance."""
    global _discovery_handler
    if _discovery_handler is None:
        _discovery_handler = VioletPoolControllerDiscovery()
    return _discovery_handler


# Global discovery instance
_discovery_handler: VioletPoolControllerDiscovery | None = None
```

---

## In `__init__.py`:

### The `async_zeroconf_get_service_info` function should look like this:

```python
@callback
def async_zeroconf_get_service_info(
    hass: HomeAssistant,
    info: ZeroconfServiceInfo,
    service_info_type: str,
) -> FlowResult | None:  # ← Can return FlowResult or None
    """Handle ZeroConf discovery of Violet Pool Controller.

    Called by HA when an _http._tcp.local. or
    _violet-controller._tcp.local. service is found.

    Args:
        hass: The Home Assistant instance.
        info: The ZeroConf service info.
        service_info_type: The service type.

    Returns:
        FlowResult if Config Flow should be started,
        None if discovery should only be stored.
    """
    from .discovery import get_discovery_handler

    _LOGGER.info("ZeroConf discovery triggered for %s", info.name)

    # Get discovery handler
    handler = get_discovery_handler()

    # Store the discovery info
    handler.async_discover_service(hass, info)

    # ❌ DO NOT RETURN A CONFIG FLOW HANDLER!
    # HA automatically takes care of starting the flow
    # when the user clicks "Configure"

    return None  # Optional: Explicitly return None
```

---

## How the Config Flow Gets Discovered Info

### In `config_flow.py` during setup:

```python
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Violet Pool Controller config flow."""

    def __init__(self) -> None:
        """Initialize config flow."""
        self._discovered_info: dict[str, Any] | None = None

    async def async_step_user(self, user_input=None):
        """Handle user init."""
        # Show discovered devices if available
        from .discovery import get_discovery_handler

        handler = get_discovery_handler()
        discovered = handler.async_get_discovered_devices()

        if discovered and not user_input:
            # Show discovered devices in UI
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("discovery_id"): vol.In({
                        name: f"{info['host']}:{info['port']}"
                        for name, info in discovered.items()
                    })
                })
            )

        # ... normal setup flow
```

---

## Why My Tests Failed

### Test Error:

```python
# In test_discovery.py:
result = await handler.async_discover_service(mock_hass, mock_zeroconf_info)

# I expected a Config Flow Handler back:
assert result is not None  # ❌ This fails!

# But the correct behavior is:
# async_discover_service returns NOTHING (None)!
# It only stores the info!
```

### Correct Tests:

```python
@pytest.mark.asyncio
async def test_async_discover_service():
    """Test discovering a service."""
    handler = VioletPoolControllerDiscovery()
    mock_hass = MagicMock(spec=HomeAssistant)

    # Call discovery
    result = handler.async_discover_service(mock_hass, mock_zeroconf_info)

    # ✅ Correct: Returns NOTHING!
    assert result is None

    # ✅ Verify that device was stored
    assert mock_zeroconf_info.name in handler._discovered_devices
    assert handler._discovered_devices[mock_zeroconf_info.name]["host"] == "192.168.178.55"
```

---

## Summary

### ❌ Wrong (what I did):
```python
return config_entries.ConfigFlowHandler(...)  # Class does not exist!
```

### ✅ Correct:
```python
# Store discovery info
self._discovered_devices[name] = {...}
# No return!
```

---

## What Needs to Be Changed

1. **`discovery.py`**:
   - `async_discover_service` returns `None` (not ConfigFlowHandler)
   - Only stores device info

2. **`__init__.py`**:
   - `async_zeroconf_get_service_info` returns `None`
   - Only calls discovery handler

3. **`test_discovery.py`**:
   - Tests expect `None` as return value
   - Tests check `_discovered_devices` dict

4. **`config_flow.py`** (optional):
   - Can show discovered devices during setup
   - User selects from discovered devices

---

**This is the reason why 4 tests failed!**

The tests expected a `ConfigFlowHandler` back, but:
1. The class does not exist
2. The method returns nothing at all
3. It only stores info

**Fix**: Adjust all 4 tests to expect `None` return value.
