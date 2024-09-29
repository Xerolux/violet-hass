import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout
import aiohttp
from typing import Any, Dict

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
    
    # Retrieve configuration data from the config entry
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD)
    }

    # Log configuration data
    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    # Get a shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)

    # Create a coordinator for data updates
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Log before first data fetch
    _LOGGER.debug("First data fetch for Violet Pool Controller is being performed")

    try:
        # Ensure the first data fetch happens during setup
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
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "binary_sensor"]
    )

    # Remove the coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")
    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.ip_address: str = config["ip_address"]
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.session: aiohttp.ClientSession = session
        self.use_ssl: bool = config["use_ssl"]
        self.device_id: int = config["device_id"]

        _LOGGER.info(f"Initializing data coordinator for device {self.device_id} (IP: {self.ip_address}, SSL: {self.use_ssl})")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API."""
        retries = 3
        for attempt in range(retries):
            try:
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{self.ip_address}{API_READINGS}"
                _LOGGER.debug(f"Fetching data from: {url}")

                auth = aiohttp.BasicAuth(self.username, self.password)

                async with async_timeout.timeout(10):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        _LOGGER.debug(f"Status Code: {response.status}")
                        _LOGGER.debug(f"Response Headers: {response.headers}")
                        response.raise_for_status()
                        data = await response.json()
                        _LOGGER.debug(f"Data received: {data}")
                        return data

            except aiohttp.ClientError as client_err:
                _LOGGER.warning(f"Attempt {attempt + 1}/{retries} - HTTP error while fetching data: {client_err}")
                if attempt + 1 == retries:
                    raise UpdateFailed(f"HTTP error after {retries} attempts: {client_err}")
            except asyncio.TimeoutError:
                _LOGGER.warning(f"Attempt {attempt + 1}/{retries} - Timeout while fetching data from {self.ip_address}")
                if attempt + 1 == retries:
                    raise UpdateFailed(f"Timeout after {retries} attempts")
            except Exception as err:
                _LOGGER.error(f"Unexpected error while fetching data from {self.ip_address}: {err}")
                raise UpdateFailed(f"Unexpected error: {err}")

            await asyncio.sleep(2 ** attempt)  # Exponential backoff on retries
