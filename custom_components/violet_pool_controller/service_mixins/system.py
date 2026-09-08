"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from violet_poolcontroller_api.api import VioletPoolAPIError

from ..const import DOMAIN
from ..http_control import VioletControlClient
from ..service_helpers import as_device_id_list

_LOGGER = logging.getLogger(__name__)




class SystemServiceHandlersMixin:
    """Mixin for system services."""

    manager: Any

    async def handle_test_output(self, call: ServiceCall) -> None:
        """Handle the output test service."""
        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        output = call.data["output"]
        mode = call.data.get("mode", "SWITCH")
        duration = call.data.get("duration", 120)

        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if not coordinator:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="device_not_found",
                    translation_placeholders={"device_id": device_id},
                )

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
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"output test: {err}"},
                ) from err

            await coordinator.async_request_refresh()

    async def handle_configure_sensor_calibration(self, call: ServiceCall) -> None:
        """Configure sensor calibration offsets and multipliers."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        sensor_id = int(call.data.get("sensor_id", 0))

        if not 1 <= sensor_id <= 12:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="value_out_of_range",
                translation_placeholders={"value": str(sensor_id), "min": "1", "max": "12"},
            )

        config_updates = {}

        # ``is not None`` rather than truthiness: an offset of 0.0 is a
        # meaningful calibration value and used to be silently dropped.
        for field, suffix in (
            ("offset", "offset"),
            ("multiplier", "multiplier"),
            ("min_value", "min"),
            ("max_value", "max"),
        ):
            value = call.data.get(field)
            if value is not None:
                config_updates[f"SENSOR_{sensor_id}_{suffix}"] = value

        if not config_updates:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_parameters",
                translation_placeholders={"service": "configure_sensor_calibration"},
            )

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
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"sensor {sensor_id} calibration: {err}"},
                ) from err

