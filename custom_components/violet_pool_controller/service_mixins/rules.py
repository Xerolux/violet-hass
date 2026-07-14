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



class RulesServiceHandlersMixin:
    """Mixin for rules services."""

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
                    result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
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
                    raise HomeAssistantError(f"Unsupported digital rule action: {action}")

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

    async def handle_configure_analog_rule(self, call: ServiceCall) -> None:
        """Configure analog input rule (ANALOGRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = int(call.data.get("rule_id", 0))
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
                control = VioletControlClient(coordinator.device.api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Analog rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(f"Failed to configure analog rule {rule_id}: {err}")

    async def handle_configure_switching_rule(self, call: ServiceCall) -> None:
        """Configure switching input rule (SWITCHINGRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = int(call.data.get("rule_id", 0))
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
                control = VioletControlClient(coordinator.device.api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Switching rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(f"Failed to configure switching rule {rule_id}: {err}")

    async def handle_configure_timer_rule(self, call: ServiceCall) -> None:
        """Configure timer rule (TIMERRULE_1-8)."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_id = int(call.data.get("rule_id", 0))
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
                control = VioletControlClient(coordinator.device.api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Timer rule %d configured on %s",
                    rule_id,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(f"Failed to configure timer rule {rule_id}: {err}")

    async def handle_enable_rule(self, call: ServiceCall) -> None:
        """Enable/disable any rule type."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        rule_type = call.data.get("rule_type")
        rule_id = int(call.data.get("rule_id", 0))
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
                control = VioletControlClient(coordinator.device.api)
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
                raise HomeAssistantError(f"Failed to enable/disable rule: {err}")

