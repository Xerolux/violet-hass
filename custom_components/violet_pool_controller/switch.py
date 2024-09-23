import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Device Switch."""

    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get(self._key) == 1

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            async with self.coordinator.session.post(f"{self.coordinator.api_url}/turn_on/{self._key}") as response:
                response.raise_for_status()
        except Exception as err:
            _LOGGER.error(f"Error turning on {self._key}: {err}")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            async with self.coordinator.session.post(f"{self.coordinator.api_url}/turn_off/{self._key}") as response:
                response.raise_for_status()
        except Exception as err:
            _LOGGER.error(f"Error turning off {self._key}: {err}")

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["icon"])
        for switch in SWITCHES
    ]
    async_add_entities(switches)

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},  # Switch for controlling the pump
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},  # Switch for controlling the pool light
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},  # Switch for Eco mode
    {"name": "Chlorine Dosing Switch", "key": "DOS_1_CL", "icon": "mdi:chemical-weapon"},  # Chlorine dosing switch
    {"name": "pH-minus Dosing Switch", "key": "DOS_4_PHM", "icon": "mdi:chemical-weapon"},  # pH-minus dosing switch
]
