"""Cover Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, List

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_API_URL, CONF_DEVICE_NAME, MANUFACTURER, INTEGRATION_VERSION

_LOGGER = logging.getLogger(__name__)


class VioletCover(CoordinatorEntity, CoverEntity):
    """Repräsentation der Pool-Abdeckung (Cover)."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(self, coordinator, config_entry: ConfigEntry):
        """Initialisiere die Cover-Entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} Cover"
        self._attr_unique_id = f"{config_entry.entry_id}_cover"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed."""
        state = self.coordinator.data.get("COVER_STATE")
        return state == "CLOSED"

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        state = self.coordinator.data.get("LAST_MOVING_DIRECTION")
        return state == "OPEN" and not self.is_closed and not self.is_open

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        state = self.coordinator.data.get("LAST_MOVING_DIRECTION")
        return state == "CLOSE" and not self.is_closed and not self.is_open
        
    @property
    def is_open(self) -> bool:
        """Return if the cover is fully open."""
        state = self.coordinator.data.get("COVER_STATE")
        return state == "OPEN"

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """Send command to the cover."""
        try:
            # Verwende die Cover-spezifische API-Methode
            await self.coordinator.api.set_cover_state(action=action)
            await self.coordinator.async_request_refresh()
            _LOGGER.debug("Cover-Befehl gesendet: %s", action)
        except Exception as err:
            _LOGGER.error("Fehler bei Cover-Befehl %s: %s", action, err)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up Violet Cover from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Überprüfe, ob die erforderlichen Daten für das Cover vorhanden sind
    if "COVER_STATE" in coordinator.data:
        async_add_entities([VioletCover(coordinator, config_entry)])
    else:
        _LOGGER.info("Kein Cover in den API-Daten gefunden, Cover wird nicht hinzugefügt")
