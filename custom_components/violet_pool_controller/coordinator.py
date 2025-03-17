"""DataUpdateCoordinator für den Violet Pool Controller."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VioletPoolAPI  # <-- falls du es brauchst
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

    async def _async_update_data(self) -> Dict[str, Any]:
        """Methode zum Abruf der Daten (wird durch den Coordinator automatisch aufgerufen)."""
        # Hier kannst du deinen Retry-Mechanismus einbauen:
        for attempt in range(self.retries):
            try:
                # *** Anstatt direkt session.get() zu nutzen, rufst du jetzt deine API-Methode auf ***
                data = await self.api.get_readings()

                # Beispielhafter Check, ob die nötigen Keys vorhanden sind
                if not isinstance(data, dict) or "IMP1_value" not in data:
                    raise UpdateFailed(f"Unerwartetes Antwortformat: {data}")

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
