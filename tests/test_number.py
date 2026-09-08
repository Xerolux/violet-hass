"""Setpoint number entities must report the controller, not a plausible guess.

Two problems were reported for this platform:

* a successful write appeared to revert for up to a minute, because getConfig
  values are only re-read every ``CONFIG_REFRESH_INTERVAL`` seconds and nothing
  seeded the coordinator's setpoint cache;
* ``native_value`` fell back to the configured default (pH 7.2, ORP 700 mV,
  pump speed 2) whenever the controller reported nothing, which contradicts the
  read-only security model in SECURITY.md.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.number import NumberEntityDescription
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DOMAIN,
    SETPOINT_DEFINITIONS,
)
from custom_components.violet_pool_controller.number import VioletNumber
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData


def _setpoint(key: str) -> dict:
    """Return the shipped definition of one setpoint."""
    return next(d for d in SETPOINT_DEFINITIONS if d["key"] == key)


def _number(hass, setpoint_key: str, data: dict) -> VioletNumber:
    """Build a number entity for a shipped setpoint on a mocked coordinator."""
    config = _setpoint(setpoint_key)

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"},
    )
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.device_info = {}
    coordinator.last_update_success = True
    coordinator.device.available = True
    coordinator.update_setpoint_cache = MagicMock()
    for method in (
        "set_ph_target",
        "set_orp_target",
        "set_min_chlorine_level",
        "set_pump_speed",
        "set_device_temperature",
        "set_target_value",
        "set_dosing_parameters",
    ):
        setattr(coordinator.device.api, method, AsyncMock(return_value={"success": True}))
    entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

    description = NumberEntityDescription(
        key=str(config["key"]),
        name=str(config["name"]),
        native_unit_of_measurement=config.get("unit_of_measurement"),
    )
    entity = VioletNumber(coordinator, entry, description, config)
    entity.async_write_ha_state = MagicMock()
    # The delayed refresh sleeps in a background task; these tests are about
    # what is sent and cached, not about when it is confirmed.
    entity._delayed_refresh = AsyncMock()
    return entity


async def _write(entity: VioletNumber, value: float) -> None:
    """Write a value and let the scheduled refresh task finish."""
    await entity.async_set_native_value(value)
    await asyncio.sleep(0)


class TestSetpointCacheIsSeeded:
    """A write must be visible before the getConfig cache expires."""

    @pytest.mark.parametrize(
        ("setpoint_key", "value", "expected_key"),
        [
            ("ph_setpoint", 7.4, "DOSAGE_phminus_setpoint"),
            ("orp_setpoint", 750, "DOSAGE_chlorine_setpoint_orp"),
            ("chlorine_setpoint", 0.8, "DOSAGE_chlorine_lowerval_cl"),
            ("heater_target_temp", 30.0, "HEATER_set_temp"),
            ("solar_target_temp", 32.0, "SOLAR_maxtemp"),
            ("chlorine_canister_volume", 5000, "DOS_1_CL_TOTAL_CAN_AMOUNT_ML"),
        ],
    )
    async def test_write_seeds_the_coordinator_cache(
        self, hass, setpoint_key, value, expected_key
    ) -> None:
        """The cache key must be the config key the write actually landed in."""
        entity = _number(hass, setpoint_key, {"pH_value": 7.2, "orp_value": 700})

        await _write(entity, value)

        entity.coordinator.update_setpoint_cache.assert_called_once()
        cached_key, cached_value = entity.coordinator.update_setpoint_cache.call_args.args
        assert cached_key == expected_key
        assert cached_value == pytest.approx(value)

    async def test_pump_speed_is_not_a_config_value(self, hass) -> None:
        """Pump speed is an output command, so there is no config key to seed."""
        entity = _number(hass, "pump_speed", {"PUMP": "1"})

        await _write(entity, 3)

        entity.coordinator.update_setpoint_cache.assert_not_called()


class TestNativeValueIsNeverInvented:
    """An unknown setpoint is reported as unknown."""

    @pytest.mark.parametrize(
        "setpoint_key", ["ph_setpoint", "orp_setpoint", "chlorine_setpoint", "pump_speed"]
    )
    def test_missing_setpoint_reports_none(self, hass, setpoint_key) -> None:
        """The default value used to be indistinguishable from a real reading."""
        entity = _number(hass, setpoint_key, {})

        assert entity.native_value is None

    def test_reported_setpoint_is_returned(self, hass) -> None:
        """A value the controller reports is passed through unchanged."""
        entity = _number(hass, "ph_setpoint", {"DOSAGE_phminus_setpoint": "7.35"})

        assert entity.native_value == pytest.approx(7.35)


class TestPumpSpeedLevel:
    """PUMP_RPM_n holds a state code, not an RPM value."""

    def test_off_state_code_is_not_an_active_speed(self, hass) -> None:
        """Code 6 is "manual off"; ">0" used to report speed 2 for it."""
        entity = _number(hass, "pump_speed", {"PUMP_RPM_2": "6", "PUMP_RPM_1": "0"})

        assert entity.native_value is None

    @pytest.mark.parametrize("code", ["1", "3", "4"])
    def test_on_state_codes_report_the_level(self, hass, code) -> None:
        """Codes 1, 3 and 4 mean the speed output is running."""
        entity = _number(hass, "pump_speed", {"PUMP_RPM_2": code})

        assert entity.native_value == 2.0

    def test_no_level_four_is_probed(self, hass) -> None:
        """The controller has PUMP_RPM_0..3; PUMP_RPM_4 does not exist."""
        entity = _number(hass, "pump_speed", {"PUMP_RPM_4": "4"})

        assert entity.native_value is None
