"""DataUpdateCoordinator für den Violet Pool Controller."""
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .device import VioletPoolControllerDevice

_LOGGER = logging.getLogger(__name__)

class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator für Datenaktualisierungen."""

    def __init__(self, hass: HomeAssistant, device: VioletPoolControllerDevice, config_entry: ConfigEntry) -> None:
        """Initialisiere den Koordinator."""
        self.device = device
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.device_id}",
            update_interval=timedelta(seconds=device.polling_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Aktualisiere die Daten."""
        try:
            return await self.device.async_update()
        except Exception as e:
            if hasattr(self.device, '_available'):
                self.device._available = False
            _LOGGER.error(f"Error during data update for {self.name}: {e}")
            raise UpdateFailed(f"Error during data update for {self.name}: {e}") from e
