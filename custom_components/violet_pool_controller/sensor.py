import logging
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Violet Device sensors from a config entry."""
    api_url = config_entry.data.get(CONF_API_URL)
    polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)

    # Create a coordinator to manage polling and updating sensors
    coordinator = VioletDataUpdateCoordinator(hass, api_url, polling_interval)

    # Fetch initial data so we can create sensors dynamically based on the keys
    await coordinator.async_refresh()

    # Create sensors for each key in the API data
    sensors = []
    for key in coordinator.data.keys():
        sensors.append(VioletDeviceSensor(coordinator, key))

    async_add_entities(sensors, True)


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Device data."""

    def __init__(self, hass, api_url, polling_interval):
        """Initialize the coordinator."""
        self.api_url = api_url
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the Violet API."""
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(self.api_url, ssl=False)
                    return await response.json()
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class VioletDeviceSensor(Entity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, key):
        self.coordinator = coordinator
        self._key = key
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Violet {self._key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # No need to do anything here; coordinator handles data updates
        await self.coordinator.async_request_refresh()
