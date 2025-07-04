"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import json
from typing import Any, Dict, Optional, Union

import aiohttp

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

# HTTP Methods
HTTP_GET = "GET"
HTTP_POST = "POST"

# Actions
ACTION_ON = "ON"
ACTION_OFF = "OFF"
ACTION_AUTO = "AUTO"
ACTION_PUSH = "PUSH"
ACTION_MAN = "MAN"
ACTION_COLOR = "COLOR"  # For light color pulse
ACTION_ALLON = "ALLON"  # For DMX bulk ON
ACTION_ALLOFF = "ALLOFF" # For DMX bulk OFF
ACTION_ALLAUTO = "ALLAUTO" # For DMX bulk AUTO
ACTION_LOCK = "LOCK"    # For DIRULE lock
ACTION_UNLOCK = "UNLOCK" # For DIRULE unlock

# Query types
QUERY_ALL = "ALL"

# Target types
TARGET_PH = "pH"
TARGET_ORP = "ORP"
TARGET_MIN_CHLORINE = "MinChlorine"

# Special Keys
KEY_MAINTENANCE = "MAINTENANCE"
KEY_PVSURPLUS = "PVSURPLUS"


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
        method: str = HTTP_GET,
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
            async with asyncio.timeout(self.timeout):
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
            query: Abfrage (z.B. 'pH_value') oder QUERY_ALL.
            query: Abfrage (z.B. 'pH_value') oder QUERY_ALL.

        Returns:
            Dict[str, Any]: API-Daten.
        """
        if not query or not isinstance(query, str):
            query = QUERY_ALL
        result = await self.api_request(endpoint=API_READINGS, raw_query=query if query != QUERY_ALL else None)
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
            key: Switch-Name (z.B. 'PUMP', a key from SWITCH_FUNCTIONS, DOSING_FUNCTIONS, or KEY_MAINTENANCE, KEY_PVSURPLUS).
                 The key determines the specific device or function to control.
            action: Action string (e.g., ACTION_ON, ACTION_OFF, ACTION_AUTO, ACTION_PUSH, ACTION_MAN,
                 ACTION_COLOR, ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO, ACTION_LOCK, ACTION_UNLOCK).
                 The specific action to perform on the given key.
            duration: Dauer in Sekunden (WERT_1 in API docs). Its meaning depends on the 'key' and 'action':
                 - For timed operations (e.g., manual dosing, some light effects): Duration of the action.
                 - For 'PVSURPLUS': Represents RPM for the pump (speed 1-3).
                 - For many simple switches or actions like 'ON'/'OFF'/'AUTO': Often 0 or ignored.
                 - For 'LIGHT' with 'COLOR' action: 0.
                 - For DMX bulk operations ('ALLON', 'ALLOFF', 'ALLAUTO'): 0.
                 - For 'DIRULE_X' with 'LOCK'/'UNLOCK': 0.
            last_value: Letzter Wert (WERT_2 in API docs). Its meaning also depends on the 'key' and 'action':
                 - For 'PUMP' (variable speed pumps): Represents RPM or speed level.
                 - For 'PVSURPLUS': Not used (typically 0).
                 - For most other switches/actions: Often 0 or ignored.
                 - For 'LIGHT' with 'COLOR' action: 0.
                 - For DMX bulk operations ('ALLON', 'ALLOFF', 'ALLAUTO'): 0.
                 - For 'DIRULE_X' with 'LOCK'/'UNLOCK': 0.
                 Refer to the device manual for /setFunctionManually for specific key/action combinations.

        Returns:
            Dict[str, Any]: Antwort.
        """
        # PVSURPLUS is also a valid key here, though it has a dedicated method.
        # MAINTENANCE is also a valid key.
        # DMX_SCENEX and DIRULE_X keys (used by specialized methods) are part of SWITCH_FUNCTIONS.
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, KEY_MAINTENANCE, KEY_PVSURPLUS}
        if key not in valid_keys:
            raise VioletPoolCommandError(f"Ungültiger Switch-Key: {key}. Key muss in SWITCH_FUNCTIONS, DOSING_FUNCTIONS, oder einer der speziellen Keys sein.")

        raw_query = f"{key},{action},{max(0, duration)},{max(0, last_value)}"
        result = await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY, raw_query=raw_query, method=HTTP_GET
        )
        return self._normalize_response(result)

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuere die Pool-Abdeckung.

        Args:
            action: Action string, must be a key in COVER_FUNCTIONS (e.g., "OPEN", "CLOSE", "STOP").

        Returns:
            Dict[str, Any]: Antwort.
        """
        if action not in COVER_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültige Cover-Aktion: {action}. Gültige Aktionen: {', '.join(COVER_FUNCTIONS.keys())}")
        cover_api_key = COVER_FUNCTIONS[action]
        return await self.set_switch_state(cover_api_key, ACTION_PUSH, 0, 0)

    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere PV-Überschussmodus.

        Args:
            active: True zum Aktivieren, False zum Deaktivieren.
            pump_speed: Pumpendrehzahl (1-3, optional).

        Returns:
            Dict[str, Any]: Antwort.
        """
        action = ACTION_ON if active else ACTION_OFF
        pump_speed_val = max(1, min(3, pump_speed)) if active and pump_speed is not None else 0
        return await self.set_switch_state(KEY_PVSURPLUS, action, pump_speed_val, 0)

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
        result = await self.api_request(
            endpoint=API_SET_DOSING_PARAMETERS, raw_query=raw_query, method=HTTP_GET
        )
        return self._normalize_response(result)

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löse manuelle Dosierung aus.

        Args:
            dosing_type: Typ (z.B. 'pH+'), must be a key in DOSING_FUNCTIONS.
            duration_seconds: Dauer in Sekunden (1-3600).

        Returns:
            Dict[str, Any]: Antwort.
        """
        duration_s = max(1, min(3600, duration_seconds))
        dosing_api_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_api_key:
            raise VioletPoolCommandError(
                f"Ungültiger Dosierungstyp: {dosing_type}. "
                f"Gültige Typen: {', '.join(DOSING_FUNCTIONS.keys())}"
            )
        return await self.set_switch_state(dosing_api_key, ACTION_MAN, duration_s, 0)

    async def set_target_value(self, target_type: str, value: Union[float, int]) -> Dict[str, Any]:
        """Setze einen Sollwert.

        Args:
            target_type: Typ des Sollwerts (z.B. TARGET_PH, TARGET_ORP, TARGET_MIN_CHLORINE).
            value: Neuer Wert.

        Returns:
            Dict[str, Any]: Antwort.
        """
        self._validate_target_value(target_type, value)
        raw_query = f"{target_type},{value}"
        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES, raw_query=raw_query, method=HTTP_GET
        )
        return self._normalize_response(result)

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setze den pH-Sollwert."""
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setze den Redox-Sollwert."""
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setze den minimalen Chlorgehalt."""
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere Wartungsmodus."""
        action = ACTION_ON if enabled else ACTION_OFF
        return await self.set_switch_state(KEY_MAINTENANCE, action)

    async def start_water_analysis(self) -> Dict[str, Any]:
        """Starte Wasseranalyse."""
        result = await self.api_request(endpoint="/startWaterAnalysis", method=HTTP_GET) # Assuming GET
        return self._normalize_response(result)

    # New methods to be added below

    async def set_light_color_pulse(self) -> Dict[str, Any]:
        """Triggers the light color change pulse (COLOR action)."""
        # "LIGHT" is a key in SWITCH_FUNCTIONS
        if "LIGHT" not in SWITCH_FUNCTIONS:
            # This should not happen if const.py is correctly populated
            raise VioletPoolCommandError("LIGHT key not defined in SWITCH_FUNCTIONS.")
        return await self.set_switch_state("LIGHT", ACTION_COLOR, 0, 0)

    async def set_all_dmx_scenes(self, action: str) -> Dict[str, Any]:
        """
        Sets all DMX scenes to ON, OFF, or AUTO.
        The API uses any DMX_SCENEX key (e.g., DMX_SCENE1) as a placeholder for these bulk actions.

        Args:
            action: One of ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO.

        Returns:
            Dict[str, Any]: API response.
        """
        valid_actions = {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}
        if action not in valid_actions:
            raise VioletPoolCommandError(
                f"Ungültige Aktion für DMX Szenen: {action}. "
                f"Gültige Aktionen: {', '.join(valid_actions)}"
            )
        
        # Use "DMX_SCENE1" as the placeholder key as per device manual behavior
        dmx_placeholder_key = "DMX_SCENE1"
        if dmx_placeholder_key not in SWITCH_FUNCTIONS:
            # This should not happen if const.py is correctly populated
            raise VioletPoolCommandError(f"{dmx_placeholder_key} nicht in SWITCH_FUNCTIONS gefunden.")

        return await self.set_switch_state(dmx_placeholder_key, action, 0, 0)

    async def set_digital_input_rule_lock(
        self, rule_key: str, lock: bool
    ) -> Dict[str, Any]:
        """
        Locks or unlocks a digital input rule (DIRULE_X).

        Args:
            rule_key: The key of the rule to lock/unlock (e.g., "DIRULE_1").
                      Must be a valid DIRULE_X key from SWITCH_FUNCTIONS.
            lock: True to lock (ACTION_LOCK), False to unlock (ACTION_UNLOCK).

        Returns:
            Dict[str, Any]: API response.
        """
        # Validate that rule_key starts with "DIRULE_" and is in SWITCH_FUNCTIONS
        if not rule_key.startswith("DIRULE_") or rule_key not in SWITCH_FUNCTIONS:
            valid_dirules = [k for k in SWITCH_FUNCTIONS if k.startswith("DIRULE_")]
            raise VioletPoolCommandError(
                f"Ungültiger DIRULE Key: {rule_key}. "
                f"Gültige Keys: {', '.join(valid_dirules) if valid_dirules else 'Keine DIRULEs definiert in SWITCH_FUNCTIONS'}"
            )

        action = ACTION_LOCK if lock else ACTION_UNLOCK
        return await self.set_switch_state(rule_key, action, 0, 0)

    async def trigger_digital_input_rule(self, rule_key: str) -> Dict[str, Any]:
        """Triggers a Digital Input Rule (simulates a PUSH action).

        Args:
            rule_key: The key of the rule to trigger (e.g., "DIRULE_1").
                      Must be a key present in SWITCH_FUNCTIONS.

        Returns:
            API response dictionary.
        """
        # Basic format check, though set_switch_state will do the ultimate validation against SWITCH_FUNCTIONS
        if not rule_key.startswith("DIRULE_") or not rule_key.split("_")[-1].isdigit():
            _LOGGER.warning(f"Invalid rule_key format passed to trigger_digital_input_rule: {rule_key}. Proceeding with API call.")
            # No explicit error raise here; let set_switch_state handle if key is truly invalid.
        
        # ACTION_PUSH is already a global constant in this file.
        # Using set_switch_state for consistency, as DIRULEs are (or should be) in SWITCH_FUNCTIONS.
        _LOGGER.debug(f"Attempting to trigger Digital Input Rule '{rule_key}' with PUSH action.")
        return await self.set_switch_state(key=rule_key, action=ACTION_PUSH, duration=0, last_value=0)

    async def set_device_temperature(self, device_type: str, temperature: float) -> Dict[str, Any]:
        """Setzt die Zieltemperatur für ein bestimmtes Gerät (z.B. HEATER, SOLAR).

        Args:
            device_type: Typ des Geräts (z.B. "HEATER", "SOLAR").
            temperature: Die einzustellende Zieltemperatur.

        Returns:
            Dict[str, Any]: API-Antwort.
        """
        # Assuming device_type is a valid key like HEATER or SOLAR that the /set_temperature endpoint understands.
        # This was previously handled by device.py's async_send_command with endpoint "/set_temperature"
        # and raw_query like f"{command.get('type', '')},{command.get('temperature', 0)}"
        raw_query = f"{device_type},{temperature}"
        result = await self.api_request(endpoint="/set_temperature", raw_query=raw_query, method=HTTP_GET)
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
        if target_type == TARGET_PH and (value < 6.8 or value > 7.8):
            _LOGGER.warning("pH-Sollwert %s außerhalb des empfohlenen Bereichs (6.8-7.8)", value)
        elif target_type == TARGET_ORP and (value < 600 or value > 800):
            _LOGGER.warning("ORP-Sollwert %s außerhalb des empfohlenen Bereichs (600-800 mV)", value)
        elif target_type == TARGET_MIN_CHLORINE and (value < 0.2 or value > 2.0):
            _LOGGER.warning("Chlor-Sollwert %s außerhalb des empfohlenen Bereichs (0.2-2.0 mg/l)", value)