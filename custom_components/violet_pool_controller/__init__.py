import logging
from datetime import timedelta
from typing import Any, Dict
import asyncio

import aiohttp
from async_timeout import timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    CONF_DEVICE_ID,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_USE_SSL,
    API_READINGS
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD),
        "timeout": entry.options.get("timeout", 10),
        "retries": entry.options.get("retries", 3)
    }

    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    session = aiohttp_client.async_get_clientsession(hass)

    coordinator = VioletDataUpdateCoordinator(
        hass=hass,
        config=config,
        session=session,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"First data fetch failed: {err}")
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to supported platforms (e.g., sensor, switch, binary_sensor, etc.)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch", "binary_sensor"])
    )

    _LOGGER.info("Violet Pool Controller setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "switch", "binary_sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")

    return unload_ok

class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage data updates from the Violet Pool Controller."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.ip_address: str = config.get("ip_address", "Unknown")
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.session: aiohttp.ClientSession = session
        self.use_ssl: bool = config["use_ssl"]
        self.device_id: int = config["device_id"]
        self.timeout: int = config["timeout"]
        self.retries: int = config["retries"]
        self.data: Dict[str, Any] = {} 

        _LOGGER.info(
            f"Initializing data coordinator for device {self.device_id} "
            f"(IP: {self.ip_address}, SSL: {self.use_ssl})"
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    def get_device_info(self) -> DeviceInfo:
        """Return device info for the controller. This method ensures that all entities (sensors, switches, and binary sensors) are grouped under one device in Home Assistant, and displays the correct IP address."""
        """Return device info for the controller. This method ensures that all entities (sensors, switches, and binary sensors) are grouped under one device in Home Assistant."""
        return DeviceInfo(
            connections={("ip", self.ip_address)},
            identifiers={(DOMAIN, str(self.device_id))},
            name=f"Violet Pool Controller {self.device_id}",
            manufacturer="Violet",
            model="Pool Controller",
            sw_version="1.0",
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API with a retry mechanism using exponential backoff."""
        for attempt in range(self.retries):
            try:
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{self.ip_address}{API_READINGS}"
                _LOGGER.debug(f"Fetching data from: {url}, attempt {attempt + 1}")

                auth = aiohttp.BasicAuth(self.username, self.password) if self.username and self.password else None

                async with timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        _LOGGER.debug(f"Status Code: {response.status}")
                        response.raise_for_status()
                        data = await response.json()
                        _LOGGER.debug(f"Data received: {data}")

                        if not isinstance(data, dict) or "IMP1_value" not in data:
                            raise UpdateFailed(f"Unexpected response structure: {data}")

                        self.data = data
                        return data

            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                _LOGGER.error(f"Attempt {attempt + 1}/{self.retries} - Error while fetching data: {err}")
                if attempt + 1 == self.retries:
                    raise UpdateFailed(
                        f"Error after {self.retries} attempts (Device ID: {self.device_id}, URL: {url}): {err}"
                    )
                
                # Exponential backoff: Wait 2^attempt seconds before retrying
                await asyncio.sleep(2 ** attempt)

        raise UpdateFailed("Failed to update data after all retries")

