"""DataUpdateCoordinator für den Violet Pool Controller."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional, List, Set, Union

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .api import VioletPoolAPI, VioletPoolAPIError, VioletPoolConnectionError
from .const import (
    DOMAIN,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordiniert das zyklische Abrufen der Daten vom Violet Pool Controller."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        device: Any,
        name: str,
        polling_interval: int = DEFAULT_POLLING_INTERVAL
    ) -> None:
        """Initialisiert den Coordinator.
        
        Args:
            hass: Home Assistant-Instanz
            device: Die Pool Controller Geräteinstanz
            name: Ein eindeutiger Name für den Coordinator
            polling_interval: Abfrageintervall in Sekunden
        """
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=polling_interval),
        )
        
        self.device = device
        self.last_exception: Optional[Exception] = None
        self.last_failure_time: Optional[float] = None
        
        _LOGGER.debug(
            "VioletPoolDataUpdateCoordinator für %s initialisiert (Interval: %d s)",
            name,
            polling_interval
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Holt Daten vom Gerät ab.
        
        Diese Methode wird vom Coordinator automatisch aufgerufen.
        
        Returns:
            Dict[str, Any]: Die aktuellen Gerätedaten
            
        Raises:
            UpdateFailed: Wenn Daten nicht abgerufen werden konnten
        """
        try:
            # Holt die Daten direkt vom Gerät ab
            return await self.device.async_update()
                
        except VioletPoolConnectionError as err:
            # Verbindungsprobleme speziell behandeln
            self.last_exception = err
            error_msg = f"Verbindungsfehler: {err}"
            _LOGGER.error(error_msg)
            raise UpdateFailed(error_msg) from err
            
        except VioletPoolAPIError as err:
            # API-Fehler speziell behandeln
            self.last_exception = err
            error_msg = f"API-Fehler: {err}"
            _LOGGER.error(error_msg)
            raise UpdateFailed(error_msg) from err
            
        except Exception as err:
            # Sonstige Fehler
            self.last_exception = err
            error_msg = f"Unerwarteter Fehler bei Datenaktualisierung: {err}"
            _LOGGER.exception(error_msg)
            raise UpdateFailed(error_msg) from err

    def get_device_status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Status des Geräts zurück.
        
        Returns:
            Dict[str, Any]: Statusinformationen zum Gerät
        """
        return {
            "available": self.device.available,
            "last_update_success": self.last_update_success,
            "last_update_time": self.last_update_success_time,
            "last_exception": str(self.last_exception) if self.last_exception else None,
            "firmware_version": self.device.firmware_version,
        }
