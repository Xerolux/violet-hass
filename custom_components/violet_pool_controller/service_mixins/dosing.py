"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any, cast

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api.api import VioletPoolAPIError
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

from ..const import (
    ACTION_OFF,
    DEVICE_PARAMETERS,
)
from ..http_control import VioletControlClient
from ..service_helpers import (
    DEFAULT_SAFETY_INTERVAL,
    DOSING_API_MAPPING,
    DOSING_TYPE_MAPPING,
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



class DosingServiceHandlersMixin:
    """Mixin for dosing services."""

    async def handle_smart_dosing(self, call: ServiceCall) -> None:
        """Handle smart dosing service."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]

        duration_raw = call.data.get("duration", 30)
        duration = InputSanitizer.validate_duration(duration_raw, min_sec=5, max_sec=300)

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
                # Enforce cooldown via central SafetyGuard.  ``enforce`` raises
                # HomeAssistantError when the lock is active and is bypassed
                # (with a WARNING audit log) when safety_override=True.
                await self.manager.safety_guard.enforce(device_key, safety_override=safety_override)

                result: dict[str, Any] = {"success": False}

                if action == "manual_dose":
                    api_dosing_type = DOSING_API_MAPPING.get(dosing_type, dosing_type)
                    result = await coordinator.device.api.manual_dosing(api_dosing_type, duration)

                    if not safety_override:
                        safety_interval = cast(
                            int,
                            DEVICE_PARAMETERS.get(device_key, {}).get(
                                "safety_interval", DEFAULT_SAFETY_INTERVAL
                            ),
                        )
                        self.manager.set_safety_lock(device_key, safety_interval)

                elif action == "auto":
                    api_dosing_type = DOSING_API_MAPPING.get(dosing_type, dosing_type)
                    result = await coordinator.device.api.set_dosage_enabled(
                        api_dosing_type, enabled=True
                    )
                    _LOGGER.info("Dosing %s set to AUTO (enabled)", dosing_type)

                elif action == "stop":
                    # DOS_* OFF is routed through /triggerManualDosing as
                    # DOSSTOP - stops a running manual dose without
                    # persistently disabling the channel in the config.
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF
                    )
                    # Clear any active cooldown when the user explicitly stops
                    # a dose, so a follow-on dose is not wrongly blocked.
                    self.manager.safety_guard.clear_lock(device_key)
                    _LOGGER.info("Dosing %s stopped (DOSSTOP)", dosing_type)

                if result.get("success") is not True:
                    _LOGGER.warning("Dosing action failed: %s", result.get("response", result))

            except VioletPoolAPIError as err:
                _LOGGER.error("Smart dosing error: %s", err)
                raise HomeAssistantError(f"Dosing failed: {err}") from err

            await coordinator.async_request_refresh()

    async def handle_manual_dosing_http(self, call: ServiceCall) -> None:
        """Trigger manual dosing via HTTP (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = str(call.data.get("dosing_system", ""))
        runtime = call.data.get("runtime_seconds", 30)
        safety_override = bool(call.data.get("safety_override", False))

        dosing_index = DOSING_INDEX_MAP.get(dosing_system)
        if dosing_index is None:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        from_param = DOSING_FROM_PARAM_MAP.get(dosing_system, 1)
        device_key = DOSING_SYSTEM_TO_KEY.get(dosing_system, dosing_system)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                # Enforce the cooldown before dispatching any dosing command.
                await self.manager.safety_guard.enforce(device_key, safety_override=safety_override)

                await control.trigger_manual_dosing(dosing_index, runtime, from_param=from_param)
                _LOGGER.info(
                    "Manual dosing: %s for %ds on %s",
                    dosing_system,
                    runtime,
                    device_name,
                )

                # Arm a cooldown equal to the runtime so back-to-back doses are
                # spaced, and arm a restart-safe auto-stop (dosing runs that
                # outlive a restart should be stopped).
                if not safety_override:
                    safety_interval = cast(
                        int,
                        DEVICE_PARAMETERS.get(device_key, {}).get(
                            "safety_interval", DEFAULT_SAFETY_INTERVAL
                        ),
                    )
                    self.manager.set_safety_lock(device_key, safety_interval)
                await self.manager.safety_guard.arm_auto_stop(
                    device_key,
                    duration_seconds=float(runtime),
                    stop_target={
                        "method": "set_switch_state",
                        "args": [device_key],
                        "kwargs": {"action": ACTION_OFF},
                    },
                )

                await coordinator.async_request_refresh()

            except VioletPoolAPIError as err:
                _LOGGER.error("Dosing control error: %s", err)
                raise HomeAssistantError(f"Dosing control failed: {err}") from err
            except HomeAssistantError:
                raise
            except Exception as err:
                _LOGGER.error("Dosing control error: %s", err)
                raise HomeAssistantError(f"Dosing control failed: {err}") from err

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
                control = VioletControlClient(coordinator.device.api)
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
                control = VioletControlClient(coordinator.device.api)
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
                control = VioletControlClient(coordinator.device.api)
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
                control = VioletControlClient(coordinator.device.api)
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
                control = VioletControlClient(coordinator.device.api)
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

