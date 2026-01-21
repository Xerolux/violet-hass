"""Violet Pool Controller Device Module - SMART FAILURE LOGGING + AUTO RECOVERY."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any, Mapping

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VioletPoolAPI, VioletPoolAPIError
from .const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    SPECIFIC_FULL_REFRESH_INTERVAL,
    SPECIFIC_READING_GROUPS,
)

_LOGGER = logging.getLogger(__name__)

# ✅ LOGGING OPTIMIZATION: Throttling-Konstanten
FAILURE_LOG_INTERVAL = 300  # Nur alle 5 Minuten bei wiederholten Fehlern

# ✅ RECOVERY OPTIMIZATION: Auto-Recovery-Konstanten
RECOVERY_MAX_ATTEMPTS = 10  # Maximale Recovery-Versuche
RECOVERY_BASE_DELAY = 10.0  # Basis-Delay für Exponential Backoff (10s)
RECOVERY_MAX_DELAY = 300.0  # Maximaler Delay zwischen Versuchen (5 Min)


class VioletPoolControllerDevice:
    """Violet Pool Controller Device - SMART LOGGING + AUTO RECOVERY."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI
    ) -> None:
        """Initialisiere die Geräteinstanz mit Smart Logging und Auto-Recovery."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: dict[str, Any] = {}
        self._firmware_version: str | None = None
        self._last_error: str | None = None
        self._api_lock = asyncio.Lock()
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        self._update_counter = 0
        self._full_refresh_interval = max(1, SPECIFIC_FULL_REFRESH_INTERVAL)
        self._specific_categories: list[str] = list(SPECIFIC_READING_GROUPS)
        self._supports_specific_updates = True

        # ✅ LOGGING OPTIMIZATION: Smart Failure Tracking
        self._last_failure_log = 0.0  # Timestamp für Throttling
        self._first_failure_logged = False  # Flag für erste Warnung
        self._recovery_logged = False  # Flag für Recovery-Message
        self._fw_logged = False  # Flag für Firmware-Version-Logging

        # ✅ RECOVERY OPTIMIZATION: Auto-Recovery Tracking
        self._recovery_attempts = 0  # Zähler für Recovery-Versuche
        self._in_recovery_mode = False  # Flag für Recovery-Modus
        self._last_recovery_attempt = 0.0  # Timestamp letzter Recovery-Versuch
        self._recovery_task: asyncio.Task | None = None  # Recovery-Task
        self._recovery_lock = asyncio.Lock()  # ✅ Lock für thread-safe Recovery

        # ✅ DIAGNOSTIC SENSORS: Connection health monitoring
        self._last_update_time = 0.0  # Timestamp of last successful update
        self._connection_latency = 0.0  # Last connection latency in milliseconds
        self._system_health = 100.0  # System health percentage (0-100)

        # Konfiguration extrahieren (mit Options-Support)
        entry_data = config_entry.data
        entry_options = config_entry.options
        self.api_url = self._extract_api_url(entry_data)
        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        # ✅ MULTI-CONTROLLER: Priorisiere Options (nachträgliche Änderungen), dann Data
        self.controller_name = entry_options.get(
            CONF_CONTROLLER_NAME,
            entry_data.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
        )

        _LOGGER.info(
            "Device initialized: '%s' (Controller: %s, URL: %s, SSL: %s, "
            "Device-ID: %d)",
            self.device_name,
            self.controller_name,
            self.api_url,
            self.use_ssl,
            self.device_id,
        )

    def _should_log_failure(self) -> bool:
        """
        Check if failure should be logged (throttling).

        ✅ LOGGING OPTIMIZATION: Prevents log spam for persistent issues.

        Returns:
            True if failure should be logged, False otherwise.
        """
        now = time.time()

        if now - self._last_failure_log > FAILURE_LOG_INTERVAL:
            self._last_failure_log = now
            return True
        return False

    async def async_update(self) -> dict[str, Any]:
        """
        Aktualisiert Gerätedaten vom Controller - SMART FAILURE LOGGING.

        ✅ LOGGING OPTIMIZATION:
        - Erste Warnung sofort
        - Zwischenwarnungen nur alle 5 Minuten
        - Kritischer Fehler bei Max-Failures
        - Recovery-Info nach Wiederherstellung
        """
        try:
            async with self._api_lock:
                # ✅ DIAGNOSTIC: Measure connection latency
                start_time = time.time()
                data = await self._fetch_controller_data()
                # Convert to milliseconds
                self._connection_latency = (time.time() - start_time) * 1000

                # Validiere Daten
                if not data or not isinstance(data, dict):
                    self._consecutive_failures += 1

                    # ✅ LOGGING OPTIMIZATION: Intelligentes Failure-Logging
                    if self._consecutive_failures == 1:
                        # First warning only if was available (not first setup)
                        if self._available or len(self._data) > 0:
                            _LOGGER.warning(
                                "Controller '%s' antwortet nicht (erste Warnung)",
                                self.device_name,
                            )
                            self._first_failure_logged = True
                            self._recovery_logged = False
                        else:
                            # Beim ersten Setup nur Debug-Level
                            _LOGGER.debug(
                                "Controller '%s' antwortet nicht (Setup-Phase)",
                                self.device_name,
                            )

                    elif self._consecutive_failures >= self._max_consecutive_failures:
                        # Kritisch: Wird unavailable - IMMER loggen
                        _LOGGER.error(
                            "Controller '%s' nach %d aufeinanderfolgenden Fehlern als "
                            "unavailable markiert. Starte Auto-Recovery...",
                            self.device_name,
                            self._consecutive_failures,
                        )
                        self._available = False

                        # ✅ RECOVERY: Start automatic recovery
                        await self._start_recovery_background_task()

                        raise UpdateFailed(
                            f"Controller '{self.device_name}' nicht erreichbar "
                            f"({self._consecutive_failures} Fehler), Recovery gestartet"
                        )

                    elif self._should_log_failure():
                        # Zwischenwarnungen nur throttled
                        _LOGGER.warning(
                            "Controller '%s' weiterhin nicht erreichbar "
                            "(%d/%d aufeinanderfolgende Fehler)",
                            self.device_name,
                            self._consecutive_failures,
                            self._max_consecutive_failures,
                        )

                    # ✅ DIAGNOSTIC: Degrade system health based on failures
                    self._system_health = max(
                        0.0, 100.0 - (self._consecutive_failures * 20.0)
                    )

                    # Gebe alte Daten zurück bei temporären Problemen
                    return self._data

                # ✅ LOGGING OPTIMIZATION: Erfolg nach Fehlern = wichtige Info
                if self._consecutive_failures > 0 and not self._recovery_logged:
                    _LOGGER.info(
                        "✓ Controller '%s' wieder erreichbar (nach %d Fehler%s)",
                        self.device_name,
                        self._consecutive_failures,
                        "n" if self._consecutive_failures > 1 else "",
                    )
                    self._recovery_logged = True
                    self._first_failure_logged = False

                # Update erfolgreich
                self._data = data
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None

                # ✅ DIAGNOSTIC: Update health metrics
                self._last_update_time = time.time()
                self._system_health = 100.0  # Perfect health

                # Firmware-Version extrahieren (mehrere Fallbacks)
                # ✅ FIX: Erweiterte Firmware-Extraktion mit mehr Fallback-Optionen
                self._firmware_version = (
                    data.get("FW")
                    or data.get("fw")
                    or data.get("SW_VERSION")
                    or data.get("sw_version")
                    or data.get("VERSION")
                    or data.get("version")
                    or data.get("SW_VERSION_CARRIER")
                    or data.get("FIRMWARE_VERSION")
                    or data.get("firmware_version")
                    or self._firmware_version  # Behalte alten Wert wenn nichts gefunden
                )

                # Debug-Log nur wenn Firmware gefunden wurde und sich geändert hat
                if self._firmware_version and not hasattr(self, "_fw_logged"):
                    _LOGGER.debug(
                        "Firmware-Version erkannt: %s", self._firmware_version
                    )
                    self._fw_logged = True

                return data

        except VioletPoolAPIError as err:
            self._last_error = str(err)
            self._consecutive_failures += 1

            # ✅ LOGGING OPTIMIZATION: Konsolidiertes Error-Logging
            if self._consecutive_failures == 1:
                # Beim ersten Setup nur Debug, sonst Error
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "API-Fehler bei Setup von '%s': %s",
                        self.device_name,
                        str(err)[:200],
                    )
                else:
                    _LOGGER.error(
                        "API-Fehler bei Update von '%s': %s",
                        self.device_name,
                        str(err)[:200],  # Gekürzt auf 200 Zeichen
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d API-Fehlern nicht mehr verfügbar",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Controller nicht erreichbar: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende API-Probleme bei '%s' (%d/%d Fehler)",
                    self.device_name,
                    self._consecutive_failures,
                    self._max_consecutive_failures,
                )

            # Gebe alte Daten zurück bei temporären Fehlern
            return self._data

        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1

            # ✅ LOGGING: Unexpected errors always logged
            if self._consecutive_failures == 1:
                # Beim ersten Setup nur Debug, sonst volle Exception
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "Fehler bei Setup von '%s': %s", self.device_name, err
                    )
                else:
                    _LOGGER.exception(
                        "Unerwarteter Fehler bei Update von '%s'", self.device_name
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d unerwarteten Fehlern nicht verfügbar",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Update error: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende Probleme bei '%s': %s (%d/%d Fehler)",
                    self.device_name,
                    type(err).__name__,  # Nur Exception-Typ, nicht full trace
                    self._consecutive_failures,
                    self._max_consecutive_failures,
                )

            return self._data

    async def _fetch_controller_data(self) -> dict[str, Any]:
        """Fetch controller data with support for partial refreshes."""

        self._update_counter += 1

        full_refresh_due = (
            self._update_counter == 1
            or (
                self._full_refresh_interval
                and self._update_counter % self._full_refresh_interval == 0
            )
            or not self._supports_specific_updates
        )

        if full_refresh_due:
            data = await self.api.get_readings()
            self._specific_categories = self._derive_specific_categories(data)
            self._supports_specific_updates = True
            return data

        categories = self._specific_categories or list(SPECIFIC_READING_GROUPS)

        try:
            return await self.api.get_specific_readings(categories)
        except VioletPoolAPIError as err:
            _LOGGER.debug(
                "Spezifischer Datenabruf fehlgeschlagen (%s). Fallback auf Vollabruf.",
                err,
            )
            self._supports_specific_updates = False
            return await self.api.get_readings()

    def _derive_specific_categories(self, data: Mapping[str, Any]) -> list[str]:
        """Build a list of categories used for specific reading refreshes."""

        categories: set[str] = set(SPECIFIC_READING_GROUPS)

        for key in data.keys():
            if not isinstance(key, str) or not key:
                continue
            prefix = key.split("_")[0]
            if not prefix:
                continue
            if prefix.lower() in {"date", "time"}:
                categories.add(prefix.lower())
            else:
                categories.add(prefix.upper())

        ordered = sorted(categories)
        # Limit the number of categories to keep the query string reasonable
        if len(ordered) > 30:
            ordered = ordered[:30]
        return ordered

    @property
    def available(self) -> bool:
        """Gibt den Verfügbarkeitsstatus zurück."""
        return self._available

    @property
    def firmware_version(self) -> str | None:
        """Gibt die Firmware-Version zurück."""
        return self._firmware_version

    @property
    def data(self) -> dict[str, Any]:
        """Gibt die aktuellen Daten zurück."""
        return self._data

    @property
    def last_error(self) -> str | None:
        """Gibt den letzten Fehler zurück."""
        return self._last_error

    @property
    def consecutive_failures(self) -> int:
        """Gibt die Anzahl aufeinanderfolgender Fehler zurück."""
        return self._consecutive_failures

    @property
    def device_info(self) -> dict[str, Any]:
        """
        Gibt die Geräteinformationen für Home Assistant zurück.

        ✅ MULTI-CONTROLLER SUPPORT:
        - Verwendet controller_name für visuelle Unterscheidung
        - suggested_area ermöglicht automatische Bereichszuweisung
        - Kein Caching, damit Options-Änderungen sofort wirksam werden
        """
        return {
            "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
            # ✅ Uses Controller-Name instead of Device-Name
            "name": self.controller_name,
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Pool Controller",
            "sw_version": self._firmware_version or "Unbekannt",
            "suggested_area": self.controller_name,  # ✅ Auto-Area für Multi-Controller
        }

    @property
    def system_health(self) -> float:
        """
        Return the system health percentage (0-100).

        ✅ DIAGNOSTIC SENSOR: Overall connection health.
        """
        return self._system_health

    @property
    def connection_latency(self) -> float:
        """
        Return the last connection latency in milliseconds.

        ✅ DIAGNOSTIC SENSOR: Connection response time.
        """
        return self._connection_latency

    @property
    def last_event_age(self) -> float:
        """
        Return seconds since the last successful update.

        ✅ DIAGNOSTIC SENSOR: Data freshness indicator.
        """
        if self._last_update_time == 0.0:
            return 0.0
        return time.time() - self._last_update_time

    async def _attempt_recovery(self) -> bool:
        """
        Attempt automatic connection recovery.

        ✅ RECOVERY OPTIMIZATION:
        - Exponential backoff for recovery attempts.
        - Thread-safe with asyncio.Lock (Race Condition Fix).

        Returns:
            True if recovery was successful, False otherwise.
        """
# ✅ RACE CONDITION FIX: Complete atomic recovery with proper lock protection
        async with self._recovery_lock:
            # Atomic check-and-set under same lock
            if self._in_recovery_mode:
                _LOGGER.debug("Recovery bereits im Gange, überspringe")
                return False

            if self._recovery_attempts > RECOVERY_MAX_ATTEMPTS:
                _LOGGER.warning("Maximum recovery attempts reached")
                return False

            # Set recovery state atomically
            self._in_recovery_mode = True
            self._recovery_attempts += 1
            current_attempt = self._recovery_attempts

        try:
            # Calculate exponential backoff delay
            delay = min(
                RECOVERY_MAX_DELAY,
                RECOVERY_BASE_DELAY * (2 ** (current_attempt - 1)),
            )
            
            _LOGGER.info(
                "🔄 Recovery-Versuch %d/%d für '%s' (Delay: %.1fs)",
                current_attempt,
                RECOVERY_MAX_ATTEMPTS,
                self.device_name,
                delay,
            )
            
            await asyncio.sleep(delay)
            
            # Attempt data retrieval
            data = await self._fetch_controller_data()
            
            if data and isinstance(data, dict):
                # Recovery successful - reset state atomically
                async with self._recovery_lock:
                    self._consecutive_failures = 0
                    self._recovery_attempts = 0
                    self._available = True
                    self._recovery_logged = True
                
                _LOGGER.info("Recovery successful for '%s'", self.device_name)
                return True
            
            return False
            
        except Exception as err:
            _LOGGER.debug(
                "Recovery-Versuch %d fehlgeschlagen: %s",
                current_attempt,
                err,
            )
            return False
            
        finally:
            # Always ensure recovery state is reset under lock protection
            async with self._recovery_lock:
                self._in_recovery_mode = False
                self._last_recovery_attempt = asyncio.get_event_loop().time()

    async def _start_recovery_background_task(self) -> None:
        """
        Start recovery in the background.

        ✅ RECOVERY OPTIMIZATION: Prevents blocking normal updates.
        """
        if self._recovery_task and not self._recovery_task.done():
            _LOGGER.debug("Recovery-Task läuft bereits")
            return

        if self._recovery_attempts >= RECOVERY_MAX_ATTEMPTS:
            _LOGGER.warning(
                "⚠️ Maximale Recovery-Versuche (%d) erreicht für '%s'. "
                "Manuelle Intervention erforderlich.",
                RECOVERY_MAX_ATTEMPTS,
                self.device_name,
            )
            return

        async def recovery_loop():
            """Recovery-Loop im Hintergrund."""
            while self._recovery_attempts < RECOVERY_MAX_ATTEMPTS:
                if await self._attempt_recovery():
                    _LOGGER.info(
                        "✅ Background Recovery erfolgreich für '%s'",
                        self.device_name,
                    )
                    return

                # Warte vor nächstem Versuch
                await asyncio.sleep(5)

            _LOGGER.error(
                "❌ Background Recovery fehlgeschlagen für '%s' nach %d Versuchen",
                self.device_name,
                RECOVERY_MAX_ATTEMPTS,
            )

        self._recovery_task = asyncio.create_task(recovery_loop())
        _LOGGER.info(
            "🔄 Background Recovery gestartet für '%s'",
            self.device_name,
        )

    def _extract_api_url(self, entry_data: Mapping[str, Any]) -> str:
        """
        Extract the API URL from config data.

        Args:
            entry_data: The configuration data dictionary.

        Returns:
            The API URL.

        Raises:
            ValueError: If no API URL is found.
        """
        url = (
            entry_data.get(CONF_API_URL)
            or entry_data.get("host")
            or entry_data.get("base_ip")
        )

        if not url:
            raise ValueError("Keine IP-Adresse in Config Entry gefunden")

        if not isinstance(url, str):
            raise ValueError("API URL ist kein String")

        return url.strip()


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data Update Coordinator - SMART FAILURE LOGGING."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: VioletPoolControllerDevice,
        name: str,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
    ) -> None:
        """Initialisiere den Coordinator mit Smart Logging."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=polling_interval),
        )
        self.device = device

        _LOGGER.info(
            "Coordinator initialisiert für '%s' (Abruf alle %ds)",
            name,
            polling_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Update data from the device.

        ✅ LOGGING OPTIMIZATION:
        - Errors are already smartly logged in the device.
        - Minimal logging here.

        Returns:
            A dictionary containing the updated data.

        Raises:
            UpdateFailed: If the update fails.
        """
        try:
            return await self.device.async_update()
        except VioletPoolAPIError as err:
            # ✅ Bereits im Device geloggt, hier nur Exception propagieren
            raise UpdateFailed(f"API error: {err}") from err


async def async_setup_device(
    hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI
) -> VioletPoolDataUpdateCoordinator:
    """
    Setup des Violet Pool Controller Devices - SMART FAILURE LOGGING + RETRY LOGIC.

    ✅ LOGGING OPTIMIZATION: Fokus auf Setup-Erfolg/Fehler, nicht auf Details.
    ✅ RETRY LOGIC: Mehrere Versuche beim ersten Setup für bessere Zuverlässigkeit.
    """
    try:
        # Device erstellen
        device = VioletPoolControllerDevice(hass, config_entry, api)

        # Ersten Update durchführen mit Retry-Logik (max 3 Versuche)
        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                _LOGGER.debug(
                    "Setup-Versuch %d/%d für '%s'",
                    attempt,
                    max_retries,
                    device.device_name,
                )

                await device.async_update()

                if device.available:
                    _LOGGER.debug("Setup-Versuch %d erfolgreich", attempt)
                    break

            except Exception as err:
                last_error = err
                _LOGGER.debug("Setup-Versuch %d fehlgeschlagen: %s", attempt, err)

            # Warte zwischen Versuchen (außer beim letzten)
            if attempt < max_retries:
                await asyncio.sleep(2)

        if not device.available:
            # ✅ Clear setup error message after all attempts
            error_msg = (
                f"Controller '{device.device_name}' nicht erreichbar nach "
                f"{max_retries} Versuchen. "
                f"Bitte Verbindung und Controller-Status prüfen."
            )
            if last_error:
                error_msg += f" Letzter Fehler: {last_error}"

            raise ConfigEntryNotReady(error_msg)

        # Polling-Intervall aus Options oder Data holen
        polling_interval = config_entry.options.get(
            CONF_POLLING_INTERVAL,
            config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        )

        # Coordinator erstellen
        coordinator = VioletPoolDataUpdateCoordinator(
            hass,
            device,
            config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
            polling_interval,
        )

        # Ersten Refresh durchführen
        await coordinator.async_config_entry_first_refresh()

        # ✅ Erfolgreicher Setup = wichtige Info
        _LOGGER.info(
            "✓ Device Setup erfolgreich: '%s' (FW: %s, %d Datenpunkte)",
            device.device_name,
            device.firmware_version or "Unbekannt",
            len(device.data) if device.data else 0,
        )

        return coordinator

    except ConfigEntryNotReady:
        # Bereits korrekt formatierte Exception durchreichen
        raise

    except Exception as err:
        # ✅ Setup-Fehler immer loggen (kritisch)
        _LOGGER.exception("Device Setup fehlgeschlagen: %s", err)
        raise ConfigEntryNotReady(f"Setup-Fehler: {err}") from err
