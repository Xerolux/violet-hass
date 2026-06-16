"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

from homeassistant.const import ATTR_DEVICE_ID
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
    DOMAIN,
)
from .http_control import VioletControlClient
from .service_helpers import (
    DEFAULT_SAFETY_INTERVAL,
    DOSING_API_MAPPING,
    DOSING_TYPE_MAPPING,
    as_device_id_list,
)

_LOGGER = logging.getLogger(__name__)

DOSING_INDEX_MAP = {
    "chlorine": 0,      # DOS_1_CL
    "electrolysis": 1,  # DOS_2_ELO
    "ph_minus": 3,      # DOS_4_PHM (index 2 is unused in firmware)
    "ph_plus": 4,       # DOS_5_PHP
    "flocculant": 5,    # DOS_6_FLOC
    "h2o2": 0,          # shares DOS_1_CL physical output, from_param=3 distinguishes it
}

DOSING_FROM_PARAM_MAP = {
    "h2o2": 3,          # H2O2 uses from=3; all others default to from=1
}

DOSING_SYSTEMS = {
    "chlorine": "DOSAGE_chlorine",
    "electrolysis": "DOSAGE_electrolysis",
    "ph_minus": "DOSAGE_phminus",
    "ph_plus": "DOSAGE_phplus",
    "flocculant": "DOSAGE_floc",
    "h2o2": "DOSAGE_h2o2",
}


