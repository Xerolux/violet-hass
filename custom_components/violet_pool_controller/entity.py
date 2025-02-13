import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_DEVICE_ID
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_API_URL, CONF_POLLING_INTERVAL
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class VioletPoolControllerEntity(CoordinatorEntity):
    """Base class for a Violet Pool Controller entity."""

    def __init__(self, coordinator, config_entry, entity_description):
        """Initialize the entity."""
        super().__init__(coordinator)  # Initialize CoordinatorEntity
        self.config_entry = config_entry
        self.entity_description = entity_description
        self._name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {entity_description.name}"
        # Use entry_id for unique ID, crucial for multiple devices.
        self._unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._state = None
        self._available = True  # Assume available initially
        self.api_url = config_entry.data.get(CONF_API_URL)  # Store for reference
        self.polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)
        self._logger = logging.getLogger(f"{DOMAIN}.{self._unique_id}")  # Logger with unique ID

        self._logger.info(f"Initialized {self._name} with unique ID: {self._unique_id}")

        # Set device info.  Crucially, use entry_id as the identifier.
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{config_entry.data.get(CONF_DEVICE_NAME)} ({config_entry.data.get(CONF_API_URL)})", # Include IP
            "manufacturer": "PoolDigital GmbH & Co. KG",  # Corrected manufacturer
            "model": "Violet Model X", #  Consider making this dynamic if possible
            "sw_version": self.coordinator.data.get('fw', 'Unknown'), #  Consistent version key
            "configuration_url": f"http://{config_entry.data.get(CONF_API_URL)}",
        }


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
        return self._available and self.coordinator.last_update_success # Check coordinator

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "polling_interval": self.polling_interval,
            "api_url": self.api_url,
            "last_updated": self.coordinator.last_update_success_time,  # Add last update time
        }

    async def async_update(self):
        """Fetch new state data for the entity.  This is now handled by the coordinator."""
        # No need to fetch data here, the coordinator handles it.
        # We just need to update the entity's state from the coordinator's data.
        try:
            if self.coordinator.data:  # Check if coordinator has data
                self._update_state(self.coordinator.data)
                self._available = True
                self._logger.debug(f"Updated {self._name} state: {self._state}")
            else:
                self._available = False
                self._logger.warning(f"No data available from coordinator for {self._name}.")

        except Exception as e:
            self._available = False
            self._logger.error(f"Unexpected error updating {self._name}: {e}")


    def _update_state(self, data):
        """Update the entity's state from the coordinator's data."""
        try:
            new_state = data.get(self.entity_description.key)
            if new_state is not None:  # Only update if the key exists and has a value
                self._state = new_state
                self._logger.debug(f"New state for {self.name}: {self._state}")
            else:
                self._logger.warning(f"Key {self.entity_description.key} not found or has no value in data.")
                self._available = False # Mark as unavailable if the key is missing

        except KeyError:  # This shouldn't happen if we check for None first, but keep for safety.
            self._logger.error(f"Key {self.entity_description.key} not found in response.")
            self._available = False
