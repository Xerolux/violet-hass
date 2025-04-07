"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import json
from typing import Any, Dict, Optional, Union

import aiohttp
import async_timeout

from .const import (
    API_READINGS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES,
    SWITCH_FUNCTIONS,
    COVER_FUNCTIONS,
    DOSING_FUNCTIONS,
)

_LOGGER = logging.getLogger(__name__)

class VioletPoolAPIError(Exception):
    """Basisklasse für API-Fehler des Violet Pool Controllers."""
    pass

class VioletPoolConnectionError(VioletPoolAPIError):
    """Fehler bei der Verbindung zum Violet Pool Controller."""
    pass

class VioletPoolCommandError(VioletPoolAPIError):
    """Fehler bei der Ausführung eines Befehls am Violet Pool Controller."""
    pass

class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        timeout: int = 10,
    ):
        """Initialisiere das API-Objekt.

        Args:
            host: IP-Adresse oder Hostname des Controllers
            session: Aktive aiohttp.ClientSession
            username: Optionaler Benutzername für Authentifizierung
            password: Optionales Passwort für Authentifizierung
            use_ssl: True für HTTPS, False für HTTP
            timeout: Timeout in Sekunden für API-Anfragen
        """
        self.host = host.strip('/')
        self.session = session
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.protocol = "https" if use_ssl else "http"
        self.base_url = f"{self.protocol}://{self.host}"
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None

    async def api_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        raw_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Führt einen API-Request aus und gibt das Ergebnis zurück.

        Args:
            endpoint: API-Endpunkt (z.B. "/getReadings")
            method: HTTP-Methode ("GET" oder "POST")
            params: Dictionary mit GET-Parametern
            data: Dictionary mit POST-Daten (als JSON gesendet)
            raw_query: Roher Query-String (alternative zu params)

        Returns:
            Dict[str, Any]: Normalisierte Antwort als Dictionary

        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Befehlsfehlern
            VioletPoolAPIError: Bei sonstigen Fehlern
        """
        url = f"{self.base_url}{endpoint}"
        if raw_query:
            url = f"{url}?{raw_query}"

        _LOGGER.debug(
            "%s request to %s (params=%s, data=%s, raw_query=%s)",
            method,
            url,
            params,
            data,
            raw_query,
        )

        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data if method == "POST" else None,
                    auth=self.auth,
                    ssl=self.use_ssl,
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text}"
                        _LOGGER.error("API-Fehler: %s", error_msg)
                        raise VioletPoolCommandError(error_msg)

                    content_type = response.headers.get("Content-Type", "").lower()
                    text = await response.text()

                    if "application/json" in content_type or not text.strip().startswith("<"):
                        try:
                            result = json.loads(text)
                            _LOGGER.debug("API-JSON-Antwort: %s", result)
                            return result if isinstance(result, dict) else {"response": result, "success": True}
                        except json.JSONDecodeError:
                            _LOGGER.debug("API-Text-Antwort (kein JSON): %s", text)
                            return {"response": text, "success": "OK" in text or "SUCCESS" in text}
                    else:
                        _LOGGER.debug("API-Text-Antwort: %s", text)
                        return {"response": text, "success": "OK" in text or "SUCCESS" in text}

        except asyncio.TimeoutError as err:
            error_msg = f"Timeout bei Verbindung zu {self.host}: {err}"
            _LOGGER.error(error_msg)
            raise VioletPoolConnectionError(error_msg) from err
        except aiohttp.ClientError as err:
            error_msg = f"Verbindungsfehler zu {self.host}: {err}"
            _LOGGER.error(error_msg)
            raise VioletPoolConnectionError(error_msg) from err
        except Exception as err:
            error_msg = f"Unerwarteter Fehler bei API-Anfrage: {err}"
            _LOGGER.exception(error_msg)
            raise VioletPoolAPIError(error_msg) from err

    async def get_readings(self, query: str = "ALL") -> Dict[str, Any]:
        """Liest aktuelle Werte vom Pool-Controller.

        Args:
            query: Spezifische Abfrage (z.B. 'pH_value,orp_value' oder 'ALL')

        Returns:
            Dict[str, Any]: Abgefragte Werte
        """
        return await self.api_request(
            endpoint=API_READINGS,
            raw_query=query if query != "ALL" else None,
        )

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0,
    ) -> Dict[str, Any]:
        """Steuert einen Switch (z.B. 'PUMP', 'LIGHT').

        Args:
            key: Name des Switches (z.B. 'PUMP')
            action: Aktion ("ON", "OFF", "AUTO", "MAN", "PUSH")
            duration: Dauer in Sekunden (falls anwendbar)
            last_value: Letzter Wert (falls anwendbar)

        Returns:
            Dict[str, Any]: Antwort vom Gerät

        Raises:
            VioletPoolCommandError: Bei ungültigem Switch-Key
        """
        valid_keys = {**SWITCH_FUNCTIONS, **DOSING_FUNCTIONS, "MAINTENANCE"}
        if key not in valid_keys:
            error_msg = f"Ungültiger Switch-Key: {key}"
            _LOGGER.warning(error_msg)
            raise VioletPoolCommandError(error_msg)

        raw_query = f"{key},{action},{duration},{last_value}"
        return await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY,
            raw_query=raw_query,
            method="GET",
        )

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuert die Pool-Abdeckung.

        Args:
            action: "OPEN", "CLOSE", "STOP"

        Returns:
            Dict[str, Any]: Antwort vom Gerät
        """
        valid_actions = ["OPEN", "CLOSE", "STOP"]
        if action not in valid_actions:
            error_msg = f"Ungültige Cover-Aktion: {action}"
            _LOGGER.error(error_msg)
            raise VioletPoolCommandError(error_msg)

        cover_key = COVER_FUNCTIONS.get(action)
        if cover_key:
            return await self.set_switch_state(cover_key, "PUSH", 0, 0)

        error_msg = f"Cover-Aktion {action} nicht unterstützt"
        _LOGGER.error(error_msg)
        raise VioletPoolCommandError(error_msg)

    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviert oder deaktiviert den Photovoltaik-Überschussmodus.

        Args:
            active: True für aktivieren, False für deaktivieren
            pump_speed: Pumpendrehzahl (1-3, optional)

        Returns:
            Dict[str, Any]: Antwort vom Gerät
        """
        action = "ON" if active else "OFF"
        pump_speed = max(1, min(3, pump_speed)) if active and pump_speed is not None else 0
        return await self.set_switch_state("PVSURPLUS", action, pump_speed, 0)

    async def set_dosing_parameters(
        self,
        dosing_type: str,
        parameter_name: str,
        value: Union[str, int, float],
    ) -> Dict[str, Any]:
        """Setzt Dosierungsparameter.

        Args:
            dosing_type: Dosierungstyp (z.B. "pH-", "pH+", "Chlor")
            parameter_name: Name des Parameters
            value: Neuer Wert

        Returns:
            Dict[str, Any]: Antwort vom Gerät
        """
        raw_query = f"{dosing_type},{parameter_name},{value}"
        return await self.api_request(
            endpoint=API_SET_DOSING_PARAMETERS,
            raw_query=raw_query,
            method="GET",
        )

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löst eine manuelle Dosierung aus.

        Args:
            dosing_type: Dosierungstyp (z.B. "pH-", "pH+", "Chlor")
            duration_seconds: Dauer in Sekunden (1-3600)

        Returns:
            Dict[str, Any]: Antwort vom Gerät
        """
        dosing_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_key:
            error_msg = f"Ungültiger Dosierungstyp: {dosing_type}"
            _LOGGER.error(error_msg)
            raise VioletPoolCommandError(error_msg)

        duration_seconds = max(1, min(3600, duration_seconds))
        return await self.set_switch_state(dosing_key, "MAN", duration_seconds, 0)

    async def set_target_value(
        self,
        target_type: str,
        value: Union[float, int],
    ) -> Dict[str, Any]:
        """Setzt einen Sollwert (z.B. pH, ORP).

        Args:
            target_type: Typ des Sollwerts ("pH", "ORP", "MinChlorine")
            value: Neuer Wert

        Returns:
            Dict[str, Any]: Antwort vom Gerät
        """
        if target_type == "pH" and not 6.8 <= value <= 7.8:
            _LOGGER.warning("pH-Sollwert %f außerhalb des Bereichs 6.8-7.8", value)
        elif target_type == "ORP" and not 600 <= value <= 800:
            _LOGGER.warning("ORP-Sollwert %d außerhalb des Bereichs 600-800 mV", value)
        elif target_type == "MinChlorine" and not 0.2 <= value <= 2.0:
            _LOGGER.warning("Chlor-Sollwert %f außerhalb des Bereichs 0.2-2.0 mg/l", value)

        raw_query = f"{target_type},{value}"
        return await self.api_request(
            endpoint=API_SET_TARGET_VALUES,
            raw_query=raw_query,
            method="GET",
        )

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setzt den pH-Sollwert."""
        return await self.set_target_value("pH", round(float(value), 1))

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setzt den Redox-Sollwert (ORP)."""
        return await self.set_target_value("ORP", int(value))

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setzt den minimalen Chlorgehalt."""
        return await self.set_target_value("MinChlorine", round(float(value), 1))

    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviert oder deaktiviert den Wartungsmodus."""
        return await self.set_switch_state("MAINTENANCE", "ON" if enabled else "OFF")

    async def start_water_analysis(self) -> Dict[str, Any]:
        """Startet eine Wasseranalyse."""
        return await self.api_request(endpoint="/startWaterAnalysis")
