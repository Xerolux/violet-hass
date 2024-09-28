import logging
import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, API_SET_FUNCTION_MANUALLY

_LOGGER = logging.getLogger(__name__)

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self.ip_address = coordinator.ip_address
        self.username = coordinator.username
        self.password = coordinator.password

    def _get_switch_state(self):
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        return self._get_switch_state() == 1

    async def async_turn_on(self, **kwargs):
        try:
            if self.username and self.password and self.ip_address:
                url = f"http://{self.username}:{self.password}@{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},ON,0,0"
                async with self.coordinator.session.post(url) as response:
                    response.raise_for_status()
                _LOGGER.debug(f"Successfully turned on {self._key} at {url}")
            else:
                _LOGGER.error(f"Missing credentials or IP address for {self._key}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error turning on {self._key}: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error when turning on {self._key}: {err}")

    async def async_turn_off(self, **kwargs):
        try:
            if self.username and self.password and self.ip_address:
                url = f"http://{self.username}:{self.password}@{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},OFF,0,0"
                async with self.coordinator.session.post(url) as response:
                    response.raise_for_status()
                _LOGGER.debug(f"Successfully turned off {self._key} at {url}")
            else:
                _LOGGER.error(f"Missing credentials or IP address for {self._key}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error turning off {self._key}: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error when turning off {self._key}: {err}")

    async def async_turn_auto(self, **kwargs):
        try:
            if self.username and self.password and self.ip_address:
                url = f"http://{self.username}:{self.password}@{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},AUTO,0,0"
                async with self.coordinator.session.post(url) as response:
                    response.raise_for_status()
                _LOGGER.debug(f"Successfully set {self._key} to auto at {url}")
            else:
                _LOGGER.error(f"Missing credentials or IP address for {self._key}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error setting {self._key} to auto: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error when setting {self._key} to auto: {err}")

    @property
    def icon(self):
        if self._key == "PUMP":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "LIGHT":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        elif self._key == "ECO":
            return "mdi:leaf" if self.is_on else "mdi:leaf-off"
        elif self._key == "DOS_1_CL":
            return "mdi:flask" if self.is_on else "mdi:atom"
        elif self._key == "DOS_4_PHM":
            return "mdi:flask" if self.is_on else "mdi:atom"
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw', 'Unknown'),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["icon"])
        for switch in SWITCHES
    ]
    async_add_entities(switches)

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Chlorine Dosing Switch", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "pH-minus Dosing Switch", "key": "DOS_4_PHM", "icon": "mdi:flask"},
]
