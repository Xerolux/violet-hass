"""Service handlers for the Violet Pool Controller integration - WITH INPUT SANITIZATION.

Note on Validation:
    Service schemas use `vol.Coerce(int)` combined with `vol.Range()` for numeric inputs.
    This ensures that values passed from automations (which might be strings) are correctly
    converted to integers before use. This differs from the config flow, which uses
    `selector.NumberSelector` to provide a rich UI, as service calls are often programmatic.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Iterable

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .api import VioletPoolAPIError
from .const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
    DEVICE_PARAMETERS,
    DOMAIN,
)
from .utils_sanitizer import InputSanitizer

_LOGGER = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================


# Common validators
def _as_device_id_list(value: Any) -> list[str]:
    """
    Normalize raw device id input into a list of strings.

    Args:
        value: The raw device ID input (string or list).

    Returns:
        A list of device ID strings.
    """
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
    """
    Get all service schemas.

    Returns:
        A dictionary mapping service names to schemas.
    """
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
                vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 8)]),
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
        # Diagnostic Log Export
        "export_diagnostic_logs": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Optional("lines", default=100): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=10000)
                ),
                vol.Optional("include_timestamps", default=True): cv.boolean,
                vol.Optional("include_config", default=True): cv.boolean,
                vol.Optional("include_history", default=True): cv.boolean,
                vol.Optional("include_states", default=True): cv.boolean,
                vol.Optional("include_raw_data", default=True): cv.boolean,
                vol.Optional("save_to_file", default=False): cv.boolean,
            }
        ),
    }


# =============================================================================
# SERVICE MANAGER
# =============================================================================


class VioletServiceManager:
    """Manages all Violet Pool Controller services."""

    def __init__(self, hass: HomeAssistant):
        """
        Initialize the service manager.

        Args:
            hass: The Home Assistant instance.
        """
        self.hass = hass
        self._safety_locks: dict[str, float] = {}

    async def get_coordinator_for_device(self, device_id: str):
        """
        Get coordinator for device ID.

        Args:
            device_id: The device ID.

        Returns:
            The coordinator instance or None.
        """
        domain_data = self.hass.data.get(DOMAIN, {})

        # 1. Check if device_id is directly a config_entry_id (legacy/direct usage)
        for coordinator in domain_data.values():
            if hasattr(coordinator, "device") and coordinator.device:
                if str(coordinator.config_entry.entry_id) == device_id:
                    return coordinator

        # 2. Check if device_id is a device registry ID
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(device_id)

        if device:
            for config_entry_id in device.config_entries:
                coordinator = domain_data.get(config_entry_id)
                if coordinator and hasattr(coordinator, "device") and coordinator.device:
                    return coordinator

        return None

    async def get_coordinators_for_entities(self, entity_ids: list[str]) -> list[Any]:
        """
        Get coordinators for entity IDs.

        Args:
            entity_ids: A list of entity IDs.

        Returns:
            A list of coordinator instances.
        """
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
        """
        Extract device key from entity ID.

        Args:
            entity_id: The entity ID.

        Returns:
            The device key.

        Raises:
            ValueError: If entity_id is invalid or cannot be parsed.
        """
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError(f"Invalid entity_id: {entity_id}")

        if "." not in entity_id:
            raise ValueError(
                f"Entity ID must contain domain separator '.': {entity_id}"
            )

        # switch.violet_pool_pump -> PUMP
        parts = entity_id.split(".")[-1].split("_")

        # Remove common prefixes (filter out all occurrences)
        parts = [p for p in parts if p not in ("violet", "pool")]

        if not parts:
            raise ValueError(
                f"Cannot extract device key from {entity_id}: no parts remaining"
            )

        return "_".join(parts).upper()

    def check_safety_lock(self, device_key: str) -> bool:
        """
        Check if device has active safety lock.

        Args:
            device_key: The device key.

        Returns:
            True if locked, False otherwise.
        """
        if device_key not in self._safety_locks:
            return False

        return time.time() < self._safety_locks[device_key]

    def set_safety_lock(self, device_key: str, duration: int) -> None:
        """
        Set safety lock for device.

        Args:
            device_key: The device key.
            duration: The duration in seconds.
        """
        self._safety_locks[device_key] = time.time() + duration

    def get_remaining_lock_time(self, device_key: str) -> int:
        """
        Get remaining lock time in seconds.

        Args:
            device_key: The device key.

        Returns:
            Remaining time in seconds.
        """
        if not self.check_safety_lock(device_key):
            return 0

        return int(self._safety_locks[device_key] - time.time())


# =============================================================================
# SERVICE HANDLERS
# =============================================================================


class VioletServiceHandlers:
    """Handles all service calls."""

    def __init__(self, manager: VioletServiceManager):
        """
        Initialize service handlers.

        Args:
            manager: The service manager instance.
        """
        self.manager = manager
        self.hass = manager.hass

    @staticmethod
    def _normalize_device_ids(raw: Any) -> list[str]:
        """
        Normalize a raw device id payload to a list of ids.

        Args:
            raw: The raw device ID input.

        Returns:
            A list of device IDs.
        """
        # Use the module-level function to avoid duplication
        return _as_device_id_list(raw)

    async def handle_control_pump(self, call: ServiceCall) -> None:
        """
        Handle pump control service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails.
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        action = call.data["action"]

        # ✅ INPUT SANITIZATION: Validiere speed und duration
        speed_raw = call.data.get("speed", 2)
        duration_raw = call.data.get("duration", 0)

        speed = InputSanitizer.validate_speed(speed_raw, min_speed=1, max_speed=3)
        duration = InputSanitizer.validate_duration(
            duration_raw, min_sec=0, max_sec=86400
        )

        _LOGGER.debug(
            "Pump control: action=%s, speed=%d (raw: %s), duration=%d (raw: %s)",
            action,
            speed,
            speed_raw,
            duration,
            duration_raw,
        )

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
                    _LOGGER.info("Pump speed set to %d (sanitized)", speed)

                elif action == "force_off":
                    safe_duration = duration or 600
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_OFF, duration=safe_duration
                    )
                    _LOGGER.info("Pump forced OFF for %ds (sanitized)", safe_duration)

                elif action == "eco_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_ON, duration=duration, last_value=1
                    )
                    _LOGGER.info("Pump ECO mode activated (duration: %ds)", duration)

                elif action == "boost_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_ON, duration=duration, last_value=3
                    )
                    _LOGGER.info("Pump BOOST mode activated (duration: %ds)", duration)

                elif action == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP", action=ACTION_AUTO
                    )
                    _LOGGER.info("Pump set to AUTO")

                if result.get("success") is not True:
                    _LOGGER.warning(
                        "Pump action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("Pump control error: %s", err)
                raise HomeAssistantError(f"Pump control failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_smart_dosing(self, call: ServiceCall) -> None:
        """
        Handle smart dosing service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails or type is unknown.
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]

        # ✅ INPUT SANITIZATION: Validiere duration (max 300s für Dosierung)
        duration_raw = call.data.get("duration", 30)
        duration = InputSanitizer.validate_duration(
            duration_raw, min_sec=5, max_sec=300
        )

        safety_override = call.data.get("safety_override", False)

        _LOGGER.debug(
            "Smart dosing: type=%s, action=%s, duration=%d (raw: %s), safety_override=%s",
            dosing_type,
            action,
            duration,
            duration_raw,
            safety_override,
        )

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
                    _LOGGER.info(
                        "Manual dosing %s for %ds (sanitized)", dosing_type, duration
                    )

                    # Set safety lock
                    if not safety_override:
                        from typing import cast

                        safety_interval = cast(
                            int,
                            DEVICE_PARAMETERS.get(device_key, {}).get(
                                "safety_interval", DEFAULT_SAFETY_INTERVAL
                            ),
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

                if result.get("success") is not True:
                    _LOGGER.warning(
                        "Dosing action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("Smart dosing error: %s", err)
                raise HomeAssistantError(f"Dosing failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_manage_pv_surplus(self, call: ServiceCall) -> None:
        """
        Handle PV surplus management service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails.
        """
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

                if result.get("success") is not True:
                    _LOGGER.warning(
                        "PV surplus action failed: %s", result.get("response", result)
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("PV surplus error: %s", err)
                raise HomeAssistantError(f"PV surplus failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_control_dmx_scenes(self, call: ServiceCall) -> None:
        """
        Handle DMX scene control service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails or is unsupported.
        """
        device_ids = self._normalize_device_ids(call.data[ATTR_DEVICE_ID])
        action = call.data["action"]
        sequence_delay = call.data.get("sequence_delay", 2)

        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if not coordinator:
                raise HomeAssistantError(f"Device not found: {device_id}")

            try:
                if action == "all_on":
                    result = await coordinator.device.api.set_all_dmx_scenes(
                        ACTION_ALLON
                    )
                    _LOGGER.info("All DMX scenes ON (device %s)", device_id)

                elif action == "all_off":
                    result = await coordinator.device.api.set_all_dmx_scenes(
                        ACTION_ALLOFF
                    )
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

                if result.get("success") is not True:
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
        """
        Handle light color pulse service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails.
        """
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

                    if result.get("success") is not True:
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
        """
        Handle digital rules management service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails or is unsupported.
        """
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
                    raise HomeAssistantError(
                        f"Unsupported digital rule action: {action}"
                    )

                if result.get("success") is not True:
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
        """
        Handle the output test service.

        Args:
            call: The service call object.

        Raises:
            HomeAssistantError: If the action fails.
        """

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
                if result.get("success") is not True:
                    _LOGGER.warning(
                        "Test mode could not be activated for %s: %s",
                        device_id,
                        result.get("response", result),
                    )
            except VioletPoolAPIError as err:
                _LOGGER.error("Test mode error (%s): %s", device_id, err)
                raise HomeAssistantError(f"Test mode failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_export_diagnostic_logs(self, call: ServiceCall) -> dict[str, Any]:
        """
        Handle the export diagnostic logs service.

        This service collects recent integration logs and optionally saves them to a file.

        Args:
            call: The service call object.

        Returns:
            A text response containing the exported logs.

        Raises:
            HomeAssistantError: If the export fails.
        """
        import os
        from datetime import datetime

        device_ids = self._normalize_device_ids(call.data[ATTR_DEVICE_ID])
        lines = call.data.get("lines", 100)
        include_timestamps = call.data.get("include_timestamps", True)
        include_config = call.data.get("include_config", True)
        include_history = call.data.get("include_history", True)
        include_states = call.data.get("include_states", True)
        include_raw_data = call.data.get("include_raw_data", True)
        save_to_file = call.data.get("save_to_file", False)

        # Validate lines parameter
        lines = max(10, min(10000, int(lines)))

        # Get coordinator for device info
        coordinator = None
        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if coordinator:
                break

        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_ids[0]}")

        try:
            # Get logs from Home Assistant's logging system
            # We'll collect recent logs related to this integration
            log_entries = []
            device_name = coordinator.device.device_name

            # Read from the main log file if available
            log_path = self.hass.config.path("home-assistant.log")
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read last N lines
                        all_lines = f.readlines()
                        # Filter for violet-related entries
                        violet_lines = [
                            line for line in all_lines
                            if 'violet_pool_controller' in line.lower()
                        ]
                        # Take last N lines
                        recent_lines = violet_lines[-lines:] if len(violet_lines) > lines else violet_lines

                        for line in recent_lines:
                            if include_timestamps:
                                log_entries.append(line.rstrip())
                            else:
                                # Remove timestamp (format: [2026-02-24 17:35:23.304] ...)
                                import re
                                cleaned = re.sub(r'^\[?\d{4}-\d{2}-\d{2}[^]]*\]?\s*', '', line)
                                log_entries.append(cleaned.rstrip())

                except Exception as e:
                    _LOGGER.warning("Could not read log file: %s", e)

            # If no logs found, provide system information
            if not log_entries:
                log_entries.append("=== Violet Pool Controller Diagnostic Export ===")
                log_entries.append(f"Device: {device_name}")
                log_entries.append(f"Timestamp: {datetime.now().isoformat()}")
                log_entries.append("")
                log_entries.append("Controller Information:")
                log_entries.append(f"  Name: {coordinator.device.controller_name}")
                log_entries.append(f"  API URL: {coordinator.device.api_url}")
                log_entries.append(f"  Device ID: {coordinator.device.device_id}")
                log_entries.append(f"  Available: {coordinator.device.available}")
                log_entries.append(f"  Firmware: {coordinator.device.firmware_version or 'Unknown'}")
                log_entries.append(f"  Last Update: {coordinator.device.last_event_age:.1f}s ago")
                log_entries.append(f"  Connection Latency: {coordinator.device.connection_latency:.1f}ms")
                log_entries.append(f"  System Health: {coordinator.device.system_health:.0f}%")
                log_entries.append(f"  Update Counter: {coordinator.device._update_counter}")
                log_entries.append(f"  Consecutive Failures: {coordinator.device.consecutive_failures}")
                log_entries.append("")

                # Add Configuration Information
                if include_config and hasattr(coordinator, "config_entry") and coordinator.config_entry:
                    from .const import (
                        CONF_POLLING_INTERVAL,
                        CONF_TIMEOUT_DURATION,
                        CONF_RETRY_ATTEMPTS,
                        CONF_FORCE_UPDATE,
                        CONF_USE_SSL,
                        CONF_VERIFY_SSL,
                        CONF_POOL_SIZE,
                        CONF_POOL_TYPE,
                        CONF_DISINFECTION_METHOD,
                        CONF_ACTIVE_FEATURES,
                        CONF_SELECTED_SENSORS,
                        CONF_PASSWORD
                    )

                    config = coordinator.config_entry.data
                    log_entries.append("Configuration Settings:")

                    # Safe keys to export directly
                    safe_keys = {
                        "Polling Interval": CONF_POLLING_INTERVAL,
                        "Timeout": CONF_TIMEOUT_DURATION,
                        "Retries": CONF_RETRY_ATTEMPTS,
                        "Force Update": CONF_FORCE_UPDATE,
                        "Use SSL": CONF_USE_SSL,
                        "Verify SSL": CONF_VERIFY_SSL,
                        "Pool Size": CONF_POOL_SIZE,
                        "Pool Type": CONF_POOL_TYPE,
                        "Disinfection": CONF_DISINFECTION_METHOD,
                    }

                    for label, key in safe_keys.items():
                        if key in config:
                            log_entries.append(f"  {label}: {config[key]}")

                    # Handle lists (features/sensors)
                    if CONF_ACTIVE_FEATURES in config:
                        features = config[CONF_ACTIVE_FEATURES]
                        if isinstance(features, list):
                            log_entries.append(f"  Active Features: {len(features)} enabled")
                            # Optional: list them if not too long
                            # log_entries.append(f"    {', '.join(features)}")

                    if CONF_SELECTED_SENSORS in config:
                        sensors = config[CONF_SELECTED_SENSORS]
                        if isinstance(sensors, list):
                            log_entries.append(f"  Selected Sensors: {len(sensors)} enabled")

                    log_entries.append("")

                # Polling History
                if include_history and hasattr(coordinator.device, "_first_poll") and coordinator.device._first_poll:
                    log_entries.append("Polling History:")
                    log_entries.append(f"  First Poll: {coordinator.device._first_poll.strftime('%Y-%m-%d %H:%M:%S')}")

                    if hasattr(coordinator.device, "_poll_history") and coordinator.device._poll_history:
                        history = list(coordinator.device._poll_history)
                        log_entries.append(f"  Last {len(history)} Polls:")
                        for item in history:
                            if len(item) == 4:
                                timestamp, count, latency, snapshot = item
                                details = []
                                # Fixed order for consistency
                                for key in ["Pool Temp", "Redox", "pH", "Chlorine", "Overflow", "Flow", "Inflow"]:
                                    if key in snapshot:
                                        details.append(f"{key}: {snapshot[key]}")

                                detail_str = " | ".join(details)
                                log_entries.append(f"    - {timestamp.strftime('%H:%M:%S')}: {count} items ({latency:.1f}ms) -> {detail_str}")
                            else:
                                timestamp, count, latency = item
                                log_entries.append(f"    - {timestamp.strftime('%H:%M:%S')}: {count} items ({latency:.1f}ms)")
                    else:
                        log_entries.append("  No history available.")
                    log_entries.append("")

                # Entity States
                if include_states:
                    try:
                        if hasattr(coordinator, "config_entry") and coordinator.config_entry:
                            entry_id = coordinator.config_entry.entry_id
                            registry = er.async_get(self.hass)
                            entities = er.async_entries_for_config_entry(registry, entry_id)

                            if entities:
                                log_entries.append("Entity States:")
                                sorted_entities = sorted(entities, key=lambda e: e.entity_id)

                                for entity in sorted_entities:
                                    state = self.hass.states.get(entity.entity_id)
                                    if state:
                                        # Limit attribute output to avoid massive logs
                                        attrs = dict(state.attributes)
                                        attr_str = str(attrs)
                                        if len(attr_str) > 200:
                                            attr_str = attr_str[:197] + "..."

                                        log_entries.append(f"  - {entity.entity_id}: {state.state} (attrs: {attr_str})")
                                    else:
                                        log_entries.append(f"  - {entity.entity_id}: <No State>")
                                log_entries.append("")
                    except Exception as e:
                        _LOGGER.warning("Could not dump entity states: %s", e)
                        log_entries.append(f"Error dumping entity states: {e}")
                        log_entries.append("")

                # Raw Data Dump
                if include_raw_data:
                    try:
                        import json
                        if hasattr(coordinator, "data") and coordinator.data:
                            log_entries.append("Latest Raw Data:")

                            # Deep copy and redact
                            raw_data = dict(coordinator.data)
                            sensitive_keys = ["wifi_password", "password", "key", "token", "secret"]

                            redacted_data = {}
                            for key, value in raw_data.items():
                                lower_key = str(key).lower()
                                if any(sensitive in lower_key for sensitive in sensitive_keys):
                                    redacted_data[key] = "***REDACTED***"
                                else:
                                    redacted_data[key] = value

                            json_str = json.dumps(redacted_data, indent=2, default=str, sort_keys=True)
                            log_entries.append(json_str)
                            log_entries.append("")
                    except Exception as e:
                        _LOGGER.warning("Could not dump raw data: %s", e)
                        log_entries.append(f"Error dumping raw data: {e}")
                        log_entries.append("")

                log_entries.append("No detailed log entries found in home-assistant.log.")
                log_entries.append("Logs may have been rotated or not contain recent entries.")

                # Check log level
                try:
                    logger = logging.getLogger("custom_components.violet_pool_controller")
                    level = logger.getEffectiveLevel()
                    if level > logging.DEBUG:
                        log_entries.append("")
                        log_entries.append("NOTE: Debug logging is currently disabled.")
                        log_entries.append("To see more details, enable debug logging for this integration.")
                except Exception:
                    pass

            # Create export text
            export_header = f"""
{'='*80}
Violet Pool Controller - Diagnostic Log Export
{'='*80}
Device: {device_name}
Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Lines: {len(log_entries)}
{'='*80}
"""

            export_text = export_header + "\n".join(log_entries)

            # Save to file if requested
            if save_to_file:
                filename = f"violet_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = f"/config/{filename}"

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(export_text)

                    _LOGGER.info(
                        "Diagnostic logs exported to file: %s (%d lines)",
                        filename,
                        len(log_entries)
                    )

                    # Also return the content
                    return {
                        "success": True,
                        "filename": filename,
                        "filepath": filepath,
                        "lines_exported": len(log_entries),
                        "message": f"Logs saved to {filename} ({len(log_entries)} lines)"
                    }
                except Exception as e:
                    _LOGGER.error("Failed to save log file: %s", e)
                    raise HomeAssistantError(f"Failed to save log file: {e}") from e
            else:
                # Return as service response
                _LOGGER.info(
                    "Diagnostic logs exported: %d lines for device %s",
                    len(log_entries),
                    device_name
                )

                return {
                    "success": True,
                    "lines_exported": len(log_entries),
                    "logs": export_text,
                    "message": f"Exported {len(log_entries)} log lines"
                }

        except Exception as err:
            _LOGGER.error("Log export error: %s", err)
            raise HomeAssistantError(f"Log export failed: {err}") from err


# =============================================================================
# REGISTRATION
# =============================================================================


async def async_register_services(hass: HomeAssistant) -> None:
    """
    Register all Violet Pool services.

    Args:
        hass: The Home Assistant instance.
    """
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
    # Regular services (no return value)
    regular_services = {
        "control_pump": handlers.handle_control_pump,
        "smart_dosing": handlers.handle_smart_dosing,
        "manage_pv_surplus": handlers.handle_manage_pv_surplus,
        "control_dmx_scenes": handlers.handle_control_dmx_scenes,
        "set_light_color_pulse": handlers.handle_set_light_color_pulse,
        "manage_digital_rules": handlers.handle_manage_digital_rules,
        "test_output": handlers.handle_test_output,
    }

    for service_name, handler in regular_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # Services returning data
    hass.services.async_register(
        DOMAIN,
        "export_diagnostic_logs",
        handlers.handle_export_diagnostic_logs,
        schema=schemas.get("export_diagnostic_logs"),
        supports_response=SupportsResponse.ONLY,
    )

    _LOGGER.info(
        "Successfully registered %d services",
        len(regular_services) + 1,
    )
