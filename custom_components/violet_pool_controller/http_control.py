# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Thin facade over the public API for the ``*_http`` control services.

This used to be a second, parallel implementation of the controller protocol:
it built ``FUNCTION,ACTION[,param]`` payloads by hand and posted them through
the API client's *private* ``_request``.  Doing so bypassed everything
``VioletPoolAPI`` does around a command - the duration validation, the routing
of dosing outputs to ``/triggerManualDosing``, the dosing-standalone guard, the
cover ``acknowledge_unsafe`` gate and the auth guard that raises the
``controller_requires_auth`` repair on a 401 - and it got the command grammar
wrong for the cover (``COVER,OPEN`` instead of the ``COVER_OPEN`` function).

Every method below is now a one-line call into a public API method, so the
services keep their convenient names while the protocol lives in exactly one
place.
"""

from __future__ import annotations

import logging
from typing import Any

from violet_poolcontroller_api.api import VioletPoolAPI
from violet_poolcontroller_api.const_api import (
    ACTION_OFF,
    ACTION_ON,
    DOSING_OUTPUT_INDEX,
)

_LOGGER = logging.getLogger(__name__)

# ``trigger_manual_dosing`` addresses a channel by the firmware's output index;
# the public API addresses it by key, so invert the API's own table.
DOSING_INDEX_TO_KEY = {index: key for key, index in DOSING_OUTPUT_INDEX.items()}


def _succeeded(result: Any) -> bool:
    """Normalise a command result into the boolean the services expect."""
    if isinstance(result, dict):
        return result.get("success") is True
    return bool(result)


class VioletControlClient:
    """Convenience wrapper around :class:`VioletPoolAPI` for manual commands."""

    def __init__(self, api: VioletPoolAPI) -> None:
        """Initialize control client.

        Args:
            api: VioletPoolAPI instance for HTTP communication.
        """
        self.api = api

    # ------------------------------------------------------------------
    # Pump
    # ------------------------------------------------------------------

    async def set_pump_speed(self, rpm_level: int) -> bool:
        """Switch the pump to manual ON at ``rpm_level``.

        Args:
            rpm_level: Speed level 1-3.  Level 0 is not a speed but "off" and
                is rejected here - use :meth:`set_pump_off` instead.

        Raises:
            ValueError: If ``rpm_level`` is outside 1-3.
        """
        if not 1 <= rpm_level <= 3:
            raise ValueError(f"Pump speed must be 1-3, got {rpm_level}")
        return _succeeded(
            await self.api.set_switch_state("PUMP", ACTION_ON, last_value=rpm_level)
        )

    async def set_pump_off(self) -> bool:
        """Turn the pump off."""
        return _succeeded(await self.api.set_switch_state("PUMP", ACTION_OFF))

    # ------------------------------------------------------------------
    # Heater and solar
    # ------------------------------------------------------------------

    async def set_heater_on(self) -> bool:
        """Turn the heater on."""
        return _succeeded(await self.api.set_switch_state("HEATER", ACTION_ON))

    async def set_heater_off(self) -> bool:
        """Turn the heater off."""
        return _succeeded(await self.api.set_switch_state("HEATER", ACTION_OFF))

    async def set_solar_on(self) -> bool:
        """Turn solar heating on."""
        return _succeeded(await self.api.set_switch_state("SOLAR", ACTION_ON))

    async def set_solar_off(self) -> bool:
        """Turn solar heating off."""
        return _succeeded(await self.api.set_switch_state("SOLAR", ACTION_OFF))

    # ------------------------------------------------------------------
    # Cover
    # ------------------------------------------------------------------

    async def _cover(self, action: str) -> bool:
        """Send a cover command through the API's guarded cover entry point.

        ``acknowledge_unsafe`` is passed because the caller is a service the
        user invoked deliberately; the API's gate exists to stop *implicit*
        cover movement, which the integration never performs.
        """
        return _succeeded(await self.api.set_cover_command(action, acknowledge_unsafe=True))

    async def set_cover_open(self) -> bool:
        """Open the pool cover."""
        return await self._cover("OPEN")

    async def set_cover_close(self) -> bool:
        """Close the pool cover."""
        return await self._cover("CLOSE")

    async def set_cover_stop(self) -> bool:
        """Stop the pool cover."""
        return await self._cover("STOP")

    # ------------------------------------------------------------------
    # Backwash
    # ------------------------------------------------------------------

    async def set_backwash_run(self, duration: int | None = None) -> bool:
        """Start a backwash cycle, optionally bounded by ``duration`` seconds."""
        return _succeeded(
            await self.api.set_switch_state("BACKWASH", ACTION_ON, duration=duration)
        )

    async def set_backwash_abort(self) -> bool:
        """Abort a running backwash cycle."""
        return _succeeded(await self.api.set_switch_state("BACKWASH", ACTION_OFF))

    # ------------------------------------------------------------------
    # Dosing
    # ------------------------------------------------------------------

    async def trigger_manual_dosing(
        self,
        dosing_index: int,
        runtime_seconds: int,
        from_param: int = 1,
        action: str = "DOSSTART",
    ) -> bool:
        """Start or stop a manual dosing run for one channel.

        ``set_switch_state`` routes every ``DOS_*`` key to
        ``/triggerManualDosing`` itself, so this is a key lookup plus one
        public call.

        Args:
            dosing_index: Firmware output index (0=Chlorine, 1=Electrolysis,
                3=pH-, 4=pH+, 5=Flocculant).
            runtime_seconds: Runtime in seconds; ignored for ``DOSSTOP``.
            from_param: The firmware's ``from`` field, which selects the
                chemical on a channel shared by more than one agent.  The
                installed API exposes no way to set it, so only the default
                (1, the channel's primary agent) is accepted - silently
                ignoring it would dose the wrong chemical.
            action: ``"DOSSTART"`` or ``"DOSSTOP"``.

        Raises:
            ValueError: If a parameter is out of range or unsupported.
        """
        action_upper = action.strip().upper()
        if action_upper not in ("DOSSTART", "DOSSTOP"):
            raise ValueError(f"action must be 'DOSSTART' or 'DOSSTOP', got {action!r}")
        key = DOSING_INDEX_TO_KEY.get(dosing_index)
        if key is None:
            raise ValueError(
                f"Dosing index must be one of {sorted(DOSING_INDEX_TO_KEY)}, got {dosing_index}"
            )
        if from_param != 1:
            raise ValueError(
                f"Dosing source {from_param} is not supported by the installed API; "
                "only the channel's primary agent (from=1) can be dosed"
            )

        if action_upper == "DOSSTOP":
            return _succeeded(await self.api.set_switch_state(key, ACTION_OFF))

        return _succeeded(
            await self.api.set_switch_state(key, ACTION_ON, duration=runtime_seconds)
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    async def set_config(self, config_updates: dict[str, Any]) -> bool:
        """Update controller configuration.

        Boolean-ish values are normalised to 0/1 first: the controller expects
        integers for flag keys such as ``*_use``, and a Python ``True`` or a
        float ``1.0`` would otherwise be sent verbatim.

        Args:
            config_updates: Dictionary of CONFIG keys and values.

        Returns:
            True if the controller accepted the update.
        """
        normalized_updates: dict[str, Any] = {}
        for key, value in config_updates.items():
            if isinstance(value, bool):
                normalized_updates[key] = int(value)
            elif (
                isinstance(value, (int, float))
                and key.endswith(("_use", "_enabled"))
                and not key.endswith("_count")
            ):
                normalized_updates[key] = int(bool(value))
            else:
                normalized_updates[key] = value

        _LOGGER.debug("Updating config: %s", list(normalized_updates))
        result = await self.api.set_config(normalized_updates)

        if _succeeded(result):
            _LOGGER.info("Configuration updated: %s", list(normalized_updates))
            return True

        _LOGGER.warning("Config update failed for: %s", list(normalized_updates))
        return False
