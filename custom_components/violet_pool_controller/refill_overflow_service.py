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
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .const import DOMAIN
from .http_control import VioletControlClient

_LOGGER = logging.getLogger(__name__)

# Service field -> controller config key, for the fields that are written
# verbatim.  Every one of them is optional and only sent when the caller
# actually supplied it: a call meant to raise the overflow level must not
# switch on the dry-run or bathing protections as a side effect (SECURITY.md,
# "only acts on explicit user commands").
REFILL_CONFIG_KEYS = {
    "max_fill_time": "REFILL_maxtime",
    "target_level": "REFILL_target_level",
}

OVERFLOW_CONFIG_KEYS = {
    "dryrun_level": "OVERFLOW_dryrun_level",
    "overflow_level": "OVERFLOW_overflow_level",
    "overflow_rpm": "OVERFLOW_overflow_rpm",
    "overflow_runtime": "OVERFLOW_overflow_runtime",
    "bathing_level_change": "OVERFLOW_bathing_levelchange",
    "bathing_level_time": "OVERFLOW_bathing_levelchange_time",
    "bathing_pump_rpm": "OVERFLOW_bathing_rpm",
    "bathing_runtime": "OVERFLOW_bathing_runtime",
}

# Boolean service field -> controller flag key.
OVERFLOW_FLAG_KEYS = {
    "enabled": "OVERFLOW_use",
    "dryrun_enabled": "OVERFLOW_dryrun_use",
    "bathing_ai_enabled": "OVERFLOW_bathing_use",
}


def _as_int(value: Any, default: int = 0) -> int:
    """Parse a controller reading into an int without ever raising.

    A reading can arrive as an int, as a numeric string, or as a composite
    state such as ``"3|PUMP_ANTI_FREEZE"``; comparing any of the latter two
    with ``>`` or feeding them to ``int()`` used to surface as a 500 from the
    status services.  Anything unparseable falls back to ``default``.
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        head = value.split("|", 1)[0].strip()
        try:
            return int(float(head))
        except (TypeError, ValueError):
            return default
    return default


def _as_float(value: Any) -> float | None:
    """Parse a controller reading into a float, or ``None`` if it is not one."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.split("|", 1)[0].strip())
        except (TypeError, ValueError):
            return None
    return None


class VioletRefillOverflowServiceHandlers:
    """Handlers for refill and overflow protection services."""

    manager: Any

    async def _apply_config(
        self,
        coordinators: list[Any],
        config_updates: dict[str, Any],
        what: str,
    ) -> None:
        """Write a config update to every targeted controller."""
        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device.api)
                await control.set_config(config_updates)
                _LOGGER.info("%s configured on %s", what, coordinator.device.device_name)
                await coordinator.async_request_refresh()
            except Exception as err:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"detail": f"{what}: {err}"},
                ) from err

    async def handle_configure_refill(self, call: ServiceCall) -> None:
        """Configure water refill system."""
        coordinators = await self.manager.get_coordinators_for_call(call)
        refill_type = int(call.data.get("refill_type", 0))

        if not 1 <= refill_type <= 3:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="value_out_of_range",
                translation_placeholders={"value": str(refill_type), "min": "1", "max": "3"},
            )

        config_updates: dict[str, Any] = {"REFILL_type": refill_type}
        if (enabled := call.data.get("enabled")) is not None:
            config_updates["REFILL_use"] = 1 if enabled else 0
        # ``is not None`` rather than truthiness: a target level of 0 and
        # blocks_dosing=False are meaningful values that used to be dropped.
        for field, key in REFILL_CONFIG_KEYS.items():
            value = call.data.get(field)
            if value is not None:
                config_updates[key] = value
        if (blocks_dosing := call.data.get("blocks_dosing")) is not None:
            config_updates["REFILL_blocks_dosage"] = 1 if blocks_dosing else 0

        await self._apply_config(coordinators, config_updates, f"Refill system type {refill_type}")

    async def handle_configure_overflow(self, call: ServiceCall) -> None:
        """Configure overflow protection system.

        Only the fields the caller actually supplied are written.  The service
        used to default ``OVERFLOW_use``, ``OVERFLOW_dryrun_use`` and
        ``OVERFLOW_bathing_use`` to ``True``, so a call meant only to raise the
        overflow level silently switched two other protections on.
        """
        coordinators = await self.manager.get_coordinators_for_call(call)

        config_updates: dict[str, Any] = {}
        for field, key in OVERFLOW_FLAG_KEYS.items():
            value = call.data.get(field)
            if value is not None:
                config_updates[key] = 1 if value else 0
        for field, key in OVERFLOW_CONFIG_KEYS.items():
            value = call.data.get(field)
            if value is not None:
                config_updates[key] = value

        if not config_updates:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_parameters",
                translation_placeholders={"service": "configure_overflow"},
            )

        await self._apply_config(coordinators, config_updates, "Overflow protection")

    async def _status_targets(self, call: ServiceCall) -> list[Any]:
        """Return the coordinators a status service should report on."""
        coordinators: list[Any] = await self.manager.get_coordinators_for_call(call)
        if not coordinators:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_devices",
            )
        return coordinators

    @staticmethod
    def _single_or_list(results: list[dict[str, Any]]) -> dict[str, Any]:
        """Return one result directly, several under a ``devices`` key."""
        if not results:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="no_data",
            )
        return results[0] if len(results) == 1 else {"devices": results}

    async def handle_get_refill_status(self, call: ServiceCall) -> dict[str, Any]:
        """Get refill system status."""
        coordinators = await self._status_targets(call)

        results = []
        for coordinator in coordinators:
            if coordinator.data is None:
                continue
            results.append(
                {
                    "refill_enabled": _as_int(coordinator.data.get("REFILL_use")) == 1,
                    "refill_type": _as_int(coordinator.data.get("REFILL_type")),
                    "water_level": coordinator.data.get("ADC2_value"),
                    "refill_active": _as_int(coordinator.data.get("REFILL_state")) > 0,
                    "error_code": coordinator.data.get("REFILL_error"),
                }
            )

        return self._single_or_list(results)

    async def handle_get_overflow_status(self, call: ServiceCall) -> dict[str, Any]:
        """Get overflow protection status."""
        coordinators = await self._status_targets(call)

        results = []
        for coordinator in coordinators:
            if coordinator.data is None:
                continue
            water_level = _as_float(coordinator.data.get("ADC2_value"))
            dryrun_level = _as_float(coordinator.data.get("OVERFLOW_dryrun_level"))
            overflow_level = _as_float(coordinator.data.get("OVERFLOW_overflow_level"))

            results.append(
                {
                    "overflow_enabled": _as_int(coordinator.data.get("OVERFLOW_use")) == 1,
                    "water_level": coordinator.data.get("ADC2_value"),
                    "dryrun_active": (
                        water_level is not None
                        and dryrun_level is not None
                        and water_level <= dryrun_level
                    ),
                    "overflow_active": (
                        water_level is not None
                        and overflow_level is not None
                        and water_level >= overflow_level
                    ),
                    "bathing_detected": (
                        _as_int(coordinator.data.get("OVERFLOW_bathing_state")) > 0
                    ),
                    "dryrun_error": coordinator.data.get("OVERFLOW_dryrun_error"),
                    "overflow_error": coordinator.data.get("OVERFLOW_overflow_error"),
                }
            )

        return self._single_or_list(results)
