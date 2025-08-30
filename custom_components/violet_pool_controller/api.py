"""API-Modul für die Kommunikation mit dem Violet Pool Controller - COMPLETE POST-FIXED VERSION."""
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
    """Kapselt Requests an den Violet Pool Controller - COMPLETE POST-FIXED VERSION."""

    def __init__(
        self, host: str, session: aiohttp.ClientSession,
        username: Optional[str] = None, password: Optional[str] = None,
        use_ssl: bool = True, timeout: int = 10
    ) -> None:
        """Initialisiere das API-Objekt."""
        self.host = host.strip()
        self.session = session
        self.username = username
        self.password = password
        self.base_url = f"{'https' if use_ssl else 'http'}://{self.host}"
        self.timeout = timeout
        self._ssl_context = use_ssl
        
        _LOGGER.info("API initialisiert: %s (SSL: %s, Auth verfügbar: %s)", 
                    self.base_url, use_ssl, bool(username and password))

    def _get_auth(self, require_auth: bool = False) -> Optional[aiohttp.BasicAuth]:
        """Gib Auth zurück basierend auf Requirement."""
        if require_auth and self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        elif require_auth and not (self.username and self.password):
            raise VioletPoolCommandError("Authentifizierung erforderlich für Steuerungsbefehle, aber keine Credentials konfiguriert")
        return None  # Für Read-Only Operationen

    def _parse_raw_query_to_dict(self, raw_query: str) -> Dict[str, str]:
        """Parse raw query string to dictionary for POST data."""
        result = {}
        if raw_query:
            # Einfaches Parsing von "key=value&key2=value2" oder "value1,value2,value3"
            if '=' in raw_query:
                # URL-Parameter Format
                for param in raw_query.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        result[key] = value
            else:
                # Komma-separierte Werte (Violet Pool Format)
                result['values'] = raw_query
        return result

    async def api_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_query: Optional[str] = None,
        require_auth: bool = False
    ) -> Union[Dict[str, Any], str]:
        """Führe einen API-Request aus - COMPLETE POST-FIXED VERSION."""
        
        # URL zusammenbauen
        if raw_query:
            if method == "POST":
                # Für POST-Anfragen: Query-Parameter in den Body
                url = f"{self.base_url}{endpoint}"
                if not data:
                    data = {}
                # Raw query als Form-Data senden
                data.update(self._parse_raw_query_to_dict(raw_query))
            else:
                # Für GET-Anfragen: Query-Parameter in der URL
                url = f"{self.base_url}{endpoint}?{raw_query}"
        else:
            url = f"{self.base_url}{endpoint}"
            
        # Auth nur wenn erforderlich
        auth = self._get_auth(require_auth)
        auth_info = f"mit Auth ({self.username})" if auth else "ohne Auth"
        
        _LOGGER.debug("API-Anfrage: %s %s (%s)", method, url, auth_info)
        if data:
            _LOGGER.debug("POST-Daten: %s", data)

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout * 2)
            
            # Headers für POST-Anfragen
            headers = {'User-Agent': 'HomeAssistant-VioletPool/1.1'}
            if method == "POST" and data:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            async with self.session.request(
                method=method, 
                url=url, 
                params=params if method == "GET" else None,
                data=data if method == "POST" else None,
                auth=auth,
                ssl=False if not self._ssl_context else None,
                timeout=timeout,
                headers=headers
            ) as response:
                
                _LOGGER.debug("Response Status: %d für %s", response.status, endpoint)
                
                if response.status >= 400:
                    error_text = await response.text()
                    
                    # Spezielle Behandlung für Auth-Fehler bei Steuerungsbefehlen
                    if response.status == 401 and require_auth:
                        _LOGGER.error("Authentifizierung fehlgeschlagen - prüfen Sie Username/Passwort")
                        raise VioletPoolCommandError("Authentifizierung fehlgeschlagen. Bitte Username/Passwort in den Optionen überprüfen.")
                    elif response.status == 404:
                        _LOGGER.error("Endpunkt nicht gefunden: %s %s - %s", method, endpoint, error_text[:200])
                        raise VioletPoolCommandError(f"API-Endpunkt nicht gefunden: {method} {endpoint}. Controller-Firmware möglicherweise veraltet.")
                    elif response.status == 500:
                        _LOGGER.error("Controller HTTP 500 - möglicherweise überlastet oder falscher Endpunkt")
                        if require_auth:
                            raise VioletPoolCommandError(f"Steuerungsbefehl fehlgeschlagen (HTTP 500). Möglicherweise falscher Endpunkt oder Controller überlastet.")
                        else:
                            raise VioletPoolConnectionError(f"Controller überlastet beim Datenabruf (HTTP 500).")
                    else:
                        _LOGGER.error("API-Fehler: HTTP %d - %s", response.status, error_text[:200])
                        raise VioletPoolCommandError(f"HTTP {response.status}: {error_text}")

                text = await response.text()
                
                # JSON-Erkennung und -Parsing
                content_type = response.headers.get("Content-Type", "").lower()
                if "application/json" in content_type or text.strip().startswith('{'):
                    try:
                        result = json.loads(text)
                        _LOGGER.debug("JSON-Response mit %d Keys erhalten", len(result) if isinstance(result, dict) else 0)
                        return result
                    except json.JSONDecodeError as e:
                        _LOGGER.warning("JSON decode error: %s", e)
                        return text
                else:
                    return text

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout bei %s: %s", endpoint, err)
            raise VioletPoolConnectionError(f"Timeout nach {self.timeout*2}s: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Verbindungsfehler bei %s: %s", endpoint, err)
            raise VioletPoolConnectionError(f"Verbindungsfehler: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler bei %s: %s", endpoint, err)
            raise VioletPoolAPIError(f"Unerwarteter Fehler: {err}") from err

    # =========================================================================
    # READ-ONLY OPERATIONS (GET-Methoden)
    # =========================================================================

    async def get_readings(self, query: str = QUERY_ALL) -> Dict[str, Any]:
        """Lese aktuelle Werte - MIT GET (korrekt für Lesezugriff)."""
        
        if not query or query == QUERY_ALL:
            query_param = "ALL"
        else:
            query_param = query
            
        _LOGGER.debug("Lese Daten mit Query: %s (mit GET)", query_param)
        
        try:
            # WICHTIG: GET für Lesen ist korrekt
            result = await self.api_request(
                endpoint=API_READINGS, 
                method="GET",
                raw_query=query_param,
                require_auth=False  # Kein Auth für Lesen
            )
            
            normalized = self._normalize_response(result)
            _LOGGER.info("Erfolgreich %d Datenpunkte gelesen", len(normalized) if isinstance(normalized, dict) else 0)
            
            return normalized
            
        except Exception as e:
            _LOGGER.error("Fehler beim Lesen der Daten: %s", e)
            raise

    # =========================================================================
    # CONTROL OPERATIONS (POST-Methoden)
    # =========================================================================

    async def set_switch_state(self, key: str, action: str, duration: int = 0, last_value: int = 0) -> Dict[str, Any]:
        """Steuere einen Switch - MIT POST (FIXED)."""
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, KEY_MAINTENANCE, KEY_PVSURPLUS}
        if key not in valid_keys:
            raise VioletPoolCommandError(f"Ungültiger Key: {key}. Gültige Keys: {', '.join(valid_keys)}")
        
        raw_query = f"{key},{action},{max(0, duration)},{max(0, last_value)}"
        _LOGGER.info("Setze Switch %s auf %s (mit POST)", key, action)
        
        # WICHTIG: POST für Steuerung
        result = await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY, 
            method="POST",  # ← FIXED: POST statt GET
            raw_query=raw_query,
            require_auth=True
        )
        return self._normalize_response(result)

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuere die Pool-Abdeckung - MIT POST."""
        if action not in COVER_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültige Aktion: {action}. Gültige Aktionen: {', '.join(COVER_FUNCTIONS.keys())}")
        return await self.set_switch_state(COVER_FUNCTIONS[action], ACTION_PUSH, 0, 0)

    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere PV-Überschussmodus - MIT POST."""
        action = ACTION_ON if active else ACTION_OFF
        pump_speed_val = max(1, min(3, pump_speed)) if active and pump_speed else 0
        return await self.set_switch_state(KEY_PVSURPLUS, action, pump_speed_val, 0)

    async def set_dosing_parameters(self, dosing_type: str, parameter_name: str, value: Union[str, int, float]) -> Dict[str, Any]:
        """Setze Dosierungsparameter - MIT POST (FIXED)."""
        raw_query = f"{dosing_type},{parameter_name},{value}"
        _LOGGER.info("Setze Dosierungsparameter: %s (mit POST)", raw_query)
        
        result = await self.api_request(
            endpoint=API_SET_DOSING_PARAMETERS, 
            method="POST",  # ← FIXED: POST statt GET
            raw_query=raw_query,
            require_auth=True
        )
        return self._normalize_response(result)

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löse manuelle Dosierung aus - MIT POST."""
        duration_s = max(1, min(3600, duration_seconds))
        dosing_api_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_api_key:
            raise VioletPoolCommandError(f"Ungültiger Dosierungstyp: {dosing_type}. Gültige Typen: {', '.join(DOSING_FUNCTIONS.keys())}")
        return await self.set_switch_state(dosing_api_key, ACTION_MAN, duration_s, 0)

    async def set_target_value(self, target_type: str, value: Union[float, int]) -> Dict[str, Any]:
        """Setze einen Sollwert - MIT POST (FIXED)."""
        self._validate_target_value(target_type, value)
        raw_query = f"{target_type},{value}"
        _LOGGER.info("Setze Sollwert %s auf %s (mit POST)", target_type, value)
        
        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES, 
            method="POST",  # ← FIXED: POST statt GET - DAS WAR DER HAUPTFEHLER!
            raw_query=raw_query,
            require_auth=True
        )
        return self._normalize_response(result)

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setze pH-Sollwert - MIT POST."""
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setze Redox-Sollwert - MIT POST."""
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setze minimalen Chlorgehalt - MIT POST."""
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviere/Deaktiviere Wartungsmodus - MIT POST."""
        return await self.set_switch_state(KEY_MAINTENANCE, ACTION_ON if enabled else ACTION_OFF)

    async def start_water_analysis(self) -> Dict[str, Any]:
        """Starte Wasseranalyse - MIT POST."""
        result = await self.api_request(
            endpoint="/startWaterAnalysis",
            method="POST",  # ← POST für Aktionen
            require_auth=True
        )
        return self._normalize_response(result)

    async def set_light_color_pulse(self) -> Dict[str, Any]:
        """Löse Lichtfarbenpuls aus - MIT POST."""
        if "LIGHT" not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError("LIGHT key not defined in SWITCH_FUNCTIONS")
        return await self.set_switch_state("LIGHT", ACTION_COLOR, 0, 0)

    async def set_all_dmx_scenes(self, action: str) -> Dict[str, Any]:
        """Setze alle DMX-Szenen - MIT POST."""
        valid_actions = {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}
        if action not in valid_actions:
            raise VioletPoolCommandError(f"Ungültige Aktion: {action}. Gültige Aktionen: {', '.join(valid_actions)}")
        if "DMX_SCENE1" not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError("DMX_SCENE1 not defined in SWITCH_FUNCTIONS")
        return await self.set_switch_state("DMX_SCENE1", action, 0, 0)

    async def set_digital_input_rule_lock(self, rule_key: str, lock: bool) -> Dict[str, Any]:
        """Sperre/Entsperre digitale Eingaberegel - MIT POST."""
        if not rule_key.startswith("DIRULE_") or rule_key not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültiger Key: {rule_key}. Gültige Keys: {', '.join(k for k in SWITCH_FUNCTIONS if k.startswith('DIRULE_'))}")
        return await self.set_switch_state(rule_key, ACTION_LOCK if lock else ACTION_UNLOCK, 0, 0)

    async def trigger_digital_input_rule(self, rule_key: str) -> Dict[str, Any]:
        """Triggere digitale Eingaberegel - MIT POST."""
        if not rule_key.startswith("DIRULE_") or rule_key not in SWITCH_FUNCTIONS:
            raise VioletPoolCommandError(f"Ungültiger Key: {rule_key}. Gültige Keys: {', '.join(k for k in SWITCH_FUNCTIONS if k.startswith('DIRULE_'))}")
        return await self.set_switch_state(rule_key, ACTION_PUSH, 0, 0)

    async def set_device_temperature(self, device_type: str, temperature: float) -> Dict[str, Any]:
        """Setze Zieltemperatur für ein Gerät - MIT POST."""
        raw_query = f"{device_type},{temperature}"
        result = await self.api_request(
            endpoint="/set_temperature", 
            method="POST",  # ← POST für Steuerung
            raw_query=raw_query,
            require_auth=True
        )
        return self._normalize_response(result)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

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

    # =========================================================================
    # ADVANCED CONTROL METHODS
    # =========================================================================

    async def set_pump_speed(self, speed: int, duration: int = 0) -> Dict[str, Any]:
        """Setze Pumpengeschwindigkeit - MIT POST."""
        if not 1 <= speed <= 3:
            raise VioletPoolCommandError(f"Pumpengeschwindigkeit muss 1-3 sein, erhalten: {speed}")
        return await self.set_switch_state("PUMP", ACTION_ON, duration, speed)

    async def force_pump_off(self, duration: int = 600) -> Dict[str, Any]:
        """Zwangsabschaltung der Pumpe - MIT POST."""
        return await self.set_switch_state("PUMP", ACTION_OFF, duration, 0)

    async def set_heater_temperature(self, temperature: float) -> Dict[str, Any]:
        """Setze Heizungstemperatur - MIT POST."""
        if not 20.0 <= temperature <= 40.0:
            raise VioletPoolCommandError(f"Temperatur muss zwischen 20-40°C liegen, erhalten: {temperature}")
        return await self.set_device_temperature("HEATER", temperature)

    async def set_solar_temperature(self, temperature: float) -> Dict[str, Any]:
        """Setze Solartemperatur - MIT POST."""
        if not 20.0 <= temperature <= 40.0:
            raise VioletPoolCommandError(f"Temperatur muss zwischen 20-40°C liegen, erhalten: {temperature}")
        return await self.set_device_temperature("SOLAR", temperature)

    async def trigger_backwash(self, duration: int = 180) -> Dict[str, Any]:
        """Triggere Rückspülung - MIT POST."""
        if not 60 <= duration <= 900:
            raise VioletPoolCommandError(f"Rückspüldauer muss 60-900s sein, erhalten: {duration}")
        return await self.set_switch_state("BACKWASH", ACTION_ON, duration, 0)

    async def trigger_backwash_rinse(self, duration: int = 60) -> Dict[str, Any]:
        """Triggere Nachspülung - MIT POST."""
        if not 30 <= duration <= 300:
            raise VioletPoolCommandError(f"Nachspüldauer muss 30-300s sein, erhalten: {duration}")
        return await self.set_switch_state("BACKWASHRINSE", ACTION_ON, duration, 0)

    async def dose_ph_minus(self, duration: int = 30) -> Dict[str, Any]:
        """Dosiere pH-Minus - MIT POST."""
        return await self.manual_dosing("pH-", duration)

    async def dose_ph_plus(self, duration: int = 30) -> Dict[str, Any]:
        """Dosiere pH-Plus - MIT POST."""
        return await self.manual_dosing("pH+", duration)

    async def dose_chlorine(self, duration: int = 30) -> Dict[str, Any]:
        """Dosiere Chlor - MIT POST."""
        return await self.manual_dosing("Chlor", duration)

    async def dose_flocculant(self, duration: int = 60) -> Dict[str, Any]:
        """Dosiere Flockmittel - MIT POST."""
        return await self.manual_dosing("Flockmittel", duration)

    # =========================================================================
    # EXTENSION RELAY CONTROL
    # =========================================================================

    async def set_extension_relay(self, bank: int, relay: int, state: str, duration: int = 0) -> Dict[str, Any]:
        """Steuere Erweiterungsrelais - MIT POST."""
        if bank not in [1, 2]:
            raise VioletPoolCommandError(f"Bank muss 1 oder 2 sein, erhalten: {bank}")
        if not 1 <= relay <= 8:
            raise VioletPoolCommandError(f"Relais muss 1-8 sein, erhalten: {relay}")
        
        relay_key = f"EXT{bank}_{relay}"
        return await self.set_switch_state(relay_key, state, duration, 0)

    async def set_omni_output(self, output: int, state: str, duration: int = 0) -> Dict[str, Any]:
        """Steuere Omni-Ausgang - MIT POST."""
        if not 0 <= output <= 5:
            raise VioletPoolCommandError(f"Omni-Ausgang muss 0-5 sein, erhalten: {output}")
        
        omni_key = f"OMNI_DC{output}"
        return await self.set_switch_state(omni_key, state, duration, 0)

    # =========================================================================
    # STATUS AND DIAGNOSTICS
    # =========================================================================

    async def get_system_status(self) -> Dict[str, Any]:
        """Hole vollständigen Systemstatus - MIT GET."""
        try:
            # Alle verfügbaren Daten abrufen
            data = await self.get_readings("ALL")
            
            # Basis-Systeminfo extrahieren
            status = {
                "firmware": data.get("FW", "Unknown"),
                "hardware": data.get("HW_VERSION", "Unknown"),
                "uptime": data.get("CPU_UPTIME", "Unknown"),
                "temperature": {
                    "water": data.get("onewire1_value"),
                    "air": data.get("onewire2_value"),
                    "solar": data.get("onewire3_value"),
                    "heater": data.get("onewire5_value"),
                },
                "chemistry": {
                    "ph": data.get("pH_value"),
                    "orp": data.get("orp_value"),
                    "chlorine": data.get("pot_value"),
                },
                "devices": {
                    "pump": data.get("PUMP"),
                    "heater": data.get("HEATER"),
                    "solar": data.get("SOLAR"),
                    "light": data.get("LIGHT"),
                },
                "last_update": data.get("time", "Unknown")
            }
            
            return status
            
        except Exception as e:
            _LOGGER.error("Fehler beim Abrufen des Systemstatus: %s", e)
            raise

    async def ping_controller(self) -> bool:
        """Teste Verbindung zum Controller."""
        try:
            result = await self.api_request(
                endpoint=API_READINGS,
                method="GET",
                raw_query="FW",
                require_auth=False
            )
            return bool(result)
        except Exception:
            return False

    # =========================================================================
    # EMERGENCY AND SAFETY METHODS
    # =========================================================================

    async def emergency_stop_all(self) -> Dict[str, Any]:
        """Notaus - alle Geräte stoppen - MIT POST."""
        _LOGGER.warning("NOTAUS aktiviert - alle Geräte werden gestoppt!")
        
        results = {}
        critical_devices = ["PUMP", "HEATER", "SOLAR", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC"]
        
        for device in critical_devices:
            try:
                result = await self.set_switch_state(device, ACTION_OFF, 3600, 0)  # 1h Sperre
                results[device] = result
            except Exception as e:
                _LOGGER.error("Fehler beim Stoppen von %s: %s", device, e)
                results[device] = {"error": str(e)}
        
        return {"emergency_stop": True, "results": results}

    async def reset_all_locks(self) -> Dict[str, Any]:
        """Alle Sperren zurücksetzen - MIT POST."""
        _LOGGER.info("Setze alle Gerätesperren zurück")
        
        results = {}
        lockable_devices = ["PUMP", "HEATER", "SOLAR", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP"]
        
        for device in lockable_devices:
            try:
                result = await self.set_switch_state(device, ACTION_AUTO, 0, 0)
                results[device] = result
            except Exception as e:
                _LOGGER.error("Fehler beim Entsperren von %s: %s", device, e)
                results[device] = {"error": str(e)}
        
        return {"locks_reset": True, "results": results}

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    async def set_multiple_switches(self, switch_actions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Setze mehrere Switches gleichzeitig - MIT POST."""
        results = {}
        
        for switch_key, params in switch_actions.items():
            action = params.get("action", ACTION_AUTO)
            duration = params.get("duration", 0)
            last_value = params.get("last_value", 0)
            
            try:
                result = await self.set_switch_state(switch_key, action, duration, last_value)
                results[switch_key] = result
                await asyncio.sleep(0.1)  # Kurze Pause zwischen Befehlen
            except Exception as e:
                _LOGGER.error("Fehler beim Setzen von %s: %s", switch_key, e)
                results[switch_key] = {"error": str(e)}
        
        return {"bulk_operation": True, "results": results}

    async def set_multiple_targets(self, target_values: Dict[str, Union[float, int]]) -> Dict[str, Any]:
        """Setze mehrere Sollwerte gleichzeitig - MIT POST."""
        results = {}
        
        for target_type, value in target_values.items():
            try:
                result = await self.set_target_value(target_type, value)
                results[target_type] = result
                await asyncio.sleep(0.1)  # Kurze Pause zwischen Befehlen
            except Exception as e:
                _LOGGER.error("Fehler beim Setzen von Sollwert %s: %s", target_type, e)
                results[target_type] = {"error": str(e)}
        
        return {"bulk_targets": True, "results": results}

