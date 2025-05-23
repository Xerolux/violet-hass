"""Violet Pool Controller Device Module."""
import logging
import asyncio
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

from .api import VioletPoolAPI, VioletPoolAPIError, VioletPoolConnectionError, VioletPoolCommandError
from .coordinator import VioletPoolDataUpdateCoordinator
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
            config_entry: Konfigurationseintrag.
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

        self.entry_data = config_entry.data
        self.api_url = self.entry_data.get("base_ip")
        self.use_ssl = self.entry_data.get(CONF_USE_SSL, True)
        self.device_id = self.entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = self.entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self.username = self.entry_data.get(CONF_USERNAME)
        self.password = self.entry_data.get(CONF_PASSWORD)

        options = config_entry.options
        self.polling_interval = int(options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
        self.timeout_duration = int(options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
        self.retry_attempts = int(options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))
        self.active_features = options.get(CONF_ACTIVE_FEATURES, [])

        self.api = VioletPoolAPI(
            host=self.api_url,
            session=self._session,
            username=self.username,
            password=self.password,
            use_ssl=self.use_ssl,
            timeout=self.timeout_duration,
        )

        protocol = "https" if self.use_ssl else "http" # Keep for device_info and other non-API calls if any
        self.api_base_url = f"{protocol}://{self.api_url}"
        # self.api_readings_url and self.auth were here, ensure they are removed if any commented lines remain.

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
        """Richte das Gerät ein."""
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
        """Aktualisiere Gerätedaten."""
        async with self._api_lock:
            try:
                # api_data = await self._fetch_api_data(self.api_readings_url, self.retry_attempts)
                api_data = await self.api.get_readings("ALL")
                if not api_data:
                    # This case should ideally be handled by VioletPoolAPI raising an error
                    # if the response is empty but expected to have data.
                    # If api_data can be an empty dict on success (e.g. no sensors),
                    # this check might need adjustment or removal.
                    raise UpdateFailed(f"Keine Daten von {self.api_url}")
                self._firmware_version = api_data.get("fw")
                self._data = self._process_api_data(api_data)
                self._available = True
                self._last_error = None # Clear last error on success
                return self._data
            except (VioletPoolConnectionError, VioletPoolAPIError) as e:
                self._available = False
                self._last_error = str(e)
                _LOGGER.error("Update-Fehler für %s: %s", self.device_name, e)
                raise UpdateFailed(f"Fehler bei der Kommunikation mit {self.device_name}: {e}") from e
            except Exception as e: # Catch any other unexpected error
                self._available = False
                self._last_error = str(e)
                _LOGGER.exception("Unerwarteter Update-Fehler für %s:", self.device_name)
                raise UpdateFailed(f"Unerwarteter Fehler bei {self.device_name}: {e}") from e

    # _fetch_api_data method was here and is now removed.

    def _process_api_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeite API-Daten."""
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

    async def async_send_command(self, endpoint: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Sende einen Befehl an das Gerät über self.api und verwaltet den _api_lock."""
        async with self._api_lock:
            try:
                _LOGGER.debug("Sending command to endpoint %s with data %s", endpoint, command)
                if endpoint == API_SET_FUNCTION_MANUALLY or endpoint == "/set_switch":
                    return await self.api.set_switch_state(
                        key=command['id'],
                        action=command['action'],
                        duration=command.get('duration', 0),
                        last_value=command.get('value', 0)
                    )
                elif endpoint == API_SET_TARGET_VALUES:
                    return await self.api.set_target_value(
                        target_type=command['target_type'],
                        value=command['value']
                    )
                elif endpoint == API_SET_DOSING_PARAMETERS:
                    return await self.api.set_dosing_parameters(
                        dosing_type=command['dosing_type'],
                        parameter_name=command['parameter_name'],
                        value=command['value']
                    )
                elif endpoint == "/startWaterAnalysis":
                    return await self.api.start_water_analysis()
                elif endpoint == "/set_temperature": # Specific handling for temperature
                    # Assuming command structure: {"type": "HEATER", "temperature": temp_value}
                    # Mapping 'type' to 'target_type' for the API.
                    # The actual target_type string (e.g., "HEATER", "POOL_TEMP_TARGET")
                    # needs to be what VioletPoolAPI's set_target_value expects for temperature.
                    # Using command.get('type', 'TARGET_TEMP') as a placeholder for target_type.
                    target_type = command.get('type', 'TARGET_TEMP') # Default if 'type' not in command
                    temperature_value = command['temperature']
                    return await self.api.set_target_value(
                        target_type=target_type, # e.g. "HEATER" or a more generic "POOL_TEMP"
                        value=temperature_value
                    )
                # Add other specific endpoint mappings to self.api methods here if needed
                # For example, for cover:
                # elif endpoint == "/set_cover":
                #    # Assuming command dict contains 'action' for 'OPEN', 'CLOSE', 'STOP'
                #    return await self.api.set_cover_state(action=command['action'])

                else:
                    _LOGGER.error(f"Unsupported endpoint in async_send_command: {endpoint}")
                    # Consider raising a specific error or returning a structured error response
                    raise VioletPoolCommandError(f"Unsupported endpoint: {endpoint}")

            except (VioletPoolConnectionError, VioletPoolAPIError) as err:
                _LOGGER.error(f"API Error sending command to endpoint {endpoint} with command {command}: {err}")
                self._last_error = str(err)
                raise # Re-raise to be caught by calling methods or DataUpdateCoordinator
            except KeyError as err:
                _LOGGER.error(f"Missing key in command for endpoint {endpoint}: {err}. Command: {command}")
                self._last_error = f"Invalid command structure for {endpoint}: Missing {err}"
                raise VioletPoolCommandError(f"Invalid command for {endpoint}: Missing {err}") from err
            except Exception as err: # Catch any other unexpected errors
                _LOGGER.exception(f"Unexpected error sending command to endpoint {endpoint} with command {command}:")
                self._last_error = f"Unexpected error: {err}"
                raise VioletPoolAPIError(f"Unexpected error during command: {err}") from err

    async def async_set_swimming_pool_temperature(self, temperature: float) -> bool:
        """Setze die Pool-Temperatur."""
        try:
            # The command structure is based on the old direct call,
            # /set_temperature endpoint now handled in async_send_command
            command = {"type": "HEATER", "temperature": float(temperature)}
            # Using "/set_temperature" as the endpoint key
            result = await self.async_send_command("/set_temperature", command)
            # Check for a success field or rely on absence of exceptions
            return result.get("success", True) if isinstance(result, dict) else True
        except (VioletPoolConnectionError, VioletPoolAPIError, VioletPoolCommandError) as e:
            _LOGGER.error("Temperatur setzen fehlgeschlagen: %s", e)
            # self._last_error is already set by async_send_command
            return False
        except Exception as e: # Catch any other unexpected error from async_send_command
            _LOGGER.error("Unerwarteter Fehler beim Setzen der Temperatur: %s", e)
            self._last_error = f"Unerwarteter Fehler: {e}"
            return False

    async def async_set_switch_state(self, switch_id: str, state: bool) -> bool:
        """Setze den Schalterzustand."""
        try:
            action = "ON" if state else "OFF"
            command = {"id": switch_id, "action": action, "duration": 0, "value": 0}
            # Using API_SET_FUNCTION_MANUALLY as the endpoint key, as it's more specific
            result = await self.async_send_command(API_SET_FUNCTION_MANUALLY, command)
            return result.get("success", True) if isinstance(result, dict) else True
        except (VioletPoolConnectionError, VioletPoolAPIError, VioletPoolCommandError) as e:
            _LOGGER.error("Schalter %s setzen fehlgeschlagen: %s", switch_id, e)
            # self._last_error is already set by async_send_command
            return False
        except Exception as e: # Catch any other unexpected error from async_send_command
            _LOGGER.error("Unerwarteter Fehler beim Setzen des Schalters %s: %s", switch_id, e)
            self._last_error = f"Unerwarteter Fehler: {e}"
            return False

    def is_feature_active(self, feature_id: str) -> bool:
        """Prüfe, ob ein Feature aktiv ist."""
        return feature_id in self.active_features

    async def async_manual_dosing(self, dosing_key: str, duration_seconds: int) -> bool:
        """Trigger manual dosing for a specific dosing unit."""
        _LOGGER.debug(f"Attempting manual dosing for {dosing_key} for {duration_seconds}s on device {self.device_name}")
        async with self._api_lock: # Ensure thread safety for API calls
            try:
                # dosing_key from the entity should match the dosing_type expected by api.manual_dosing
                await self.api.manual_dosing(dosing_type=dosing_key, duration_seconds=duration_seconds)
                _LOGGER.info(f"Manual dosing command sent for {dosing_key} for {duration_seconds}s.")
                return True
            except (VioletPoolConnectionError, VioletPoolAPIError) as e:
                _LOGGER.error(f"Manual dosing failed for {dosing_key}: {e}")
                self._last_error = str(e)
                return False
            except Exception as e:
                _LOGGER.error(f"Unexpected error during manual dosing for {dosing_key}: {e}", exc_info=True)
                self._last_error = str(e)
                return False

# VioletPoolDataUpdateCoordinator class definition was removed from here and moved to coordinator.py

async def async_setup_device(hass: HomeAssistant, config_entry: ConfigEntry) -> Optional[VioletPoolDataUpdateCoordinator]:
    """Richte das Gerät ein."""
    device = VioletPoolControllerDevice(hass, config_entry)
    if not await device.async_setup():
        raise ConfigEntryNotReady(f"Setup fehlgeschlagen: {device.last_error}")
    coordinator = VioletPoolDataUpdateCoordinator(hass, device, config_entry)
    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Initialer Datenabruf fehlgeschlagen")
    return coordinator