import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device sensors from a config entry."""
    api_url = config_entry.data.get(CONF_API_URL)
    polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)

    # Get the shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)

    # Create a coordinator to manage polling and updating sensors
    coordinator = VioletDataUpdateCoordinator(
        hass, api_url, polling_interval, session
    )

    # Fetch initial data to create sensors dynamically based on the keys
    await coordinator.async_config_entry_first_refresh()

    # Create sensors for each key in the API data
    sensors = [
        VioletDeviceSensor(coordinator, key)
        for key in coordinator.data.keys()
    ]

    async_add_entities(sensors)


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Device data."""

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
        """Fetch data from the Violet API."""
        try:
            async with self.session.get(self.api_url, ssl=False, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, key):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)

