# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""HTTP control layer for Violet Pool Controller manual commands."""

from __future__ import annotations

import logging
from typing import Any

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)


class VioletControlClient:
    """HTTP client for pool controller manual commands and configuration."""

    def __init__(self, api: VioletPoolAPI) -> None:
        """Initialize control client.

        Args:
            api: VioletPoolAPI instance for HTTP communication.
        """
        self.api = api

    async def set_function_manually(
        self,
        function: str,
        action: str,
        param: str | int | None = None,
        timeout: float = 10.0,
    ) -> bool:
        """Execute manual control command via setFunctionManually.

        Args:
            function: Target function (PUMP, HEATER, SOLAR, COVER, etc.)
            action: Action (ON, OFF, OPEN, CLOSE, STOP, etc.)
            param: Optional parameter (RPM level, speed, etc.)
            timeout: Request timeout in seconds.

        Returns:
            True if successful, False otherwise.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        # Build command
        cmd = f"{function},{action},{param}" if param is not None else f"{function},{action}"

        try:
            _LOGGER.debug("Executing command: setFunctionManually?%s", cmd)

            # Send command via API
            response = await self.api._request(
                f"/setFunctionManually?{cmd}",
                method="GET",
            )

            # Check response (non-empty text response indicates success)
            if response:
                _LOGGER.info(
                    "Command successful: %s %s %s",
                    function,
                    action,
                    param or "",
                )
                return True

            _LOGGER.warning(
                "Command failed: %s %s",
                function,
                action,
            )
            return False

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API error executing command %s %s: %s",
                function,
                action,
                err,
            )
            raise
        except TimeoutError as err:
            _LOGGER.error(
                "Timeout executing command %s %s", function, action
            )
            raise VioletPoolAPIError(
                f"Timeout executing {function} {action}",
                original_exception=err,
            ) from err
        except Exception as err:
            _LOGGER.error(
                "Unexpected error executing command %s %s: %s",
                function,
                action,
                err,
            )
            raise VioletPoolAPIError(
                f"Error executing {function} {action}: {err}",
                original_exception=err,
            )

    async def set_pump_speed(
        self, rpm_level: int, timeout: float = 10.0
    ) -> bool:
        """Set pump speed via manual control.

        Args:
            rpm_level: Speed level 0-3.
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
            ValueError: If rpm_level out of range.
        """
        if not 0 <= rpm_level <= 3:
            raise ValueError(f"RPM level must be 0-3, got {rpm_level}")

        return await self.set_function_manually(
            "PUMP", "ON", rpm_level, timeout
        )

    async def set_pump_off(self, timeout: float = 10.0) -> bool:
        """Turn pump off.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually("PUMP", "OFF", timeout=timeout)

    async def set_heater_on(self, timeout: float = 10.0) -> bool:
        """Turn heater on.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "HEATER", "ON", timeout=timeout
        )

    async def set_heater_off(self, timeout: float = 10.0) -> bool:
        """Turn heater off.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "HEATER", "OFF", timeout=timeout
        )

    async def set_solar_on(self, timeout: float = 10.0) -> bool:
        """Turn solar on.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "SOLAR", "ON", timeout=timeout
        )

    async def set_solar_off(self, timeout: float = 10.0) -> bool:
        """Turn solar off.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "SOLAR", "OFF", timeout=timeout
        )

    async def set_cover_open(self, timeout: float = 10.0) -> bool:
        """Open cover.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "COVER", "OPEN", timeout=timeout
        )

    async def set_cover_close(self, timeout: float = 10.0) -> bool:
        """Close cover.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "COVER", "CLOSE", timeout=timeout
        )

    async def set_cover_stop(self, timeout: float = 10.0) -> bool:
        """Stop cover movement.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "COVER", "STOP", timeout=timeout
        )

    async def set_backwash_run(self, timeout: float = 10.0) -> bool:
        """Start backwash cycle.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "BACKWASH", "RUN", timeout=timeout
        )

    async def set_backwash_abort(self, timeout: float = 10.0) -> bool:
        """Abort backwash cycle.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        return await self.set_function_manually(
            "BACKWASH", "ABORT", timeout=timeout
        )

    async def trigger_manual_dosing(
        self,
        dosing_index: int,
        runtime_seconds: int,
        from_param: int = 1,
        action: str = "DOSSTART",
        timeout: float = 10.0,
    ) -> bool:
        """Trigger or stop a manual dosing run for a system.

        Wraps ``POST /triggerManualDosing``.  The controller firmware
        (``includes/triggerManualDosing.js``) accepts two actions:

        * ``DOSSTART`` – start a manual dosing run for ``runtime_seconds``.
          Requires the filter pump to be ON and no backwash in progress,
          otherwise the controller returns ``PUMP_OFF_ERROR`` /
          ``BACKWASH_ERROR``.
        * ``DOSSTOP`` – cancel a running manual dosing run and return the
          channel to automatic mode.  ``runtime_seconds`` is ignored by
          the firmware and may be ``0``.

        Args:
            dosing_index: Dosing system index (0-5). 0=Chlorine/H2O2,
                1=Electrolysis, 3=pH-, 4=pH+, 5=Flocculant.
                (Index 2 is reserved for H2O2 via ``from_param=3`` and
                reuses the Chlorine physical output.)
            runtime_seconds: Runtime in seconds.  Required for DOSSTART;
                ignored for DOSSTOP (pass ``0``).
            from_param: Source identifier. 1=normal dosing, 3=H2O2
                (shares DOS_1_CL physical output with Chlorine but uses
                a different firmware path).
            action: Either ``"DOSSTART"`` (default) or ``"DOSSTOP"``.
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
            ValueError: If parameters out of range or action is unknown.

        """
        action_upper = action.strip().upper()
        if action_upper not in ("DOSSTART", "DOSSTOP"):
            raise ValueError(
                f"action must be 'DOSSTART' or 'DOSSTOP', got {action!r}"
            )
        if not 0 <= dosing_index <= 5:
            raise ValueError(f"Dosing index must be 0-5, got {dosing_index}")
        if action_upper == "DOSSTART" and runtime_seconds <= 0:
            raise ValueError(
                f"Runtime must be > 0 for DOSSTART, got {runtime_seconds}"
            )

        try:
            _LOGGER.debug(
                "Triggering manual dosing: action=%s index=%d, runtime=%ds, from=%d",
                action_upper,
                dosing_index,
                runtime_seconds,
                from_param,
            )

            runtime_formatted = (
                f"{runtime_seconds // 60:02d}:{runtime_seconds % 60:02d}"
            )
            form_data = {
                "action": action_upper,
                "output": str(dosing_index),
                "runtime": str(runtime_seconds),
                "from": str(from_param),
                "runtime_formatted": runtime_formatted,
            }

            response = await self.api._request(
                "/triggerManualDosing",
                method="POST",
                data=form_data,
            )

            response_text = str(response).strip() if response else ""

            if "PUMP_OFF_ERROR" in response_text:
                _LOGGER.warning("Manual dosing blocked: pump is OFF")
                return False

            if "BACKWASH_ERROR" in response_text:
                _LOGGER.warning("Manual dosing blocked: backwash in progress")
                return False

            success_token = (
                "MANDOS_STARTED" if action_upper == "DOSSTART" else "MANDOS_STOPPED"
            )
            if "\nOK" in response_text or success_token in response_text:
                _LOGGER.info(
                    "Manual dosing %s: index=%d, runtime=%ds",
                    action_upper,
                    dosing_index,
                    runtime_seconds,
                )
                return True

            _LOGGER.warning(
                "Manual dosing unexpected response (%s): %s",
                action_upper,
                response_text,
            )
            return False

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API error triggering dosing (%s): %s",
                action_upper,
                err,
            )
            raise
        except TimeoutError as err:
            _LOGGER.error(
                "Timeout triggering manual dosing (%s)", action_upper
            )
            raise VioletPoolAPIError(
                f"Timeout triggering manual dosing ({action_upper})",
                original_exception=err,
            ) from err

    async def set_config(
        self,
        config_updates: dict[str, Any],
        timeout: float = 10.0,
    ) -> bool:
        """Update controller configuration.

        Args:
            config_updates: Dictionary of CONFIG keys and values.
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
        """
        try:
            _LOGGER.debug(
                "Updating config: %s",
                list(config_updates.keys()),
            )

            result = await self.api.set_config(config_updates)

            if result:
                _LOGGER.info(
                    "Configuration updated: %s",
                    list(config_updates.keys()),
                )
                return True

            _LOGGER.warning(
                "Config update failed",
            )
            return False

        except VioletPoolAPIError as err:
            _LOGGER.error("API error updating config: %s", err)
            raise
