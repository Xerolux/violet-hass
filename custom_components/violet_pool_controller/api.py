"""API-Modul für die Kommunikation mit dem Violet Pool Controller - LOGGING OPTIMIZED."""
import logging
import asyncio
import json
import time
from typing import Any
from dataclasses import dataclass
from enum import Enum

import aiohttp

from .const import (
    API_READINGS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES,
    SWITCH_FUNCTIONS,
    COVER_FUNCTIONS,
    DOSING_FUNCTIONS,
    ACTION_ON,
    ACTION_OFF,
    ACTION_AUTO,
    ACTION_PUSH,
    ACTION_MAN,
    ACTION_COLOR,
    ACTION_ALLON,
    ACTION_ALLOFF,
    ACTION_ALLAUTO,
    ACTION_LOCK,
    ACTION_UNLOCK,
    QUERY_ALL,
    TARGET_PH,
    TARGET_ORP,
    TARGET_MIN_CHLORINE,
    KEY_MAINTENANCE,
    KEY_PVSURPLUS,
)

_LOGGER = logging.getLogger(__name__)

# API Request Konstanten
MAX_BULK_OPERATIONS = 50
BULK_OPERATION_DELAY = 0.15
EMERGENCY_STOP_DELAY = 0.1
REQUEST_TIMEOUT_MULTIPLIER = 2
DEFAULT_RETRY_DELAY = 1.0

# Validierung Konstanten
MIN_TIMEOUT = 5
MIN_RETRIES = 1
MIN_TEMPERATURE = 20.0
MAX_TEMPERATURE = 40.0
MIN_DOSING_DURATION = 5
MAX_DOSING_DURATION = 300

