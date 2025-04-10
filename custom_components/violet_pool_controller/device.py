"""Violet Pool Controller Device Module."""
import logging
import asyncio
import time
import json
from datetime import timedelta
from typing import Any, Dict, Optional

import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .const import (
    DOMAIN,
    API_READINGS,
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
    API_SET_FUNCTION_MANUALLY,
    API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES,
)

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerDevice:
    """Repräsentiert ein Violet Pool Controller Gerät."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialisiere die Geräteinstanz.

        Args:
            hass: Home Assistant Instanz.
            config_entry: Konfigurationseintrag des Geräts.
        """
        self.hass = hass
        self.config_entry = config_entry
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: Dict[str, Any] = {}
        self._device_info: Dict[str, Any] = {}
        self._firmware_version: Optional[str] = None
        self._last_error: Optional[str] = None
        self._api_lock = asyncio.Lock()

        # Konfigurationsdaten laden
        self.entry_data = config_entry.data
        self.api_url = self.entry_data.get("base_ip")
        self.use_ssl = self.entry_data.get(CONF_USE_SSL, True)
        self.device_id = self.entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = self.entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self.username = self.entry_data.get(CONF_USERNAME)
        self.password = self.entry_data.get(CONF_PASSWORD)

        # Optionen oder Standardwerte
        options = config_entry.options
        self.polling_interval = int(options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
        self.timeout_duration = int(options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
        self.retry_attempts = int(options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))
        self.active_features = options.get(CONF_ACTIVE_FEATURES, [])

        # API-URL zusammenstellen
        protocol = "https" if self.use_ssl else "http"
        self.api_base_url = f"{protocol}://{self.api_url}"
        self.api_readings_url = f"{self.api_base_url}{API_READINGS}?ALL"

        # Authentifizierung
        self.auth = aiohttp.BasicAuth(self.username, self.password or "") if self.username else None

        _LOGGER.info("Initialisiere %s an %s (ID: %s)", self.device_name, self.api_url, self.device_id)

    @property
    def available(self) -> bool:
        """Gibt an, ob das Gerät verfügbar ist."""
        return self._available

    @property
    def firmware_version(self) -> Optional[str]:
        """Gibt die Firmware-Version zurück."""
        return self._firmware_version

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
        """Gibt den letzten Fehler zurück."""
        return self._last_error

    async def async_setup(self) -> bool:
        """Richtet das Gerät ein."""
        try:
            await self.async_update()
            self._available = True
            return True
        except Exception as e:
            self._last_error = str(e)
            self._available = False
            _LOGGER.error("Setup-Fehler für %s: %s", self.device_name, e)
            return False

    async def async_update(self) -> Dict[str, Any]:
        """Aktualisiert die Gerätedaten."""
        async with self._api_lock:
            try:
                api_data = await self._fetch_api_data(self.api_readings_url, self.retry_attempts)
                if not api_data:
                    raise UpdateFailed(f"Keine Daten von {self.api_readings_url}")
                self._firmware_version = api_data.get("fw")
                self._data = self._process_api_data(api_data)
                self._available = True
                return self._data
            except Exception as e:
                self._available = False
                self._last_error = str(e)
                _LOGGER.error("Update-Fehler: %s", e)
                raise UpdateFailed(str(e))

    async def _fetch_api_data(self, url: str, retries: int) -> Dict[str, Any]:
        """Ruft API-Daten mit Wiederholungen ab."""
        for attempt in range(retries):
            try:
                async with async_timeout.timeout(self.timeout_duration):
                    async with self._session.get(url, auth=self.auth, ssl=self.use_ssl) as response:
                        response.raise_for_status()
                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" in content_type:
                            return await response.json()
                        text = await response.text()
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return {"raw_response": text}
            except Exception as e:
                _LOGGER.warning("Fehler bei %s, Versuch %d/%d: %s", url, attempt + 1, retries, e)
                if attempt + 1 == retries:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Fehler bei _fetch_api_data für {url}")

    def _process_api_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet API-Daten."""
        if not data:
            return {}
        processed = dict(data)
        for key, value in processed.items():
            if isinstance(value, str):
                if value.replace(".", "", 1).isdigit():
                    processed[key] = float(value) if "." in value else int(value)
                elif value.lower() in ["true", "false", "on", "off", "1", "0"]:
                    processed[key] = value.lower() in ["true", "on", "1"]
        key_mappings = {
            "ph_current": "ph_value",
            "orp_current": "orp_value",
            "temp_current": "temp_value",
            "onewire1_value": "water_temp",
            "onewire2_value": "air_temp",
        }
        for old, new in key_mappings.items():
            if old in processed and new not in processed:
                processed[new] = processed[old]
        if "ph_value" in processed:
            processed["ph_value"] = round(float(processed["ph_value"]), 2)
        return processed

    async def async_send_command(self, endpoint: str, command: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
        """Sendet einen Befehl an das Gerät."""
        url = f"{self.api_base_url}{endpoint}"
        raw_query = {
            API_SET_FUNCTION_MANUALLY: f"{command.get('id', '')},{command.get('action', '')},{command.get('duration', 0)},{command.get('value', 0)}",
            "/set_switch": f"{command.get('id', '')},{command.get('action', '')},{command.get('duration', 0)},{command.get('value', 0)}",
            "/set_temperature": f"{command.get('type', '')},{command.get('temperature', 0)}",
            API_SET_TARGET_VALUES: f"{command.get('target_type', '')},{command.get('value', 0)}",
            "/set_cover": f"{command.get('action', '')}",
            API_SET_DOSING_PARAMETERS: f"{command.get('dosing_type', '')},{command.get('parameter_name', '')},{command.get('value', '')}",
            "/startWaterAnalysis": ""
        }.get(endpoint)
        if raw_query is not None:
            url += f"?{raw_query}"

        for attempt in range(retries):
            try:
                async with async_timeout.timeout(self.timeout_duration):
                    async with self._session.get(url, auth=self.auth, ssl=self.use_ssl) as response:
                        response.raise_for_status()
                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" in content_type:
                            return await response.json()
                        text = await response.text()
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return {"success": "OK" in text.upper() or "SUCCESS" in text.upper(), "raw_response": text}
            except Exception as e:
                if attempt + 1 == retries:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Fehler bei async_send_command für {url}")

    async def async_set_swimming_pool_temperature(self, temperature: float) -> bool:
        """Setzt die Pool-Temperatur."""
        try:
            command = {"type": "HEATER", "temperature": float(temperature)}
            result = await self.async_send_command("/set_temperature", command)
            return result.get("success", False)
        except Exception as e:
            _LOGGER.error("Temperatur setzen fehlgeschlagen: %s", e)
            return False

    async def async_set_switch_state(self, switch_id: str, state: bool) -> bool:
        """Setzt den Schalterzustand."""
        try:
            action = "ON" if state else "OFF"
            command = {"id": switch_id, "action": action, "duration": 0, "value": 0}
            result = await self.async_send_command("/set_switch", command)
            return result.get("success", False)
        except Exception as e:
            _LOGGER.error("Schalter %s setzen fehlgeschlagen: %s", switch_id, e)
            return False

    def is_feature_active(self, feature_id: str) -> bool:
        """Prüft, ob ein Feature aktiv ist."""
        return feature_id in self.active_features

class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator für Datenaktualisierungen."""

    def __init__(self, hass: HomeAssistant, device: VioletPoolControllerDevice, config_entry: ConfigEntry) -> None:
        """Initialisiert den Koordinator."""
        self.device = device
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.device_id}",
            update_interval=timedelta(seconds=device.polling_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Aktualisiert die Daten."""
        try:
            return await self.device.async_update()
        except Exception as e:
            self.device._available = False
            raise UpdateFailed(str(e))

async def async_setup_device(hass: HomeAssistant, config_entry: ConfigEntry) -> Optional[VioletPoolDataUpdateCoordinator]:
    """Richtet das Gerät ein."""
    device = VioletPoolControllerDevice(hass, config_entry)
    if not await device.async_setup():
        raise ConfigEntryNotReady(f"Setup fehlgeschlagen: {device.last_error}")
    coordinator = VioletPoolDataUpdateCoordinator(hass, device, config_entry)
    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Initialer Datenabruf fehlgeschlagen")
    return coordinator
