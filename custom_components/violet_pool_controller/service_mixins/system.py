"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api.api import VioletPoolAPIError

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



class SystemServiceHandlersMixin:
    """Mixin for system services."""

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

    async def handle_configure_sensor_calibration(self, call: ServiceCall) -> None:
        """Configure sensor calibration offsets and multipliers."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        sensor_id = int(call.data.get("sensor_id", 0))

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
                control = VioletControlClient(coordinator.device.api)
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

