"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""

import aiohttp
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(self, host, username, password, use_ssl=True, timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout

        # Wichtig: ClientSession wird von außen (z.B. Home Assistant) übergeben
        # und in __init__.py oder an anderer Stelle initialisiert.
        self.session = None

    async def get_readings(self):
        """Beispiel: Liest aktuelle Werte vom Pool-Controller (GET)."""
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}/api/readings"  # ggf. anpassen

        _LOGGER.debug("GET readings from URL: %s", url)

        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ConnectionError(f"Fehler beim Abrufen der Pool-Daten: {err}") from err

    async def set_pump_state(self, pump_on: bool):
        """Beispiel: Schaltet die Pumpe ein/aus via POST."""
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}/api/pump"

        _LOGGER.debug("POST pump state to %s, pump_on=%s", url, pump_on)

        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )
        payload = {"pump_on": pump_on}

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.post(url, auth=auth, ssl=self.use_ssl, json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ConnectionError(f"Fehler beim Setzen des Pumpen-Status: {err}") from err
