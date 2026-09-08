# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/xerolux/violet-hass
# =============================================================================

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower

from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

_PUMP_SPEED_WATT: dict[int, float] = {
    0: 0.0,
    1: 120.0,
    2: 280.0,
    3: 450.0,
}


class VioletPumpPowerSensor(VioletPoolControllerEntity, SensorEntity):
    """Estimated pump power consumption based on current speed level."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        description = SensorEntityDescription(
            key="pump_estimated_power",
            translation_key="pump_estimated_power",
            name="Pump Power (est.)",
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
            entity_registry_enabled_default=False,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        speed = self._get_active_speed()
        if speed is None:
            return 0.0
        return _PUMP_SPEED_WATT.get(speed, 0.0)

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        speed = self._get_active_speed()
        return {
            "speed_level": speed,
            "estimation_note": "Estimated based on pump speed level",
        }

    def _get_active_speed(self) -> int | None:
        """Return the pump speed level whose output currently reports on.

        ``PUMP_RPM_n`` holds a state code, not an RPM value: 2 (rule-blocked),
        5 (emergency off) and 6 (manual off) all mean the output is off, so the
        previous ``> 0`` test reported power draw for a stopped pump.
        """
        return self.get_active_pump_speed()
