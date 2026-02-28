"""ZeroConf discovery for Violet Pool Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components.zeroconf import AsyncServiceInfo
from homeassistant.core import HomeAssistant, callback

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
        service_info: AsyncServiceInfo,
    ) -> None:
        """Discover a Violet Pool Controller device.

        This method is called by Home Assistant when a matching ZeroConf service
        is discovered on the network. It stores the device information for later
        use in the config flow.

        Args:
            hass: The Home Assistant instance.
            service_info: The ZeroConf service info.

        Returns:
            None. Device info is stored in _discovered_devices for later retrieval.
        """
        _LOGGER.info(
            "Discovered Violet Pool Controller: %s at %s:%s",
            service_info.name,
            service_info.host,
            service_info.port,
        )

        # Store discovered device info as dict for later use
        self._discovered_devices[service_info.name] = {
            "host": service_info.host,
            "port": service_info.port,
            "hostname": service_info.hostname,
            "name": service_info.name,
            "type": service_info.type,
        }

    @callback
    def async_get_discovered_devices(
        self,
    ) -> dict[str, dict[str, Any]]:
        """Return list of discovered devices.

        Returns:
            Dictionary of discovered devices with connection info.
        """
        return dict(self._discovered_devices)  # Return a copy

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
