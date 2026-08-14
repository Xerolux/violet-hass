"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api.api import VioletPoolAPIError

from ..const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_OFF,
    ACTION_ON,
)
from ..http_control import VioletControlClient
from ..service_helpers import (
    as_device_id_list,
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



class ExtensionServiceHandlersMixin:
    """Mixin for extension services."""

    manager: Any
    hass: Any

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
                    result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                    _LOGGER.info("All DMX scenes ON (device %s)", device_id)

                elif action == "all_off":
                    result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLOFF)
                    _LOGGER.info("All DMX scenes OFF (device %s)", device_id)

                elif action == "all_auto":
                    result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLAUTO)
                    _LOGGER.info("All DMX scenes AUTO (device %s)", device_id)

                elif action == "sequence":
                    scenes = [f"DMX_SCENE{i}" for i in range(1, 13)]
                    _LOGGER.info(
                        "Starting DMX sequence: %d scenes (device %s)",
                        len(scenes),
                        device_id,
                    )

                    async def _run_sequence() -> None:
                        try:
                            failed: list[str] = []
                            for scene in scenes:
                                try:
                                    r_on = await coordinator.device.api.set_switch_state(
                                        key=scene, action=ACTION_ON
                                    )
                                    if r_on.get("success") is not True:
                                        _LOGGER.warning(
                                            "DMX scene %s ON failed: %s",
                                            scene,
                                            r_on.get("response"),
                                        )
                                        failed.append(scene)
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
                                except VioletPoolAPIError as exc:
                                    _LOGGER.warning("DMX scene %s error: %s", scene, exc)
                                    failed.append(scene)
                            if failed:
                                _LOGGER.warning(
                                    "DMX sequence completed with failures: %s",
                                    ", ".join(failed),
                                )
                            else:
                                _LOGGER.info("DMX sequence completed successfully")
                        except Exception as exc:
                            _LOGGER.error("DMX sequence background task crashed: %s", exc)

                    self.hass.async_create_background_task(
                        _run_sequence(), f"violet_dmx_sequence_{device_id}"
                    )
                    result = {"success": True, "response": "Sequence started"}

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

    async def handle_control_extension_relay(self, call: ServiceCall) -> None:
        """Control extension relay outputs (EXT1_1 to EXT8_8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        relay_id = int(call.data.get("relay_id", 0))

        if not 1 <= relay_id <= 8:
            raise HomeAssistantError(f"Relay ID must be 1-8, got {relay_id}")

        action = call.data.get("action", "on")
        state = call.data.get("state")
        duration = call.data.get("duration", 0)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)

                if state is not None:
                    await control.set_function_manually(f"EXT{relay_id}_1", str(state), duration)
                    _LOGGER.info(
                        "Extension relay EXT%d_1 set to state %d on %s",
                        relay_id,
                        state,
                        coordinator.device.device_name,
                    )
                elif action == "on":
                    await control.set_function_manually(f"EXT{relay_id}_1", "4", duration)
                    _LOGGER.info(
                        "Extension relay EXT%d_1 turned ON on %s",
                        relay_id,
                        coordinator.device.device_name,
                    )
                elif action == "off":
                    await control.set_function_manually(f"EXT{relay_id}_1", "6", duration)
                    _LOGGER.info(
                        "Extension relay EXT%d_1 turned OFF on %s",
                        relay_id,
                        coordinator.device.device_name,
                    )
                elif action == "toggle":
                    await control.set_function_manually(f"EXT{relay_id}_1", "0", duration)
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

