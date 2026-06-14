# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Rule management service handlers for all 4 rule types."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .http_control import VioletControlClient

_LOGGER = logging.getLogger(__name__)


class RuleManagementServiceHandlers:
    """Handlers for rule creation, update, delete, and testing."""

    manager: Any

    async def handle_configure_temp_rule(self, call: ServiceCall) -> None:
        """Configure temperature rule (TEMPRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = call.data.get("rule_id")  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"TEMPRULE_{rule_id}_prog"

        # Basic enable/disable
        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        # Optional parameters
        if sensor1 := call.data.get("sensor_1"):
            config_updates[f"{prefix}_sensor_1"] = sensor1
        if sensor2 := call.data.get("sensor_2"):
            config_updates[f"{prefix}_sensor_2"] = sensor2
        if logic := call.data.get("logic"):
            config_updates[f"{prefix}_logic"] = logic
        if diffval := call.data.get("diff_value"):
            config_updates[f"{prefix}_diffval"] = diffval
        if hystval := call.data.get("hyst_value"):
            config_updates[f"{prefix}_hystval"] = hystval
        if runtime_on := call.data.get("runtime_on"):
            config_updates[f"{prefix}_runtime_on"] = runtime_on
        if runtime_off := call.data.get("runtime_off"):
            config_updates[f"{prefix}_runtime_off"] = runtime_off

        for i in range(1, 4):
            if output := call.data.get(f"output_{i}"):
                config_updates[f"{prefix}_output_{i}"] = output
            if state := call.data.get(f"output_{i}_state"):
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
        rule_id = call.data.get("rule_id")  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"ANALOGRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if adc_input := call.data.get("adc_input"):
            config_updates[f"{prefix}_input"] = adc_input
        if logic := call.data.get("logic"):
            config_updates[f"{prefix}_logic"] = logic
        if threshold := call.data.get("threshold"):
            config_updates[f"{prefix}_value"] = threshold
        if hyst := call.data.get("hysteresis"):
            config_updates[f"{prefix}_hyst"] = hyst
        if runtime_on := call.data.get("runtime_on"):
            config_updates[f"{prefix}_runtime_on"] = runtime_on
        if runtime_off := call.data.get("runtime_off"):
            config_updates[f"{prefix}_runtime_off"] = runtime_off

        for i in range(1, 4):
            if output := call.data.get(f"output_{i}"):
                config_updates[f"{prefix}_output_{i}"] = output
            if state := call.data.get(f"output_{i}_state"):
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
        rule_id = call.data.get("rule_id")  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"SWITCHINGRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if di_input := call.data.get("di_input"):
            config_updates[f"{prefix}_input"] = di_input
        if contact := call.data.get("contact_type"):
            config_updates[f"{prefix}_contact"] = contact
        if output := call.data.get("output"):
            config_updates[f"{prefix}_output"] = output
        if action_on := call.data.get("action_on"):
            config_updates[f"{prefix}_action_on"] = action_on
        if action_off := call.data.get("action_off"):
            config_updates[f"{prefix}_action_off"] = action_off
        if timeout := call.data.get("timeout"):
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
        rule_id = call.data.get("rule_id")  # 1-8
        enabled = call.data.get("enabled", True)

        if not 1 <= rule_id <= 8:
            raise HomeAssistantError(f"Rule ID must be 1-8, got {rule_id}")

        config_updates = {}
        prefix = f"TIMERRULE_{rule_id}_prog"

        config_updates[f"{prefix}_use"] = 1 if enabled else 0

        if on_time := call.data.get("on_time"):
            config_updates[f"{prefix}_on_time"] = on_time
        if off_time := call.data.get("off_time"):
            config_updates[f"{prefix}_off_time"] = off_time
        if weekdays := call.data.get("weekdays"):
            config_updates[f"{prefix}_on_weekdays"] = weekdays

        for i in range(1, 4):
            if output := call.data.get(f"output_{i}"):
                config_updates[f"{prefix}_output_{i}"] = output
            if state := call.data.get(f"output_{i}_state"):
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
        rule_type = call.data.get("rule_type")  # temprule, analogrule, etc.
        rule_id = call.data.get("rule_id")  # 1-8
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
