# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Dosing system configuration service handlers."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .http_control import VioletControlClient

_LOGGER = logging.getLogger(__name__)

DOSING_SYSTEMS = {
    "chlorine": "DOSAGE_chlorine",
    "electrolysis": "DOSAGE_electrolysis",
    "ph_minus": "DOSAGE_phminus",
    "ph_plus": "DOSAGE_phplus",
    "flocculant": "DOSAGE_floc",
    "h2o2": "DOSAGE_h2o2",
}


class DosingConfigServiceHandlers:
    """Handlers for dosing system configuration."""

    manager: Any

    async def handle_configure_dosing(self, call: ServiceCall) -> None:
        """Configure dosing system parameters."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        dosing_system = call.data.get("dosing_system")
        config_key = call.data.get("config_key")
        value = call.data.get("value")

        if dosing_system not in DOSING_SYSTEMS:
            raise HomeAssistantError(f"Unknown dosing system: {dosing_system}")

        prefix = DOSING_SYSTEMS[dosing_system]
        full_key = f"{prefix}_{config_key}"

        # Ensure _use keys send integers (0 or 1), not floats
        if config_key.endswith("_use"):
            value = int(bool(value))

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({full_key: value})
                _LOGGER.info(
                    "Dosing config updated: %s = %s on %s",
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
        key = f"{prefix}_set_ppm" if dosing_system in ("chlorine", "electrolysis") else f"{prefix}_set_ph"

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: target_value})
                _LOGGER.info(
                    "Dosing target set: %s = %s on %s",
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
        day_end = call.data.get("day_end")      # HH:MM

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
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config(config_updates)
                _LOGGER.info(
                    "Dosing daytime set: %s (%s-%s) on %s",
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
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: max_ml})
                _LOGGER.info(
                    "Dosing max daily set: %s = %d ml on %s",
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
                control = VioletControlClient(coordinator.device._api)
                device_name = coordinator.device.device_name

                await control.set_config({key: value})
                state = "enabled" if enabled else "disabled"
                _LOGGER.info(
                    "Dosing system %s: %s on %s",
                    dosing_system,
                    state,
                    device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error("Dosing enable error: %s", err)
                raise HomeAssistantError(f"Failed to enable/disable dosing: {err}")
