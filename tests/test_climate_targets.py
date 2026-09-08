"""The thermostats must report the controller's setpoint, not invent one.

``_get_target_temperature`` used to substitute a hard-coded 28 °C whenever the
controller's setpoint fell outside a range this file made up (20-35 °C for the
heater, 20-40 °C for solar), and ``async_set_temperature`` silently dropped a
write outside that range. The controller accepts far more, per
``SETPOINT_RANGES`` in the API package.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry
from violet_poolcontroller_api import SETPOINT_RANGES

from custom_components.violet_pool_controller.climate import (
    VioletClimateEntity,
    temperature_range,
)
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DOMAIN,
)
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData


def _climate(hass, climate_type: str, data: dict | None) -> VioletClimateEntity:
    """Build a climate entity on a mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"},
    )
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.data = data
    coordinator._setpoint_cache = {}
    coordinator.device.hardware_config = None
    coordinator.device.device_info = {}
    coordinator.last_update_success = True
    coordinator.device.available = True
    coordinator.device.api.set_device_temperature = AsyncMock(return_value={"success": True})
    coordinator.device.api.set_switch_state = AsyncMock(return_value={"success": True})
    entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

    entity = VioletClimateEntity(coordinator, entry, climate_type)
    entity.async_write_ha_state = MagicMock()
    # The delayed refresh runs in a background task; these tests are about what
    # is sent and reported, not about when the write is confirmed.
    entity._delayed_refresh = AsyncMock()
    return entity


class TestTemperatureLimits:
    """The limits come from the API package, not from a local guess."""

    def test_heater_range_matches_the_api(self, hass) -> None:
        """HEATER_set_temp accepts 5-45 °C."""
        assert temperature_range("HEATER") == SETPOINT_RANGES["HEATER_set_temp"]

    def test_solar_range_matches_the_api(self, hass) -> None:
        """SOLAR_maxtemp accepts 5-55 °C."""
        assert temperature_range("SOLAR") == SETPOINT_RANGES["SOLAR_maxtemp"]

    def test_entity_limits_follow_the_climate_type(self, hass) -> None:
        """A solar absorber must not be capped at the heater's maximum."""
        heater = _climate(hass, "HEATER", {"HEATER": "1"})
        solar = _climate(hass, "SOLAR", {"SOLAR": "1"})

        assert (heater.min_temp, heater.max_temp) == SETPOINT_RANGES["HEATER_set_temp"]
        assert (solar.min_temp, solar.max_temp) == SETPOINT_RANGES["SOLAR_maxtemp"]


class TestTargetTemperatureIsReal:
    """The reported setpoint is the one the controller holds."""

    def test_heater_setpoint_above_the_old_range(self, hass) -> None:
        """38 °C used to be replaced by a fabricated 28 °C."""
        entity = _climate(hass, "HEATER", {"HEATER": "1", "HEATER_set_temp": 38})

        assert entity.target_temperature == 38.0

    def test_solar_setpoint_above_the_old_range(self, hass) -> None:
        """The solar absorber goes higher than the old 40 °C cap."""
        entity = _climate(hass, "SOLAR", {"SOLAR": "1", "SOLAR_maxtemp": 48})

        assert entity.target_temperature == 48.0

    def test_unknown_setpoint_is_unknown(self, hass) -> None:
        """No setpoint field means unknown, not 28 °C."""
        entity = _climate(hass, "HEATER", {"HEATER": "1"})

        assert entity.target_temperature is None

    def test_no_data_is_unknown(self, hass) -> None:
        """An unreachable controller reports nothing at all."""
        entity = _climate(hass, "HEATER", None)

        assert entity.target_temperature is None


class TestSetTemperature:
    """Out-of-range writes are refused loudly, not dropped."""

    async def test_accepts_a_value_the_controller_takes(self, hass) -> None:
        """40 °C is inside the heater's real range."""
        entity = _climate(hass, "HEATER", {"HEATER": "1", "HEATER_set_temp": 28})

        await entity.async_set_temperature(temperature=40.0)
        await asyncio.sleep(0)

        entity.device.api.set_device_temperature.assert_awaited_once_with("HEATER", 40.0)

    async def test_rejects_a_value_outside_the_range(self, hass) -> None:
        """A silent return left the UI showing a value that was never sent."""
        entity = _climate(hass, "HEATER", {"HEATER": "1", "HEATER_set_temp": 28})

        with pytest.raises(ServiceValidationError):
            await entity.async_set_temperature(temperature=60.0)

        entity.device.api.set_device_temperature.assert_not_awaited()


class TestCompositeStates:
    """A running heater must not be reported as idle."""

    @pytest.mark.parametrize(
        ("raw", "mode", "action"),
        [
            ("4", HVACMode.HEAT, HVACAction.HEATING),
            ("4|HEATER_MANUAL", HVACMode.HEAT, HVACAction.HEATING),
            ("1|HEATER_SCHEDULE", HVACMode.AUTO, HVACAction.HEATING),
            ("3|PUMP_ANTI_FREEZE", HVACMode.AUTO, HVACAction.HEATING),
            ("6|HEATER_MANUAL_OFF", HVACMode.OFF, HVACAction.OFF),
            ("2|HEATER_BLOCKED", HVACMode.AUTO, HVACAction.IDLE),
        ],
    )
    def test_hvac_mode_and_action_from_composite_state(self, hass, raw, mode, action) -> None:
        """int() on the whole string returned None and defaulted to idle."""
        entity = _climate(hass, "HEATER", {"HEATER": raw})

        assert entity.hvac_mode == mode
        assert entity.hvac_action == action

    def test_state_constants_are_not_redefined(self) -> None:
        """climate.py used to define STATE_AUTO_ACTIVE = 3 next to a shared 1."""
        from custom_components.violet_pool_controller import climate, state_constants

        assert climate.STATE_AUTO_ACTIVE == state_constants.STATE_AUTO_ACTIVE == 1
