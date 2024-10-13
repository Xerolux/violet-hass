import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import async_timeout

from .const import (
    DOMAIN, 
    API_SET_FUNCTION_MANUALLY
)

_LOGGER = logging.getLogger(__name__)

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self.ip_address = coordinator.ip_address
        self.username = coordinator.username
        self.password = coordinator.password
        self.session = coordinator.session
        self.timeout = coordinator.timeout if hasattr(coordinator, 'timeout') else 10  # Customizable timeout
        self.auto_reset_time = None  # For automatic reset after duration

        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error(f"Missing credentials or IP address for switch {self._key}")
        else:
            _LOGGER.info(f"VioletSwitch for {self._key} initialized with IP {self.ip_address}")

    def _get_switch_state(self):
        """Fetches the current state of the switch."""
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        return self._get_switch_state() in (1, 4)

    @property
    def is_auto(self):
        return self._get_switch_state() == 0

    async def _send_command(self, action, duration=0, last_value=0):
        """Sends the control command to the API and handles retries."""
        url = f"http://{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},{last_value}"
        auth = aiohttp.BasicAuth(self.username, self.password)

        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.get(url, auth=auth) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        lines = response_text.strip().split('\n')
                        if len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2]):
                            _LOGGER.debug(f"Successfully sent {action} command to {self._key} with duration {duration} and last value {last_value}")
                            await self.coordinator.async_request_refresh()
                            return
                        else:
                            _LOGGER.error(f"Unexpected response from server when sending {action} command to {self._key}: {response_text}")
            except aiohttp.ClientResponseError as resp_err:
                _LOGGER.error(f"Response error when sending {action} command to {self._key}: {resp_err.status} {resp_err.message}")
            except aiohttp.ClientError as err:
                _LOGGER.error(f"Client error when sending {action} command to {self._key}: {err}")
            except asyncio.TimeoutError:
                _LOGGER.error(f"Timeout sending {action} command to {self._key}, attempt {attempt + 1} of {retry_attempts}")
            except Exception as err:
                _LOGGER.error(f"Unexpected error when sending {action} command to {self._key}: {err}")

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug(f"async_turn_on called for {self._key} with arguments: {kwargs}")
        duration = kwargs.get("duration", 0)
        last_value = kwargs.get("last_value", 0)
        await self._send_command("ON", duration, last_value)
        
        auto_delay = kwargs.get("auto_delay", 0)
        if auto_delay > 0:
            self.auto_reset_time = datetime.now() + timedelta(seconds=auto_delay)
            _LOGGER.debug(f"Auto-reset to AUTO after {auto_delay} seconds for {self._key}")
            await asyncio.sleep(auto_delay)
            await self.async_turn_auto()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug(f"async_turn_off called for {self._key} with arguments: {kwargs}")
        last_value = kwargs.get("last_value", 0)
        await self._send_command("OFF", 0, last_value)

    async def async_turn_auto(self, **kwargs):
        """Set the switch to AUTO mode."""
        _LOGGER.debug(f"async_turn_auto called for {self._key} with arguments: {kwargs}")
        auto_delay = kwargs.get("auto_delay", 0)
        last_value = kwargs.get("last_value", 0)
        await self._send_command("AUTO", auto_delay, last_value)
        self.auto_reset_time = None

    @property
    def icon(self):
        """Return the icon depending on the switch's state."""
        if self._key == "PUMP":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "LIGHT":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        elif self._key == "ECO":
            return "mdi:leaf" if self.is_on else "mdi:leaf-off"
        elif self._key in ["DOS_1_CL", "DOS_4_PHM"]:
            return "mdi:flask" if self.is_on else "mdi:flask-outline"
        elif "EXT" in self._key:
            return "mdi:power-socket" if self.is_on else "mdi:power-socket-off"
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes for the switch."""
        attributes = super().extra_state_attributes or {}
        attributes['status_detail'] = "AUTO" if self.is_auto else "MANUAL"
        attributes['duration_remaining'] = self._get_switch_state() if not self.is_auto else "N/A"
        if self.auto_reset_time:
            remaining_time = (self.auto_reset_time - datetime.now()).total_seconds()
            attributes['auto_reset_in'] = max(0, remaining_time)
        else:
            attributes['auto_reset_in'] = "N/A"
        return attributes

    @property
    def device_info(self):
        """Return device information for the Violet Pool Controller."""
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION', 'Unknown'),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Violet switches based on config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    available_switches = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"])
        for switch in available_switches
    ]
    async_add_entities(switches)

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
]
