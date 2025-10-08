"""API-Modul für die Kommunikation mit dem Violet Pool Controller - IMPROVED VERSION."""
import logging
import asyncio
import json
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

import aiohttp

from .const import (
    API_READINGS, API_SET_FUNCTION_MANUALLY, API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES, SWITCH_FUNCTIONS, COVER_FUNCTIONS, DOSING_FUNCTIONS,
    ACTION_ON, ACTION_OFF, ACTION_AUTO, ACTION_PUSH, ACTION_MAN, ACTION_COLOR,
    ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO, ACTION_LOCK, ACTION_UNLOCK,
    QUERY_ALL, TARGET_PH, TARGET_ORP, TARGET_MIN_CHLORINE, KEY_MAINTENANCE, KEY_PVSURPLUS
)

_LOGGER = logging.getLogger(__name__)

# Konstanten für Rate-Limiting und Timeouts
MAX_BULK_OPERATIONS = 50
BULK_OPERATION_DELAY = 0.15  # Sekunden zwischen Bulk-Operationen
REQUEST_TIMEOUT_MULTIPLIER = 2
DEFAULT_RETRY_DELAY = 1.0


class ResponseFormat(Enum):
    """Enum für erwartete Response-Formate."""
    JSON = "json"
    TEXT = "text"
    AUTO = "auto"


@dataclass
class ValidationRange:
    """Datenklasse für Validierungsbereiche."""
    min_val: float
    max_val: float
    name: str
    unit: str


class VioletPoolAPIError(Exception):
    """Basisklasse für API-Fehler."""
    pass


class VioletPoolConnectionError(VioletPoolAPIError):
    """Verbindungsfehler zum Controller."""
    pass


class VioletPoolCommandError(VioletPoolAPIError):
    """Befehlsausführungsfehler."""
    pass


class VioletPoolValidationError(VioletPoolAPIError):
    """Validierungsfehler für Parameter."""
    pass


