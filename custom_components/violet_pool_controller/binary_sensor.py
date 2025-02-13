import logging
from typing import Any, Dict, List
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Map the API numeric values to ON (True) or OFF (False) states
STATE_MAP: Dict[int, bool] = {
    0: False,  # AUTO (not on)
    1: True,   # AUTO (on)
    2: False,  # OFF by control rule
    3: True,   # ON by emergency rule
    4: True,   # MANUAL ON
    5: False,  # OFF by emergency rule
    6: False,  # MANUAL OFF
}

# Define the binary sensors to be created.  Include the 'name' field.
BINARY_SENSORS: List[Dict[str, Any]] = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb"},
]


class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, key: str, name: str, icon: str, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry  # Speichere config_entry
        self._attr_name = name  # Verwende den definierten Namen
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{key}"  # Eindeutige ID mit entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},  # Eindeutiger Bezeichner
            "name": f"Violet Pool Controller ({config_entry.data.get('ip_address', 'Unknown IP')})",  # IP im Gerätenamen
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Platzhalter, ggf. API-Daten abrufen
            "sw_version": self.coordinator.data.get("fw", "Unknown"),  # Firmware-Version
            "configuration_url": f"http://{config_entry.data.get('ip_address', 'Unknown IP')}",
        }
        self._has_logged_none_state = False  # Verhindert wiederholte Logs bei None-Zustand

    def _get_sensor_state(self) -> bool:
        """Hilfsmethode zum Abrufen und Mappen des aktuellen Sensorzustands von der API."""
        state = self.coordinator.data.get(self._key, None)

        if state is None:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Sensor {self._key} returned None as its state. Defaulting to 'OFF'.")
                self._has_logged_none_state = True  # Nur einmal loggen
            return False  # Standardmäßig OFF, wenn state None ist

        # Numerischen Zustand mit STATE_MAP mappen; bei unbekannten Werten default zu False.
        return STATE_MAP.get(state, False)

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return self._get_sensor_state()

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor, changing based on state."""
        return self._icon if self.is_on else f"{self._icon}-off"


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Erstelle Binary Sensor Entities basierend auf der BINARY_SENSORS Liste.
    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["name"], sensor["icon"], config_entry)
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)
