"""Violet Pool Controller Device Module."""
import logging
import asyncio
from datetime import timedelta
from typing import Any, Optional

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
    """Repräsentiert ein Violet Pool Controller Gerät."""

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
        self._data: dict[str, Any] = {}
        self._device_info: dict[str, Any] = {}
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
        
        # Username und Password (können leer sein)
        username = entry_data.get(CONF_USERNAME, "")
        password = entry_data.get(CONF_PASSWORD, "")
        
        _LOGGER.info(
            "Device initialisiert: '%s' (URL: %s, SSL: %s, Device-ID: %d)",
            self.device_name, self.api_url, self.use_ssl, self.device_id
        )

    async def async_update(self) -> dict[str, Any]:
        """
        Aktualisiert Gerätedaten vom Controller.
        
        Returns:
            Dict mit aktuellen Gerätedaten
            
        Raises:
            UpdateFailed: Nach zu vielen aufeinanderfolgenden Fehlern
        """
        try:
            async with self._api_lock:
                _LOGGER.debug("Starte API-Update für '%s'", self.device_name)
                
                data = await self.api.get_readings()
                
                # Validiere Daten
                if not data or not isinstance(data, dict):
                    _LOGGER.warning(
                        "Leere oder ungültige Daten vom Controller (Versuch %d/%d)",
                        self._consecutive_failures + 1,
                        self._max_consecutive_failures
                    )
                    self._consecutive_failures += 1
                    
                    if self._consecutive_failures >= self._max_consecutive_failures:
                        self._available = False
                        raise UpdateFailed(
                            f"Controller antwortet nicht ({self._consecutive_failures} Fehler)"
                        )
                    
                    # Gebe alte Daten zurück bei temporären Problemen
                    return self._data
                
                # Update erfolgreich
                self._data = data
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None
                
                # Firmware-Version extrahieren
                if "FW" in data or "fw" in data:
                    self._firmware_version = data.get("FW") or data.get("fw")
                    _LOGGER.debug("Firmware-Version: %s", self._firmware_version)
                
                _LOGGER.debug(
                    "Update erfolgreich: %d Datenpunkte empfangen", 
                    len(data)
                )
                
                return data
                
        except VioletPoolAPIError as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            
            _LOGGER.error(
                "API-Fehler bei Update von '%s' (%d/%d): %s", 
                self.device_name,
                self._consecutive_failures, 
                self._max_consecutive_failures, 
                err
            )
            
            # Nach zu vielen Fehlern: Gerät als nicht verfügbar markieren
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._available = False
                raise UpdateFailed(
                    f"Controller nicht erreichbar: {err}"
                ) from err
            
            # Gebe alte Daten zurück bei temporären Fehlern
            return self._data
            
        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            
            _LOGGER.exception(
                "Unerwarteter Fehler bei Update von '%s' (%d/%d): %s", 
                self.device_name,
                self._consecutive_failures, 
                self._max_consecutive_failures, 
                err
            )
            
            # Nach zu vielen Fehlern: Exception werfen
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._available = False
                raise UpdateFailed("Update error: %s" % err) from err
            
            # Gebe alte Daten zurück bei temporären Fehlern
            return self._data

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
        """Gibt die Geräteinformationen für Home Assistant zurück."""
        if not self._device_info:
            self._device_info = {
                "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
                "name": self.device_name,
                "manufacturer": "PoolDigital GmbH & Co. KG",
                "model": "Violet Pool Controller",
                "sw_version": self._firmware_version or "Unbekannt",
            }
        return self._device_info

    def _extract_api_url(self, entry_data: Dict) -> str:
        """
        Extrahiert die API-URL aus den Config-Daten.
        
        Unterstützt verschiedene Schlüssel für Abwärtskompatibilität.
        
        Args:
            entry_data: Config Entry Daten
            
        Returns:
            Bereinigte IP-Adresse/URL
            
        Raises:
            ValueError: Wenn keine IP-Adresse gefunden wurde
        """
        url = (
            entry_data.get(CONF_API_URL) or
            entry_data.get("host") or
            entry_data.get("base_ip")
        )
        
        if not url:
            raise ValueError("Keine IP-Adresse in Config Entry gefunden")
        
        return url.strip()


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Data Update Coordinator für Violet Pool Controller."""
    
    def __init__(
        self, 
        hass: HomeAssistant, 
        device: VioletPoolControllerDevice, 
        name: str, 
        polling_interval: int = DEFAULT_POLLING_INTERVAL
    ) -> None:
        """Initialisiere den Coordinator."""
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
        
        Returns:
            Dict mit aktuellen Daten
            
        Raises:
            UpdateFailed: Bei Kommunikationsfehlern
        """
        try:
            return await self.device.async_update()
        except VioletPoolAPIError as err:
            _LOGGER.error("Fehler beim Datenabruf: %s", err)
            raise UpdateFailed("API error: %s" % err) from err


async def async_setup_device(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    api: VioletPoolAPI
) -> VioletPoolDataUpdateCoordinator:
    """
    Setup des Violet Pool Controller Devices.
    
    Args:
        hass: Home Assistant Instanz
        config_entry: Config Entry
        api: API-Instanz
        
    Returns:
        Initialisierter Coordinator
        
    Raises:
        ConfigEntryNotReady: Bei Setup-Fehlern
    """
    try:
        # Device erstellen
        device = VioletPoolControllerDevice(hass, config_entry, api)
        
        _LOGGER.debug("Führe ersten Update durch...")
        
        # Ersten Update durchführen (Verfügbarkeit prüfen)
        await device.async_update()
        
        if not device.available:
            raise ConfigEntryNotReady(
                f"Controller '{device.device_name}' nicht erreichbar bei Setup"
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
        _LOGGER.debug("Führe ersten Coordinator Refresh durch...")
        await coordinator.async_config_entry_first_refresh()
        
        _LOGGER.info(
            "Device Setup erfolgreich: '%s' (FW: %s, %d Datenpunkte)", 
            device.device_name, 
            device.firmware_version or "Unbekannt",
            len(device.data)
        )
        
        return coordinator
        
    except ConfigEntryNotReady:
        # Bereits korrekt formatierte Exception durchreichen
        raise
        
    except Exception as err:
        _LOGGER.exception("Device Setup fehlgeschlagen: %s", err)
        raise ConfigEntryNotReady(f"Setup-Fehler: {err}") from err