class VioletControlServiceHandlers:
    """Handlers for control and action-oriented services."""

    manager: Any

    async def handle_control_pump(self, call: ServiceCall) -> None:
        """Handle pump control service."""
        coordinators = await self.manager.get_coordinators_for_call(call)
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
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]

        duration_raw = call.data.get("duration", 30)
        duration = InputSanitizer.validate_duration(
            duration_raw, min_sec=5, max_sec=300
        )

        safety_override = call.data.get("safety_override", False)

        _LOGGER.debug(
            "Smart dosing: type=%s, action=%s, duration=%d"
            " (raw: %s), safety_override=%s",
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
                    api_dosing_type = DOSING_API_MAPPING.get(
                        dosing_type, dosing_type
                    )
                    result = await coordinator.device.api.manual_dosing(
                        api_dosing_type, duration
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
                    api_dosing_type = DOSING_API_MAPPING.get(
                        dosing_type, dosing_type
                    )
                    result = await coordinator.device.api.set_dosage_enabled(
                        api_dosing_type, enabled=True
                    )
                    _LOGGER.info("Dosing %s set to AUTO (enabled)", dosing_type)

                elif action == "stop":
                    # DOS_* OFF is routed through /triggerManualDosing as
                    # DOSSTOP - stops a running manual dose without
                    # persistently disabling the channel in the config
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF
                    )
                    _LOGGER.info("Dosing %s stopped (DOSSTOP)", dosing_type)

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
        coordinators = await self.manager.get_coordinators_for_call(call)
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
        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
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

                    failed_scenes: list[str] = []
                    for scene in scenes:
                        r_on = await coordinator.device.api.set_switch_state(
                            key=scene, action=ACTION_ON
                        )
                        if r_on.get("success") is not True:
                            _LOGGER.warning(
                                "DMX scene %s ON failed: %s",
                                scene,
                                r_on.get("response"),
                            )
                            failed_scenes.append(scene)
                        await asyncio.sleep(sequence_delay)
                        r_off = await coordinator.device.api.set_switch_state(
                            key=scene, action=ACTION_OFF
                        )
                        if r_off.get("success") is not True:
                            _LOGGER.warning(
                                "DMX scene %s OFF failed: %s",
                                scene,
                                r_off.get("response"),
                            )

                    if failed_scenes:
                        result = {
                            "success": False,
                            "response": f"Sequence failed for: {', '.join(failed_scenes)}",
                        }
                    else:
                        result = {"success": True, "response": "Sequence completed"}

                elif action == "party_mode":
                    _LOGGER.info("Party mode activated! (device %s)", device_id)
                    r_dmx = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                    r_pulse = await coordinator.device.api.set_light_color_pulse()
                    if r_dmx.get("success") is True and r_pulse.get("success") is True:
                        result = {"success": True, "response": "Party mode activated"}
                    else:
                        result = {
                            "success": False,
                            "response": (
                                f"Party mode partially failed — "
                                f"DMX: {r_dmx.get('response')}, "
                                f"pulse: {r_pulse.get('response')}"
                            ),
                        }

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
        coordinators = await self.manager.get_coordinators_for_call(call)
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
        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
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
                        rule_key, locked=True
                    )
                    _LOGGER.info("Rule %s locked (device %s)", rule_key, device_id)

                elif action == "unlock":
                    result = await coordinator.device.api.set_digital_input_rule_lock(
                        rule_key, locked=False
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
        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
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

    # =================================================================
    # NEW HTTP-BASED CONTROL SERVICES (Direct setFunctionManually API)
    # =================================================================

    async def handle_control_pump_http(self, call: ServiceCall) -> None:
        """Control pump via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        speed = call.data.get("speed")
        action = call.data.get("action")
        force_off = call.data.get("force_off", False)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if force_off:
                    await control.set_pump_off()
                    _LOGGER.info("Pump forced OFF: %s", device_name)
                elif action == "off":
                    await control.set_pump_off()
                    _LOGGER.info("Pump turned OFF: %s", device_name)
                elif action == "on" or speed is not None:
                    rpm = speed if speed is not None else 1
                    await control.set_pump_speed(rpm)
                    _LOGGER.info("Pump set to RPM %d: %s", rpm, device_name)
                elif action == "eco":
                    await control.set_pump_speed(1)
                    _LOGGER.info("Pump ECO mode (RPM 1): %s", device_name)
                elif action == "boost":
                    await control.set_pump_speed(3)
                    _LOGGER.info("Pump BOOST mode (RPM 3): %s", device_name)

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Pump control error: %s", err)
                raise HomeAssistantError(f"Pump control failed: {err}")

    async def handle_control_heater_http(self, call: ServiceCall) -> None:
        """Control heater via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        target_temp = call.data.get("target_temperature")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if action == "on":
                    await control.set_heater_on()
                    _LOGGER.info("Heater turned ON: %s", device_name)
                elif action == "off":
                    await control.set_heater_off()
                    _LOGGER.info("Heater turned OFF: %s", device_name)

                if target_temp is not None:
                    await control.set_config({"HEATER_target_temp": target_temp})
                    _LOGGER.info(
                        "Heater target temp: %.1f°C on %s", target_temp, device_name
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Heater control error: %s", err)
                raise HomeAssistantError(f"Heater control failed: {err}")

    async def handle_control_solar_http(self, call: ServiceCall) -> None:
        """Control solar via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        target_temp = call.data.get("target_temperature")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if action == "on":
                    await control.set_solar_on()
                    _LOGGER.info("Solar turned ON: %s", device_name)
                elif action == "off":
                    await control.set_solar_off()
                    _LOGGER.info("Solar turned OFF: %s", device_name)

                if target_temp is not None:
                    await control.set_config({"SOLAR_target_temp": target_temp})
                    _LOGGER.info(
                        "Solar target temp: %.1f°C on %s", target_temp, device_name
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Solar control error: %s", err)
                raise HomeAssistantError(f"Solar control failed: {err}")

    async def handle_control_cover_http(self, call: ServiceCall) -> None:
        """Control cover via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action", "open")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if action == "open":
                    await control.set_cover_open()
                    _LOGGER.info("Cover OPEN: %s", device_name)
                elif action == "close":
                    await control.set_cover_close()
                    _LOGGER.info("Cover CLOSE: %s", device_name)
                elif action == "stop":
                    await control.set_cover_stop()
                    _LOGGER.info("Cover STOP: %s", device_name)

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Cover control error: %s", err)
                raise HomeAssistantError(f"Cover control failed: {err}")

    async def handle_control_backwash_http(self, call: ServiceCall) -> None:
        """Control backwash via HTTP setFunctionManually (NEW API).

        For 'run' action: automatically stops after specified duration.
        Duration is required for safety - prevents indefinite backwash.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        duration_seconds = call.data.get("duration_seconds")

        if action == "run" and duration_seconds is None:
            raise HomeAssistantError(
                "Backwash duration is required for safety. "
                "Specify duration_seconds (10-3600 seconds)"
            )

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if action == "run":
                    await control.set_backwash_run()
                    _LOGGER.info(
                        "Backwash started on %s with %ds timeout",
                        device_name,
                        duration_seconds,
                    )

                    # Auto-stop backwash after specified duration for safety
                    async def auto_stop_backwash() -> None:
                        await asyncio.sleep(duration_seconds)
                        try:
                            await control.set_backwash_abort()
                            _LOGGER.info(
                                "Backwash auto-stopped on %s after %ds",
                                device_name,
                                duration_seconds,
                            )
                            await coordinator.async_request_refresh()
                        except Exception as err:
                            _LOGGER.error("Backwash auto-stop failed: %s", err)

                    # Schedule through Home Assistant so the task is tracked by HA.
                    self.hass.async_create_task(
                        auto_stop_backwash(),
                        name=f"{DOMAIN}_auto_stop_backwash",
                    )

                elif action == "abort":
                    await control.set_backwash_abort()
                    _LOGGER.info("Backwash aborted on %s", device_name)
                    await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Backwash control error: %s", err)
                raise HomeAssistantError(f"Backwash control failed: {err}")

    async def handle_manual_dosing_http(self, call: ServiceCall) -> None:
        """Trigger manual dosing via HTTP (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        runtime = call.data.get("runtime_seconds", 30)

        dosing_index = DOSING_INDEX_MAP.get(dosing_system)
        if dosing_index is None:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        from_param = DOSING_FROM_PARAM_MAP.get(dosing_system, 1)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.trigger_manual_dosing(dosing_index, runtime, from_param=from_param)
                _LOGGER.info(
                    "Manual dosing: %s for %ds on %s",
                    dosing_system,
                    runtime,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing control error: %s", err)
                raise HomeAssistantError(f"Dosing control failed: {err}")

    async def handle_control_refill_http(self, call: ServiceCall) -> None:
        """Control water refill via HTTP setFunctionManually (NEW API).

        For 'fill' action: automatically stops after specified duration.
        Duration is REQUIRED for safety - prevents flooding/tank overflow.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        duration_seconds = call.data.get("duration_seconds")

        if action == "fill" and duration_seconds is None:
            raise HomeAssistantError(
                "Refill duration is REQUIRED for safety to prevent flooding! "
                "Specify duration_seconds (10-3600 seconds)"
            )

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                if action == "fill":
                    await control.set_function_manually("REFILL", "ON")
                    _LOGGER.critical(
                        "🚨 WATER REFILL STARTED on %s - WILL AUTO-STOP after %ds",
                        device_name,
                        duration_seconds,
                    )

                    # Auto-stop refill after specified duration for CRITICAL SAFETY
                    async def auto_stop_refill() -> None:
                        await asyncio.sleep(duration_seconds)
                        try:
                            await control.set_function_manually("REFILL", "OFF")
                            _LOGGER.critical(
                                "🚨 WATER REFILL AUTO-STOPPED on %s after %ds (OVERFLOW PREVENTED)",
                                device_name,
                                duration_seconds,
                            )
                            await coordinator.async_request_refresh()
                        except Exception as err:
                            _LOGGER.error("CRITICAL: Refill auto-stop FAILED: %s", err)

                    # Schedule through Home Assistant so the task is tracked by HA.
                    self.hass.async_create_task(
                        auto_stop_refill(),
                        name=f"{DOMAIN}_auto_stop_refill",
                    )

                elif action == "stop":
                    await control.set_function_manually("REFILL", "OFF")
                    _LOGGER.critical("WATER REFILL STOPPED on %s (manual)", device_name)
                    await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("CRITICAL: Refill control error: %s", err)
                raise HomeAssistantError(f"Refill control FAILED (FLOODING RISK): {err}")

    # =================================================================
    # DOSING SYSTEM CONFIGURATION SERVICES
    # =================================================================

    async def handle_configure_dosing(self, call: ServiceCall) -> None:
        """Configure dosing system parameters via setConfig."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        config_key = call.data.get("config_key")
        value = call.data.get("value")

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]
        full_key = f"{prefix}_{config_key}"

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({full_key: value})
                _LOGGER.info(
                    "Dosing config: %s = %s on %s",
                    full_key,
                    value,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing config error: %s", err)
                raise HomeAssistantError(f"Failed to update dosing config: {err}")

    async def handle_set_dosing_target(self, call: ServiceCall) -> None:
        """Set dosing system target value (ppm, pH, etc.)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        target_value = call.data.get("target_value")

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]
        key = (
            f"{prefix}_set_ppm"
            if dosing_system in ("chlorine", "electrolysis")
            else f"{prefix}_set_ph"
        )

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: target_value})
                _LOGGER.info(
                    "Dosing target: %s = %s on %s",
                    dosing_system,
                    target_value,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing target error: %s", err)
                raise HomeAssistantError(f"Failed to set dosing target: {err}")

    async def handle_set_dosing_daytime(self, call: ServiceCall) -> None:
        """Set dosing day/night mode times."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        day_start = call.data.get("day_start")  # HH:MM
        day_end = call.data.get("day_end")  # HH:MM

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]

        config_updates = {}
        if day_start:
            config_updates[f"{prefix}_daytime_on"] = day_start
        if day_end:
            config_updates[f"{prefix}_daytime_off"] = day_end

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config(config_updates)
                _LOGGER.info(
                    "Dosing daytime: %s (%s-%s) on %s",
                    dosing_system,
                    day_start or "unchanged",
                    day_end or "unchanged",
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing daytime error: %s", err)
                raise HomeAssistantError(f"Failed to set dosing daytime: {err}")

    async def handle_set_dosing_max_daily(self, call: ServiceCall) -> None:
        """Set maximum daily dosing amount."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        max_ml = call.data.get("max_daily_ml")

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]
        key = f"{prefix}_max_daily_ml"

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: max_ml})
                _LOGGER.info(
                    "Dosing max daily: %s = %d ml on %s",
                    dosing_system,
                    max_ml,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing max daily error: %s", err)
                raise HomeAssistantError(f"Failed to set dosing max daily: {err}")

    async def handle_enable_dosing(self, call: ServiceCall) -> None:
        """Enable/disable dosing system."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        enabled = call.data.get("enabled", True)

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]
        key = f"{prefix}_use"
        value = 1 if enabled else 0

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: value})
                state = "enabled" if enabled else "disabled"
                _LOGGER.info(
                    "Dosing %s: %s on %s",
                    dosing_system,
                    state,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing enable error: %s", err)
                raise HomeAssistantError(f"Failed to enable/disable dosing: {err}")

    # =================================================================
    # RULE MANAGEMENT SERVICES (All 4 Types: Temp, Analog, Switching, Timer)
    # =================================================================

    async def handle_configure_temp_rule(self, call: ServiceCall) -> None:
        """Configure temperature rule (TEMPRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = call.data.get("rule_id")  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"TEMPRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if (sensor1 := call.data.get("sensor_1")) is not None:
            config_updates[f"{prefix}_sensor_1"] = sensor1
        if (sensor2 := call.data.get("sensor_2")) is not None:
            config_updates[f"{prefix}_sensor_2"] = sensor2
        if (logic := call.data.get("logic")) is not None:
            config_updates[f"{prefix}_logic"] = logic
        if (diffval := call.data.get("diff_value")) is not None:
            config_updates[f"{prefix}_diffval"] = diffval
        if (hystval := call.data.get("hyst_value")) is not None:
            config_updates[f"{prefix}_hystval"] = hystval
        if (runtime_on := call.data.get("runtime_on")) is not None:
            config_updates[f"{prefix}_runtime_on"] = runtime_on
        if (runtime_off := call.data.get("runtime_off")) is not None:
            config_updates[f"{prefix}_runtime_off"] = runtime_off

        for i in range(1, 4):
            if (output := call.data.get(f"output_{i}")) is not None:
                config_updates[f"{prefix}_output_{i}"] = output
            if (state := call.data.get(f"output_{i}_state")) is not None:
                config_updates[f"{prefix}_output_{i}_state"] = state

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Temperature rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure temperature rule {rule_id}: {err}"
                )

    async def handle_configure_analog_rule(self, call: ServiceCall) -> None:
        """Configure analog input rule (ANALOGRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = call.data.get("rule_id")
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"ANALOGRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if (adc_input := call.data.get("adc_input")) is not None:
            config_updates[f"{prefix}_input"] = adc_input
        if (logic := call.data.get("logic")) is not None:
            config_updates[f"{prefix}_logic"] = logic
        if (threshold := call.data.get("threshold")) is not None:
            config_updates[f"{prefix}_value"] = threshold
        if (hyst := call.data.get("hysteresis")) is not None:
            config_updates[f"{prefix}_hyst"] = hyst
        if (runtime_on := call.data.get("runtime_on")) is not None:
            config_updates[f"{prefix}_runtime_on"] = runtime_on
        if (runtime_off := call.data.get("runtime_off")) is not None:
            config_updates[f"{prefix}_runtime_off"] = runtime_off

        for i in range(1, 4):
            if (output := call.data.get(f"output_{i}")) is not None:
                config_updates[f"{prefix}_output_{i}"] = output
            if (state := call.data.get(f"output_{i}_state")) is not None:
                config_updates[f"{prefix}_output_{i}_state"] = state

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Analog rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure analog rule {rule_id}: {err}"
                )

    async def handle_configure_switching_rule(
        self, call: ServiceCall
    ) -> None:
        """Configure switching input rule (SWITCHINGRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = call.data.get("rule_id")
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"SWITCHINGRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if (di_input := call.data.get("di_input")) is not None:
            config_updates[f"{prefix}_input"] = di_input
        if (contact := call.data.get("contact_type")) is not None:
            config_updates[f"{prefix}_contact"] = contact
        if (output := call.data.get("output")) is not None:
            config_updates[f"{prefix}_output"] = output
        if (action_on := call.data.get("action_on")) is not None:
            config_updates[f"{prefix}_action_on"] = action_on
        if (action_off := call.data.get("action_off")) is not None:
            config_updates[f"{prefix}_action_off"] = action_off
        if (timeout := call.data.get("timeout")) is not None:
            config_updates[f"{prefix}_timeout"] = timeout

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Switching rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure switching rule {rule_id}: {err}"
                )

    async def handle_configure_timer_rule(self, call: ServiceCall) -> None:
        """Configure timer rule (TIMERRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = call.data.get("rule_id")
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"TIMERRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if (on_time := call.data.get("on_time")) is not None:
            config_updates[f"{prefix}_on_time"] = on_time
        if (off_time := call.data.get("off_time")) is not None:
            config_updates[f"{prefix}_off_time"] = off_time
        if (weekdays := call.data.get("weekdays")) is not None:
            config_updates[f"{prefix}_on_weekdays"] = weekdays

        for i in range(1, 4):
            if (output := call.data.get(f"output_{i}")) is not None:
                config_updates[f"{prefix}_output_{i}"] = output
            if (state := call.data.get(f"output_{i}_state")) is not None:
                config_updates[f"{prefix}_output_{i}_state"] = state

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Timer rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure timer rule {rule_id}: {err}"
                )

    async def handle_enable_rule(self, call: ServiceCall) -> None:
        """Enable/disable any rule type."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_type = call.data.get("rule_type")
        rule_id = call.data.get("rule_id")
        enabled = call.data.get("enabled", True)

        valid_types = [
            "temprule",
            "analogrule",
            "switchingrule",
            "timerrule",
        ]
        if rule_type not in valid_types:
            raise HomeAssistantError(f"Invalid rule type: {rule_type}")
        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        key = f"{rule_type.upper()}_{rule_id}_prog_use"
        value = 1 if enabled else 0

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config({key: value})
                state = "enabled" if enabled else "disabled"
                _LOGGER.info(
                    "Rule %s_%d %s on %s",
                    rule_type,
                    rule_id,
                    state,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to enable/disable rule: {err}"
                )

    # PHASE 4: SYSTEM CONFIGURATION SERVICES

    async def handle_control_extension_relay(self, call: ServiceCall) -> None:
        """Control extension relay outputs (EXT1_1 to EXT8_8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        relay_id = call.data.get("relay_id")

        if not 1 <= relay_id <= 8:
            raise HomeAssistantError(f"Relay ID must be 1-8, got {relay_id}")

        action = call.data.get("action", "on")
        state = call.data.get("state")
        duration = call.data.get("duration", 0)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if state is not None:
                    await control.set_function_manually(
                        f"EXT{relay_id}_1", state, duration
                    )
                    _LOGGER.info(
                        "Extension relay EXT%d_1 set to state %d on %s",
                        relay_id,
                        state,
                        coordinator.device.device_name,
                    )
                elif action == "on":
                    await control.set_function_manually(
                        f"EXT{relay_id}_1", 4, duration
                    )
                    _LOGGER.info(
                        "Extension relay EXT%d_1 turned ON on %s",
                        relay_id,
                        coordinator.device.device_name,
                    )
                elif action == "off":
                    await control.set_function_manually(
                        f"EXT{relay_id}_1", 6, duration
                    )
                    _LOGGER.info(
                        "Extension relay EXT%d_1 turned OFF on %s",
                        relay_id,
                        coordinator.device.device_name,
                    )
                elif action == "toggle":
                    await control.set_function_manually(
                        f"EXT{relay_id}_1", 0, duration
                    )
                    _LOGGER.info(
                        "Extension relay EXT%d_1 toggled on %s",
                        relay_id,
                        coordinator.device.device_name,
                    )

                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to control extension relay EXT{relay_id}_1: {err}"
                )

    async def handle_configure_sensor_calibration(
        self, call: ServiceCall
    ) -> None:
        """Configure sensor calibration offsets and multipliers."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        sensor_id = call.data.get("sensor_id")

        if not 1 <= sensor_id <= 12:
            raise HomeAssistantError(f"Sensor ID must be 1-12, got {sensor_id}")

        config_updates = {}

        if offset := call.data.get("offset"):
            config_updates[f"SENSOR_{sensor_id}_offset"] = offset
        if multiplier := call.data.get("multiplier"):
            config_updates[f"SENSOR_{sensor_id}_multiplier"] = multiplier
        if min_value := call.data.get("min_value"):
            config_updates[f"SENSOR_{sensor_id}_min"] = min_value
        if max_value := call.data.get("max_value"):
            config_updates[f"SENSOR_{sensor_id}_max"] = max_value

        if not config_updates:
            raise HomeAssistantError("No calibration parameters specified")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Sensor %d calibration configured on %s",
                    sensor_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure sensor {sensor_id} calibration: {err}"
                )
