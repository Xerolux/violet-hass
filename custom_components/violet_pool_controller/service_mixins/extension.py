"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from violet_poolcontroller_api.api import VioletPoolAPIError

from ..const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
    DOMAIN,
)
from ..service_helpers import as_device_id_list

_LOGGER = logging.getLogger(__name__)

# The extension-relay service takes an action, not a state: the controller's
# command grammar is EXT<bank>_<relay>,{ON|OFF|AUTO},<duration>,0.
RELAY_ACTIONS = {
    "on": ACTION_ON,
    "off": ACTION_OFF,
    "auto": ACTION_AUTO,
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
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="device_not_found",
                    translation_placeholders={"device_id": device_id},
                )

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
                    raise ServiceValidationError(
                        translation_domain=DOMAIN,
                        translation_key="invalid_action",
                        translation_placeholders={"action": str(action)},
                    )

                if result.get("success") is not True:
                    _LOGGER.warning(
                        "DMX action failed for %s: %s",
                        device_id,
                        result.get("response", result),
                    )

            except VioletPoolAPIError as err:
                _LOGGER.error("DMX control error (%s): %s", device_id, err)
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"DMX control: {err}"},
                ) from err

            await coordinator.async_request_refresh()

    async def handle_set_light_color_pulse(self, call: ServiceCall) -> None:
        """Handle light color pulse service.

        Up to ten pulses two seconds apart add up to 20 s of sleeping, which is
        far longer than a service call may block the event loop, so the
        sequence runs as a background task exactly like the DMX sequence does.
        The service returns as soon as the sequence has been scheduled.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        pulse_count = int(call.data.get("pulse_count", 1))
        pulse_interval = int(call.data.get("pulse_interval", 500))

        async def _run_pulses(coordinator: Any) -> None:
            try:
                for index in range(pulse_count):
                    result = await coordinator.device.api.set_light_color_pulse()
                    if result.get("success") is not True:
                        _LOGGER.warning(
                            "Pulse %d/%d failed: %s",
                            index + 1,
                            pulse_count,
                            result.get("response", result),
                        )
                    if index < pulse_count - 1:
                        await asyncio.sleep(pulse_interval / 1000)
                _LOGGER.info("Color pulse sequence completed (%d pulses)", pulse_count)
            except VioletPoolAPIError as err:
                _LOGGER.error("Color pulse error: %s", err)
            except Exception as err:  # noqa: BLE001 - a background task must not escape
                _LOGGER.error("Color pulse background task crashed: %s", err)
            else:
                await coordinator.async_request_refresh()

        for coordinator in coordinators:
            _LOGGER.info(
                "Starting %d color pulses (interval: %dms)",
                pulse_count,
                pulse_interval,
            )
            self.hass.async_create_background_task(
                _run_pulses(coordinator),
                f"violet_color_pulse_{coordinator.config_entry.entry_id}",
            )

    async def handle_control_extension_relay(self, call: ServiceCall) -> None:
        """Control one extension relay output (EXT1_1..EXT1_8, EXT2_1..EXT2_8).

        The controller has two extension modules of eight relays each, so a
        relay is addressed by bank *and* relay number.  The command grammar is
        ``EXT<bank>_<relay>,{ON|OFF|AUTO},<duration>,0`` - the 0-6 numbers the
        readings report are *states*, not actions, and sending one as an action
        is rejected by the controller.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        bank = int(call.data["bank"])
        relay = int(call.data["relay"])
        action = call.data.get("action", "on")
        duration = int(call.data.get("duration", 0))

        api_action = RELAY_ACTIONS.get(action)
        if api_action is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_action",
                translation_placeholders={"action": str(action)},
            )

        key = f"EXT{bank}_{relay}"
        for coordinator in coordinators:
            try:
                await coordinator.device.api.set_switch_state(
                    key,
                    api_action,
                    duration=duration or None,
                )
                _LOGGER.info(
                    "Extension relay %s set to %s on %s",
                    key,
                    api_action,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except VioletPoolAPIError as err:
                _LOGGER.error("Extension relay error (%s): %s", key, err)
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"{key}: {err}"},
                ) from err