# HTTP Status Codes
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# ✅ LOGGING OPTIMIZATION: Throttling-Konstanten
LOG_THROTTLE_SECONDS = 60  # Wiederholte Messages nur alle 60s


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
    """Kapselt Requests an den Violet Pool Controller - LOGGING OPTIMIZED."""

    VALIDATION_RANGES = {
        TARGET_PH: ValidationRange(6.8, 7.8, "pH-Wert", "pH"),
        TARGET_ORP: ValidationRange(600, 800, "ORP-Wert", "mV"),
        TARGET_MIN_CHLORINE: ValidationRange(0.2, 2.0, "Chlor-Wert", "mg/l"),
    }

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
        use_ssl: bool = True,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        """Initialisiere das API-Objekt mit Logging-Optimierung."""
        if not host or not host.strip():
            raise ValueError("Host darf nicht leer sein")

        self.host = host.strip()
        self.session = session
        self.username = username
        self.password = password if password is not None else ""
        self.base_url = f"{'https' if use_ssl else 'http'}://{self.host}"
        self.timeout = max(MIN_TIMEOUT, timeout)
        self.max_retries = max(MIN_RETRIES, max_retries)
        self._ssl_context = use_ssl
        self._request_counter = 0

        # ✅ LOGGING OPTIMIZATION: Throttling-Cache
        self._last_log_time: dict[str, float] = {}
        self._last_connection_state = True  # Für Connection State Change Detection

        _LOGGER.info(
            "API initialisiert: %s (SSL: %s, Auth: %s, Timeout: %ds, Retries: %d)",
            self.base_url,
            use_ssl,
            bool(username),
            self.timeout,
            self.max_retries,
        )

    def _should_log_throttled(self, key: str) -> bool:
        """
        Prüfe ob Log-Message gesendet werden soll (Throttling).
        
        ✅ LOGGING OPTIMIZATION: Verhindert Log-Spam bei wiederholten Fehlern.
        """
        now = time.time()
        last_time = self._last_log_time.get(key, 0)
        
        if now - last_time > LOG_THROTTLE_SECONDS:
            self._last_log_time[key] = now
            return True
        return False

    def _get_auth(self, require_auth: bool = False) -> aiohttp.BasicAuth | None:
        """Gib Auth zurück basierend auf Requirement."""
        if require_auth:
            if not self.username:
                raise VioletPoolCommandError(
                    "Authentifizierung erforderlich, aber kein Username konfiguriert"
                )
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    def _parse_raw_query_to_dict(self, raw_query: str) -> dict[str, str]:
        """Parse raw query string to dictionary."""
        if not raw_query or not raw_query.strip():
            return {}

        result = {}
        raw_query = raw_query.strip()

        try:
            if "=" in raw_query:
                for param in raw_query.split("&"):
                    param = param.strip()
                    if "=" in param:
                        key, value = param.split("=", 1)
                        result[key.strip()] = value.strip()
            else:
                result["values"] = raw_query
        except Exception as e:
            # ✅ LOGGING OPTIMIZATION: Nur wenn throttled
            if self._should_log_throttled(f"parse_error_{raw_query[:20]}"):
                _LOGGER.warning("Fehler beim Parsen von Query '%s': %s", raw_query, e)
            result["values"] = raw_query

        return result

    def _validate_response_status(
        self, status: int, error_text: str, endpoint: str, require_auth: bool
    ) -> None:
        """Validiere HTTP Response Status."""
        if status < 400:
            return

        error_prefix = f"API-Fehler bei {endpoint}"

        if status == HTTP_UNAUTHORIZED:
            if require_auth:
                _LOGGER.error("Authentifizierung fehlgeschlagen für %s", endpoint)
                raise VioletPoolCommandError(
                    "Authentifizierung fehlgeschlagen. "
                    "Bitte Username/Passwort in den Optionen überprüfen."
                )
            else:
                # ✅ LOGGING OPTIMIZATION: Throttled warning
                if self._should_log_throttled(f"auth_warn_{endpoint}"):
                    _LOGGER.warning("401 bei nicht-authentifiziertem Request an %s", endpoint)
        elif status == HTTP_FORBIDDEN:
            raise VioletPoolCommandError(f"{error_prefix}: Zugriff verweigert (HTTP 403)")
        elif status == HTTP_NOT_FOUND:
            _LOGGER.error("Endpunkt nicht gefunden: %s - %s", endpoint, error_text[:200])
            raise VioletPoolCommandError(
                f"API-Endpunkt nicht gefunden: {endpoint}. "
                "Controller-Firmware möglicherweise veraltet."
            )
        elif status == HTTP_SERVER_ERROR:
            _LOGGER.error("Controller HTTP 500 bei %s - %s", endpoint, error_text[:200])
            raise VioletPoolCommandError(
                f"Controller-Fehler (HTTP 500) bei {endpoint}. "
                "Möglicherweise überlastet oder falscher Endpunkt."
            )
        elif status == HTTP_SERVICE_UNAVAILABLE:
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
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        raw_query: str | None = None,
        require_auth: bool = False,
        expected_format: ResponseFormat = ResponseFormat.AUTO,
    ) -> dict[str, Any] | str:
        """
        Führe einen API-Request aus - LOGGING OPTIMIZED.
        
        ✅ LOGGING OPTIMIZATION: 
        - Reduzierte Logs bei Retries
        - Konsolidierte Fehler-Messages
        - Connection State Change Detection
        """

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

        auth = self._get_auth(require_auth)

        # ✅ LOGGING OPTIMIZATION: Nur beim ersten Request oder nach Throttle-Zeit loggen
        if self._should_log_throttled(f"request_{endpoint}"):
            auth_info = f"mit Auth ({self.username})" if auth else "ohne Auth"
            _LOGGER.debug("API-Anfrage: %s %s (%s)", method, url, auth_info)
            if data:
                sanitized_data = {
                    k: "***" if "password" in k.lower() else v for k, v in data.items()
                }
                _LOGGER.debug("POST-Daten: %s", sanitized_data)

        # Rate-Limiting Tracking
        self._request_counter += 1

        # Retry-Loop mit optimiertem Logging
        last_exception = None
        first_attempt = True
        
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout * REQUEST_TIMEOUT_MULTIPLIER)
                headers = {"User-Agent": "HomeAssistant-VioletPool/1.3"}
                
                if method == "POST" and data:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"

                async with self.session.request(
                    method=method,
                    url=url,
                    params=params if method == "GET" else None,
                    data=data if method == "POST" else None,
                    auth=auth,
                    ssl=False if not self._ssl_context else None,
                    timeout=timeout,
                    headers=headers,
                ) as response:

                    # ✅ LOGGING OPTIMIZATION: Nur bei Problemen loggen
                    if response.status >= 400:
                        error_text = await response.text()
                        self._validate_response_status(
                            response.status, error_text, endpoint, require_auth
                        )

                    text = await response.text()

                    # ✅ LOGGING OPTIMIZATION: Erfolg nach Fehler = wichtige Info
                    if last_exception and not first_attempt:
                        _LOGGER.info(
                            "Verbindung wiederhergestellt nach %d Versuchen: %s",
                            attempt + 1,
                            endpoint
                        )
                        self._last_connection_state = True

                    return self._parse_response(text, response, expected_format)

            except asyncio.TimeoutError as err:
                last_exception = err
                first_attempt = False
                
                # ✅ LOGGING OPTIMIZATION: Nur letzten Fehler oder throttled loggen
                if attempt == self.max_retries - 1:
                    _LOGGER.error(
                        "Timeout nach %d Versuchen bei %s",
                        self.max_retries,
                        endpoint
                    )
                    self._last_connection_state = False
                elif self._should_log_throttled(f"timeout_{endpoint}"):
                    _LOGGER.debug(
                        "Timeout bei %s (Versuch %d/%d, wird wiederholt...)",
                        endpoint,
                        attempt + 1,
                        self.max_retries
                    )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue

            except aiohttp.ClientError as err:
                last_exception = err
                first_attempt = False
                
                # ✅ LOGGING OPTIMIZATION: Konsolidiertes Error-Logging
                if attempt == self.max_retries - 1:
                    _LOGGER.error(
                        "Verbindungsfehler nach %d Versuchen bei %s: %s",
                        self.max_retries,
                        endpoint,
                        str(err)[:100]  # Gekürzt
                    )
                    self._last_connection_state = False
                elif self._should_log_throttled(f"connection_{endpoint}"):
                    _LOGGER.debug(
                        "Verbindungsfehler bei %s (Versuch %d/%d)",
                        endpoint,
                        attempt + 1,
                        self.max_retries
                    )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue

            except VioletPoolAPIError:
                raise

            except Exception as err:
                last_exception = err
                _LOGGER.error("Unerwarteter Fehler bei %s: %s", endpoint, err)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                continue

        # Alle Versuche fehlgeschlagen - konsolidierte Exception
        if isinstance(last_exception, asyncio.TimeoutError):
            raise VioletPoolConnectionError(
                f"Timeout nach {self.max_retries} Versuchen"
            ) from last_exception
        elif isinstance(last_exception, aiohttp.ClientError):
            raise VioletPoolConnectionError(
                f"Verbindungsfehler nach {self.max_retries} Versuchen"
            ) from last_exception
        else:
            raise VioletPoolAPIError(
                f"Fehler nach {self.max_retries} Versuchen"
            ) from last_exception

    def _parse_response(
        self,
        text: str,
        response: aiohttp.ClientResponse,
        expected_format: ResponseFormat,
    ) -> dict[str, Any] | str:
        """Parse Response basierend auf erwartetem Format."""
        content_type = response.headers.get("Content-Type", "").lower()

        if expected_format == ResponseFormat.TEXT:
            return text

        is_json_content = "application/json" in content_type
        looks_like_json = text.strip().startswith(("{", "["))

        if expected_format == ResponseFormat.JSON or is_json_content or looks_like_json:
            try:
                result = json.loads(text)
                return result
            except json.JSONDecodeError as e:
                if expected_format == ResponseFormat.JSON:
                    _LOGGER.error("JSON-Parsing fehlgeschlagen: %s", e)
                    raise VioletPoolAPIError(f"Ungültige JSON-Antwort: {e}") from e
                return text

        return text

    def _normalize_response(self, result: dict[str, Any] | str) -> dict[str, Any]:
        """Normalisiere API-Antworten."""
        if isinstance(result, dict):
            return result

        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                result_upper = result.upper()
                return {
                    "response": result,
                    "success": "OK" in result_upper and "ERROR" not in result_upper,
                }

        return {"response": str(result), "success": False}

    def _validate_target_value(self, target_type: str, value: float | int) -> None:
        """Validiere Sollwerte."""
        if target_type not in self.VALIDATION_RANGES:
            return

        range_info = self.VALIDATION_RANGES[target_type]

        if value < range_info.min_val or value > range_info.max_val:
            _LOGGER.warning(
                "%s %.2f%s außerhalb des empfohlenen Bereichs (%.2f-%.2f%s)",
                range_info.name,
                value,
                range_info.unit,
                range_info.min_val,
                range_info.max_val,
                range_info.unit,
            )
            raise VioletPoolValidationError(
                f"{range_info.name} {value}{range_info.unit} außerhalb des gültigen Bereichs "
                f"({range_info.min_val}-{range_info.max_val}{range_info.unit})"
            )

    # =========================================================================
    # READ-ONLY OPERATIONS
    # =========================================================================

    async def get_readings(self, query: str = QUERY_ALL) -> dict[str, Any]:
        """Lese aktuelle Werte vom Controller."""
        query_param = "ALL" if not query or query == QUERY_ALL else query

        result = await self.api_request(
            endpoint=API_READINGS,
            method="GET",
            raw_query=query_param,
            require_auth=False,
            expected_format=ResponseFormat.JSON,
        )

        normalized = self._normalize_response(result)
        
        # ✅ LOGGING OPTIMIZATION: Nur bei Erfolg nach Fehler loggen
        if not self._last_connection_state:
            data_points = len(normalized) if isinstance(normalized, dict) else 0
            _LOGGER.info("Erfolgreich %d Datenpunkte gelesen (Verbindung wiederhergestellt)", data_points)
            self._last_connection_state = True

        return normalized

    async def ping_controller(self) -> bool:
        """Prüfe Verbindung zum Controller."""
        try:
            result = await self.api_request(
                endpoint=API_READINGS,
                method="GET",
                raw_query="FW",
                require_auth=False,
                expected_format=ResponseFormat.AUTO,
            )
            return bool(result)
        except Exception:
            return False

    async def get_system_status(self) -> dict[str, Any]:
        """Hole detaillierten Systemstatus."""
        try:
            all_data = await self.get_readings(QUERY_ALL)
            return {
                "firmware": all_data.get("fw") or all_data.get("firmware_version") or "unknown",
                "hardware": all_data.get("hw") or all_data.get("hardware_version") or "unknown",
                "uptime": all_data.get("uptime", 0),
                "last_update": all_data.get("timestamp"),
                "devices": all_data,
            }
        except Exception as e:
            _LOGGER.error("Fehler beim Abrufen des Systemstatus: %s", e)
            return {"error": str(e)}

    # =========================================================================
    # CONTROL OPERATIONS (alle anderen Methoden bleiben gleich)
    # =========================================================================

    async def set_switch_state(
        self, key: str, action: str, duration: int = 0, last_value: int = 0
    ) -> dict[str, Any]:
        """Steuere einen Switch."""
        valid_keys = {*SWITCH_FUNCTIONS, *DOSING_FUNCTIONS, KEY_MAINTENANCE, KEY_PVSURPLUS}
        if key not in valid_keys:
            raise VioletPoolCommandError(
                f"Ungültiger Key: {key}. Gültige Keys: {', '.join(sorted(valid_keys))}"
            )

        duration = max(0, int(duration))
        last_value = max(0, int(last_value))
        raw_query = f"{key},{action},{duration},{last_value}"
        
        _LOGGER.info("Setze Switch %s auf %s (Dauer: %ds)", key, action, duration)

        result = await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY,
            method="POST",
            raw_query=raw_query,
            require_auth=True,
            expected_format=ResponseFormat.AUTO,
        )
        return self._normalize_response(result)

    async def set_target_value(self, target_type: str, value: float | int) -> dict[str, Any]:
        """Setze einen Sollwert mit Validierung."""
        self._validate_target_value(target_type, value)
        raw_query = f"{target_type},{value}"
        
        _LOGGER.info("Setze Sollwert %s auf %.2f", target_type, value)

        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES,
            method="POST",
            raw_query=raw_query,
            require_auth=True,
            expected_format=ResponseFormat.AUTO,
        )
        return self._normalize_response(result)

    async def set_device_temperature(self, device_key: str, temperature: float) -> dict[str, Any]:
        """Setze Zieltemperatur für Heizung oder Solar."""
        if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
            raise VioletPoolValidationError(
                f"Temperatur {temperature}°C außerhalb gültigen Bereichs "
                f"({MIN_TEMPERATURE}-{MAX_TEMPERATURE}°C)"
            )

        target_key = f"{device_key}_TARGET_TEMP"
        _LOGGER.info("Setze %s auf %.1f°C", device_key, temperature)

        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES,
            method="POST",
            raw_query=f"{target_key},{temperature}",
            require_auth=True,
            expected_format=ResponseFormat.AUTO,
        )
        return self._normalize_response(result)

    # =========================================================================
    # BULK OPERATIONS & EMERGENCY - bleiben unverändert
    # =========================================================================

    async def set_multiple_switches(self, switch_actions: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Setze mehrere Switches gleichzeitig mit Rate-Limiting."""
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

        _LOGGER.info("Bulk-Operation: %d erfolgreich, %d fehlgeschlagen", successful, failed)

        return {
            "bulk_operation": True,
            "total": len(switch_actions),
            "successful": successful,
            "failed": failed,
            "results": results,
        }

    async def emergency_stop_all(self) -> dict[str, Any]:
        """Notaus - alle kritischen Geräte stoppen."""
        _LOGGER.warning("NOTAUS aktiviert - stoppe alle kritischen Geräte!")

        critical_devices = [
            "PUMP", "HEATER", "SOLAR", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC",
        ]

        results = {}
        stopped = 0

        for device in critical_devices:
            try:
                result = await self.set_switch_state(device, ACTION_OFF, 3600, 0)
                results[device] = {"success": True, "result": result}
                stopped += 1
                _LOGGER.info("Gerät %s gestoppt", device)
                await asyncio.sleep(EMERGENCY_STOP_DELAY)
            except Exception as e:
                _LOGGER.error("Fehler beim Stoppen von %s: %s", device, e)
                results[device] = {"success": False, "error": str(e)}

        success_rate = (stopped / len(critical_devices)) * 100
        _LOGGER.warning("Notaus: %d/%d Geräte gestoppt (%.1f%%)", stopped, len(critical_devices), success_rate)

        return {
            "emergency_stop": True,
            "devices_stopped": stopped,
            "total_devices": len(critical_devices),
            "success_rate": success_rate,
            "results": results,
        }

    # =========================================================================
    # CONVENIENCE METHODS - bleiben unverändert
    # =========================================================================

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Setze pH-Sollwert."""
        return await self.set_target_value(TARGET_PH, value)

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Setze ORP/Redox-Sollwert."""
        return await self.set_target_value(TARGET_ORP, value)

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Setze Mindest-Chlor-Level."""
        return await self.set_target_value(TARGET_MIN_CHLORINE, value)

    async def manual_dosing(self, dosing_type: str, duration: int) -> dict[str, Any]:
        """Führe manuelle Dosierung durch."""
        device_mapping = {
            "pH-": "DOS_4_PHM",
            "pH+": "DOS_5_PHP",
            "Chlor": "DOS_1_CL",
            "Flockmittel": "DOS_6_FLOC",
        }

        device_key = device_mapping.get(dosing_type)
        if not device_key:
            raise VioletPoolCommandError(f"Unbekannter Dosiertyp: {dosing_type}")

        if not MIN_DOSING_DURATION <= duration <= MAX_DOSING_DURATION:
            raise VioletPoolValidationError(
                f"Dosierdauer {duration}s außerhalb gültigen Bereichs "
                f"({MIN_DOSING_DURATION}-{MAX_DOSING_DURATION}s)"
            )

        _LOGGER.info("Manuelle Dosierung %s für %ds", dosing_type, duration)
        return await self.set_switch_state(key=device_key, action=ACTION_MAN, duration=duration)

    async def set_pv_surplus(self, active: bool, pump_speed: int = 2) -> dict[str, Any]:
        """Setze PV-Überschuss Modus."""
        action = ACTION_ON if active else ACTION_OFF
        _LOGGER.info("PV-Überschuss %s (Speed %d)", action, pump_speed)
        return await self.set_switch_state(key="PVSURPLUS", action=action, last_value=pump_speed)

    async def set_all_dmx_scenes(self, dmx_action: str) -> dict[str, Any]:
        """Setze alle DMX-Szenen gleichzeitig."""
        valid_actions = [ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO]
        if dmx_action not in valid_actions:
            raise VioletPoolCommandError(f"Ungültige DMX-Aktion: {dmx_action}")

        _LOGGER.info("Setze alle DMX-Szenen auf %s", dmx_action)
        return await self.set_switch_state(key="DMX_SCENE1", action=dmx_action)

    async def trigger_digital_input_rule(self, rule_key: str) -> dict[str, Any]:
        """Löse digitale Schaltregel aus."""
        valid_rules = [f"DIRULE_{i}" for i in range(1, 8)]
        if rule_key not in valid_rules:
            raise VioletPoolCommandError(f"Ungültige Regel: {rule_key}")

        _LOGGER.info("Triggere Regel %s", rule_key)
        return await self.set_switch_state(key=rule_key, action=ACTION_PUSH)

    async def set_digital_input_rule_lock(self, rule_key: str, lock_state: bool) -> dict[str, Any]:
        """Sperre oder entsperre digitale Schaltregel."""
        valid_rules = [f"DIRULE_{i}" for i in range(1, 8)]
        if rule_key not in valid_rules:
            raise VioletPoolCommandError(f"Ungültige Regel: {rule_key}")

        action = ACTION_LOCK if lock_state else ACTION_UNLOCK
        _LOGGER.info("%s Regel %s", action, rule_key)
        return await self.set_switch_state(key=rule_key, action=action)

    async def set_light_color_pulse(self) -> dict[str, Any]:
        """Sende Farbpuls an Beleuchtung."""
        _LOGGER.info("Sende Licht-Farbpuls")
        return await self.set_switch_state(key="LIGHT", action=ACTION_COLOR)


def create_api_instance(host: str, session: aiohttp.ClientSession, **kwargs) -> VioletPoolAPI:
    """Factory-Methode zum Erstellen einer API-Instanz."""
    return VioletPoolAPI(host=host, session=session, **kwargs)


async def test_api_connection(api: VioletPoolAPI) -> dict[str, Any]:
    """Teste API-Verbindung und gib Diagnose-Info zurück."""
    try:
        ping_result = await api.ping_controller()

        if not ping_result:
            return {
                "connected": False,
                "error": "Ping fehlgeschlagen",
                "troubleshooting": [
                    "IP-Adresse prüfen",
                    "Controller eingeschaltet?",
                    "Netzwerkverbindung prüfen",
                    "Firewall-Einstellungen überprüfen",
                ],
            }

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
                    "ssl": api._ssl_context,
                },
                "test_passed": True,
            }

        except Exception as e:
            return {
                "connected": True,
                "basic_connection": "OK",
                "extended_test": f"Teilweise: {e}",
                "recommendation": "Controller erreichbar, aber einige Funktionen eingeschränkt",
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
                "Netzwerk-Firewall überprüfen",
            ],
        }
