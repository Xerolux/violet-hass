import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout
import aiohttp
from typing import Any, Dict
import asyncio

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
    
    # Extract configuration parameters from the entry
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD),
        "timeout": entry.options.get("timeout", 10),  # Adding customizable timeout
        "retries": entry.options.get("retries", 3)  # Adding customizable retry count
    }

    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    # Create a session to manage HTTP connections
    session = aiohttp_client.async_get_clientsession(hass)

    # Initialize the data coordinator to manage periodic data fetching
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Attempt to perform the first data fetch to ensure everything is working
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"First data fetch failed: {err}")
        return False

    # Store the coordinator in hass.data for access by platform files
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to platforms (e.g., switch, sensor, binary sensor)
    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor", "binary_sensor"])

    _LOGGER.info("Violet Pool Controller setup completed successfully")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms associated with this config entry
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "binary_sensor"]
    )

    if unload_ok:
        # Remove the coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")
    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        # Store configuration parameters
        self.hass = hass
        self.ip_address: str = config["ip_address"]
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.session: aiohttp.ClientSession = session
        self.use_ssl: bool = config["use_ssl"]
        self.device_id: int = config["device_id"]
        self.timeout: int = config["timeout"]  # Customizable timeout
        self.retries: int = config["retries"]  # Customizable retries

        _LOGGER.info(f"Initializing data coordinator for device {self.device_id} (IP: {self.ip_address}, SSL: {self.use_ssl})")

        # Initialize the base DataUpdateCoordinator with update interval
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API."""
        # Attempt to fetch data, retrying if necessary
        for attempt in range(self.retries):
            try:
                # Determine the protocol based on SSL configuration
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{self.ip_address}{API_READINGS}"
                _LOGGER.debug(f"Fetching data from: {url}")

                # Set up authentication if username and password are provided
                auth = aiohttp.BasicAuth(self.username, self.password) if self.username and self.password else None

                # Perform the HTTP GET request with a timeout
                async with async_timeout.timeout(self.timeout):  # Use customizable timeout
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        _LOGGER.debug(f"Status Code: {response.status}")
                        response.raise_for_status()  # Raise an error if the request failed
                        data = await response.json()  # Parse response as JSON
                        _LOGGER.debug(f"Data received: {data}")
                        
                        # Validate response structure - Ensure at least one key is present, e.g., 'IMP1_value'
                        if not isinstance(data, dict) or "IMP1_value" not in data:
                            raise UpdateFailed(f"Unexpected response structure: {data}")
                        
                        # Return the fetched data if successful
                        return data

            # Handle HTTP client errors (e.g., connection issues)
            except aiohttp.ClientError as client_err:
                _LOGGER.error(f"Attempt {attempt + 1}/{self.retries} - HTTP error while fetching data: {client_err}")
                if attempt + 1 == self.retries:
                    # Raise an UpdateFailed exception after all retries are exhausted
                    raise UpdateFailed(f"HTTP error after {self.retries} attempts (Device ID: {self.device_id}, URL: {url}): {client_err}")
            # Handle timeout errors
            except asyncio.TimeoutError:
                _LOGGER.error(f"Attempt {attempt + 1}/{self.retries} - Timeout while fetching data from {self.ip_address}")
                if attempt + 1 == self.retries:
                    # Raise an UpdateFailed exception after all retries are exhausted
                    raise UpdateFailed(f"Timeout after {self.retries} attempts (Device ID: {self.device_id}, IP: {self.ip_address})")
            # Handle any other unexpected exceptions
            except Exception as err:
                _LOGGER.error(f"Unexpected error while fetching data from {self.ip_address}: {err}")
                raise UpdateFailed(f"Unexpected error (Device ID: {self.device_id}, IP: {self.ip_address}): {err}")

            # Exponential backoff before retrying
            await asyncio.sleep(2 ** attempt)  # Wait longer each time before retrying
