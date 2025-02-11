import logging
import aiohttp
import asyncio
from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_POLLING_INTERVAL,
    CONF_DEVICE_ID,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_POLLING_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["switch", "sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""

    config = {
        CONF_API_URL: entry.data[CONF_API_URL],  # Get the full URL
        CONF_POLLING_INTERVAL: entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        CONF_DEVICE_ID: entry.data.get(CONF_DEVICE_ID, 1),
        CONF_USERNAME: entry.data.get(CONF_USERNAME),
        CONF_PASSWORD: entry.data.get(CONF_PASSWORD),
        "timeout": entry.options.get("timeout", 10),
        "retries": entry.options.get("retries", 3)
    }

    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    coordinator = VioletDataUpdateCoordinator(hass, config=config)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"First data fetch failed: {err}")
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS) # Use constant for platforms.

    _LOGGER.info("Violet Pool Controller setup completed successfully")

    entry.async_on_unload(entry.add_update_listener(update_listener)) # Update listener for config changes.

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")
    return unload_ok

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.api_url: str = config[CONF_API_URL]  # Use the full URL
        self.username: str = config[CONF_USERNAME]
        self.password: str = config[CONF_PASSWORD]
        self.session: aiohttp.ClientSession = aiohttp_client.async_get_clientsession(hass)
        self.device_id: int = config[CONF_DEVICE_ID]
        self.timeout: int = config["timeout"]
        self.retries: int = config["retries"]

        _LOGGER.info(f"Initializing data coordinator for device {self.device_id} (URL: {self.api_url})")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config[CONF_POLLING_INTERVAL]),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API."""
        auth = aiohttp.BasicAuth(self.username, self.password) if self.username and self.password else None
        timeout = aiohttp.ClientTimeout(total=self.timeout)  # Use aiohttp.ClientTimeout

        for attempt in range(self.retries):
            try:
                _LOGGER.debug(f"Fetching data from: {self.api_url}")
                async with self.session.get(self.api_url, auth=auth, timeout=timeout) as response:
                    _LOGGER.debug(f"Status Code: {response.status}")
                    response.raise_for_status()  # Raise for any HTTP errors
                    data = await response.json()
                    _LOGGER.debug(f"Data received: {data}")

                    if not isinstance(data, dict) or "IMP1_value" not in data: # Basic validation
                        raise UpdateFailed(f"Unexpected response structure: {data}")

                    return data

            except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as err:
                _LOGGER.error(f"Attempt {attempt + 1}/{self.retries} - Error while fetching data: {err}")
                if attempt + 1 == self.retries:
                    raise UpdateFailed(f"Error after {self.retries} attempts (Device ID: {self.device_id}, URL: {self.api_url}): {err}") from err

            await asyncio.sleep(2 ** attempt)  # Exponential backoff
