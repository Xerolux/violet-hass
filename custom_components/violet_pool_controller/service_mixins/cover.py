"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api.api import VioletPoolAPIError

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



class CoverServiceHandlersMixin:
    """Mixin for cover services."""

    manager: Any

    async def handle_control_cover_http(self, call: ServiceCall) -> None:
        """Control cover via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action", "open")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
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

    async def handle_control_refill_http(self, call: ServiceCall) -> None:
        """Control water refill via HTTP setFunctionManually (NEW API).

        For 'fill' action: automatically stops after specified duration.
        Duration is REQUIRED for safety - prevents flooding/tank overflow.
        The auto-stop timer is persisted so it survives a HA restart.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        duration_seconds = call.data.get("duration_seconds")
        safety_override = bool(call.data.get("safety_override", False))

        if action == "fill" and (duration_seconds is None or float(duration_seconds) <= 0):
            raise HomeAssistantError(
                "Refill duration is REQUIRED for safety to prevent flooding! "
                "Specify duration_seconds (10-3600 seconds)"
            )
        refill_seconds = float(duration_seconds or 0)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                if action == "fill":
                    # Enforce cooldown before starting a refill.
                    await self.manager.safety_guard.enforce(
                        "REFILL", safety_override=safety_override
                    )

                    await control.set_function_manually("REFILL", "ON")
                    _LOGGER.warning(
                        "WATER REFILL STARTED on %s - WILL AUTO-STOP after %ss",
                        device_name,
                        refill_seconds,
                    )

                    # Restart-safe auto-stop: persists deadline so the refill
                    # is stopped even if HA restarts mid-run (flood prevention).
                    await self.manager.safety_guard.arm_auto_stop(
                        "REFILL",
                        duration_seconds=refill_seconds,
                        stop_target={
                            "method": "set_function_manually",
                            "args": ["REFILL", "OFF"],
                        },
                    )
                    if not safety_override:
                        self.manager.set_safety_lock("REFILL", DEFAULT_SAFETY_INTERVAL)

                elif action == "stop":
                    await control.set_function_manually("REFILL", "OFF")
                    # Cancel any pending auto-stop and clear the cooldown.
                    self.manager.safety_guard.cancel_auto_stop("REFILL")
                    self.manager.safety_guard.clear_lock("REFILL")
                    _LOGGER.warning("WATER REFILL STOPPED on %s (manual)", device_name)
                    await coordinator.async_request_refresh()

            except VioletPoolAPIError as err:
                _LOGGER.error("CRITICAL: Refill control error: %s", err)
                raise HomeAssistantError(f"Refill control FAILED (FLOODING RISK): {err}") from err
            except HomeAssistantError:
                raise
            except Exception as err:
                _LOGGER.error("CRITICAL: Refill control error: %s", err)
                raise HomeAssistantError(f"Refill control FAILED (FLOODING RISK): {err}") from err

