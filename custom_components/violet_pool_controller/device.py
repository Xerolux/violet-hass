"""Violet Pool Controller Device Module."""
import logging
import asyncio
from datetime import timedelta
from typing import Any, Dict, List, Optional, Callable, Union
import async_timeout

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL

from .const import (
    DOMAIN,
    API_READINGS,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_DEVICE_ID,
    CONF_POLLING_INTERVAL,
    CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)


class VioletPoolControllerDevice:
    """Repräsentiert ein Violet Pool Controller Gerät."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry,
    ) -> None:
        """Initialisieren der Geräteinstanz.
        
        Args:
            hass: Home Assistant-Instanz
            config_entry: Die Config Entry des Geräts
        """
        self.hass = hass
        self.config_entry = config_entry
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: Dict[str, Any] = {}
        self._status_data: Dict[str, Any] = {}
        self._device_info: Dict[str, Any] = {}
        self._firmware_version: Optional[str] = None
        self._last_error: Optional[str] = None
        self._api_lock = asyncio.Lock()  # Verhindert gleichzeitige API-Zugriffe
        
        # Konfigurationsdaten extrahieren
        self.entry_data = config_entry.data
        self.api_url = self.entry_data.get(CONF_API_URL)
        self.use_ssl = self.entry_data.get(CONF_USE_SSL, True)
        self.device_id = self.entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = self.entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self.username = self.entry_data.get(CONF_USERNAME)
        self.password = self.entry_data.get(CONF_PASSWORD)
        
        # Werte aus Options oder Defaults
        options = config_entry.options
        self.polling_interval = int(options.get(
            CONF_POLLING_INTERVAL, 
            self.entry_data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        ))
        self.timeout_duration = int(options.get(
            CONF_TIMEOUT_DURATION, 
            self.entry_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
        ))
        self.retry_attempts = int(options.get(
            CONF_RETRY_ATTEMPTS, 
            self.entry_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
        ))
        self.active_features = options.get(
            CONF_ACTIVE_FEATURES, 
            self.entry_data.get(CONF_ACTIVE_FEATURES, [])
        )
        
        # Vollständige API URL zusammenbauen
        protocol = "https" if self.use_ssl else "http"
        self.api_base_url = f"{protocol}://{self.api_url}"
        self.api_readings_url = f"{self.api_base_url}{API_READINGS}"
        
        # Authentifizierung konfigurieren, falls vorhanden
        self.auth = None
        if self.username:
            self.auth = aiohttp.BasicAuth(
                login=self.username, 
                password=self.password or ""
            )

        _LOGGER.info(
            "Initialisiere Violet Pool Controller: %s an %s (ID: %s)",
            self.device_name,
            self.api_url,
            self.device_id
        )

    @property
    def available(self) -> bool:
        """Gibt an, ob das Gerät verfügbar ist."""
        return self._available

    @property
    def firmware_version(self) -> Optional[str]:
        """Gibt die Firmwareversion des Geräts zurück."""
        return self._firmware_version

    @property
    def device_info(self) -> Dict[str, Any]:
        """Gibt die Geräteinformationen für die Geräteeintrag zurück."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": f"{self.device_name} ({self.api_url})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": self._device_info.get("model", "Violet Pool Controller"),
            "sw_version": self._firmware_version or "Unbekannt",
            "configuration_url": f"{self.api_base_url}",
        }

    @property
    def last_error(self) -> Optional[str]:
        """Gibt den letzten aufgetretenen Fehler zurück."""
        return self._last_error

    async def async_setup(self) -> bool:
        """Führt das Setup des Geräts durch.
        
        Returns:
            bool: True, wenn das Setup erfolgreich war, sonst False.
        """
        try:
            # Initialen Abruf durchführen, um die Verbindung zu testen
            await self.async_update()
            self._available = True
            return True
        except Exception as e:
            self._last_error = str(e)
            self._available = False
            _LOGGER.error("Fehler beim Setup von %s: %s", self.device_name, e)
            return False

    async def async_update(self) -> Dict[str, Any]:
        """Aktualisiert die Gerätedaten.
        
        Returns:
            Dict[str, Any]: Die aktuellen Gerätedaten.
            
        Raises:
            UpdateFailed: Bei einem Fehler während der Aktualisierung.
        """
        try:
            # Verwende Lock, um gleichzeitige API-Zugriffe zu vermeiden
            async with self._api_lock:
                # Lese Daten vom API-Endpoint
                api_data = await self._fetch_api_data(
                    self.api_readings_url, 
                    retries=self.retry_attempts
                )
                
                if not api_data:
                    raise UpdateFailed(f"Keine Daten von {self.api_readings_url} erhalten")
                
                # Firmwareversion speichern, falls vorhanden
                if "fw" in api_data:
                    self._firmware_version = api_data["fw"]
                
                # Daten vorverarbeiten und strukturieren
                self._data = self._process_api_data(api_data)
                self._available = True
                
                return self._data
                
        except asyncio.TimeoutError:
            self._available = False
            self._last_error = f"Zeitüberschreitung beim Verbinden mit {self.api_url}"
            raise UpdateFailed(self._last_error)
        except aiohttp.ClientError as err:
            self._available = False
            self._last_error = f"Verbindungsfehler mit {self.api_url}: {err}"
            raise UpdateFailed(self._last_error)
        except Exception as err:
            self._available = False
            self._last_error = f"Unerwarteter Fehler: {err}"
            _LOGGER.exception("Fehler beim Abrufen der Daten")
            raise UpdateFailed(self._last_error)

    async def _fetch_api_data(
        self, 
        url: str, 
        retries: int = 3
    ) -> Dict[str, Any]:
        """Daten von einer API-URL abrufen mit Retry-Logik.
        
        Args:
            url: Die API-URL
            retries: Anzahl der Wiederholungsversuche
            
        Returns:
            Dict[str, Any]: Die API-Antwortdaten
            
        Raises:
            Exception: Bei Fehlern in der API-Kommunikation
        """
        for attempt in range(retries):
            try:
                async with async_timeout.timeout(self.timeout_duration):
                    _LOGGER.debug(
                        "Abruf von %s, Versuch %d/%d",
                        url,
                        attempt + 1,
                        retries,
                    )
                    
                    async with self._session.get(url, auth=self.auth, ssl=self.use_ssl) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            error_msg = f"HTTP {response.status}: {response.reason}"
                            
                            if response.status == 401:
                                raise aiohttp.ClientResponseError(
                                    request_info=response.request_info,
                                    history=response.history,
                                    status=response.status,
                                    message="Authentifizierungsfehler. Bitte Benutzername und Passwort prüfen.",
                                    headers=response.headers
                                )
                            elif response.status == 404:
                                raise aiohttp.ClientResponseError(
                                    request_info=response.request_info,
                                    history=response.history,
                                    status=response.status,
                                    message="API-Endpunkt nicht gefunden. Bitte URL prüfen.",
                                    headers=response.headers
                                )
                            else:
                                raise aiohttp.ClientResponseError(
                                    request_info=response.request_info,
                                    history=response.history,
                                    status=response.status,
                                    message=error_msg,
                                    headers=response.headers
                                )
                        
                        data = await response.json()
                        _LOGGER.debug("API-Antwort: %s", data)
                        return data
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.warning(
                    "Fehler beim Abruf von %s: %s (Versuch %d/%d)",
                    url,
                    err,
                    attempt + 1,
                    retries,
                )
                
                if attempt + 1 == retries:
                    # Letzter Versuch fehlgeschlagen
                    _LOGGER.error(
                        "Alle %d Versuche zum Abruf von %s fehlgeschlagen", 
                        retries, 
                        url
                    )
                    raise
                    
                # Exponentielles Backoff für Wiederholungsversuche
                await asyncio.sleep(2 ** attempt)
                
        # Diese Zeile sollte nie erreicht werden, da wir bei Fehler oben rausspringen
        raise RuntimeError(f"Unerwartetes Ende der _fetch_api_data für {url}")

    def _process_api_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet die API-Daten für die spätere Verwendung.
        
        Args:
            data: Die Rohdaten von der API
            
        Returns:
            Dict[str, Any]: Die verarbeiteten Daten
        """
        if not data:
            return {}
            
        processed_data = dict(data)  # Kopie erstellen
        
        # Datentyp- und Format-Anpassungen vornehmen
        for key, value in processed_data.items():
            # Zahlenformatierungen: z.B. "25.4" -> 25.4
            if isinstance(value, str) and value.replace(".", "", 1).isdigit():
                try:
                    processed_data[key] = float(value)
                    # Ganzzahlen als int speichern
                    if processed_data[key].is_integer():
                        processed_data[key] = int(processed_data[key])
                except ValueError:
                    # Bei Fehler Originalwert behalten
                    pass
            
            # Boolesche Werte verarbeiten
            elif isinstance(value, str) and value.lower() in ["true", "false", "on", "off", "1", "0"]:
                processed_data[key] = value.lower() in ["true", "on", "1"]
        
        # Spezielle Schlüssel verarbeiten und vereinheitlichen
        key_mappings = {
            # Beispiel: "ph_current" -> "ph_value" falls der erste Schlüssel existiert
            "ph_current": "ph_value",
            "orp_current": "orp_value",
            "temp_current": "temp_value",
            "onewire1_value": "water_temp",
            "onewire2_value": "air_temp",
        }
        
        # Abgeleitete Werte berechnen und hinzufügen
        if "ph_value" in processed_data:
            # pH-Wert auf zwei Dezimalstellen formatieren
            try:
                processed_data["ph_value"] = round(float(processed_data["ph_value"]), 2)
            except (ValueError, TypeError):
                pass
                
        # Mappings anwenden
        for old_key, new_key in key_mappings.items():
            if old_key in processed_data and new_key not in processed_data:
                processed_data[new_key] = processed_data[old_key]
        
        return processed_data
        
    async def async_send_command(
        self, 
        endpoint: str, 
        command: Dict[str, Any], 
        retries: int = 3
    ) -> Dict[str, Any]:
        """Sendet einen Befehl an das Gerät.
        
        Args:
            endpoint: Der API-Endpunkt (ohne Basis-URL)
            command: Der zu sendende Befehl als Dictionary
            retries: Anzahl der Wiederholungsversuche
            
        Returns:
            Dict[str, Any]: Die Antwort des Geräts
            
        Raises:
            Exception: Bei Kommunikationsfehlern
        """
        url = f"{self.api_base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                async with async_timeout.timeout(self.timeout_duration):
                    _LOGGER.debug(
                        "Sende Befehl an %s: %s (Versuch %d/%d)",
                        url,
                        command,
                        attempt + 1,
                        retries,
                    )
                    
                    async with self._session.post(
                        url, 
                        json=command, 
                        auth=self.auth, 
                        ssl=self.use_ssl
                    ) as response:
                        response.raise_for_status()
                        result = await response.json()
                        _LOGGER.debug("Befehlsantwort: %s", result)
                        return result
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.warning(
                    "Fehler beim Senden des Befehls an %s: %s (Versuch %d/%d)",
                    url,
                    err,
                    attempt + 1,
                    retries,
                )
                
                if attempt + 1 == retries:
                    # Letzter Versuch fehlgeschlagen
                    raise
                    
                # Exponentielles Backoff
                await asyncio.sleep(2 ** attempt)
                
        # Diese Zeile sollte nie erreicht werden
        raise RuntimeError(f"Unerwartetes Ende der async_send_command für {url}")

    async def async_set_swimming_pool_temperature(self, temperature: float) -> bool:
        """Setzt die Zieltemperatur für den Pool.
        
        Args:
            temperature: Die gewünschte Temperatur in °C
            
        Returns:
            bool: True bei Erfolg, False bei Fehlern
        """
        if "heating" not in self.active_features:
            _LOGGER.warning("Heizungsfunktion ist nicht aktiv")
            return False
            
        try:
            command = {"temperature": float(temperature)}
            result = await self.async_send_command("/set_temperature", command)
            return result.get("success", False)
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der Temperatur: %s", err)
            return False
            
    async def async_set_switch_state(self, switch_id: str, state: bool) -> bool:
        """Setzt den Zustand eines Schalters.
        
        Args:
            switch_id: Die ID des Schalters
            state: Der gewünschte Zustand (True=Ein, False=Aus)
            
        Returns:
            bool: True bei Erfolg, False bei Fehlern
        """
        try:
            command = {"id": switch_id, "state": state}
            result = await self.async_send_command("/set_switch", command)
            return result.get("success", False)
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des Schalters %s: %s", switch_id, err)
            return False

    def is_feature_active(self, feature_id: str) -> bool:
        """Prüft, ob ein bestimmtes Feature aktiv ist.
        
        Args:
            feature_id: Die ID des Features
            
        Returns:
            bool: True, wenn das Feature aktiv ist, sonst False
        """
        return feature_id in self.active_features


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator zum Abrufen von Daten vom Violet Pool Controller."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        device: VioletPoolControllerDevice,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialisiert den Koordinator.
        
        Args:
            hass: Home Assistant-Instanz
            device: Die Pool Controller Geräteinstanz
            config_entry: Die Config Entry des Geräts
        """
        self.device = device
        self.config_entry = config_entry
        
        update_interval = timedelta(seconds=device.polling_interval)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.device_id}",
            update_interval=update_interval,
        )
        
        _LOGGER.info(
            "DataUpdateCoordinator für %s initialisiert (Interval: %s)",
            device.device_name,
            update_interval
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Implementierung der Datenaktualisierungsmethode.
        
        Returns:
            Dict[str, Any]: Aktualisierte Daten
            
        Raises:
            UpdateFailed: Bei einem Fehler während der Aktualisierung
        """
        try:
            return await self.device.async_update()
        except Exception as e:
            _LOGGER.error("Fehler bei der Datenaktualisierung: %s", e)
            raise UpdateFailed(f"Fehler: {e}")


async def async_setup_device(
    hass: HomeAssistant, 
    config_entry: ConfigEntry
) -> Optional[VioletPoolDataUpdateCoordinator]:
    """Richtet ein Violet Pool Controller Gerät ein.
    
    Args:
        hass: Home Assistant-Instanz
        config_entry: Die Config Entry des Geräts
        
    Returns:
        Optional[VioletPoolDataUpdateCoordinator]: Der Daten-Koordinator oder None bei Fehlern
        
    Raises:
        ConfigEntryNotReady: Wenn das Gerät nicht bereit ist
    """
    try:
        # Gerät initialisieren
        device = VioletPoolControllerDevice(hass, config_entry)
        
        # Gerät einrichten
        if not await device.async_setup():
            raise ConfigEntryNotReady(
                f"Gerät {device.device_name} ist nicht bereit: {device.last_error}"
            )
        
        # Coordinator erstellen und initialen Abruf durchführen
        coordinator = VioletPoolDataUpdateCoordinator(hass, device, config_entry)
        await coordinator.async_refresh()
        
        if not coordinator.last_update_success:
            raise ConfigEntryNotReady(
                f"Initialer Datenabruf für {device.device_name} fehlgeschlagen"
            )
            
        return coordinator
        
    except Exception as err:
        _LOGGER.exception("Fehler beim Einrichten des Violet Pool Controllers: %s", err)
        raise ConfigEntryNotReady(f"Einrichtungsfehler: {err}")
