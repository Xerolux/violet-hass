"""Violet Pool Controller Device Module - IMPROVED VERSION."""
import logging
import asyncio
import json
import aiohttp
from datetime import timedelta
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .const import (
    DOMAIN, API_READINGS, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_NAME, CONF_DEVICE_ID,
    CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES,
    DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT_DURATION, DEFAULT_RETRY_ATTEMPTS
)
from .api import VioletPoolAPI, VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)


class VioletPoolControllerDevice:
    """Repräsentiert ein Violet Pool Controller Gerät - IMPROVED."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        api: VioletPoolAPI
    ) -> None:
        """Initialisiere die Geräteinstanz."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: Dict[str, Any] = {}
        self._device_info: Dict[str, Any] = {}
        self._firmware_version: Optional[str] = None
        self._last_error: Optional[str] = None
        self._api_lock = asyncio.Lock()
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5

        # Konfiguration extrahieren
        entry_data = config_entry.data
        self.api_url = self._extract_api_url(entry_data)
        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        
        # FIX: Korrektur für aiohttp.BasicAuth - password niemals None
        username = entry_data.get(CONF_USERNAME)
        password = entry_data.get(CONF_PASSWORD)
        
        # KRITISCHER FIX: Sicherstellen dass password ein String ist
        if username:
            # Wenn password None ist, leeren String verwenden
            password = password if password is not None else ""
            self.auth = aiohttp.BasicAuth(username, password)
            _LOGGER.debug("Auth konfiguriert für User: %s", username)
        else:
            self.auth = None
            _LOGGER.debug("Keine Authentifizierung konfiguriert")
        
        # Optionen
        self.polling_interval = int(
            config_entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        )
        self.timeout_duration = int(
            config_entry.options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
        )
        self.retry_attempts = int(
            config_entry.options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
        )
        self.active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, [])

        self.api_base_url = f"{'https' if self.use_ssl else 'http'}://{self.api_url}"
        self.api_readings_url = f"{self.api_base_url}{API_READINGS}?ALL"
        
        _LOGGER.info(
            "Gerät initialisiert: %s @ %s (ID: %s, Poll: %ds)", 
            self.device_name, self.api_url, self.device_id, self.polling_interval
        )

    def _extract_api_url(self, entry_data: Dict[str, Any]) -> str:
        """Extrahiere API-URL aus Config-Entry - NEW."""
        url = (
            entry_data.get(CONF_API_URL) or 
            entry_data.get("host") or 
            entry_data.get("base_ip")
        )
        
        if not url:
            raise ValueError(
                "Keine gültige API-URL in Config-Entry gefunden. "
                "Erwartete Keys: api_url, host oder base_ip"
            )
        
        return url.strip()

    @property
    def available(self) -> bool:
        """Gibt Geräteverfügbarkeit zurück."""
        return self._available

    @property
    def firmware_version(self) -> Optional[str]:
        """Gibt Firmware-Version zurück."""
        return self._firmware_version

    @property
    def name(self) -> str:
        """Gibt Gerätenamen zurück."""
        return self.device_name

    @property
    def device_info(self) -> Dict[str, Any]:
        """Gibt Geräteinformationen zurück."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": f"{self.device_name} ({self.api_url})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": self._device_info.get("model", "Violet Pool Controller"),
            "sw_version": self._firmware_version or "Unbekannt",
            "configuration_url": self.api_base_url,
        }

    @property
    def last_error(self) -> Optional[str]:
        """Gibt letzten Fehler zurück."""
        return self._last_error

    @property
    def consecutive_failures(self) -> int:
        """Gibt Anzahl aufeinanderfolgender Fehler zurück - NEW."""
        return self._consecutive_failures

    async def async_setup(self) -> bool:
        """Richte Gerät ein - IMPROVED."""
        try:
            _LOGGER.info("Starte Setup für %s", self.device_name)
            await self.async_update()
            self._available = True
            self._consecutive_failures = 0
            _LOGGER.info("Setup erfolgreich für %s", self.device_name)
            return True
        except Exception as e:
            self._last_error = str(e)
            self._available = False
            self._consecutive_failures += 1
            _LOGGER.error(
                "Setup-Fehler für %s (Versuch %d/%d): %s", 
                self.device_name, self._consecutive_failures, 
                self._max_consecutive_failures, e
            )
            
            # Bei zu vielen Fehlern aufgeben
            if self._consecutive_failures >= self._max_consecutive_failures:
                raise ConfigEntryNotReady(
                    f"Setup nach {self._consecutive_failures} Versuchen fehlgeschlagen: {e}"
                ) from e
            
            return False

    async def async_update(self) -> Dict[str, Any]:
        """Aktualisiere Gerätedaten - IMPROVED."""
        async with self._api_lock:
            try:
                # Daten über API holen
                data = await self.api.get_readings("ALL")
                
                if not data:
                    raise VioletPoolAPIError("Keine Daten empfangen")
                
                if not isinstance(data, dict):
                    _LOGGER.warning("Unerwarteter Datentyp: %s", type(data))
                    raise VioletPoolAPIError(f"Ungültiger Datentyp: {type(data)}")
                
                # Firmware-Version extrahieren
                self._firmware_version = (
                    data.get("fw") or 
                    data.get("firmware_version") or 
                    data.get("FW")
                )
                
                # Daten verarbeiten
                self._data = self._process_api_data(data)
                
                # Status aktualisieren
                self._available = True
                self._last_error = None
                self._consecutive_failures = 0
                
                _LOGGER.debug(
                    "Update erfolgreich: %d Datenpunkte, FW: %s", 
                    len(self._data), self._firmware_version or "unknown"
                )
                
                return self._data
                
            except VioletPoolAPIError as e:
                self._available = False
                self._last_error = str(e)
                self._consecutive_failures += 1
                
                _LOGGER.error(
                    "API-Update-Fehler (Fehler %d/%d): %s", 
                    self._consecutive_failures, self._max_consecutive_failures, e
                )
                
                raise UpdateFailed(str(e)) from e
                
            except Exception as e:
                self._available = False
                self._last_error = str(e)
                self._consecutive_failures += 1
                
                _LOGGER.error(
                    "Unerwarteter Update-Fehler (Fehler %d/%d): %s", 
                    self._consecutive_failures, self._max_consecutive_failures, e
                )
                
                raise UpdateFailed(str(e)) from e

    def _process_api_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeite API-Daten - IMPROVED."""
        if not isinstance(data, dict):
            _LOGGER.warning("API-Daten sind kein Dictionary: %s", type(data))
            return {}
        
        processed = {}
        conversion_errors = 0
        
        for key, value in data.items():
            try:
                # String-zu-Nummer-Konvertierung
                if isinstance(value, str):
                    # Versuche numerische Konvertierung
                    clean_value = value.replace(",", ".").strip()
                    
                    # Float-Konvertierung
                    if '.' in clean_value or 'e' in clean_value.lower():
                        try:
                            processed[key] = float(clean_value)
                            continue
                        except ValueError:
                            pass
                    
                    # Integer-Konvertierung
                    if clean_value.isdigit() or (clean_value.startswith('-') and clean_value[1:].isdigit()):
                        try:
                            processed[key] = int(clean_value)
                            continue
                        except ValueError:
                            pass
                    
                    # Boolean-Konvertierung
                    value_upper = clean_value.upper()
                    if value_upper in ('TRUE', 'FALSE', 'ON', 'OFF', 'YES', 'NO'):
                        processed[key] = value_upper in ('TRUE', 'ON', 'YES')
                        continue
                    
                    # Als String beibehalten
                    processed[key] = value
                else:
                    # Nicht-String direkt übernehmen
                    processed[key] = value
                    
            except Exception as e:
                _LOGGER.debug("Konvertierungsfehler für %s=%s: %s", key, value, e)
                processed[key] = value
                conversion_errors += 1
        
        if conversion_errors > 0:
            _LOGGER.debug(
                "Datenverarbeitung: %d Werte, %d Konvertierungsfehler", 
                len(processed), conversion_errors
            )
        
        return processed

    def get_data_point(self, key: str, default: Any = None) -> Any:
        """Hole einzelnen Datenpunkt - NEW."""
        return self._data.get(key, default)

    def get_numeric_value(self, key: str, default: float = 0.0) -> float:
        """Hole numerischen Wert mit Fallback - NEW."""
        value = self._data.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            _LOGGER.debug("Konnte %s nicht zu Float konvertieren: %s", key, value)
            return default

    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """Hole Boolean-Wert mit intelligenter Konvertierung - NEW."""
        value = self._data.get(key, default)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_upper = value.upper()
            return value_upper in ('TRUE', 'ON', 'YES', '1', 'ACTIVE')
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        return default


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator für regelmäßige Daten-Updates - IMPROVED."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        device: VioletPoolControllerDevice,
        update_interval: timedelta
    ) -> None:
        """Initialisiere den Coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.device_id}",
            update_interval=update_interval,
        )
        self.device = device
        self._update_failures = 0
        self._max_update_failures = 10

    async def _async_update_data(self) -> Dict[str, Any]:
        """Hole neue Daten vom Gerät - IMPROVED."""
        try:
            data = await self.device.async_update()
            self._update_failures = 0
            return data
        except UpdateFailed as e:
            self._update_failures += 1
            
            if self._update_failures >= self._max_update_failures:
                _LOGGER.error(
                    "Zu viele aufeinanderfolgende Update-Fehler (%d). "
                    "Integration wird möglicherweise neu geladen.",
                    self._update_failures
                )
            
            raise e
        except Exception as e:
            self._update_failures += 1
            _LOGGER.error("Unerwarteter Coordinator-Fehler: %s", e)
            raise UpdateFailed(f"Unerwarteter Fehler: {e}") from e


async def async_setup_device(
    hass: HomeAssistant, 
    config_entry: ConfigEntry,
    api: VioletPoolAPI
) -> VioletPoolDataUpdateCoordinator:
    """Richte Gerät und Coordinator ein - IMPROVED."""
    device = VioletPoolControllerDevice(hass, config_entry, api)
    
    # Initiales Setup
    setup_success = await device.async_setup()
    if not setup_success:
        raise ConfigEntryNotReady(
            f"Gerät-Setup fehlgeschlagen: {device.last_error}"
        )
    
    # Coordinator erstellen
    update_interval = timedelta(seconds=device.polling_interval)
    coordinator = VioletPoolDataUpdateCoordinator(hass, device, update_interval)
    
    # Ersten Update durchführen
    await coordinator.async_config_entry_first_refresh()
    
    _LOGGER.info(
        "Gerät und Coordinator eingerichtet: %s (Update alle %ds)",
        device.name, device.polling_interval
    )
    
    return coordinator
