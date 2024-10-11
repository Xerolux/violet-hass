import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_DEVICE_ID
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_API_URL, CONF_POLLING_INTERVAL

class VioletPoolControllerEntity(Entity):
    """Base class for a Violet Pool Controller entity."""

    def __init__(self, config_entry, api_data):
        """Initialize the entity."""
        self.config_entry = config_entry
        self.api_data = api_data
        self._name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {self.entity_description.name}"
        self._unique_id = f"{config_entry.data.get(CONF_DEVICE_ID)}_{self.entity_description.key}"
        self._state = None
        self._available = True
        self.api_url = config_entry.data.get(CONF_API_URL)
        self.polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)
        self._logger = logging.getLogger(f"{DOMAIN}.{self._unique_id}")

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the entity."""
        return self._unique_id

    @property
    def available(self):
        """Return if the entity is available."""
        return self._available

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "polling_interval": self.polling_interval,
            "api_url": self.api_url
        }

    async def async_update(self):
        """Fetch new state data for the entity from the API."""
        try:
            # Perform API request to get updated data
            response = await self.api_data.get_data()
            if response and self.entity_description.key in response:
                # Process response data and update state
                self._state = response.get(self.entity_description.key)
                self._available = True
            else:
                self._available = False
        except Exception as e:
            self._available = False
            # Log error message if necessary
            self._logger.error(f"Error updating {self.name}: {str(e)}")