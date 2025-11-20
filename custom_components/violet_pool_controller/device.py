"""Violet Pool Controller Device Module - SMART FAILURE LOGGING + AUTO RECOVERY."""
import logging
import asyncio
import time
from datetime import timedelta
from typing import Any, Optional, Mapping

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_CONTROLLER_NAME,
    SPECIFIC_READING_GROUPS,
    SPECIFIC_FULL_REFRESH_INTERVAL,
)
from .api import VioletPoolAPI, VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)

# ✅ LOGGING OPTIMIZATION: Throttling-Konstanten
FAILURE_LOG_INTERVAL = 300  # Nur alle 5 Minuten bei wiederholten Fehlern

# ✅ RECOVERY OPTIMIZATION: Auto-Recovery-Konstanten
RECOVERY_MAX_ATTEMPTS = 10  # Maximale Recovery-Versuche
RECOVERY_BASE_DELAY = 10.0  # Basis-Delay für Exponential Backoff (10s)
RECOVERY_MAX_DELAY = 300.0  # Maximaler Delay zwischen Versuchen (5 Min)


class VioletPoolControllerDevice:
    """Repräsentiert ein Violet Pool Controller Gerät - SMART FAILURE LOGGING + AUTO RECOVERY."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: VioletPoolAPI
    ) -> None:
        """Initialisiere die Geräteinstanz mit Smart Logging und Auto-Recovery."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: dict[str, Any] = {}
        self._device_info: dict[str, Any] = {}
        self._firmware_version: Optional[str] = None
        self._last_error: Optional[str] = None
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

        # ✅ RECOVERY OPTIMIZATION: Auto-Recovery Tracking
        self._recovery_attempts = 0  # Zähler für Recovery-Versuche
        self._in_recovery_mode = False  # Flag für Recovery-Modus
        self._last_recovery_attempt = 0.0  # Timestamp letzter Recovery-Versuch
        self._recovery_task: Optional[asyncio.Task] = None  # Recovery-Task

        # Konfiguration extrahieren
        entry_data = config_entry.data
        self.api_url = self._extract_api_url(entry_data)
        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self.controller_name = entry_data.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME)

        _LOGGER.info(
            "Device initialisiert: '%s' (Controller: %s, URL: %s, SSL: %s, Device-ID: %d)",
            self.device_name, self.controller_name, self.api_url, self.use_ssl, self.device_id
        )

    def _should_log_failure(self) -> bool:
        """
        Prüfe ob Failure geloggt werden soll (Throttling).
        
        ✅ LOGGING OPTIMIZATION: Verhindert Log-Spam bei anhaltenden Problemen.
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
                data = await self._fetch_controller_data()
                
                # Validiere Daten
                if not data or not isinstance(data, dict):
                    self._consecutive_failures += 1
                    
                    # ✅ LOGGING OPTIMIZATION: Intelligentes Failure-Logging
                    if self._consecutive_failures == 1:
                        # Erste Warnung IMMER loggen
                        _LOGGER.warning(
                            "Controller '%s' antwortet nicht (erste Warnung)",
                            self.device_name
                        )
                        self._first_failure_logged = True
                        self._recovery_logged = False
                        
                    elif self._consecutive_failures >= self._max_consecutive_failures:
                        # Kritisch: Wird unavailable - IMMER loggen
                        _LOGGER.error(
                            "Controller '%s' nach %d aufeinanderfolgenden Fehlern als "
                            "unavailable markiert. Starte Auto-Recovery...",
                            self.device_name,
                            self._consecutive_failures
                        )
                        self._available = False

                        # ✅ RECOVERY OPTIMIZATION: Starte automatischen Recovery-Versuch
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
                            self._max_consecutive_failures
                        )
                    
                    # Gebe alte Daten zurück bei temporären Problemen
                    return self._data
                
                # ✅ LOGGING OPTIMIZATION: Erfolg nach Fehlern = wichtige Info
                if self._consecutive_failures > 0 and not self._recovery_logged:
                    _LOGGER.info(
                        "✓ Controller '%s' wieder erreichbar (nach %d Fehler%s)",
                        self.device_name,
                        self._consecutive_failures,
                        "n" if self._consecutive_failures > 1 else ""
                    )
                    self._recovery_logged = True
                    self._first_failure_logged = False
                
                # Update erfolgreich
                self._data = data
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None
                
                # Firmware-Version extrahieren
                if "FW" in data or "fw" in data:
                    self._firmware_version = data.get("FW") or data.get("fw")

                return data

        except VioletPoolAPIError as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            
            # ✅ LOGGING OPTIMIZATION: Konsolidiertes Error-Logging
            if self._consecutive_failures == 1:
                _LOGGER.error(
                    "API-Fehler bei Update von '%s': %s",
                    self.device_name,
                    str(err)[:200]  # Gekürzt auf 200 Zeichen
                )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d API-Fehlern nicht mehr verfügbar",
                    self.device_name,
                    self._consecutive_failures
                )
                self._available = False
                raise UpdateFailed(f"Controller nicht erreichbar: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende API-Probleme bei '%s' (%d/%d Fehler)",
                    self.device_name,
                    self._consecutive_failures,
                    self._max_consecutive_failures
                )
            
            # Gebe alte Daten zurück bei temporären Fehlern
            return self._data
            
        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            
            # ✅ LOGGING OPTIMIZATION: Unerwartete Fehler = immer loggen (aber nur Exception-Typ)
            if self._consecutive_failures == 1:
                _LOGGER.exception(
                    "Unerwarteter Fehler bei Update von '%s'",
                    self.device_name
                )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d unerwarteten Fehlern nicht verfügbar",
                    self.device_name,
                    self._consecutive_failures
                )
                self._available = False
                raise UpdateFailed(f"Update error: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende Probleme bei '%s': %s (%d/%d Fehler)",
                    self.device_name,
                    type(err).__name__,  # Nur Exception-Typ, nicht full trace
                    self._consecutive_failures,
                    self._max_consecutive_failures
                )

            return self._data

    async def _fetch_controller_data(self) -> dict[str, Any]:
        """Fetch controller data with support for partial refreshes."""

        self._update_counter += 1

        full_refresh_due = (
            self._update_counter == 1
            or (self._full_refresh_interval and self._update_counter % self._full_refresh_interval == 0)
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
    def firmware_version(self) -> Optional[str]:
        """Gibt die Firmware-Version zurück."""
        return self._firmware_version

    @property
    def data(self) -> dict[str, Any]:
        """Gibt die aktuellen Daten zurück."""
        return self._data

    @property
    def last_error(self) -> Optional[str]:
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
        """
        if not self._device_info:
            self._device_info = {
                "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
                "name": self.controller_name,  # ✅ Verwendet Controller-Name statt Device-Name
                "manufacturer": "PoolDigital GmbH & Co. KG",
                "model": "Violet Pool Controller",
                "sw_version": self._firmware_version or "Unbekannt",
                "suggested_area": self.controller_name,  # ✅ Auto-Area für Multi-Controller
            }
        return self._device_info

    async def _attempt_recovery(self) -> bool:
        """
        Versuche automatische Wiederherstellung der Verbindung.

        ✅ RECOVERY OPTIMIZATION: Exponential Backoff für Recovery-Versuche.

        Returns:
            True wenn Recovery erfolgreich, False sonst
        """
        if self._in_recovery_mode:
            _LOGGER.debug("Recovery bereits im Gange, überspringe")
            return False

        self._in_recovery_mode = True
        self._recovery_attempts += 1

        # Berechne Exponential Backoff Delay
        delay = min(
            RECOVERY_MAX_DELAY,
            RECOVERY_BASE_DELAY * (2 ** (self._recovery_attempts - 1))
        )

        _LOGGER.info(
            "🔄 Recovery-Versuch %d/%d für '%s' (Delay: %.1fs)",
            self._recovery_attempts,
            RECOVERY_MAX_ATTEMPTS,
            self.device_name,
            delay,
        )

        try:
            # Warte mit Exponential Backoff
            await asyncio.sleep(delay)

            # Versuche Daten abzurufen
            data = await self._fetch_controller_data()

            if data and isinstance(data, dict):
                # ✅ RECOVERY ERFOLGREICH!
                _LOGGER.info(
                    "✅ Recovery erfolgreich für '%s' nach %d Versuch%s",
                    self.device_name,
                    self._recovery_attempts,
                    "en" if self._recovery_attempts > 1 else "",
                )

                # Reset Recovery-Status
                self._consecutive_failures = 0
                self._recovery_attempts = 0
                self._available = True
                self._in_recovery_mode = False
                self._recovery_logged = True

                return True

            return False

        except Exception as err:
            _LOGGER.debug(
                "Recovery-Versuch %d fehlgeschlagen: %s",
                self._recovery_attempts,
                err,
            )
            return False
        finally:
            self._in_recovery_mode = False
            self._last_recovery_attempt = time.time()

    async def _start_recovery_background_task(self) -> None:
        """
        Starte Recovery im Hintergrund.

        ✅ RECOVERY OPTIMIZATION: Verhindert Blockierung des normalen Updates.
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

    def _extract_api_url(self, entry_data: dict) -> str:
        """Extrahiert die API-URL aus den Config-Daten."""
        url = (
            entry_data.get(CONF_API_URL) or
            entry_data.get("host") or
            entry_data.get("base_ip")
        )

        if not url:
            raise ValueError("Keine IP-Adresse in Config Entry gefunden")

        return url.strip()


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Data Update Coordinator - SMART FAILURE LOGGING."""
    
    def __init__(
        self, 
        hass: HomeAssistant, 
        device: VioletPoolControllerDevice, 
        name: str, 
        polling_interval: int = DEFAULT_POLLING_INTERVAL
    ) -> None:
        """Initialisiere den Coordinator mit Smart Logging."""
        super().__init__(
            hass, 
            _LOGGER,
            name=name, 
            update_interval=timedelta(seconds=polling_interval)
        )
        self.device = device
        
        _LOGGER.info(
            "Coordinator initialisiert für '%s' (Abruf alle %ds)", 
            name, 
            polling_interval
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Aktualisiere die Daten vom Device.
        
        ✅ LOGGING OPTIMIZATION: 
        - Fehler werden bereits im Device smart geloggt
        - Hier nur minimal loggen
        """
        try:
            return await self.device.async_update()
        except VioletPoolAPIError as err:
            # ✅ Bereits im Device geloggt, hier nur Exception propagieren
            raise UpdateFailed(f"API error: {err}") from err


async def async_setup_device(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    api: VioletPoolAPI
) -> VioletPoolDataUpdateCoordinator:
    """
    Setup des Violet Pool Controller Devices - SMART FAILURE LOGGING.
    
    ✅ LOGGING OPTIMIZATION: Fokus auf Setup-Erfolg/Fehler, nicht auf Details.
    """
    try:
        # Device erstellen
        device = VioletPoolControllerDevice(hass, config_entry, api)
        
        # Ersten Update durchführen (Verfügbarkeit prüfen)
        await device.async_update()
        
        if not device.available:
            # ✅ Klare Setup-Fehlermeldung
            raise ConfigEntryNotReady(
                f"Controller '{device.device_name}' nicht erreichbar bei Setup. "
                "Bitte Verbindung und Controller-Status prüfen."
            )
        
        # Polling-Intervall aus Options oder Data holen
        polling_interval = config_entry.options.get(
            CONF_POLLING_INTERVAL, 
            config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        )
        
        # Coordinator erstellen
        coordinator = VioletPoolDataUpdateCoordinator(
            hass, 
            device, 
            config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"), 
            polling_interval
        )
        
        # Ersten Refresh durchführen
        await coordinator.async_config_entry_first_refresh()
        
        # ✅ Erfolgreicher Setup = wichtige Info
        _LOGGER.info(
            "✓ Device Setup erfolgreich: '%s' (FW: %s, %d Datenpunkte)", 
            device.device_name, 
            device.firmware_version or "Unbekannt",
            len(device.data) if device.data else 0
        )
        
        return coordinator
        
    except ConfigEntryNotReady:
        # Bereits korrekt formatierte Exception durchreichen
        raise
        
    except Exception as err:
        # ✅ Setup-Fehler immer loggen (kritisch)
        _LOGGER.exception("Device Setup fehlgeschlagen: %s", err)
        raise ConfigEntryNotReady(f"Setup-Fehler: {err}") from err
