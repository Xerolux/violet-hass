# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Refill and Overflow control service handlers."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .http_control import VioletControlClient

_LOGGER = logging.getLogger(__name__)


class VioletRefillOverflowServiceHandlers:
    """Handlers for refill and overflow protection services."""

    manager: Any

    async def handle_configure_refill(self, call: ServiceCall) -> None:
        """Configure water refill system."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        refill_type = call.data.get("refill_type")

        if not 1 <= refill_type <= 3:
            raise HomeAssistantError(f"Refill type must be 1-3, got {refill_type}")

        config_updates = {}
        config_updates["REFILL_type"] = refill_type
        config_updates["REFILL_use"] = 1 if call.data.get("enabled", True) else 0

        if max_time := call.data.get("max_fill_time"):
            config_updates["REFILL_maxtime"] = max_time
        if target_level := call.data.get("target_level"):
            config_updates["REFILL_target_level"] = target_level
        if blocks_dosing := call.data.get("blocks_dosing"):
            config_updates["REFILL_blocks_dosage"] = 1 if blocks_dosing else 0

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Refill system type %d configured on %s",
                    refill_type,
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure refill system: {err}"
                )

    async def handle_configure_overflow(self, call: ServiceCall) -> None:
        """Configure overflow protection system."""
        coordinators = await self.manager.get_coordinators_for_call(call)

        config_updates = {}
        config_updates["OVERFLOW_use"] = 1 if call.data.get("enabled", True) else 0

        # Dry-run protection
        if dryrun := call.data.get("dryrun_level"):
            config_updates["OVERFLOW_dryrun_level"] = dryrun
        config_updates["OVERFLOW_dryrun_use"] = (
            1 if call.data.get("dryrun_enabled", True) else 0
        )

        # Overfill protection
        if overflow := call.data.get("overflow_level"):
            config_updates["OVERFLOW_overflow_level"] = overflow
        if overflow_rpm := call.data.get("overflow_rpm"):
            config_updates["OVERFLOW_overflow_rpm"] = overflow_rpm
        if overflow_runtime := call.data.get("overflow_runtime"):
            config_updates["OVERFLOW_overflow_runtime"] = overflow_runtime

        # Bathing AI detection
        config_updates["OVERFLOW_bathing_use"] = (
            1 if call.data.get("bathing_ai_enabled", True) else 0
        )
        if bathing_level := call.data.get("bathing_level_change"):
            config_updates["OVERFLOW_bathing_levelchange"] = bathing_level
        if bathing_time := call.data.get("bathing_level_time"):
            config_updates["OVERFLOW_bathing_levelchange_time"] = bathing_time
        if bathing_rpm := call.data.get("bathing_pump_rpm"):
            config_updates["OVERFLOW_bathing_rpm"] = bathing_rpm
        if bathing_runtime := call.data.get("bathing_runtime"):
            config_updates["OVERFLOW_bathing_runtime"] = bathing_runtime

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                await control.set_config(config_updates)
                _LOGGER.info(
                    "Overflow protection configured on %s",
                    coordinator.device.device_name,
                )
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    f"Failed to configure overflow protection: {err}"
                )

    async def handle_get_refill_status(self, call: ServiceCall) -> dict[str, Any]:
        """Get refill system status."""
        coordinators = await self.manager.get_coordinators_for_call(call)

        if not coordinators:
            raise HomeAssistantError("No coordinators found for device")

        coordinator = coordinators[0]
        if coordinator.data is None:
            raise HomeAssistantError("No data available")

        return {
            "refill_enabled": coordinator.data.get("REFILL_use", 0) == 1,
            "refill_type": coordinator.data.get("REFILL_type", 0),
            "water_level": coordinator.data.get("ADC2_value"),
            "refill_active": coordinator.data.get("REFILL_state", 0) > 0,
            "error_code": coordinator.data.get("REFILL_error"),
        }

    async def handle_get_overflow_status(
        self, call: ServiceCall
    ) -> dict[str, Any]:
        """Get overflow protection status."""
        coordinators = await self.manager.get_coordinators_for_call(call)

        if not coordinators:
            raise HomeAssistantError("No coordinators found for device")

        coordinator = coordinators[0]
        if coordinator.data is None:
            raise HomeAssistantError("No data available")

        water_level = coordinator.data.get("ADC2_value", 0)
        dryrun_level = coordinator.data.get("OVERFLOW_dryrun_level", 0)
        overflow_level = coordinator.data.get("OVERFLOW_overflow_level", 100)

        return {
            "overflow_enabled": coordinator.data.get("OVERFLOW_use", 0) == 1,
            "water_level": water_level,
            "dryrun_active": water_level <= dryrun_level,
            "overflow_active": water_level >= overflow_level,
            "bathing_detected": coordinator.data.get("OVERFLOW_bathing_state", 0) > 0,
            "dryrun_error": coordinator.data.get("OVERFLOW_dryrun_error"),
            "overflow_error": coordinator.data.get("OVERFLOW_overflow_error"),
        }
