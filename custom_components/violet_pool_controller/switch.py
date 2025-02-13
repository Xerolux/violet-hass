import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import async_timeout
import voluptuous as vol
from homeassistant.helpers import entity_platform

from .const import DOMAIN, API_SET_FUNCTION_MANUALLY, CONF_API_URL, CONF_DEVICE_NAME

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

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Device Switch."""

    def __init__(self, coordinator, key, name, icon, config_entry, timeout=None, retry_attempts=None):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry  # Store the config entry
        self._attr_name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"  # Use entry_id for uniqueness
        self.ip_address = config_entry.data.get(CONF_API_URL)  # Get IP from config entry
        self.username = coordinator.username # Get from coordinator
        self.password = coordinator.password # Get from coordinator
        self.session = coordinator.session
        self.timeout = timeout or 10
        self.retry_attempts = retry_attempts or 3
        self.auto_reset_time = None

        # Set device info. Crucially, use entry_id.
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{config_entry.data.get(CONF_DEVICE_NAME)} ({config_entry.data.get(CONF_API_URL)})", #Include IP
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  #  Consider making this dynamic.
            "sw_version": self.coordinator.data.get('fw', 'Unknown'), # Consistent version Key
            "configuration_url": f"http://{config_entry.data.get(CONF_API_URL)}",
        }

        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error(f"Missing credentials or IP address for switch {self._key}")
        else:
            _LOGGER.info(f"VioletSwitch for {self._key} initialized with IP {self.ip_address}")

    def _get_switch_state(self):
        """Fetches the current state of the switch from the coordinator."""
        return self.coordinator.data.get(self._key, None)

    @property
    def is_on(self):
        """Determine if the switch is on based on the API state."""
        # Use .get() with a default value to handle potential missing keys.
        return STATE_MAP.get(self._get_switch_state(), False)

    @property
    def is_auto(self):
        """Check if the switch is in AUTO mode (state 0)."""
        return self._get_switch_state() == 0
    
    @property
    def available(self) -> bool:
        """Return True if the switch is available."""
        # Check both coordinator success and if the key exists in the data.
        return self.coordinator.last_update_success and self._key in self.coordinator.data


    async def _send_command(self, action, duration=0, last_value=0):
        """Sends the control command to the API."""
        protocol = "https" if self._config_entry.data.get("use_ssl", False) else "http" # Determine protocol
        url = f"{protocol}://{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},{last_value}"
        _LOGGER.debug(f"Sending command to URL: {url}")  # Log the full URL
        auth = aiohttp.BasicAuth(self.username, self.password)

        for attempt in range(self.retry_attempts):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=self._config_entry.data.get("use_ssl", False)) as response: # Pass use_ssl to session.get
                        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                        response_text = await response.text()
                        lines = response_text.strip().split('\n')
                        # Check for a valid response structure.
                        if len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and \
                                ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2]):
                            _LOGGER.debug(f"Successfully sent {action} command to {self._key} (duration: {duration}, last_value: {last_value})")
                            await self.coordinator.async_request_refresh()  # Refresh data after command
                            return  # Command successful, exit retry loop

                        else:
                            _LOGGER.error(f"Unexpected response from server when sending {action} command to {self._key}: {response_text}")
            except aiohttp.ClientResponseError as resp_err:
                _LOGGER.error(f"Response error when sending {action} command to {self._key}: {resp_err.status} {resp_err.message}")
            except aiohttp.ClientError as err:
                _LOGGER.error(f"Client error when sending {action} command to {self._key}: {err}")
            except asyncio.TimeoutError:
                _LOGGER.error(f"Timeout sending {action} command to {self._key}, attempt {attempt + 1} of {self.retry_attempts}")
            except Exception as err:
                _LOGGER.error(f"Unexpected error when sending {action} command to {self._key}: {err}")

            # Exponential backoff.
            await asyncio.sleep(2 ** attempt)

        _LOGGER.error(f"Failed to send command {action} to {self._key} after {self.retry_attempts} attempts")  # Log failure after all retries


    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._execute_action("ON", **kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command("OFF", last_value=kwargs.get("last_value", 0)) # Added last_value

    async def async_turn_auto(self, **kwargs):
        """Set the switch to AUTO mode."""
        await self._execute_action("AUTO", **kwargs) # added Auto

    async def _execute_action(self, action, **kwargs):
        """Helper to handle the ON/AUTO logic with auto reset."""
        _LOGGER.debug(f"{action} action called for {self._key} with arguments: {kwargs}")
        duration = kwargs.get("duration", 0)
        last_value = kwargs.get("last_value", 0)
        auto_delay = kwargs.get("auto_delay", 0)

        await self._send_command(action, duration, last_value)

        # Handle auto reset if auto_delay is provided
        if auto_delay > 0:
            self.auto_reset_time = datetime.now() + timedelta(seconds=auto_delay)
            _LOGGER.debug(f"Auto-reset to AUTO after {auto_delay} seconds for {self._key}")
            await asyncio.sleep(auto_delay)  # Wait for the specified delay
            # Check if auto_reset_time is still in the future before resetting.
            if self.auto_reset_time and datetime.now() >= self.auto_reset_time:
                 await self.async_turn_auto()
            else:
                _LOGGER.debug(f"Auto-reset to AUTO cancelled for {self._key}")  # Log if canceled


    @property
    def icon(self):
        """Return the icon to use, dynamically if possible."""
        icon_map = {
            "PUMP": "mdi:water-pump" if self.is_on else "mdi:water-pump-off",
            "LIGHT": "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb",
            "ECO": "mdi:leaf" if self.is_on else "mdi:leaf-off", # Example
            "DOS_1_CL": "mdi:flask" if self.is_on else "mdi:flask-outline",
            "DOS_4_PHM": "mdi:flask" if self.is_on else "mdi:flask-outline",
        }
        # Return dynamic icon if available, otherwise the default icon.
        return icon_map.get(self._key, self._icon)

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes for the switch."""
        attributes = super().extra_state_attributes or {}
        attributes['status_detail'] = "AUTO" if self.is_auto else "MANUAL"
        attributes['duration_remaining'] = self._get_switch_state() if not self.is_auto else "N/A"  # Show remaining time if not in AUTO
        # Display auto_reset_in time if set
        if self.auto_reset_time:
            remaining_time = (self.auto_reset_time - datetime.now()).total_seconds()
            attributes['auto_reset_in'] = max(0, remaining_time)  # Show remaining time in seconds
        else:
            attributes['auto_reset_in'] = "N/A" # Or None if you prefer
        return attributes


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Violet switches based on config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    # Create switch entities only for switches that exist in the coordinator's data.
    available_switches = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"], config_entry, timeout=10, retry_attempts=3)
        for switch in available_switches
    ]
    async_add_entities(switches)

    # Register entity-specific services using async_register_entity_service
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "turn_auto",
        {
            vol.Optional("auto_delay", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int), # Add last_value
        },
        "async_turn_auto"
    )

    platform.async_register_entity_service(
        "turn_on",
        {
            vol.Optional("duration", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int), # Add last_value
        },
        "async_turn_on"
    )

    platform.async_register_entity_service(
        "turn_off",
        {
           vol.Optional("last_value", default=0): vol.Coerce(int), # Add last_value
        },
        "async_turn_off"
    )

# Define the available switches.
SWITCHES = [
    {"name": "Pump", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco", "key": "ECO", "icon": "mdi:leaf"}, # Example
    {"name": "Dos 1 CL", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "Dos 4 PHM", "key": "DOS_4_PHM", "icon": "mdi:flask"},
]
