"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api.api import VioletPoolAPIError
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

from ..const import (
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
)
from ..http_control import VioletControlClient
from ..service_helpers import (
    DEFAULT_SAFETY_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

DOSING_INDEX_MAP = {
    "chlorine": 0,  # DOS_1_CL
    "electrolysis": 1,  # DOS_2_ELO
    "ph_minus": 3,  # DOS_4_PHM (index 2 is unused in firmware)
    "ph_plus": 4,  # DOS_5_PHP
    "flocculant": 5,  # DOS_6_FLOC
    "h2o2": 0,  # shares DOS_1_CL physical output, from_param=3 distinguishes it
}

DOSING_FROM_PARAM_MAP = {
    "h2o2": 3,  # H2O2 uses from=3; all others default to from=1
}

DOSING_SYSTEMS = {
    "chlorine": "DOSAGE_chlorine",
    "electrolysis": "DOSAGE_electrolysis",
    "ph_minus": "DOSAGE_phminus",
    "ph_plus": "DOSAGE_phplus",
    "flocculant": "DOSAGE_floc",
    "h2o2": "DOSAGE_h2o2",
}

# Maps dosing-system slug -> physical controller switch key, used to key the
# SafetyGuard cooldown for the *_http dosing services.
DOSING_SYSTEM_TO_KEY = {
    "chlorine": "DOS_1_CL",
    "electrolysis": "DOS_2_ELO",
    "ph_minus": "DOS_4_PHM",
    "ph_plus": "DOS_5_PHP",
    "flocculant": "DOS_6_FLOC",
    "h2o2": "DOS_1_CL",
}



class PumpServiceHandlersMixin:
    """Mixin for pump services."""

    async def handle_control_pump(self, call: ServiceCall) -> None:
        """Handle pump control service."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data["action"]

        speed_raw = call.data.get("speed", 2)
        duration_raw = call.data.get("duration", 0)

        speed = InputSanitizer.validate_speed(speed_raw, min_speed=1, max_speed=3)
        duration = InputSanitizer.validate_duration(duration_raw, min_sec=0, max_sec=86400)

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
                result: dict[str, Any] = {"success": False}

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
                    _LOGGER.warning("Pump action failed: %s", result.get("response", result))

            except VioletPoolAPIError as err:
                _LOGGER.error("Pump control error: %s", err)
                raise HomeAssistantError(f"Pump control failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_control_pump_http(self, call: ServiceCall) -> None:
        """Control pump via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        speed = call.data.get("speed")
        action = call.data.get("action")
        force_off = call.data.get("force_off", False)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                if force_off:
                    await control.set_pump_off()
                    _LOGGER.info("Pump forced OFF: %s", device_name)
                elif action == "off":
                    await control.set_pump_off()
                    _LOGGER.info("Pump turned OFF: %s", device_name)
                elif action == "eco":
                    await control.set_pump_speed(1)
                    _LOGGER.info("Pump ECO mode (RPM 1): %s", device_name)
                elif action == "boost":
                    await control.set_pump_speed(3)
                    _LOGGER.info("Pump BOOST mode (RPM 3): %s", device_name)
                elif action == "on" or speed is not None:
                    rpm = speed if speed is not None else 1
                    await control.set_pump_speed(rpm)
                    _LOGGER.info("Pump set to RPM %d: %s", rpm, device_name)

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Pump control error: %s", err)
                raise HomeAssistantError(f"Pump control failed: {err}")

    async def handle_control_backwash_http(self, call: ServiceCall) -> None:
        """Control backwash via HTTP setFunctionManually (NEW API).

        For 'run' action: automatically stops after specified duration.
        Duration is required for safety - prevents indefinite backwash.
        The auto-stop timer is persisted so it survives a HA restart.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        duration_seconds = call.data.get("duration_seconds")
        safety_override = bool(call.data.get("safety_override", False))

        if action == "run" and (duration_seconds is None or float(duration_seconds) <= 0):
            raise HomeAssistantError(
                "Backwash duration is required for safety. "
                "Specify duration_seconds (10-3600 seconds)"
            )
        backwash_seconds = float(duration_seconds or 0)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                if action == "run":
                    # Enforce cooldown before starting backwash.
                    await self.manager.safety_guard.enforce(
                        "BACKWASH", safety_override=safety_override
                    )

                    await control.set_backwash_run()
                    _LOGGER.info(
                        "Backwash started on %s with %ss timeout",
                        device_name,
                        backwash_seconds,
                    )

                    # Restart-safe auto-stop: persists deadline so the backwash
                    # is aborted even if HA restarts mid-run.
                    await self.manager.safety_guard.arm_auto_stop(
                        "BACKWASH",
                        duration_seconds=backwash_seconds,
                        stop_target={
                            "method": "set_function_manually",
                            "args": ["BACKWASH", "OFF"],
                        },
                    )
                    if not safety_override:
                        self.manager.set_safety_lock("BACKWASH", DEFAULT_SAFETY_INTERVAL)

                elif action == "abort":
                    await control.set_backwash_abort()
                    # Cancel any pending auto-stop and clear the cooldown.
                    self.manager.safety_guard.cancel_auto_stop("BACKWASH")
                    self.manager.safety_guard.clear_lock("BACKWASH")
                    _LOGGER.info("Backwash aborted on %s", device_name)
                    await coordinator.async_request_refresh()

            except VioletPoolAPIError as err:
                _LOGGER.error("Backwash control error: %s", err)
                raise HomeAssistantError(f"Backwash control failed: {err}") from err
            except HomeAssistantError:
                raise
            except Exception as err:
                _LOGGER.error("Backwash control error: %s", err)
                raise HomeAssistantError(f"Backwash control failed: {err}") from err

