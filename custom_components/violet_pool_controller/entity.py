import logging
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_DEVICE_ID
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_API_URL, CONF_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerEntity(CoordinatorEntity, Entity): # Inherit from CoordinatorEntity
    """Base class for a Violet Pool Controller entity."""

    def __init__(self, coordinator, config_entry, entity_description: EntityDescription):
        """Initialize the entity."""
        super().__init__(coordinator) # Pass the coordinator to the superclass

        if not entity_description or not hasattr(entity_description, 'key') or not hasattr(entity_description, 'name'):
            raise ValueError("Invalid entity_description provided.")

        self.config_entry = config_entry
        self.entity_description = entity_description
        self._attr_name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {entity_description.name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.data.get(CONF_DEVICE_NAME),
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "configuration_url": config_entry.data.get(CONF_API_URL)
        }
        _LOGGER.info(f"Initialized {self.name} with unique ID: {self.unique_id}")


    @property
    def available(self):
        """Return if the entity is available."""
        # CoordinatorEntity handles availability based on coordinator.last_update_success
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the state of the entity."""
        # Get data from the coordinator, not self.api_data
        return self.coordinator.data.get(self.entity_description.key)

    # No async_update method is needed when using CoordinatorEntity!
