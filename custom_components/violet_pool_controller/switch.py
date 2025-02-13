import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
import async_timeout
import voluptuous as vol
from homeassistant.helpers import entity_platform
from homeassistant.config_entries import ConfigEntry

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

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        key: str,
        name: str,
        icon: str,
        config_entry: ConfigEntry,
        timeout: int = 10,
        retry_attempts: int = 3,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry

        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"
        self.ip_address: str = config_entry.data.get(CONF_API_URL)
        # Assuming the coordinator provides username, password and session attributes
        self.username: str = getattr(coordinator, "username", "")
        self.password: str = getattr(coordinator, "password", "")
        self.session: aiohttp.ClientSession = getattr(coordinator, "session", None)
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.auto_reset_time: datetime | None = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({config_entry.data.get(CONF_API_URL, 'Unknown IP')})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Dynamisch abrufbar machen, falls möglich
            "sw_version": self.coordinator.data.get("fw", "Unknown"),
            "configuration_url": f"http://{config_entry.data.get(CONF_API_URL)}",
        }

        if not all([self.ip_address, self.username, self.password, self.session]):
            _LOGGER.error("Missing credentials or IP address for switch %s", self._key)
        else:
            _LOGGER.info("VioletSwitch for %s initialized with IP %s", self._key, self.ip_address)

    def _get_switch_state(self) -> int | None:
        """Fetch the current state of the switch from the coordinator."""
        return self.coordinator.data.get(self._key, None)

    @property
    def is_on(self) -> bool:
        """Determine if the switch is on based on the API state."""
        return STATE_MAP.get(self._get_switch_state(), False)

    @property
    def is_auto(self) -> bool:
        """Check if the switch is in AUTO mode (state 0)."""
        return self._get_switch_state() == 0

    @property
    def available(self) -> bool:
        """Return True if the switch is available."""
        return self.coordinator.last_update_success and self._key in self.coordinator.data

    async def _send_command(self, action: str, duration: int = 0, last_value: int = 0) -> None:
        """Send the control command to the API."""
        use_ssl = self._config_entry.data.get("use_ssl", False)
        protocol = "https" if use_ssl else "http"
        url = f"{protocol}://{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},{last_value}"
        _LOGGER.debug("Sending command to URL: %s", url)
        auth = aiohttp.BasicAuth(self.username, self.password)

        for attempt in range(self.retry_attempts):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=use_ssl) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        lines = response_text.strip().split("\n")
                        # Check for a valid response structure.
                        if (
                            len(lines) >= 3
                            and lines[0] == "OK"
                            and lines[1] == self._key
                            and ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2])
                        ):
                            _LOGGER.debug(
                                "Successfully sent %s command to %s (duration: %d, last_value: %d)",
                                action,
                                self._key,
                                duration,
                                last_value,
                            )
                            await self.coordinator.async_request_refresh()
                            return  # Command successful, exit retry loop
                        else:
                            _LOGGER.error(
                                "Unexpected response from server when sending %s command to %s: %s",
                                action,
                                self._key,
                                response_text,
                            )
            except aiohttp.ClientResponseError as resp_err:
                _LOGGER.error(
                    "Response error when sending %s command to %s: %s %s",
                    action,
                    self._key,
                    resp_err.status,
                    resp_err.message,
                )
            except aiohttp.ClientError as err:
                _LOGGER.error("Client error when sending %s command to %s: %s", action, self._key, err)
            except asyncio.TimeoutError:
                _LOGGER.error(
                    "Timeout sending %s command to %s, attempt %d of %d",
                    action,
                    self._key,
                    attempt + 1,
                    self.retry_attempts,
                )
            except Exception as err:
                _LOGGER.error("Unexpected error when sending %s command to %s: %s", action, self._key, err)

            # Exponential backoff before retrying.
            await asyncio.sleep(2 ** attempt)

        _LOGGER.error("Failed to send command %s to %s after %d attempts", action, self._key, self.retry_attempts)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._execute_action("ON", **kwargs)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._send_command("OFF", last_value=kwargs.get("last_value", 0))

    async def async_turn_auto(self, **kwargs) -> None:
        """Set the switch to AUTO mode."""
        await self._execute_action("AUTO", **kwargs)

    async def _execute_action(self, action: str, **kwargs) -> None:
        """Helper to handle the ON/AUTO logic with auto reset."""
        _LOGGER.debug("%s action called for %s with arguments: %s", action, self._key, kwargs)
        duration: int = kwargs.get("duration", 0)
        last_value: int = kwargs.get("last_value", 0)
        auto_delay: int = kwargs.get("auto_delay", 0)

        await self._send_command(action, duration, last_value)

        # Handle auto reset if auto_delay is provided.
        if auto_delay > 0:
            self.auto_reset_time = datetime.now() + timedelta(seconds=auto_delay)
            _LOGGER.debug("Auto-reset to AUTO after %d seconds for %s", auto_delay, self._key)
            await asyncio.sleep(auto_delay)
            # Check if it's time to auto-reset.
            if self.auto_reset_time and datetime.now() >= self.auto_reset_time:
                await self.async_turn_auto()
            else:
                _LOGGER.debug("Auto-reset to AUTO cancelled for %s", self._key)

    @property
    def icon(self) -> str:
        """Return the icon to use, dynamically if possible."""
        icon_map = {
            "PUMP": "mdi:water-pump" if self.is_on else "mdi:water-pump-off",
            "LIGHT": "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb",
            "ECO": "mdi:leaf" if self.is_on else "mdi:leaf-off",
            "DOS_1_CL": "mdi:flask" if self.is_on else "mdi:flask-outline",
            "DOS_4_PHM": "mdi:flask" if self.is_on else "mdi:flask-outline",
        }
        return icon_map.get(self._key, self._icon)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the extra state attributes for the switch."""
        attributes = super().extra_state_attributes or {}
        attributes["status_detail"] = "AUTO" if self.is_auto else "MANUAL"
        attributes["duration_remaining"] = self._get_switch_state() if not self.is_auto else "N/A"
        if self.auto_reset_time:
            remaining_time = (self.auto_reset_time - datetime.now()).total_seconds()
            attributes["auto_reset_in"] = max(0, remaining_time)
        else:
            attributes["auto_reset_in"] = "N/A"
        return attributes


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up the Violet switches based on config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    # Create switch entities only for switches that exist in the coordinator's data.
    available_switches = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"], config_entry, timeout=10, retry_attempts=3)
        for switch in available_switches
    ]
    async_add_entities(switches)

    # Register entity-specific services.
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "turn_auto",
        {
            vol.Optional("auto_delay", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_auto",
    )

    platform.async_register_entity_service(
        "turn_on",
        {
            vol.Optional("duration", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_on",
    )

    platform.async_register_entity_service(
        "turn_off",
        {
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_off",
    )


# Define the available switches.
SWITCHES = [
    {"name": "Pump", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Dos 1 CL", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "Dos 4 PHM", "key": "DOS_4_PHM", "icon": "mdi:flask"},
]
