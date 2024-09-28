import logging
import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import async_timeout

from .const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_POLLING_INTERVAL, 
    CONF_USE_SSL, 
    CONF_DEVICE_ID,
    CONF_USERNAME, 
    CONF_PASSWORD,
    DEFAULT_POLLING_INTERVAL, 
    DEFAULT_USE_SSL,
    API_READINGS,
    API_SET_FUNCTION_MANUALLY
)

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
        self.use_ssl = coordinator.use_ssl
        self.session = coordinator.session
        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error("Missing credentials or IP address for the VioletSwitch")
        else:
            _LOGGER.info(f"VioletSwitch initialized for {self._key} with IP {self.ip_address}")

    def _get_switch_state(self):
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        return self._get_switch_state() == 1

    async def _send_command(self, action):
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.username}:{self.password}@{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},0,0"
        try:
            async with async_timeout.timeout(10):  # Setting a 10-second timeout
                async with self.session.post(url) as response:
                    response.raise_for_status()
                    _LOGGER.debug(f"Successfully sent {action} command to {self._key} at {url}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Client error sending {action} command to {self._key}: {err}")
        except aiohttp.ClientResponseError as resp_err:
            _LOGGER.error(f"Response error sending {action} command to {self._key}: {resp_err.status} {resp_err.message}")
        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout sending {action} command to {self._key}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error when sending {action} command to {self._key}: {err}")

    async def async_turn_on(self, **kwargs):
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs):
        await self._send_command("OFF")

    async def async_turn_auto(self, **kwargs):
        await self._send_command("AUTO")

    @property
    def icon(self):
        if self._key == "PUMP":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "LIGHT":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        elif self._key == "ECO":
            return "mdi:leaf" if self.is_on else "mdi:leaf-off"
        elif self._key == "DOS_1_CL" or self._key == "DOS_4_PHM":
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
