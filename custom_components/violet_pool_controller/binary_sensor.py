import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
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

class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry  # Store config_entry
        self._attr_name = f"Violet {key}" # Use the key directly for the name
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{key}" # Include entry_id in unique ID
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)}, # Use entry_id as unique identifier
            "name": f"Violet Pool Controller ({config_entry.data.get('host', 'Unknown IP')})",  # Include IP in device name
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Placeholder, consider fetching from API if available
            "sw_version": self.coordinator.data.get('fw', 'Unknown'), # Use a single key, 'fw' is more common
            "configuration_url": f"http://{config_entry.data.get('host', 'Unknown IP')}",
        }
        self._has_logged_none_state = False  # To avoid repeated logs

    def _get_sensor_state(self):
        """Helper method to retrieve and map the current sensor state from the API."""
        state = self.coordinator.data.get(self._key, None)

        if state is None:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Sensor {self._key} returned None as its state. Defaulting to 'OFF'.")
                self._has_logged_none_state = True  # Log only once
            return False  # Default to OFF (False) when state is None

        # Map the numeric state to True (ON) or False (OFF) using STATE_MAP
        # Use .get() with a default value to handle unexpected states.
        return STATE_MAP.get(state, False)

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._get_sensor_state()

    @property
    def icon(self):
        """Return the icon for the binary sensor, changing based on state."""
        return self._icon if self.is_on else f"{self._icon}-off"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create binary sensor entities based on the BINARY_SENSORS list.
    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"], config_entry)
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)

# Define the binary sensors to be created.  Include the 'name' field.
BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb"},
]
