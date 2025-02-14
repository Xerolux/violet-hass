import logging

from homeassistant.const import ATTR_ATTRIBUTES
from homeassistant.helpers.entity import DeviceEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Violet Pool Controller device."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VioletPoolControllerDevice(coordinator)], False)


class VioletPoolControllerDevice(DeviceEntity):
    """Representation of the Violet Pool Controller device."""

    def __init__(self, coordinator):
        """Initialize the device."""
        self.coordinator = coordinator
        self._name = "Violet Pool Controller"

    @property  # Correct indentation here
    def name(self):
        """Return the name of the device."""
        return self._name

    @property  # Correct indentation here
    def unique_id(self):
        """Return the unique ID of the device."""
        return f"{DOMAIN}_{self.coordinator.device_id}"

    @property  # Correct indentation here
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.name,
            "manufacturer": "Violet",
            "model": "Pool Controller",
            "sw_version": "1.0",
        }

    @property  # Correct indentation here
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        if self.coordinator.data:
            return self.coordinator.data
        return {}

    @property  # Correct indentation here
    def available(self):
        """Return True if the device is available."""
        return self.coordinator.last_update_success

    async def async_update(self):  # Correct indentation here
        """Update the entity with the latest data."""
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()