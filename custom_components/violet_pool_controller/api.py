"""API für die Kommunikation mit dem Violet Pool Controller."""
import asyncio
import logging
from typing import Any, Dict

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_READINGS, API_PARAMETERS, CONF_API_URL, CONF_USE_SSL

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
ERROR_THRESHOLD = 5  # Log error every 5 failed attempts
THROTTLE_PERIOD = 300  # Reset error count after 5 minutes of success


class VioletPoolControllerAPI:
    """Klasse für die API-Kommunikation."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        use_ssl: bool = False,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialisiere die API."""
        self.hass = hass
        self._host = host
        self._use_ssl = use_ssl
        self._protocol = "https" if use_ssl else "http"
        self._base_url = f"{self._protocol}://{self._host}"
        
        # Session Management
        self._session = session or async_get_clientsession(hass)
        
        # Throttled Logging
        self._error_count = 0
        self._last_error_log_time = 0.0

    # =================================================================
    # NEUE ZENTRALISIERTE URL-HELPER METHODE
    # =================================================================
    def _build_url(self, endpoint: str) -> str:
        """
        Baut die vollständige API-URL für einen gegebenen Endpunkt.
        
        Args:
            endpoint: Der API-Endpunkt (z.B. "/getReadings").
            
        Returns:
            Die vollständige URL als String.
        """
        return f"{self._base_url}{endpoint}"

    def _throttled_log_error(self, error_message: str) -> None:
        """
        Protokolliert Fehler nur gelegentlich, um Log-Spam zu vermeiden.
        """
        self._error_count += 1
        current_time = asyncio.get_event_loop().time()
        
        if self._error_count >= ERROR_THRESHOLD and (current_time - self._last_error_log_time > THROTTLE_PERIOD):
            _LOGGER.error(
                "Wiederholter API-Fehler: %s (Diese Meldung wird für %d Sekunden unterdrückt)",
                error_message,
                THROTTLE_PERIOD,
            )
            self._last_error_log_time = current_time
            self._error_count = 0  # Reset after logging
        else:
            _LOGGER.debug("API-Fehler (unterdrückt): %s", error_message)

    async def _request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Führt eine API-Anfrage aus und behandelt Fehler."""
        try:
            response = await self._session.request(
                method, url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT), **kwargs
            )
            response.raise_for_status()
            
            # Reset error count on success
            if self._error_count > 0:
                _LOGGER.info("API-Verbindung zu %s wiederhergestellt.", self._host)
                self._error_count = 0

            return response
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout bei der Verbindung zu {self._host}"
            self._throttled_log_error(error_msg)
            raise ConnectionError(error_msg) from asyncio.TimeoutError
            
        except aiohttp.ClientError as err:
            error_msg = f"Netzwerkfehler bei der Verbindung zu {self._host}: {err}"
            self._throttled_log_error(error_msg)
            raise ConnectionError(error_msg) from err

    async def async_get_readings(self) -> Dict[str, Any]:
        """Ruft alle Messwerte vom Controller ab."""
        # URL wird jetzt mit der Helper-Methode erstellt
        url = self._build_url(API_READINGS)
        params = {"ALL": ""}
        
        _LOGGER.debug("Rufe Messwerte ab von: %s", url)
        response = await self._request("get", url, params=params)
        return await response.json()

    async def async_set_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sendet Parameter an den Controller."""
        # URL wird jetzt mit der Helper-Methode erstellt
        url = self._build_url(API_PARAMETERS)
        
        _LOGGER.debug("Sende Parameter an %s: %s", url, params)
        response = await self._request("get", url, params=params)
        return await response.json()

    async def async_test_connection(self) -> bool:
        """Testet die Verbindung zum Controller."""
        try:
            await self.async_get_readings()
            return True
        except ConnectionError:
            return False
