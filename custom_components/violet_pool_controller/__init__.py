import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout

from .const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_POLLING_INTERVAL, 
    CONF_USE_SSL, 
    CONF_DEVICE_ID,
    CONF_USERNAME,  # Import the username constant
    CONF_PASSWORD,  # Import the password constant
    DEFAULT_POLLING_INTERVAL, 
    DEFAULT_USE_SSL,
    API_READINGS  # Use the correct API endpoint
)

_LOGGER = logging.getLogger(f"{DOMAIN}_logger")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""
    
    # Fetch IP address, polling interval, SSL setting, device ID, username, and password from the config entry
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD)
    }

    # Get the shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)
    
    # Create a coordinator to manage data updates
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Ensure the first data update happens during the setup
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass.data so it can be accessed by platform files
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward entry setup to platforms (sensor, binary_sensor, switch)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "switch"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor", "switch"]
    )
    
    # Remove the coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass, config, session):
        """Initialize the coordinator."""
        self.ip_address = config["ip_address"]
        self.username = config["username"]
        self.password = config["password"]
        self.session = session
        self.use_ssl = config["use_ssl"]
        self.device_id = config["device_id"]

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )


    async def _async_update_data(self):
        """Fetch data from the Violet Pool Controller API."""
        try:
            protocol = "https" if self.use_ssl else "http"
            url = f"{protocol}://{self.ip_address}{API_READINGS}"
            _LOGGER.debug(f"Fetching data from: {url} (SSL: {self.use_ssl})")

            async with async_timeout.timeout(10):
                async with self.session.get(url, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug(f"Data received: {data}")
                    return data
        except Exception as err:
            _LOGGER.error(f"Error fetching data from {self.ip_address}: {err}")
            raise UpdateFailed(f"Error fetching data: {err}")
