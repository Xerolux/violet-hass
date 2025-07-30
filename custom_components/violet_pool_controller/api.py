"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import json
from typing import Any, Dict, Optional, Union

import aiohttp

from .const import (
    API_READINGS, API_SET_FUNCTION_MANUALLY, API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES, SWITCH_FUNCTIONS, COVER_FUNCTIONS, DOSING_FUNCTIONS,
    ACTION_ON, ACTION_OFF, ACTION_AUTO, ACTION_PUSH, ACTION_MAN, ACTION_COLOR,
    ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO, ACTION_LOCK, ACTION_UNLOCK,
    QUERY_ALL, TARGET_PH, TARGET_ORP, TARGET_MIN_CHLORINE, KEY_MAINTENANCE, KEY_PVSURPLUS
)

_LOGGER = logging.getLogger(__name__)

class VioletPoolAPIError(Exception):
    """Basisklasse für API-Fehler."""
    pass

class VioletPoolConnectionError(VioletPoolAPIError):
    """Verbindungsfehler zum Controller."""
    pass

class VioletPoolCommandError(VioletPoolAPIError):
    """Befehlsausführungsfehler."""
    pass

class VioletPoolAPI:
    """Kapselt Requests an den Violet Pool Controller."""

    def __init__(
        self, host: str, session: aiohttp.ClientSession,
        username: Optional[str] = None, password: Optional[str] = None,
        use_ssl: bool = True, timeout: int = 10
    ) -> None:
        """Initialisiere das API-Objekt."""
        self.host = host.strip()
        self.session = session
        self.auth = aiohttp.BasicAuth(username, password) if username and password else None
        self.base_url = f"{'https' if use_ssl else 'http'}://{self.host}"
        self.timeout = timeout

    async def api_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_query: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """Führe einen API-Request aus."""
        url = f"{self.base_url}{endpoint}" + (f"?{raw_query}" if raw_query else "")
        _LOGGER.debug("API-Anfrage: %s %s (params=%s, data=%s)", method, url, params, data)

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.request(
                    method=method, url=url, params=params, data=data, auth=self.auth, ssl=self.base_url.startswith("https")
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        _LOGGER.error("API-Fehler: HTTP %d - %s", response.status, error_text)
                        raise VioletPoolCommandError(f"HTTP {response.status}: {error_text}")

                    text = await response.text()
                    return json.loads(text) if "application/json" in response.headers.get("Content-Type", "").lower() else text

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout: %s", err)
            raise VioletPoolConnectionError(f"Timeout: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Verbindungsfehler: %s", err)
            raise VioletPoolConnectionError(f"Verbindungsfehler: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler: %s", err)
            raise VioletPoolAPIError(f"Unerwarteter Fehler: {err}") from err

    async def get_readings(self, query: str = QUERY_ALL) -> Dict[str, Any]:
        """Lese aktuelle Werte."""
        query = QUERY_ALL if not query or not isinstance(query, str) else query
        result = await self.api_request(endpoint=API_READINGS, raw_query=query if query != QUERY_ALL else None)
        return self._normalize_response(result)

    async def set_switch_state(self, key: str, action: str, duration: int = 0, last_value: int = 0) -> Dict[str, Any]:
        """Steuere einen Switch."""
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, KEY_MAINTENANCE, KEY_PVSURPLUS}
        if key not in valid_keys:
            raise VioletPoolCommandError(f"Ungültiger Key: {key}. Gültige Keys: {', '.join(valid_keys)}")
        raw_query = f"{key},{action},{max(0, duration)},{max(0, last_value)}"
        result = await self.api_request(endpoint=API_SET_FUNCTION_MANUALLY, raw_query=raw_query)
        return self._normalize_response(result)

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuere die Pool-Abdeckung."""
        if action not in COVER_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültige Aktion: {action}. Gültige Aktionen: {', '.join(COVER_FUNCTIONS.keys())}")
        return await self.set_switch_state(COVER_FUNCTIONS[action], ACTION_PUSH, 0, 0)

    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere PV-Überschussmodus."""
        action = ACTION_ON if active else ACTION_OFF
        pump_speed_val = max(1, min(3, pump_speed)) if active and pump_speed else 0
        return await self.set_switch_state(KEY_PVSURPLUS, action, pump_speed_val, 0)

    async def set_dosing_parameters(self, dosing_type: str, parameter_name: str, value: Union[str, int, float]) -> Dict[str, Any]:
        """Setze Dosierungsparameter."""
        raw_query = f"{dosing_type},{parameter_name},{value}"
        result = await self.api_request(endpoint=API_SET_DOSING_PARAMETERS, raw_query=raw_query)
        return self._normalize_response(result)

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löse manuelle Dosierung aus."""
        duration_s = max(1, min(3600, duration_seconds))
        dosing_api_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_api_key:
            raise VioletPoolCommandError(f"Ungültiger Dosierungstyp: {dosing_type}. Gültige Typen: {', '.join(DOSING_FUNCTIONS.keys())}")
        return await self.set_switch_state(dosing_api_key, ACTION_MAN, duration_s, 0)

    async def set_target_value(self, target_type: str, value: Union[float, int]) -> Dict[str, Any]:
        """Setze einen Sollwert."""
        self._validate_target_value(target_type, value)
        raw_query = f"{target_type},{value}"
        result = await self.api_request(endpoint=API_SET_TARGET_VALUES, raw_query=raw_query)
        return self._normalize_response(result)

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setze pH-Sollwert."""
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setze Redox-Sollwert."""
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setze minimalen Chlorgehalt."""
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere Wartungsmodus."""
        return await self.set_switch_state(KEY_MAINTENANCE, ACTION_ON if enabled else ACTION_OFF)

    async def start_water_analysis(self) -> Dict[str, Any]:
        """Starte Wasseranalyse."""
        result = await self.api_request(endpoint="/startWaterAnalysis")
        return self._normalize_response(result)

    async def set_light_color_pulse(self) -> Dict[str, Any]:
        """Löse Lichtfarbenpuls aus."""
        if "LIGHT" not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError("LIGHT key not defined in SWITCH_FUNCTIONS")
        return await self.set_switch_state("LIGHT", ACTION_COLOR, 0, 0)

    async def set_all_dmx_scenes(self, action: str) -> Dict[str, Any]:
        """Setze alle DMX-Szenen."""
        valid_actions = {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}
        if action not in valid_actions:
            raise VioletPoolCommandError(f"Ungültige Aktion: {action}. Gültige Aktionen: {', '.join(valid_actions)}")
        if "DMX_SCENE1" not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError("DMX_SCENE1 not defined in SWITCH_FUNCTIONS")
        return await self.set_switch_state("DMX_SCENE1", action, 0, 0)

    async def set_digital_input_rule_lock(self, rule_key: str, lock: bool) -> Dict[str, Any]:
        """Sperre/Entsperre digitale Eingaberegel."""
        if not rule_key.startswith("DIRULE_") or rule_key not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültiger Key: {rule_key}. Gültige Keys: {', '.join(k for k in SWITCH_FUNCTIONS if k.startswith('DIRULE_'))}")
        return await self.set_switch_state(rule_key, ACTION_LOCK if lock else ACTION_UNLOCK, 0, 0)

    async def trigger_digital_input_rule(self, rule_key: str) -> Dict[str, Any]:
        """Triggere digitale Eingaberegel."""
        if not rule_key.startswith("DIRULE_") or rule_key not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültiger Key: {rule_key}. Gültige Keys: {', '.join(k for k in SWITCH_FUNCTIONS if k.startswith('DIRULE_'))}")
        return await self.set_switch_state(rule_key, ACTION_PUSH, 0, 0)

    async def set_device_temperature(self, device_type: str, temperature: float) -> Dict[str, Any]:
        """Setze Zieltemperatur für ein Gerät."""
        raw_query = f"{device_type},{temperature}"
        result = await self.api_request(endpoint="/set_temperature", raw_query=raw_query)
        return self._normalize_response(result)

    def _normalize_response(self, result: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Normalisiere API-Antworten."""
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"response": result, "success": "OK" in result.upper()}
        return result

    def _validate_target_value(self, target_type: str, value: Union[float, int]) -> None:
        """Validiere Sollwerte."""
        ranges = {
            TARGET_PH: (6.8, 7.8, "pH-Sollwert", "6.8-7.8"),
            TARGET_ORP: (600, 800, "ORP-Sollwert", "600-800 mV"),
            TARGET_MIN_CHLORINE: (0.2, 2.0, "Chlor-Sollwert", "0.2-2.0 mg/l")
        }
        if target_type in ranges:
            min_val, max_val, name, range_str = ranges[target_type]
            if value < min_val or value > max_val:
                _LOGGER.warning("%s %s außerhalb des empfohlenen Bereichs (%s)", name, value, range_str)
