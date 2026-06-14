# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Service handlers for pool controller manual control commands."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .http_control import VioletControlClient
from .service_helpers import as_device_id_list

_LOGGER = logging.getLogger(__name__)

DOSING_INDEX_MAP = {
    "chlorine": 0,
    "electrolysis": 1,
    "ph_minus": 2,
    "ph_plus": 3,
    "flocculant": 4,
    "h2o2": 5,
}


class VioletControlServiceHandlers:
    """Handlers for pool controller control services."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize service handlers.

        Args:
            hass: Home Assistant instance.
        """
        self.hass = hass

    def _get_coordinators(
        self, device_ids: list[str]
    ) -> list[VioletPoolDataUpdateCoordinator]:
        """Get coordinator instances for device IDs.

        Args:
            device_ids: List of device IDs.

        Returns:
            List of coordinators.

        Raises:
            HomeAssistantError: If device not found.
        """
        domain_data = self.hass.data.get(DOMAIN, {})
        coordinators = []

        for device_id in device_ids:
            if device_id not in domain_data:
                raise HomeAssistantError(
                    f"Device {device_id} not found. "
                    f"Available: {list(domain_data.keys())}"
                )
            coordinators.append(domain_data[device_id])

        return coordinators

    async def control_pump(self, call: ServiceCall) -> None:
        """Control pump speed and operation.

        Args:
            call: Service call with device_id, speed, action, force_off.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        speed = call.data.get("speed")
        action = call.data.get("action")
        force_off = call.data.get("force_off", False)

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if force_off:
                    await control.set_pump_off()
                    _LOGGER.info(
                        "Pump forced OFF for %s",
                        coordinator.device.device_name,
                    )
                elif action == "off":
                    await control.set_pump_off()
                    _LOGGER.info(
                        "Pump turned OFF for %s",
                        coordinator.device.device_name,
                    )
                elif action == "on" or speed is not None:
                    rpm = speed if speed is not None else 1
                    await control.set_pump_speed(rpm)
                    _LOGGER.info(
                        "Pump set to RPM %d for %s",
                        rpm,
                        coordinator.device.device_name,
                    )
                elif action == "eco":
                    await control.set_pump_speed(1)
                    _LOGGER.info(
                        "Pump set to ECO mode (RPM 1) for %s",
                        coordinator.device.device_name,
                    )
                elif action == "boost":
                    await control.set_pump_speed(3)
                    _LOGGER.info(
                        "Pump set to BOOST mode (RPM 3) for %s",
                        coordinator.device.device_name,
                    )

                # Refresh coordinator after control
                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error controlling pump for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(f"Failed to control pump: {err}")

    async def control_heater(self, call: ServiceCall) -> None:
        """Control heater operation.

        Args:
            call: Service call with device_id, action, target_temperature.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        action = call.data.get("action")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if action == "on":
                    await control.set_heater_on()
                    _LOGGER.info(
                        "Heater turned ON for %s",
                        coordinator.device.device_name,
                    )
                elif action == "off":
                    await control.set_heater_off()
                    _LOGGER.info(
                        "Heater turned OFF for %s",
                        coordinator.device.device_name,
                    )

                # Target temperature would require setConfig
                target_temp = call.data.get("target_temperature")
                if target_temp is not None:
                    await control.set_config(
                        {"HEATER_target_temp": target_temp}
                    )
                    _LOGGER.info(
                        "Heater target temperature set to %.1f°C for %s",
                        target_temp,
                        coordinator.device.device_name,
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error controlling heater for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(f"Failed to control heater: {err}")

    async def control_solar(self, call: ServiceCall) -> None:
        """Control solar heating.

        Args:
            call: Service call with device_id, action, target_temperature.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        action = call.data.get("action")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if action == "on":
                    await control.set_solar_on()
                    _LOGGER.info(
                        "Solar turned ON for %s",
                        coordinator.device.device_name,
                    )
                elif action == "off":
                    await control.set_solar_off()
                    _LOGGER.info(
                        "Solar turned OFF for %s",
                        coordinator.device.device_name,
                    )

                # Target temperature
                target_temp = call.data.get("target_temperature")
                if target_temp is not None:
                    await control.set_config(
                        {"SOLAR_target_temp": target_temp}
                    )
                    _LOGGER.info(
                        "Solar target temperature set to %.1f°C for %s",
                        target_temp,
                        coordinator.device.device_name,
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error controlling solar for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(f"Failed to control solar: {err}")

    async def control_cover(self, call: ServiceCall) -> None:
        """Control pool cover.

        Args:
            call: Service call with device_id, action.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        action = call.data.get("action", "open")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if action == "open":
                    await control.set_cover_open()
                    _LOGGER.info(
                        "Cover OPEN command sent to %s",
                        coordinator.device.device_name,
                    )
                elif action == "close":
                    await control.set_cover_close()
                    _LOGGER.info(
                        "Cover CLOSE command sent to %s",
                        coordinator.device.device_name,
                    )
                elif action == "stop":
                    await control.set_cover_stop()
                    _LOGGER.info(
                        "Cover STOP command sent to %s",
                        coordinator.device.device_name,
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error controlling cover for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(f"Failed to control cover: {err}")

    async def control_backwash(self, call: ServiceCall) -> None:
        """Control backwash cycle.

        Args:
            call: Service call with device_id, action.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        action = call.data.get("action", "run")

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                if action == "run":
                    await control.set_backwash_run()
                    _LOGGER.info(
                        "Backwash cycle started for %s",
                        coordinator.device.device_name,
                    )
                elif action == "abort":
                    await control.set_backwash_abort()
                    _LOGGER.info(
                        "Backwash cycle aborted for %s",
                        coordinator.device.device_name,
                    )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error controlling backwash for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(f"Failed to control backwash: {err}")

    async def manual_dosing(self, call: ServiceCall) -> None:
        """Trigger manual dosing.

        Args:
            call: Service call with device_id, dosing_system, runtime_seconds.
        """
        device_ids = as_device_id_list(call.data.get("device_id"))
        coordinators = self._get_coordinators(device_ids)

        dosing_system = call.data.get("dosing_system")
        runtime = call.data.get("runtime_seconds", 30)

        dosing_index = DOSING_INDEX_MAP.get(dosing_system)
        if dosing_index is None:
            raise HomeAssistantError(
                f"Unknown dosing system: {dosing_system}"
            )

        for coordinator in coordinators:
            try:
                control = VioletControlClient(coordinator.device._api)

                await control.trigger_manual_dosing(dosing_index, runtime)
                _LOGGER.info(
                    "Manual dosing started: %s for %ds on %s",
                    dosing_system,
                    runtime,
                    coordinator.device.device_name,
                )

                await coordinator.async_request_refresh()

            except Exception as err:
                _LOGGER.error(
                    "Error triggering dosing for %s: %s",
                    coordinator.device.device_name,
                    err,
                )
                raise HomeAssistantError(
                    f"Failed to trigger dosing: {err}"
                )
