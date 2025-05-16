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
    """Basisklasse für API-Fehler."""
    pass

class VioletPoolConnectionError(VioletPoolAPIError):
    """Fehler bei der Verbindung zum Controller."""
    pass

class VioletPoolCommandError(VioletPoolAPIError):
    """Fehler bei der Befehlsausführung."""
    pass

class VioletPoolAPI:
    """Kapselt Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        timeout: int = 10,
    ) -> None:
        """Initialisiere das API-Objekt.

        Args:
            host: IP-Adresse oder Hostname.
            session: aiohttp ClientSession.
            username: Optionaler Benutzername.
            password: Optionales Passwort.
            use_ssl: HTTPS (True) oder HTTP (False).
            timeout: Timeout in Sekunden.
        """
        self.host = host.strip()
        self.session = session
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.protocol = "https" if self.use_ssl else "http"
        self.base_url = f"{self.protocol}://{self.host}"
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None

    async def api_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        raw_query: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Führe einen API-Request aus.

        Args:
            endpoint: API-Endpunkt (z.B. '/getReadings').
            method: HTTP-Methode ('GET' oder 'POST').
            params: GET-Parameter.
            data: POST-Daten.
            raw_query: Roher Query-String.

        Returns:
            Union[Dict[str, Any], str]: JSON oder Text.

        Raises:
            VioletPoolConnectionError: Bei Verbindungsfehlern.
            VioletPoolCommandError: Bei HTTP-Fehlern.
            VioletPoolAPIError: Bei allgemeinen Fehlern.
        """
        url = f"{self.base_url}{endpoint}"
        if raw_query:
            url += f"?{raw_query}"

        _LOGGER.debug(
            "API-Anfrage: %s %s (params=%s, data=%s, raw_query=%s)",
            method, url, params, data, raw_query
        )

        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    auth=self.auth,
                    ssl=self.use_ssl,
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        _LOGGER.error("API-Fehler: HTTP %d - %s", response.status, error_text)
                        raise VioletPoolCommandError(f"HTTP {response.status}: {error_text}")

                    content_type = response.headers.get("Content-Type", "").lower()
                    text = await response.text()

                    if "application/json" in content_type:
                        return await response.json()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        _LOGGER.debug("Kein JSON, Rückgabe als Text: %s", text)
                        return text

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout bei Verbindung zu %s: %s", self.host, err)
            raise VioletPoolConnectionError(f"Timeout bei Verbindung zu {self.host}: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Verbindungsfehler zu %s: %s", self.host, err)
            raise VioletPoolConnectionError(f"Verbindungsfehler zu {self.host}: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler bei API-Anfrage: %s", err)
            raise VioletPoolAPIError(f"Unerwarteter Fehler: {err}") from err

    async def get_readings(self, query: str = "ALL") -> Dict[str, Any]:
        """Lese aktuelle Werte vom Controller.

        Args:
            query: Abfrage (z.B. 'pH_value') oder 'ALL'.

        Returns:
            Dict[str, Any]: API-Daten.
        """
        if not query or not isinstance(query, str):
            query = "ALL"
        result = await self.api_request(endpoint=API_READINGS, raw_query=query if query != "ALL" else None)
        return self._normalize_response(result)

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0,
    ) -> Dict[str, Any]:
        """Steuere einen Switch.

        Args:
            key: Switch-Name (z.B. 'PUMP').
            action: Aktion ('ON', 'OFF', 'AUTO').
            duration: Dauer in Sekunden.
            last_value: Letzter Wert.

        Returns:
            Dict[str, Any]: Antwort.
        """
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, "MAINTENANCE"}
        if key not in valid_keys:
            raise VioletPoolCommandError(f"Ungültiger Switch-Key: {key}")
        raw_query = f"{key},{action},{max(0, duration)},{max(0, last_value)}"
        result = await self.api_request(endpoint=API_SET_FUNCTION_MANUALLY, raw_query=raw_query, method="GET")
        return self._normalize_response(result)

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuere die Pool-Abdeckung.

        Args:
            action: 'OPEN', 'CLOSE' oder 'STOP'.

        Returns:
            Dict[str, Any]: Antwort.
        """
        valid_actions = {"OPEN", "CLOSE", "STOP"}
        if action not in valid_actions:
            raise VioletPoolCommandError(f"Ungültige Cover-Aktion: {action}")
        cover_key = COVER_FUNCTIONS.get(action)
        if not cover_key:
            raise VioletPoolCommandError(f"Cover-Aktion {action} nicht unterstützt")
        return await self.set_switch_state(cover_key, "PUSH", 0, 0)

    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere PV-Überschussmodus.

        Args:
            active: True zum Aktivieren, False zum Deaktivieren.
            pump_speed: Pumpendrehzahl (1-3, optional).

        Returns:
            Dict[str, Any]: Antwort.
        """
        action = "ON" if active else "OFF"
        pump_speed = max(1, min(3, pump_speed)) if active and pump_speed else 0
        return await self.set_switch_state("PVSURPLUS", action, pump_speed, 0)

    async def set_dosing_parameters(
        self,
        dosing_type: str,
        parameter_name: str,
        value: Union[str, int, float],
    ) -> Dict[str, Any]:
        """Setze Dosierungsparameter.

        Args:
            dosing_type: Typ (z.B. 'pH-').
            parameter_name: Parametername.
            value: Neuer Wert.

        Returns:
            Dict[str, Any]: Antwort.
        """
        raw_query = f"{dosing_type},{parameter_name},{value}"
        result = await self.api_request(endpoint=API_SET_DOSING_PARAMETERS, raw_query=raw_query, method="GET")
        return self._normalize_response(result)

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löse manuelle Dosierung aus.

        Args:
            dosing_type: Typ (z.B. 'pH+').
            duration_seconds: Dauer in Sekunden (1-3600).

        Returns:
            Dict[str, Any]: Antwort.
        """
        duration_seconds = max(1, min(3600, duration_seconds))
        dosing_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_key:
            raise VioletPoolCommandError(f"Ungültiger Dosierungstyp: {dosing_type}")
        return await self.set_switch_state(dosing_key, "MAN", duration_seconds, 0)

    async def set_target_value(self, target_type: str, value: Union[float, int]) -> Dict[str, Any]:
        """Setze einen Sollwert.

        Args:
            target_type: Typ ('pH', 'ORP', etc.).
            value: Neuer Wert.

        Returns:
            Dict[str, Any]: Antwort.
        """
        self._validate_target_value(target_type, value)
        raw_query = f"{target_type},{value}"
        result = await self.api_request(endpoint=API_SET_TARGET_VALUES, raw_query=raw_query, method="GET")
        return self._normalize_response(result)

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setze den pH-Sollwert."""
        value = float(value)
        return await self.set_target_value("pH", value)

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setze den Redox-Sollwert."""
        value = int(value)
        return await self.set_target_value("ORP", value)

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setze den minimalen Chlorgehalt."""
        value = float(value)
        return await self.set_target_value("MinChlorine", value)

    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere Wartungsmodus."""
        action = "ON" if enabled else "OFF"
        return await self.set_switch_state("MAINTENANCE", action)

    async def start_water_analysis(self) -> Dict[str, Any]:
        """Starte Wasseranalyse."""
        result = await self.api_request(endpoint="/startWaterAnalysis")
        return self._normalize_response(result)

    def _normalize_response(self, result: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Normalisiere API-Antworten."""
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"response": result, "success": "OK" in result or "SUCCESS" in result}
        return result

    def _validate_target_value(self, target_type: str, value: Union[float, int]) -> None:
        """Validiere Sollwerte."""
        if target_type == "pH" and (value < 6.8 or value > 7.8):
            _LOGGER.warning("pH-Sollwert %s außerhalb des empfohlenen Bereichs (6.8-7.8)", value)
        elif target_type == "ORP" and (value < 600 or value > 800):
            _LOGGER.warning("ORP-Sollwert %s außerhalb des empfohlenen Bereichs (600-800 mV)", value)
        elif target_type == "MinChlorine" and (value < 0.2 or value > 2.0):
            _LOGGER.warning("Chlor-Sollwert %s außerhalb des empfohlenen Bereichs (0.2-2.0 mg/l)", value)