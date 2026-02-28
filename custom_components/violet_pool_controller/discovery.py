"""ZeroConf discovery for Violet Pool Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_flow_flow import FlowResult

from . import DOMAIN, LOGGER

# Service types for discovery
SERVICE_TYPES = ["_http._tcp.local.", "_violet-controller._tcp.local."]


class VioletPoolControllerDiscovery:
    """Discovery handler for Violet Pool Controller."""

    def __init__(self) -> None:
        """Initialize discovery handler."""
        self._discovered_devices: dict[str, ZeroconfServiceInfo] = {}

    @callback
    def async_discover_service(
        self,
        hass: HomeAssistant,
        service_info: ZeroconfServiceInfo,
    ) -> config_entries.FlowHandler:
        """Discover a Violet Pool Controller device.

        Args:
            hass: The Home Assistant instance.
            service_info: The ZeroConf service info.

        Returns:
            Config entry flow handler.
        """
        LOGGER.info(
            "Discovered Violet Pool Controller: %s at %s:%s",
            service_info.name,
            service_info.host,
            service_info.port,
        )

        # Store discovered device info
        self._discovered_devices[service_info.name] = service_info

        # Return the config flow handler
        return config_entries.ConfigFlowHandler(
            DOMAIN,
            context={
                "title": f"Violet Pool Controller ({service_info.name})",
                "host": service_info.host,
                "port": service_info.port,
                "hostname": service_info.hostname,
                "discovered": True,
            },
        )

    @callback
    def async_get_discovered_devices(
        self,
    ) -> dict[str, dict[str, Any]]:
        """Return list of discovered devices.

        Returns:
            Dictionary of discovered devices.
        """
        return {
            name: {
                "host": info.host,
                "port": info.port,
                "hostname": info.hostname,
                "name": info.name,
                "type": info.type,
            }
            for name, info in self._discovered_devices.items()
        }

    def clear_discovered_devices(self) -> None:
        """Clear all discovered devices."""
        self._discovered_devices.clear()


# Global discovery instance
_discovery_handler: VioletPoolControllerDiscovery | None = None


def get_discovery_handler() -> VioletPoolControllerDiscovery:
    """Get the global discovery handler instance.

    Returns:
        The global VioletPoolControllerDiscovery instance.
    """
    global _discovery_handler
    if _discovery_handler is None:
        _discovery_handler = VioletPoolControllerDiscovery()
    return _discovery_handler