# =========================================================================
# FACTORY METHODS
# =========================================================================

def create_api_instance(host: str, session: aiohttp.ClientSession, **kwargs) -> VioletPoolAPI:
    """Factory-Methode zum Erstellen einer API-Instanz."""
    return VioletPoolAPI(host=host, session=session, **kwargs)

async def test_api_connection(api: VioletPoolAPI) -> Dict[str, Any]:
    """Teste API-Verbindung und gib Diagnose-Info zurück."""
    try:
        # Basis-Verbindungstest
        ping_result = await api.ping_controller()
        
        if not ping_result:
            return {"connected": False, "error": "Ping fehlgeschlagen"}
        
        # Erweiterte Verbindungsdiagnose
        try:
            system_status = await api.get_system_status()
            
            return {
                "connected": True,
                "controller_info": {
                    "firmware": system_status.get("firmware"),
                    "hardware": system_status.get("hardware"),
                    "uptime": system_status.get("uptime"),
                },
                "api_endpoints": {
                    "readings": "✅ GET /getReadings",
                    "control": "✅ POST /setFunctionManually",
                    "targets": "✅ POST /setTargetValues",
                    "dosing": "✅ POST /setDosingParameters"
                },
                "available_devices": _extract_available_devices(system_status),
                "test_timestamp": system_status.get("last_update")
            }
            
        except Exception as e:
            return {
                "connected": True,
                "basic_connection": "✅ OK",
                "extended_test": f"❌ Fehler: {e}",
                "recommendation": "Controller erreichbar, aber erweiterte Funktionen möglicherweise eingeschränkt"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "troubleshooting": [
                "IP-Adresse prüfen",
                "Controller eingeschaltet?",
                "Firewall-Einstellungen",
                "SSL/HTTPS-Konfiguration"
            ]
        }

def _extract_available_devices(system_status: Dict[str, Any]) -> Dict[str, str]:
    """Extrahiere verfügbare Geräte aus Systemstatus."""
    devices = {}
    device_mapping = {
        "PUMP": "Filterpumpe",
        "HEATER": "Heizung", 
        "SOLAR": "Solarabsorber",
        "LIGHT": "Beleuchtung",
        "DOS_1_CL": "Chlor-Dosierung",
        "DOS_4_PHM": "pH-Minus",
        "DOS_5_PHP": "pH-Plus",
        "DOS_6_FLOC": "Flockmittel"
    }
    
    for device_key, device_name in device_mapping.items():
        if system_status.get("devices", {}).get(device_key.lower()) is not None:
            devices[device_key] = f"✅ {device_name}"
        else:
            devices[device_key] = f"❓ {device_name} (nicht erkannt)"
    
    return devices