class VioletPoolAPI:
    """Kapselt Requests an den Violet Pool Controller - IMPROVED VERSION."""

    # Validierungsbereiche als Klassenvariablen
    VALIDATION_RANGES = {
        TARGET_PH: ValidationRange(6.8, 7.8, "pH-Wert", "pH"),
        TARGET_ORP: ValidationRange(600, 800, "ORP-Wert", "mV"),
        TARGET_MIN_CHLORINE: ValidationRange(0.2, 2.0, "Chlor-Wert", "mg/l")
    }

    def __init__(
        self, 
        host: str, 
        session: aiohttp.ClientSession,
        username: Optional[str] = None, 
        password: Optional[str] = None,
        use_ssl: bool = True, 
        timeout: int = 10,
        max_retries: int = 3
    ) -> None:
        """Initialisiere das API-Objekt."""
        if not host or not host.strip():
            raise ValueError("Host darf nicht leer sein")
        
        self.host = host.strip()
        self.session = session
        self.username = username
        # FIX: Sicherstellen dass password niemals None ist
        self.password = password or ""  # Einfacher und sicherer
        self.base_url = f"{'https' if use_ssl else 'http'}://{self.host}"
        self.timeout = max(5, timeout)  # Minimum 5 Sekunden
        self.max_retries = max(1, max_retries)
        self._ssl_context = use_ssl
        self._request_counter = 0
        self._last_request_time = 0.0
        
        _LOGGER.info(
            "API initialisiert: %s (SSL: %s, Auth: %s, Timeout: %ds, Retries: %d)", 
            self.base_url, use_ssl, bool(username), self.timeout, self.max_retries
        )

    def _get_auth(self, require_auth: bool = False) -> Optional[aiohttp.BasicAuth]:
        """Gib Auth zurück basierend auf Requirement - FIXED."""
        if require_auth:
            if not self.username:
                raise VioletPoolCommandError(
                    "Authentifizierung erforderlich, aber kein Username konfiguriert"
                )
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    def _parse_raw_query_to_dict(self, raw_query: str) -> Dict[str, str]:
        """Parse raw query string to dictionary - IMPROVED."""
        if not raw_query or not raw_query.strip():
            return {}
        
        result = {}
        raw_query = raw_query.strip()
        
        try:
            if '=' in raw_query:
                # URL-Parameter Format: "key=value&key2=value2"
                for param in raw_query.split('&'):
                    param = param.strip()
                    if '=' in param:
                        key, value = param.split('=', 1)
                        result[key.strip()] = value.strip()
            else:
                # Komma-separierte Werte (Violet Pool Format)
                result['values'] = raw_query
        except Exception as e:
            _LOGGER.warning("Fehler beim Parsen von Query '%s': %s", raw_query, e)
            # Fallback: Ganzer String als Wert
            result['values'] = raw_query
        
        return result

    def _validate_response_status(
        self, 
        status: int, 
        error_text: str, 
        endpoint: str,
        require_auth: bool
    ) -> None:
        """Validiere HTTP Response Status - IMPROVED."""
        if status < 400:
            return
        
        error_prefix = f"API-Fehler bei {endpoint}"
        
        if status == 401:
            if require_auth:
                _LOGGER.error("Authentifizierung fehlgeschlagen für %s", endpoint)
                raise VioletPoolCommandError(
                    "Authentifizierung fehlgeschlagen. "
                    "Bitte Username/Passwort in den Optionen überprüfen."
                )
            else:
                _LOGGER.warning("401 bei nicht-authentifiziertem Request an %s", endpoint)
        elif status == 403:
            raise VioletPoolCommandError(f"{error_prefix}: Zugriff verweigert (HTTP 403)")
        elif status == 404:
            _LOGGER.error("Endpunkt nicht gefunden: %s - %s", endpoint, error_text[:200])
            raise VioletPoolCommandError(
                f"API-Endpunkt nicht gefunden: {endpoint}. "
                "Controller-Firmware möglicherweise veraltet."
            )
        elif status == 500:
            _LOGGER.error("Controller HTTP 500 bei %s - %s", endpoint, error_text[:200])
            raise VioletPoolCommandError(
                f"Controller-Fehler (HTTP 500) bei {endpoint}. "
                "Möglicherweise überlastet oder falscher Endpunkt."
            )
        elif status == 503:
            raise VioletPoolConnectionError(
                f"{error_prefix}: Service nicht verfügbar (HTTP 503)"
            )
        else:
            _LOGGER.error("HTTP %d bei %s: %s", status, endpoint, error_text[:200])
            raise VioletPoolCommandError(f"HTTP {status}: {error_text[:200]}")

    async def api_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, 
        raw_query: Optional[str] = None,
        require_auth: bool = False,
        expected_format: ResponseFormat = ResponseFormat.AUTO
    ) -> Union[Dict[str, Any], str]:
        """Führe einen API-Request aus - IMPROVED VERSION."""
        
        # URL zusammenbauen
        if raw_query:
            if method == "POST":
                url = f"{self.base_url}{endpoint}"
                if not data:
                    data = {}
                data.update(self._parse_raw_query_to_dict(raw_query))
            else:
                url = f"{self.base_url}{endpoint}?{raw_query}"
        else:
            url = f"{self.base_url}{endpoint}"
        
        # Auth nur wenn erforderlich
        auth = self._get_auth(require_auth)
        auth_info = f"mit Auth ({self.username})" if auth else "ohne Auth"
        
        _LOGGER.debug("API-Anfrage: %s %s (%s)", method, url, auth_info)
        if data:
            _LOGGER.debug("POST-Daten: %s", {k: "***" if "password" in k.lower() else v for k, v in data.items()})

        # Rate-Limiting für Bulk-Operationen
        self._request_counter += 1
        if self._request_counter % 10 == 0:
            _LOGGER.debug("Request-Counter: %d", self._request_counter)

        # Retry-Loop
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout * REQUEST_TIMEOUT_MULTIPLIER)
                
                headers = {'User-Agent': 'HomeAssistant-VioletPool/1.2'}
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
                    
                    _LOGGER.debug(
                        "Response Status: %d für %s (Versuch %d/%d)", 
                        response.status, endpoint, attempt + 1, self.max_retries
                    )
                    
                    # Status-Validierung
                    if response.status >= 400:
                        error_text = await response.text()
                        self._validate_response_status(
                            response.status, error_text, endpoint, require_auth
                        )
                    
                    text = await response.text()
                    
                    # Response-Format-Erkennung
                    return self._parse_response(text, response, expected_format)

            except asyncio.TimeoutError as err:
                last_exception = err
                _LOGGER.warning(
                    "Timeout bei %s (Versuch %d/%d): %s", 
                    endpoint, attempt + 1, self.max_retries, err
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue
                
            except aiohttp.ClientError as err:
                last_exception = err
                _LOGGER.warning(
                    "Verbindungsfehler bei %s (Versuch %d/%d): %s", 
                    endpoint, attempt + 1, self.max_retries, err
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue
                
            except VioletPoolAPIError:
                # Diese Fehler nicht wiederholen
                raise
                
            except Exception as err:
                last_exception = err
                _LOGGER.error("Unerwarteter Fehler bei %s: %s", endpoint, err)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue
        
        # Alle Versuche fehlgeschlagen
        if isinstance(last_exception, asyncio.TimeoutError):
            raise VioletPoolConnectionError(
                f"Timeout nach {self.max_retries} Versuchen: {last_exception}"
            ) from last_exception
        elif isinstance(last_exception, aiohttp.ClientError):
            raise VioletPoolConnectionError(
                f"Verbindungsfehler nach {self.max_retries} Versuchen: {last_exception}"
            ) from last_exception
        else:
            raise VioletPoolAPIError(
                f"Unerwarteter Fehler nach {self.max_retries} Versuchen: {last_exception}"
            ) from last_exception

    def _parse_response(
        self, 
        text: str, 
        response: aiohttp.ClientResponse,
        expected_format: ResponseFormat
    ) -> Union[Dict[str, Any], str]:
        """Parse Response basierend auf erwartetem Format - NEW."""
        content_type = response.headers.get("Content-Type", "").lower()
        
        # Explizites Format erzwingen
        if expected_format == ResponseFormat.TEXT:
            return text
        
        # JSON-Erkennung und -Parsing
        is_json_content = "application/json" in content_type
        looks_like_json = text.strip().startswith(('{', '['))
        
        if expected_format == ResponseFormat.JSON or is_json_content or looks_like_json:
            try:
                result = json.loads(text)
                _LOGGER.debug(
                    "JSON-Response mit %d Keys erhalten", 
                    len(result) if isinstance(result, dict) else 
                    len(result) if isinstance(result, list) else 0
                )
                return result
            except json.JSONDecodeError as e:
                if expected_format == ResponseFormat.JSON:
                    _LOGGER.error("JSON-Parsing fehlgeschlagen: %s", e)
                    raise VioletPoolAPIError(f"Ungültige JSON-Antwort: {e}") from e
                _LOGGER.debug("Text ist kein JSON, gebe als String zurück")
                return text
        
        return text

    def _normalize_response(self, result: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Normalisiere API-Antworten - IMPROVED."""
        if isinstance(result, dict):
            return result
        
        if isinstance(result, str):
            # Versuche JSON-Parsing
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Prüfe auf OK/ERROR Antwort
                result_upper = result.upper()
                return {
                    "response": result, 
                    "success": "OK" in result_upper and "ERROR" not in result_upper
                }
        
        # Fallback
        return {"response": str(result), "success": False}

    def _validate_target_value(self, target_type: str, value: Union[float, int]) -> None:
        """Validiere Sollwerte - IMPROVED."""
        if target_type not in self.VALIDATION_RANGES:
            _LOGGER.debug("Keine Validierung für %s definiert", target_type)
            return
        
        range_info = self.VALIDATION_RANGES[target_type]
        
        if value < range_info.min_val or value > range_info.max_val:
            _LOGGER.warning(
                "%s %.2f%s außerhalb des empfohlenen Bereichs (%.2f-%.2f%s)",
                range_info.name, value, range_info.unit,
                range_info.min_val, range_info.max_val, range_info.unit
            )
            raise VioletPoolValidationError(
                f"{range_info.name} {value}{range_info.unit} außerhalb des gültigen Bereichs "
                f"({range_info.min_val}-{range_info.max_val}{range_info.unit})"
            )

    # =========================================================================
    # READ-ONLY OPERATIONS (GET-Methoden)
    # =========================================================================

    async def get_readings(self, query: str = QUERY_ALL) -> Dict[str, Any]:
        """Lese aktuelle Werte - MIT GET."""
        if not query or query == QUERY_ALL:
            query_param = "ALL"
        else:
            query_param = query
        
        _LOGGER.debug("Lese Daten mit Query: %s", query_param)
        
        result = await self.api_request(
            endpoint=API_READINGS, 
            method="GET",
            raw_query=query_param,
            require_auth=False,
            expected_format=ResponseFormat.JSON
        )
        
        normalized = self._normalize_response(result)
        _LOGGER.info(
            "Erfolgreich %d Datenpunkte gelesen", 
            len(normalized) if isinstance(normalized, dict) else 0
        )
        
        return normalized

    async def ping_controller(self) -> bool:
        """Prüfe Verbindung zum Controller - IMPROVED."""
        try:
            result = await self.api_request(
                endpoint=API_READINGS,
                method="GET",
                raw_query="FW",
                require_auth=False,
                expected_format=ResponseFormat.AUTO
            )
            return bool(result)
        except Exception as e:
            _LOGGER.debug("Ping fehlgeschlagen: %s", e)
            return False

    async def get_system_status(self) -> Dict[str, Any]:
        """Hole detaillierten Systemstatus - NEW."""
        try:
            all_data = await self.get_readings(QUERY_ALL)
            
            return {
                "firmware": all_data.get("fw") or all_data.get("firmware_version") or "unknown",
                "hardware": all_data.get("hw") or all_data.get("hardware_version") or "unknown",
                "uptime": all_data.get("uptime", 0),
                "last_update": all_data.get("timestamp"),
                "devices": all_data
            }
        except Exception as e:
            _LOGGER.error("Fehler beim Abrufen des Systemstatus: %s", e)
            return {"error": str(e)}

    # =========================================================================
    # CONTROL OPERATIONS (POST-Methoden)
    # =========================================================================

    async def set_switch_state(
        self, 
        key: str, 
        action: str, 
        duration: int = 0, 
        last_value: int = 0
    ) -> Dict[str, Any]:
        """Steuere einen Switch - MIT POST."""
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, KEY_MAINTENANCE, KEY_PVSURPLUS}
        if key not in valid_keys:
            raise VioletPoolCommandError(
                f"Ungültiger Key: {key}. Gültige Keys: {', '.join(sorted(valid_keys))}"
            )
        
        # Validierung der Parameter
        duration = max(0, int(duration))
        last_value = max(0, int(last_value))
        
        raw_query = f"{key},{action},{duration},{last_value}"
        _LOGGER.info("Setze Switch %s auf %s (Dauer: %ds)", key, action, duration)
        
        result = await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY, 
            method="POST",
            raw_query=raw_query,
            require_auth=True,
            expected_format=ResponseFormat.AUTO
        )
        return self._normalize_response(result)

    async def set_target_value(
        self, 
        target_type: str, 
        value: Union[float, int]
    ) -> Dict[str, Any]:
        """Setze einen Sollwert - MIT POST & VALIDATION."""
        # Validierung
        self._validate_target_value(target_type, value)
        
        raw_query = f"{target_type},{value}"
        _LOGGER.info("Setze Sollwert %s auf %.2f", target_type, value)
        
        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES, 
            method="POST",
            raw_query=raw_query,
            require_auth=True,
            expected_format=ResponseFormat.AUTO
        )
        return self._normalize_response(result)

    # =========================================================================
    # BULK OPERATIONS - IMPROVED
    # =========================================================================

    async def set_multiple_switches(
        self, 
        switch_actions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Setze mehrere Switches gleichzeitig - MIT RATE-LIMITING."""
        if len(switch_actions) > MAX_BULK_OPERATIONS:
            raise VioletPoolValidationError(
                f"Zu viele Bulk-Operationen ({len(switch_actions)} > {MAX_BULK_OPERATIONS})"
            )
        
        results = {}
        successful = 0
        failed = 0
        
        for switch_key, params in switch_actions.items():
            action = params.get("action", ACTION_AUTO)
            duration = params.get("duration", 0)
            last_value = params.get("last_value", 0)
            
            try:
                result = await self.set_switch_state(switch_key, action, duration, last_value)
                results[switch_key] = {"success": True, "result": result}
                successful += 1
                await asyncio.sleep(BULK_OPERATION_DELAY)
            except Exception as e:
                _LOGGER.error("Fehler beim Setzen von %s: %s", switch_key, e)
                results[switch_key] = {"success": False, "error": str(e)}
                failed += 1
        
        _LOGGER.info(
            "Bulk-Operation abgeschlossen: %d erfolgreich, %d fehlgeschlagen",
            successful, failed
        )
        
        return {
            "bulk_operation": True, 
            "total": len(switch_actions),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    # =========================================================================
    # EMERGENCY AND SAFETY METHODS - IMPROVED
    # =========================================================================

    async def emergency_stop_all(self) -> Dict[str, Any]:
        """Notaus - alle kritischen Geräte stoppen - IMPROVED."""
        _LOGGER.warning("🚨 NOTAUS aktiviert - stoppe alle kritischen Geräte!")
        
        critical_devices = [
            "PUMP", "HEATER", "SOLAR", 
            "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC"
        ]
        
        results = {}
        stopped = 0
        
        for device in critical_devices:
            try:
                result = await self.set_switch_state(device, ACTION_OFF, 3600, 0)
                results[device] = {"success": True, "result": result}
                stopped += 1
                _LOGGER.info("✓ Gerät %s gestoppt", device)
                await asyncio.sleep(0.1)  # Kurze Pause zwischen Stopps
            except Exception as e:
                _LOGGER.error("✗ Fehler beim Stoppen von %s: %s", device, e)
                results[device] = {"success": False, "error": str(e)}
        
        success_rate = (stopped / len(critical_devices)) * 100
        _LOGGER.warning(
            "Notaus abgeschlossen: %d/%d Geräte gestoppt (%.1f%%)",
            stopped, len(critical_devices), success_rate
        )
        
        return {
            "emergency_stop": True, 
            "timestamp": asyncio.get_event_loop().time(),
            "devices_stopped": stopped,
            "total_devices": len(critical_devices),
            "success_rate": success_rate,
            "results": results
        }


# =========================================================================
# FACTORY METHODS
# =========================================================================

def create_api_instance(
    host: str, 
    session: aiohttp.ClientSession, 
    **kwargs
) -> VioletPoolAPI:
    """Factory-Methode zum Erstellen einer API-Instanz."""
    return VioletPoolAPI(host=host, session=session, **kwargs)


async def test_api_connection(api: VioletPoolAPI) -> Dict[str, Any]:
    """Teste API-Verbindung und gib Diagnose-Info zurück - IMPROVED."""
    try:
        # Basis-Verbindungstest
        ping_result = await api.ping_controller()
        
        if not ping_result:
            return {
                "connected": False, 
                "error": "Ping fehlgeschlagen",
                "troubleshooting": [
                    "IP-Adresse prüfen",
                    "Controller eingeschaltet?",
                    "Netzwerkverbindung prüfen",
                    "Firewall-Einstellungen überprüfen"
                ]
            }
        
        # Erweiterte Verbindungsdiagnose
        try:
            system_status = await api.get_system_status()
            
            return {
                "connected": True,
                "controller_info": {
                    "firmware": system_status.get("firmware", "unknown"),
                    "hardware": system_status.get("hardware", "unknown"),
                    "uptime": system_status.get("uptime", 0),
                },
                "api_health": {
                    "requests_sent": api._request_counter,
                    "timeout": f"{api.timeout}s",
                    "retries": api.max_retries,
                    "ssl": api._ssl_context
                },
                "test_passed": True
            }
            
        except Exception as e:
            return {
                "connected": True,
                "basic_connection": "✅ OK",
                "extended_test": f"⚠️ Teilweise: {e}",
                "recommendation": "Controller erreichbar, aber einige Funktionen eingeschränkt"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "troubleshooting": [
                "IP-Adresse korrekt?",
                "Controller erreichbar?",
                "Port 80/443 offen?",
                "SSL-Einstellungen prüfen",
                "Netzwerk-Firewall überprüfen"
            ]
        }
