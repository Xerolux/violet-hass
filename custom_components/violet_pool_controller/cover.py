import logging
from homeassistant.components.cover import CoverEntity, CoverDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_DEVICE_NAME,
)

_LOGGER = logging.getLogger(__name__)

class VioletCover(CoordinatorEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.SHUTTER

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} Cover"
        self._attr_unique_id = f"{config_entry.entry_id}_cover"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "configuration_url": f"http://{self.ip_address}",
        }

    @property
    def is_closed(self):
        state = self.coordinator.data.get("COVER_STATE")
        return state == "CLOSED"

    async def async_open_cover(self, **kwargs):
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs):
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs):
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action):
        try:
            await self.coordinator.api.set_cover_state(action=action)
            await self.coordinator.async_request_refresh()
            _LOGGER.debug("Cover-Befehl gesendet: %s", action)
        except Exception as err:
            _LOGGER.error("Fehler bei Cover-Befehl %s: %s", action, err)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    if "COVER_STATE" in coordinator.data:
        async_add_entities([VioletCover(coordinator, config_entry)])
