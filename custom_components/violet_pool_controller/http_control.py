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
                "GET",
                f"/setFunctionManually?{cmd}",
                timeout=timeout,
            )

            # Check response
            if response and response.status_code == 200:
                _LOGGER.info(
                    "Command successful: %s %s %s",
                    function,
                    action,
                    param or "",
                )
                return True

            _LOGGER.warning(
                "Command failed with status %s: %s %s",
                response.status_code if response else "None",
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
        timeout: float = 10.0,
    ) -> bool:
        """Trigger manual dosing for a system.

        Args:
            dosing_index: Dosing system index (0-5).
            runtime_seconds: Runtime in seconds.
            timeout: Request timeout in seconds.

        Returns:
            True if successful.

        Raises:
            VioletPoolAPIError: If API communication fails.
            ValueError: If parameters out of range.
        """
        if not 0 <= dosing_index <= 5:
            raise ValueError(f"Dosing index must be 0-5, got {dosing_index}")
        if runtime_seconds <= 0:
            raise ValueError(
                f"Runtime must be > 0, got {runtime_seconds}"
            )

        try:
            _LOGGER.debug(
                "Triggering manual dosing: index=%d, runtime=%ds",
                dosing_index,
                runtime_seconds,
            )

            # Build command
            cmd = f"?index={dosing_index}&runtime={runtime_seconds}"

            response = await self.api._request(
                "GET",
                f"/triggerManualDosing{cmd}",
                timeout=timeout,
            )

            if response and response.status_code == 200:
                _LOGGER.info(
                    "Manual dosing triggered: index=%d, runtime=%ds",
                    dosing_index,
                    runtime_seconds,
                )
                return True

            _LOGGER.warning(
                "Manual dosing failed with status %s",
                response.status_code if response else "None",
            )
            return False

        except VioletPoolAPIError as err:
            _LOGGER.error("API error triggering dosing: %s", err)
            raise
        except TimeoutError as err:
            _LOGGER.error("Timeout triggering manual dosing")
            raise VioletPoolAPIError(
                "Timeout triggering manual dosing",
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

            response = await self.api._request(
                "POST",
                "/setConfig",
                json=config_updates,
                timeout=timeout,
            )

            if response and response.status_code == 200:
                _LOGGER.info(
                    "Configuration updated: %s",
                    list(config_updates.keys()),
                )
                return True

            _LOGGER.warning(
                "Config update failed with status %s",
                response.status_code if response else "None",
            )
            return False

        except VioletPoolAPIError as err:
            _LOGGER.error("API error updating config: %s", err)
            raise
        except TimeoutError as err:
            _LOGGER.error("Timeout updating configuration")
            raise VioletPoolAPIError(
                "Timeout updating configuration",
                original_exception=err,
            ) from err
