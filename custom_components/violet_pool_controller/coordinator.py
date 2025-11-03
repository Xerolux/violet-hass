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

    def __init__(
        self, 
        hass: HomeAssistant, 
        device: VioletPoolControllerDevice, 
        name: str, 
        polling_interval: int = DEFAULT_POLLING_INTERVAL
    ) -> None:
        """Initialisiert den Coordinator."""
        super().__init__(
            hass, 
            _LOGGER, 
            name=name, 
            update_interval=timedelta(seconds=polling_interval)
        )
        self.device = device
        _LOGGER.info(
            "Coordinator für '%s' initialisiert (Abruf alle %ds)", 
            name, 
            polling_interval
        )

    async def _async_update_data(self) -> dict:
        """
        Holt aktuelle Daten vom Gerät.
        
        Returns:
            dict: Gerätedaten vom Controller
            
        Raises:
            UpdateFailed: Bei Kommunikationsfehlern
        """
        try:
            _LOGGER.debug("Starte Datenabruf für %s", self.name)
            data = await self.device.async_update()
            _LOGGER.debug(
                "Datenabruf erfolgreich: %d Datenpunkte erhalten", 
                len(data) if isinstance(data, dict) else 0
            )
            return data
            
        except VioletPoolAPIError as err:
            _LOGGER.error(
                "Fehler beim Datenabruf von %s: %s (Typ: %s)", 
                self.name, 
                err, 
                type(err).__name__
            )
            raise UpdateFailed(f"API-Fehler bei {self.name}: {err}") from err
            
        except Exception as err:
            _LOGGER.exception(
                "Unerwarteter Fehler beim Datenabruf von %s: %s", 
                self.name, 
                err
            )
            raise UpdateFailed(f"Unerwarteter Fehler: {err}") from err

    def get_device_status(self) -> dict:
        """
        Gibt aktuellen Gerätestatus zurück.
        
        Returns:
            dict: Status-Dictionary mit Verfügbarkeit, Update-Zeiten und Fehlern
        """
        status = {
            "available": self.device.available,
            "last_update_success": self.last_update_success,
            "last_update_time": self.last_update_success_time,
            "last_exception": str(self.last_exception) if self.last_exception else None,
            "firmware_version": getattr(self.device, 'firmware_version', 'Unbekannt'),
        }
        
        _LOGGER.debug("Gerätestatus abgerufen: %s", status)
        return status

    @property
    def is_available(self) -> bool:
        """Prüft ob das Gerät verfügbar ist."""
        return self.last_update_success and self.device.available

    def get_update_interval_seconds(self) -> int:
        """Gibt das Aktualisierungsintervall in Sekunden zurück."""
        if self.update_interval:
            return int(self.update_interval.total_seconds())
        return DEFAULT_POLLING_INTERVAL
