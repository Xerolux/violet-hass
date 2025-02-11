import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,  # Import BinarySensorDeviceClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Map the API numeric values to ON (True) or OFF (False) states
STATE_MAP = {
    0: False,  # AUTO (not on)
    1: True,   # AUTO (on)
    2: False,  # OFF by control rule
    3: True,   # ON by emergency rule
    4: True,   # MANUAL ON
    5: False,  # OFF by emergency rule
    6: False,  # MANUAL OFF
}

# Define BINARY_SENSORS *before* it's used
BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump", "device_class": BinarySensorDeviceClass.POWER},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power", "device_class": BinarySensorDeviceClass.POWER},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator", "device_class": BinarySensorDeviceClass.HEAT},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb", "device_class": BinarySensorDeviceClass.LIGHT},
]

class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon, config_entry, device_class=None):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._key}"  # Truly unique ID
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION'),
            "configuration_url": f"http://{self._config_entry.data.get('host', 'Unknown IP')}",
        }
        self._has_logged_none_state = False
        self._device_class = device_class # Store the device class

    @property
    def device_class(self):
        """Return the device class of the binary sensor."""
        return self._device_class

    def _get_sensor_state(self):
        """Helper method to retrieve and map the current sensor state from the API."""
        state = self.coordinator.data.get(self._key, None)

        if state is None:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Sensor {self._key} returned None as its state. Defaulting to 'OFF'.")
                self._has_logged_none_state = True
            return False

        return STATE_MAP.get(state, False)

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._get_sensor_state()

    @property
    def icon(self):
        """Return the icon for the binary sensor."""
        return f"{self._icon}-off" if not self.is_on and self._device_class is None else self._icon

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    if not coordinator.data:
        _LOGGER.warning("Coordinator data is empty.  Initial connection likely failed.")
        return  # Exit early if no data

    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"], config_entry, sensor.get("device_class"))
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)
