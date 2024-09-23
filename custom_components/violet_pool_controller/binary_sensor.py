import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._key) == 1

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"])
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP_STATE", "icon": "mdi:water-pump"},  # Binary sensor for pump state
    {"name": "Solar State", "key": "SOLARSTATE", "icon": "mdi:solar-power"},  # Binary sensor for solar state
    {"name": "Heater State", "key": "HEATERSTATE", "icon": "mdi:radiator"},  # Binary sensor for heater state
    {"name": "Cover State", "key": "COVER_STATE", "icon": "mdi:garage"},  # Binary sensor for pool cover position
    {"name": "Refill State", "key": "REFILL_STATE", "icon": "mdi:water-boiler"},  # Binary sensor for water refill
    {"name": "Light State", "key": "LIGHT_STATE", "icon": "mdi:lightbulb"},  # Binary sensor for pool light
]
