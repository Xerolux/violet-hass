import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol
from homeassistant.helpers import entity_platform
from homeassistant.core import callback

from .const import DOMAIN, API_SET_FUNCTION_MANUALLY

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
SWITCHES = [
    {"name": "Violet Pump", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Violet Light", "key": "LIGHT", "icon": "mdi:lightbulb"},
]
class VioletSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, name, icon, timeout=None, retry_attempts=None):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{self.coordinator.config_entry.entry_id}_{self._key.lower()}" # Improved unique ID
        self.ip_address = coordinator.config_entry.data["api_url"].replace("http://","").replace(API_READINGS,"")
        self.username = coordinator.config_entry.data["username"]
        self.password = coordinator.config_entry.data["password"]
        self.session = aiohttp_client.async_get_clientsession(coordinator.hass)
        self.timeout = timeout or 10
        self.retry_attempts = retry_attempts or 3
        self.auto_reset_task = None  # Store the auto-reset task

        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error(f"Missing credentials or IP address for switch {self._key}")
        else:
            _LOGGER.info(f"VioletSwitch for {self._key} initialized with IP {self.ip_address}")

    @property
    def is_on(self):
        """Determine if the switch is on based on the API state."""
        return STATE_MAP.get(self.coordinator.data.get(self._key), False)

    @property
    def is_auto(self):
        """Check if the switch is in AUTO mode."""
        return self.coordinator.data.get(self._key) == 0

    async def _send_command(self, action, duration=0, last_value=0):
        """Sends the control command to the API."""
        url = f"http://{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},{last_value}"
        auth = aiohttp.BasicAuth(self.username, self.password)
        timeout = aiohttp.ClientTimeout(total=self.timeout) # Use aiohttp.ClientTimeout

        for attempt in range(self.retry_attempts):
            try:
                async with self.session.get(url, auth=auth, timeout=timeout) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    lines = response_text.strip().split('\n')
                    # More robust response check (example - adjust based on your API)
                    if len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and \
                            ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2]):
                        _LOGGER.debug(f"Successfully sent {action} command to {self._key} (duration: {duration}, last_value: {last_value})")
                        await self.coordinator.async_request_refresh() # Refresh data after command
                        return

                    _LOGGER.error(f"Unexpected response from server when sending {action} command to {self._key}: {response_text}")

            except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as err:
                _LOGGER.error(f"Error sending {action} command to {self._key} (attempt {attempt + 1}/{self.retry_attempts}): {err}")

            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._execute_action("ON", **kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command("OFF", last_value=kwargs.get("last_value", 0))

    async def async_turn_auto(self, **kwargs):
        """Set the switch to AUTO mode."""
        await self._execute_action("AUTO", **kwargs)

    async def _execute_action(self, action, **kwargs):
        """Helper to handle the ON/AUTO logic with auto reset."""
        _LOGGER.debug(f"{action} action called for {self._key} with arguments: {kwargs}")
        duration = kwargs.get("duration", 0)
        last_value = kwargs.get("last_value", 0)
        auto_delay = kwargs.get("auto_delay", 0)

        await self._send_command(action, duration, last_value)

        if self.auto_reset_task:
            self.auto_reset_task.cancel()
            self.auto_reset_task = None

        if auto_delay > 0:
            _LOGGER.debug(f"Auto-reset to AUTO after {auto_delay} seconds for {self._key}")
            self.auto_reset_task = self.coordinator.hass.loop.create_task(self._auto_reset(auto_delay))

    async def _auto_reset(self, delay):
        """Resets the switch to AUTO after the specified delay."""
        await asyncio.sleep(delay)
        if self.is_on: # Check to prevent race condition
            await self.async_turn_auto()
            self.auto_reset_task = None

    async def async_will_remove_from_hass(self):
        """Clean up when the entity is removed."""
        if self.auto_reset_task:
            self.auto_reset_task.cancel()
            self.auto_reset_task = None
        await super().async_will_remove_from_hass()

    @property
    def icon(self):
        """Return the icon."""
        icon_map = {
            "PUMP": "mdi:water-pump" if self.is_on else "mdi:water-pump-off",
            "LIGHT": "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb",
            "ECO": "mdi:leaf" if self.is_on else "mdi:leaf-off",
            "DOS_1_CL": "mdi:flask" if self.is_on else "mdi:flask-outline",
            "DOS_4_PHM": "mdi:flask" if self.is_on else "mdi:flask-outline",
        }
        return icon_map.get(self._key, self._icon)

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        attributes = super().extra_state_attributes or {}
        attributes['status_detail'] = "AUTO" if self.is_auto else "MANUAL"
        attributes['duration_remaining'] = self.coordinator.data.get(self._key) if not self.is_auto else "N/A"
        if self.auto_reset_task and not self.auto_reset_task.done():
            # Calculate remaining time only if the task exists and is not done
            attributes['auto_reset_in'] = "Calculating..."  # Placeholder, updated by _update_extra_state_attributes
        else:
            attributes['auto_reset_in'] = "N/A"

        return attributes
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_extra_state_attributes()  # Call the helper method
        super()._handle_coordinator_update()


    def _update_extra_state_attributes(self):
        """Helper method to calculate and update 'auto_reset_in'."""
        if self.auto_reset_task and not self.auto_reset_task.done():
            # Extract the delay from the auto-reset task's arguments
            # Assuming the delay is the only argument passed to _auto_reset
            delay = self.auto_reset_task._coro.cr_frame.f_locals.get('delay', 0)

            if delay > 0 :
                # Calculate elapsed time since entity creation
                elapsed_time = (datetime.now() - self._creation_time).total_seconds()
                remaining_time = max(0, delay - elapsed_time)
                self.hass.async_create_task(self.async_update_ha_state())
                self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    'auto_reset_in': remaining_time
                }
            else:
                self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    'auto_reset_in': "N/A"
                }
        else:
            self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    'auto_reset_in': "N/A"
            }

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION', 'Unknown'),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Violet switches."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    available_switches = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"], timeout=10, retry_attempts=3)
        for switch in available_switches
    ]
    async_add_entities(switches)

    platform = entity_platform.async_get_current_platform(hass)

    platform.async_register_entity_service(
        "turn_auto",
        {
            vol.Optional("auto_delay", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_auto"
    )

    platform.async_register_entity_service(
        "turn_on",
        {
            vol.Optional("duration", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_on"
    )

    platform.async_register_entity_service(
        "turn_off",
        {},
        "async_turn_off"
    )
