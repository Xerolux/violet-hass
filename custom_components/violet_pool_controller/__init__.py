import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL, CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""
    
    # Fetch API URL and polling interval from the config entry
    api_url = entry.data[CONF_API_URL]
    polling_interval = entry.data.get(CONF_POLLING_INTERVAL, 10)
    
    # Get the shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)
    
    # Create a coordinator to manage data updates
    coordinator = VioletDataUpdateCoordinator(
        hass,
        api_url=api_url,
        polling_interval=polling_interval,
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
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor", "switch"])
    
    # Remove the coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data."""

    def __init__(self, hass, api_url, polling_interval, session):
        """Initialize the coordinator."""
        self.api_url = api_url
        self.session = session
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the Violet Pool Controller API."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(self.api_url, ssl=False) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
