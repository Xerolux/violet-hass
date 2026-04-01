"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

from violet_poolcontroller_api.api import VioletPoolAPIError
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

from .const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
    DEVICE_PARAMETERS,
)
from .service_helpers import DEFAULT_SAFETY_INTERVAL, DOSING_TYPE_MAPPING

_LOGGER = logging.getLogger(__name__)


class VioletControlServiceHandlers:
    """Handlers for control and action-oriented services."""

    manager: Any

    async def handle_control_pump(self, call: ServiceCall) -> None:
        """Handle pump control service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        action = call.data["action"]

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
                result = {"success": True}

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
        """Handle smart dosing service."""
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]

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
                if not safety_override and self.manager.check_safety_lock(device_key):
                    remaining = self.manager.get_remaining_lock_time(device_key)
                    raise HomeAssistantError(
                        f"Safety interval active: {remaining}s remaining"
                    )

                result = {"success": True}

                if action == "manual_dose":
                    result = await coordinator.device.api.manual_dosing(
                        dosing_type, duration
                    )
                    _LOGGER.info(
                        "Manual dosing %s for %ds (sanitized)", dosing_type, duration
                    )

                    if not safety_override:
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
                result = {"success": True}

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
