"""DataUpdateCoordinator für den Violet Pool Controller."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VioletPoolAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordiniert das zyklische Abrufen der Daten vom Violet Pool Controller."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], api: VioletPoolAPI) -> None:
        """Initialisieren."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config['device_id']}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )
        self.config = config
        self.api = api
        self.retries = config.get("retries", 3)
        self.device_id = config.get("device_id", 1)
        self.device_name = config.get("device_name", "Violet Pool Controller")

    async def _async_update_data(self) -> Dict[str, Any]:
        """Methode zum Abruf der Daten (wird durch den Coordinator automatisch aufgerufen)."""
        # Hier kannst du deinen Retry-Mechanismus einbauen:
        for attempt in range(self.retries):
            try:
                # Hole alle Daten vom Pool-Controller
                data = await self.api.get_readings()

                # Beispielhafter Check, ob die nötigen Keys vorhanden sind
                if not isinstance(data, dict):
                    raise UpdateFailed(f"Unerwartetes Antwortformat: {data}")

                # Validiere einige wichtige Daten für Diagnosezwecke
                self._validate_data(data)

                # Bei Erfolg returnst du sofort die Daten
                return data

            except (ConnectionError, ValueError) as err:
                _LOGGER.error(
                    "Versuch %s/%s schlug fehl - Fehler beim Abruf der Daten: %s",
                    attempt + 1,
                    self.retries,
                    err,
                )
                if attempt + 1 == self.retries:
                    # Alle Versuche aufgebraucht => UpdateFailed werfen
                    raise UpdateFailed(f"Abbruch nach {self.retries} Versuchen: {err}")

                # Exponentielles Backoff oder feste Wartezeit
                await asyncio.sleep(2 ** attempt)

        # Theoretisch kommst du hier gar nicht mehr hin,
        # weil du bei Fehlern in der letzten Schleife 'raise' machst.
        raise UpdateFailed("Datenaktualisierung nicht möglich (unbekannter Fehler).")

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validiere die empfangenen Daten auf wichtige Felder."""
        # Firmware-Version sollte vorhanden sein
        if "fw" not in data:
            _LOGGER.warning("Firmware-Version nicht in API-Antwort gefunden")

        # Überprüfe, ob mindestens einige grundlegende Werte vorhanden sind
        # Dies hilft bei der Diagnose von API-Änderungen oder Problemen
        essential_fields = [
            "PUMP",  # Filterpumpe
            "pH_value",  # pH-Wert
            "onewire1_value"  # Wassertemperatur
        ]
        
        missing = [field for field in essential_fields if field not in data]
        if missing:
            _LOGGER.warning("Fehlende Werte in API-Antwort: %s", ", ".join(missing))
