"""Service handlers for the Violet Pool Controller integration."""

import asyncio
import logging
from typing import Any, Iterable

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .api import VioletPoolAPIError
from .const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
    ACTION_MAN,
    ACTION_OFF,
    ACTION_ON,
    DEVICE_PARAMETERS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================

# Common validators
def _as_device_id_list(value: Any) -> list[str]:
    """Normalize raw device id input into a list of strings."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value]
    return [str(value)]


DEVICE_ID_SELECTOR = vol.All(_as_device_id_list, [cv.string])

# Dosing Mappings
DOSING_TYPE_MAPPING = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Flockmittel": "DOS_6_FLOC",
}

# Validation Ranges
MIN_DOSING_DURATION = 5
MAX_DOSING_DURATION = 300
MIN_PUMP_SPEED = 1
MAX_PUMP_SPEED = 3
MIN_TEMPERATURE = 20.0
MAX_TEMPERATURE = 40.0
MIN_PH = 6.8
MAX_PH = 7.8
DEFAULT_SAFETY_INTERVAL = 300

# =============================================================================
# SERVICE SCHEMAS
# =============================================================================


def get_service_schemas() -> dict[str, vol.Schema]:
    """Get all service schemas."""
    return {
        # Pump Control
        "control_pump": vol.Schema(
            {
                vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
                vol.Required("action"): vol.In(
                    ["speed_control", "force_off", "eco_mode", "boost_mode", "auto"]
                ),
                vol.Optional("speed", default=2): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED)
                ),
                vol.Optional("duration", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=86400)
                ),
            }
        ),
        # Smart Dosing
        "smart_dosing": vol.Schema(
            {
                vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
                vol.Required("dosing_type"): vol.In(list(DOSING_TYPE_MAPPING.keys())),
                vol.Required("action"): vol.In(["manual_dose", "auto", "stop"]),
                vol.Optional("duration", default=30): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_DOSING_DURATION, max=MAX_DOSING_DURATION),
                ),
                vol.Optional("safety_override", default=False): cv.boolean,
            }
        ),
        # PV Surplus
        "manage_pv_surplus": vol.Schema(
            {
                vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
                vol.Required("mode"): vol.In(["activate", "deactivate", "auto"]),
                vol.Optional("pump_speed", default=2): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED)
                ),
            }
        ),
        # DMX Control
        "control_dmx_scenes": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("action"): vol.In(
                    ["all_on", "all_off", "all_auto", "sequence", "party_mode"]
                ),
                vol.Optional("sequence_delay", default=2): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=60)
                ),
            }
        ),
        # Light Color Pulse
        "set_light_color_pulse": vol.Schema(
            {
                vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
                vol.Optional("pulse_count", default=1): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
                vol.Optional("pulse_interval", default=500): vol.All(
                    vol.Coerce(int), vol.Range(min=100, max=2000)
                ),
            }
        ),
        # Digital Rules
        "manage_digital_rules": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("rule_key"): vol.In(
                    [f"DIRULE_{i}" for i in range(1, 8)]
                ),
                vol.Required("action"): vol.In(["trigger", "lock", "unlock"]),
            }
        ),
        "test_output": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("output"): cv.string,
                vol.Optional("mode", default="SWITCH"): vol.In(["SWITCH", "ON", "OFF"]),
                vol.Optional("duration", default=120): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=900)
                ),
            }
        ),
    }


# =============================================================================
# SERVICE MANAGER
# =============================================================================


class VioletServiceManager:
    """Manages all Violet Pool Controller services."""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._safety_locks: dict[str, float] = {}

    async def get_coordinator_for_device(self, device_id: str):
        """Get coordinator for device ID."""
        domain_data = self.hass.data.get(DOMAIN, {})
        for coordinator in domain_data.values():
            if hasattr(coordinator, "device") and coordinator.device:
                if str(coordinator.config_entry.entry_id) == device_id:
                    return coordinator
        return None

    async def get_coordinators_for_entities(
        self, entity_ids: list[str]
    ) -> list[Any]:
        """Get coordinators for entity IDs."""
        coordinators = []
        entity_reg = er.async_get(self.hass)

        for entity_id in entity_ids:
            entity = entity_reg.async_get(entity_id)
            if entity and entity.config_entry_id:
                domain_data = self.hass.data.get(DOMAIN, {})
                coordinator = domain_data.get(entity.config_entry_id)
                if coordinator and coordinator not in coordinators:
                    coordinators.append(coordinator)

        return coordinators

    def extract_device_key(self, entity_id: str) -> str:
        """Extract device key from entity ID."""
        # switch.violet_pool_pump -> PUMP
        parts = entity_id.split(".")[-1].split("_")
        if "violet" in parts:
            parts.remove("violet")
        if "pool" in parts:
            parts.remove("pool")
        return "_".join(parts).upper()

    def check_safety_lock(self, device_key: str) -> bool:
        """Check if device has active safety lock."""
        if device_key not in self._safety_locks:
            return False
        import time

        return time.time() < self._safety_locks[device_key]

    def set_safety_lock(self, device_key: str, duration: int) -> None:
        """Set safety lock for device."""
        import time

        self._safety_locks[device_key] = time.time() + duration

    def get_remaining_lock_time(self, device_key: str) -> int:
        """Get remaining lock time in seconds."""
        if not self.check_safety_lock(device_key):
            return 0
        import time

        return int(self._safety_locks[device_key] - time.time())


# =============================================================================
# SERVICE HANDLERS
# =============================================================================


class VioletServiceHandlers:
    """Handles all service calls."""

    def __init__(self, manager: VioletServiceManager):
        self.manager = manager
        self.hass = manager.hass

    @staticmethod
    def _normalize_device_ids(raw: Any) -> list[str]:
        """Normalize a raw device id payload to a list of ids."""
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, Iterable):
            return [str(device) for device in raw]
        return [str(raw)]

    async def handle_control_pump(self, call: ServiceCall) -> None:
        """Handle pump control service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        action = call.data["action"]
        speed = call.data.get("speed", 2)
        duration = call.data.get("duration", 0)

        for coordinator in coordinators:
            try:
                result = {"success": True}  # Default result

                if action == "speed_control":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_ON,
                        duration=duration,
                        last_value=speed,
                    )
                    _LOGGER.info("Pump speed set to %d", speed)

                elif action == "force_off":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_OFF, duration=duration or 600
                    )
                    _LOGGER.info("Pump forced OFF for %ds", duration or 600)

                elif action == "eco_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_ON, duration=duration, last_value=1
                    )
                    _LOGGER.info("Pump ECO mode activated")

                elif action == "boost_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_ON, duration=duration, last_value=3
                    )
                    _LOGGER.info("Pump BOOST mode activated")

                elif action == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_AUTO
                    )
                    _LOGGER.info("Pump set to AUTO")

                if not result.get("success", True):
                    _LOGGER.warning(
                        "Pump action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("Pump control error: %s", err)
                raise HomeAssistantError(f"Pump control failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_smart_dosing(self, call: ServiceCall) -> None:
        """Handle smart dosing service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]
        duration = call.data.get("duration", 30)
        safety_override = call.data.get("safety_override", False)

        device_key = DOSING_TYPE_MAPPING.get(dosing_type)
        if not device_key:
            raise HomeAssistantError(f"Unknown dosing type: {dosing_type}")

        for coordinator in coordinators:
            try:
                # Safety check unless overridden
                if not safety_override:
                    if self.manager.check_safety_lock(device_key):
                        remaining = self.manager.get_remaining_lock_time(device_key)
                        raise HomeAssistantError(
                            f"Safety interval active: {remaining}s remaining"
                        )

                result = {"success": True}  # Default result

                if action == "manual_dose":
                    result = await coordinator.device.api.manual_dosing(
                        dosing_type, duration
                    )
                    _LOGGER.info("Manual dosing %s for %ds", dosing_type, duration)

                    # Set safety lock
                    if not safety_override:
                        safety_interval = DEVICE_PARAMETERS.get(device_key, {}).get(
                            "safety_interval", DEFAULT_SAFETY_INTERVAL
                        )
                        self.manager.set_safety_lock(device_key, safety_interval)

                elif action == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_AUTO
                    )
                    _LOGGER.info("Dosing %s set to AUTO", dosing_type)

                elif action == "stop":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF
                    )
                    _LOGGER.info("Dosing %s stopped", dosing_type)

                if not result.get("success", True):
                    _LOGGER.warning(
                        "Dosing action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("Smart dosing error: %s", err)
                raise HomeAssistantError(f"Dosing failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_manage_pv_surplus(self, call: ServiceCall) -> None:
        """Handle PV surplus management service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        mode = call.data["mode"]
        try:
            pump_speed = int(call.data.get("pump_speed", 2))
        except (TypeError, ValueError):
            pump_speed = 2
        pump_speed = min(3, max(1, pump_speed))

        for coordinator in coordinators:
            try:
                result = {"success": True}  # Default result

                if mode == "activate":
                    result = await coordinator.device.api.set_pv_surplus(
                        active=True, pump_speed=pump_speed
                    )
                    _LOGGER.info("PV surplus activated (speed %d)", pump_speed)

                elif mode == "deactivate":
                    result = await coordinator.device.api.set_pv_surplus(
                        active=False, pump_speed=pump_speed
                    )
                    _LOGGER.info("PV surplus deactivated")

                elif mode == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key="PVSURPLUS", action=ACTION_AUTO
                    )
                    _LOGGER.info("PV surplus set to AUTO")

                if not result.get("success", True):
                    _LOGGER.warning(
                        "PV surplus action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("PV surplus error: %s", err)
                raise HomeAssistantError(f"PV surplus failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_control_dmx_scenes(self, call: ServiceCall) -> None:
        """Handle DMX scene control service."""
        device_ids = self._normalize_device_ids(call.data[ATTR_DEVICE_ID])
        action = call.data["action"]
        sequence_delay = call.data.get("sequence_delay", 2)

        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if not coordinator:
                raise HomeAssistantError(f"Device not found: {device_id}")

            try:
                if action == "all_on":
                    result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                    _LOGGER.info("All DMX scenes ON (device %s)", device_id)

                elif action == "all_off":
                    result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLOFF)
                    _LOGGER.info("All DMX scenes OFF (device %s)", device_id)

                elif action == "all_auto":
                    result = await coordinator.device.api.set_all_dmx_scenes(
                        ACTION_ALLAUTO
                    )
                    _LOGGER.info("All DMX scenes AUTO (device %s)", device_id)

                elif action == "sequence":
                    scenes = [f"DMX_SCENE{i}" for i in range(1, 13)]
                    _LOGGER.info(
                        "Starting DMX sequence: %d scenes (device %s)",
                        len(scenes),
                        device_id,
                    )

                    for scene in scenes:
                        await coordinator.device.api.set_switch_state(scene, ACTION_ON)
                        await asyncio.sleep(sequence_delay)
                        await coordinator.device.api.set_switch_state(scene, ACTION_OFF)

                    result = {"success": True, "response": "Sequence completed"}

                elif action == "party_mode":
                    _LOGGER.info("Party mode activated! (device %s)", device_id)
                    await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                    await coordinator.device.api.set_light_color_pulse()
                    result = {"success": True, "response": "Party mode activated"}

                else:
                    raise HomeAssistantError(f"Unsupported DMX action: {action}")

                if not result.get("success", True):
                    _LOGGER.warning(
                        "DMX action failed for %s: %s",
                        device_id,
                        result.get("response", result),
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("DMX control error (%s): %s", device_id, err)
                raise HomeAssistantError(f"DMX control failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_set_light_color_pulse(self, call: ServiceCall) -> None:
        """Handle light color pulse service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        pulse_count = call.data.get("pulse_count", 1)
        pulse_interval = call.data.get("pulse_interval", 500)

        for coordinator in coordinators:
            try:
                _LOGGER.info(
                    "Starting %d color pulses (interval: %dms)",
                    pulse_count,
                    pulse_interval,
                )

                for i in range(pulse_count):
                    result = await coordinator.device.api.set_light_color_pulse()

                    if not result.get("success", True):
                        _LOGGER.warning(
                            "Pulse %d/%d failed: %s",
                            i + 1,
                            pulse_count,
                            result.get("response", result),
                        )

                    if i < pulse_count - 1:
                        await asyncio.sleep(pulse_interval / 1000)

                _LOGGER.info("Color pulse sequence completed (%d pulses)", pulse_count)

            except VioletPoolAPIError as err:
                _LOGGER.error("Color pulse error: %s", err)
                raise HomeAssistantError(f"Color pulse failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_manage_digital_rules(self, call: ServiceCall) -> None:
        """Handle digital rules management service."""
        device_ids = self._normalize_device_ids(call.data[ATTR_DEVICE_ID])
        rule_key = call.data["rule_key"]
        action = call.data["action"]

        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if not coordinator:
                raise HomeAssistantError(f"Device not found: {device_id}")

            try:
                if action == "trigger":
                    result = await coordinator.device.api.trigger_digital_input_rule(
                        rule_key
                    )
                    _LOGGER.info("Rule %s triggered (device %s)", rule_key, device_id)

                elif action == "lock":
                    result = await coordinator.device.api.set_digital_input_rule_lock(
                        rule_key, True
                    )
                    _LOGGER.info("Rule %s locked (device %s)", rule_key, device_id)

                elif action == "unlock":
                    result = await coordinator.device.api.set_digital_input_rule_lock(
                        rule_key, False
                    )
                    _LOGGER.info("Rule %s unlocked (device %s)", rule_key, device_id)

                else:
                    raise HomeAssistantError(f"Unsupported digital rule action: {action}")

                if not result.get("success", True):
                    _LOGGER.warning(
                        "Digital rule action failed for %s: %s",
                        device_id,
                        result.get("response", result),
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("Digital rule error (%s): %s", device_id, err)
                raise HomeAssistantError(f"Digital rule failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_test_output(self, call: ServiceCall) -> None:
        """Handle the output test service."""

        device_ids = self._normalize_device_ids(call.data[ATTR_DEVICE_ID])
        output = call.data["output"]
        mode = call.data.get("mode", "SWITCH")
        duration = call.data.get("duration", 120)

        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if not coordinator:
                raise HomeAssistantError(f"Device not found: {device_id}")

            try:
                result = await coordinator.device.api.set_output_test_mode(
                    output=output,
                    mode=mode,
                    duration=int(duration),
                )
                _LOGGER.info(
                    "Test mode for %s activated (%ds, mode %s, device %s)",
                    output,
                    duration,
                    mode,
                    device_id,
                )
                if not result.get("success", True):
                    _LOGGER.warning(
                        "Test mode could not be activated for %s: %s",
                        device_id,
                        result.get("response", result),
                    )
            except VioletPoolAPIError as err:
                _LOGGER.error("Test mode error (%s): %s", device_id, err)
                raise HomeAssistantError(f"Test mode failed: {err}") from err

            await coordinator.async_request_refresh()


# =============================================================================
# REGISTRATION
# =============================================================================


async def async_register_services(hass: HomeAssistant) -> None:
    """Register all Violet Pool services."""
    # Check if services already registered
    if hass.services.has_service(DOMAIN, "control_pump"):
        _LOGGER.debug("Services already registered")
        return

    _LOGGER.info("Registering Violet Pool services")

    # Create service manager
    manager = VioletServiceManager(hass)
    handlers = VioletServiceHandlers(manager)

    # Get schemas
    schemas = get_service_schemas()

    # Register services
    service_map = {
        "control_pump": handlers.handle_control_pump,
        "smart_dosing": handlers.handle_smart_dosing,
        "manage_pv_surplus": handlers.handle_manage_pv_surplus,
        "control_dmx_scenes": handlers.handle_control_dmx_scenes,
        "set_light_color_pulse": handlers.handle_set_light_color_pulse,
        "manage_digital_rules": handlers.handle_manage_digital_rules,
        "test_output": handlers.handle_test_output,
    }

    for service_name, handler in service_map.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    _LOGGER.info("Successfully registered %d services", len(service_map))