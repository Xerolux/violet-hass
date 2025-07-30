"""DataUpdateCoordinator für den Violet Pool Controller."""
import logging
import asyncio
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import VioletPoolAPIError
from .device import VioletPoolControllerDevice
from .const import DOMAIN, DEFAULT_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)

class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordiniert zyklisches Datenabrufen vom Violet Pool Controller."""

    def __init__(self, hass: HomeAssistant, device: VioletPoolControllerDevice, name: str, polling_interval: int = DEFAULT_POLLING_INTERVAL) -> None:
        """Initialisiert den Coordinator."""
        super().__init__(hass, _LOGGER, name=name, update_interval=timedelta(seconds=polling_interval))
        self.device = device
        _LOGGER.debug("Coordinator für %s initialisiert (Intervall: %ds)", name, polling_interval)

    async def _async_update_data(self) -> dict:
        """Holt Daten vom Gerät."""
        try:
            return await self.device.async_update()
        except VioletPoolAPIError as err:
            _LOGGER.error("Fehler beim Datenabruf: %s", err)
            raise UpdateFailed(f"Fehler: {err}") from err

    def get_device_status(self) -> dict:
        """Gibt Gerätestatus zurück."""
        return {
            "available": self.device.available,
            "last_update_success": self.last_update_success,
            "last_update_time": self.last_update_success_time,
            "last_exception": str(self.last_exception) if self.last_exception else None,
            "firmware_version": self.device.firmware_version,
        }
