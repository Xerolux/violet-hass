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

    # Retrieve configuration parameters from the entry data, with defaults.
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),  # Default device ID is 1
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD),
        "timeout": entry.options.get("timeout", 10),  # Customizable timeout with a default of 10 seconds
        "retries": entry.options.get("retries", 3)  # Customizable retry count with a default of 3
    }

    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    # Get an aiohttp client session.
    session = aiohttp_client.async_get_clientsession(hass)

    # Create the data update coordinator.
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Initial data fetch to ensure connectivity and validate configuration.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"First data fetch failed: {err}")
        return False  # Fail setup if the initial fetch fails

    # Store the coordinator in hass.data for use by platforms.
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to platforms defined in const.py (e.g., switch, sensor, binary_sensor).
    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor", "binary_sensor"])

    _LOGGER.info("Violet Pool Controller setup completed successfully")
    return True  # Indicate successful setup


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms associated with this config entry.
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "binary_sensor"]
    )

    # If unloading was successful, remove the coordinator from hass.data.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")

    return unload_ok  # Return the status of the unload operation


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.ip_address: str = config["ip_address"]
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.session: aiohttp.ClientSession = session
        self.use_ssl: bool = config["use_ssl"]
        self.device_id: int = config["device_id"]
        self.timeout: int = config["timeout"]
        self.retries: int = config["retries"]

        _LOGGER.info(f"Initializing data coordinator for device {self.device_id} (IP: {self.ip_address}, SSL: {self.use_ssl})")

        # Call the superclass constructor to set up the DataUpdateCoordinator.
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",  # Unique name for this coordinator instance
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API."""
        # Retry logic: Attempt the data fetch multiple times with exponential backoff.
        for attempt in range(self.retries):
            try:
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{self.ip_address}{API_READINGS}"
                _LOGGER.debug(f"Fetching data from: {url}, attempt {attempt + 1}")

                # Use BasicAuth if username and password are provided.
                auth = aiohttp.BasicAuth(self.username, self.password) if self.username and self.password else None

                # Fetch data with a timeout.  Use session.get with context manager.
                async with timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        _LOGGER.debug(f"Status Code: {response.status}")
                        response.raise_for_status()  # Raise an exception for bad status codes
                        data = await response.json()  # Parse the JSON response
                        _LOGGER.debug(f"Data received: {data}")

                        # Validate the structure of the received data
                        if not isinstance(data, dict) or "IMP1_value" not in data:
                            raise UpdateFailed(f"Unexpected response structure: {data}")

                        return data  # Return the fetched data on success

            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                _LOGGER.error(f"Attempt {attempt + 1}/{self.retries} - Error while fetching data: {err}")
                if attempt + 1 == self.retries:
                    # If this was the last attempt, raise UpdateFailed.
                    raise UpdateFailed(
                        f"Error after {self.retries} attempts (Device ID: {self.device_id}, URL: {url}): {err}")

            # Exponential backoff: wait 2^attempt seconds before the next retry.
            await asyncio.sleep(2 ** attempt)

        raise UpdateFailed("Failed to update data after all retries")  # Should never reach here.
