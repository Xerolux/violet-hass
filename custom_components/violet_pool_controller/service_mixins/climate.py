"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from violet_poolcontroller_api.api import VioletPoolAPIError

from ..const import DOMAIN
from ..http_control import VioletControlClient

_LOGGER = logging.getLogger(__name__)


class ClimateServiceHandlersMixin:
    """Mixin for climate services."""

    manager: Any

    async def handle_manage_pv_surplus(self, call: ServiceCall) -> None:
        """Handle PV surplus management service.

        The controller documents ON and OFF for PVSURPLUS only (manual section
        26.3); the API rewrites AUTO to OFF with a warning, so the service does
        not offer an "auto" mode that would quietly do the opposite.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)
        mode = call.data["mode"]
        try:
            pump_speed = int(call.data.get("pump_speed", 2))
        except (TypeError, ValueError):
            pump_speed = 2
        pump_speed = min(3, max(1, pump_speed))

        for coordinator in coordinators:
            try:
                result: dict[str, Any] = {"success": False}

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

                if result.get("success") is not True:
                    _LOGGER.warning("PV surplus action failed: %s", result.get("response", result))

            except VioletPoolAPIError as err:
                _LOGGER.error("PV surplus error: %s", err)
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"PV surplus: {err}"},
                ) from err

            await coordinator.async_request_refresh()

    async def handle_control_heater_http(self, call: ServiceCall) -> None:
        """Control heater via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        target_temp = call.data.get("target_temperature")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                if action == "on":
                    await control.set_heater_on()
                    _LOGGER.info("Heater turned ON: %s", device_name)
                elif action == "off":
                    await control.set_heater_off()
                    _LOGGER.info("Heater turned OFF: %s", device_name)

                if target_temp is not None:
                    await control.set_config({"HEATER_target_temp": target_temp})
                    _LOGGER.info("Heater target temp: %.1f°C on %s", target_temp, device_name)

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Heater control error: %s", err)
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"Heater: {err}"},
                ) from err

    async def handle_control_solar_http(self, call: ServiceCall) -> None:
        """Control solar via HTTP setFunctionManually (NEW API)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        action = call.data.get("action")
        target_temp = call.data.get("target_temperature")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                device_name = coordinator.device.device_name

                if action == "on":
                    await control.set_solar_on()
                    _LOGGER.info("Solar turned ON: %s", device_name)
                elif action == "off":
                    await control.set_solar_off()
                    _LOGGER.info("Solar turned OFF: %s", device_name)

                if target_temp is not None:
                    await control.set_config({"SOLAR_target_temp": target_temp})
                    _LOGGER.info("Solar target temp: %.1f°C on %s", target_temp, device_name)

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Solar control error: %s", err)
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"Solar: {err}"},
                ) from err

    async def handle_configure_temp_rule(self, call: ServiceCall) -> None:
        """Configure temperature rule (TEMPRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = int(call.data.get("rule_id", 0))  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="value_out_of_range",
                translation_placeholders={"value": str(rule_id), "min": "1", "max": "8"},
            )

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
                control = VioletControlClient(coordinator.device.api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Temperature rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"temperature rule {rule_id}: {err}"},
                ) from err

