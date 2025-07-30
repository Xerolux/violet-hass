"""Violet Pool Controller Device Module."""
import logging
import asyncio
import json
from datetime import timedelta

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
from .api import VioletPoolAPI

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerDevice:
    """Repräsentiert ein Violet Pool Controller Gerät."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI) -> None:
        """Initialisiere die Geräteinstanz."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: dict = {}
        self._device_info: dict = {}
        self._firmware_version: str | None = None
        self._last_error: str | None = None
        self._api_lock = asyncio.Lock()

        entry_data = config_entry.data
        self.api_url = entry_data.get(CONF_API_URL) or entry_data.get("host") or entry_data.get("base_ip")
        if not self.api_url:
            raise ValueError("Keine gültige API-URL")

        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self.auth = aiohttp.BasicAuth(entry_data[CONF_USERNAME], entry_data.get(CONF_PASSWORD, "")) if entry_data.get(CONF_USERNAME) else None
        self.polling_interval = int(config_entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
        self.timeout_duration = int(config_entry.options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
        self.retry_attempts = int(config_entry.options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))
        self.active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, [])

        self.api_base_url = f"{'https' if self.use_ssl else 'http'}://{self.api_url}"
        self.api_readings_url = f"{self.api_base_url}{API_READINGS}?ALL"
        _LOGGER.info("Initialisiere %s an %s (ID: %s)", self.device_name, self.api_url, self.device_id)

    @property
    def available(self) -> bool:
        """Gibt Geräteverfügbarkeit zurück."""
        return self._available

    @property
    def firmware_version(self) -> str | None:
        """Gibt Firmware-Version zurück."""
        return self._firmware_version

    @property
    def name(self) -> str:
        """Gibt Gerätenamen zurück."""
        return self.device_name

    @property
    def device_info(self) -> dict:
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
    def last_error(self) -> str | None:
        """Gibt letzten Fehler zurück."""
        return self._last_error

    async def async_setup(self) -> bool:
        """Richte Gerät ein."""
        try:
            await self.async_update()
            self._available = True
            return True
        except Exception as e:
            self._last_error = str(e)
            self._available = False
            _LOGGER.error("Setup-Fehler für %s: %s", self.device_name, e)
            return False

    async def async_update(self) -> dict:
        """Aktualisiere Gerätedaten."""
        async with self._api_lock:
            try:
                data = await self._fetch_api_data(self.api_readings_url, self.retry_attempts)
                if not data:
                    raise UpdateFailed("Keine Daten empfangen")
                self._firmware_version = data.get("fw")
                self._data = self._process_api_data(data)
                self._available = True
                return self._data
            except Exception as e:
                self._available = False
                self._last_error = str(e)
                _LOGGER.error("Update-Fehler: %s", e)
                raise UpdateFailed(str(e))

    async def _fetch_api_data(self, url: str, retries: int) -> dict:
        """Rufe API-Daten ab."""
        for attempt in range(retries):
            try:
                async with asyncio.timeout(self.timeout_duration):
                    async with self._session.get(url, auth=self.auth, ssl=self.use_ssl) as response:
                        response.raise_for_status()
                        if "application/json" in response.headers.get("Content-Type", "").lower():
                            return await response.json()
                        return json.loads(await response.text())
            except (asyncio.TimeoutError, aiohttp.ClientError, json.JSONDecodeError) as e:
                if attempt + 1 == retries:
                    raise UpdateFailed(f"Fehler nach {retries} Versuchen: {e}")
                _LOGGER.warning("Fehler bei %s, Versuch %d/%d: %s", url, attempt + 1, retries, e)
                await asyncio.sleep(2 ** attempt)
        raise UpdateFailed("Fehler bei API-Datenabruf")

    def _process_api_data(self, data: dict) -> dict:
        """Verarbeite API-Daten."""
        processed = dict(data)
        for key, value in processed.items():
            if isinstance(value, str):
                if value.replace(".", "", 1).isdigit():
                    processed[key] = float(value) if "." in value else int(value)
                elif value.lower() in ("true", "false", "on", "off", "1", "0"):
                    processed[key] = value.lower() in ("true", "on", "1")
        key_mappings = {
            "ph_current": "ph_value", "orp_current": "orp_value", "temp_current": "temp_value",
            "onewire1_value": "water_temp", "onewire2_value": "air_temp"
        }
        processed.update({new: processed[old] for old, new in key_mappings.items() if old in processed and new not in processed})
        if "ph_value" in processed:
            processed["ph_value"] = round(float(processed["ph_value"]), 2)
        return processed

    def is_feature_active(self, feature_id: str) -> bool:
        """Prüfe, ob Feature aktiv ist."""
        return feature_id in self.active_features

class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator für Datenaktualisierungen."""

    def __init__(self, hass: HomeAssistant, device: VioletPoolControllerDevice, config_entry: ConfigEntry) -> None:
        """Initialisiere Koordinator."""
        self.device = device
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{device.device_id}", update_interval=timedelta(seconds=device.polling_interval))

    async def _async_update_data(self) -> dict:
        """Aktualisiere Daten."""
        try:
            return await self.device.async_update()
        except Exception as e:
            _LOGGER.error("Datenaktualisierung fehlgeschlagen für %s: %s", self.device.name, e)
            raise UpdateFailed(str(e))

async def async_setup_device(hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI) -> VioletPoolDataUpdateCoordinator | None:
    """Richte Gerät und Koordinator ein."""
    device = VioletPoolControllerDevice(hass, config_entry, api)
    if not await device.async_setup():
        raise ConfigEntryNotReady(f"Setup für {device.name} fehlgeschlagen: {device.last_error}")

    coordinator = VioletPoolDataUpdateCoordinator(hass, device, config_entry)
    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Initialer Datenabruf fehlgeschlagen")
    return coordinator
