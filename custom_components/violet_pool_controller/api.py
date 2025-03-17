"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import aiohttp
from typing import Any, Dict, Optional

from .const import API_READINGS, API_SET_FUNCTION_MANUALLY

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        username: Optional[str],
        password: Optional[str],
        use_ssl: bool = True,
        timeout: int = 10,
    ):
        """Initialisiere das API-Objekt."""
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout

        # Die aiohttp.ClientSession wird extern (z.B. in __init__.py) gesetzt.
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_readings(self) -> Dict[str, Any]:
        """
        Liest aktuelle Werte vom Pool-Controller (GET).
        Beispiel: Temperatur, Pumpenstatus usw.
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}{API_READINGS}"
        _LOGGER.debug("GET readings from URL: %s", url)

        # Basic-Auth erzeugen, wenn Nutzer/Passwort existieren
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        try:
            # Timeout via asyncio
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Abrufen der Pool-Daten: %s", err)
            raise ConnectionError(f"Fehler beim Abrufen der Pool-Daten: {err}") from err

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0
    ) -> str:
        """
        Steuert einen Switch (z.B. 'PUMP', 'LIGHT', 'ECO', 'DOS_1_CL', etc.).
        
        :param key: Name des Switches, z.B. 'PUMP'
        :param action: Aktion, z.B. "ON", "OFF", "AUTO"
        :param duration: Optionaler Zeitwert, falls du am Gerät einen Timer setzen willst
        :param last_value: Optionaler Parameter (ggf. Wert, der vorher an war)
        :return: Der Text der Antwort vom Gerät (oder wirf Exception bei Fehler)
        """
        protocol = "https" if self.use_ssl else "http"
        # URL zusammenbauen, so wie du es in deinem Switch-Code gemacht hast
        url = (
            f"{protocol}://{self.host}{API_SET_FUNCTION_MANUALLY}"
            f"?{key},{action},{duration},{last_value}"
        )
        _LOGGER.debug(
            "set_switch_state -> Sende Kommando: key=%s, action=%s, duration=%d, last_value=%d, URL=%s",
            key,
            action,
            duration,
            last_value,
            url,
        )

        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    return response_text
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Setzen des Switch-Status '%s': %s", action, err)
            raise ConnectionError(f"Fehler beim Setzen des Switch-Status '{action}': {err}") from err
