"""The mode selects must offer options the controller can actually take.

Four problems were reported for this platform:

* the dosing selects offered "on", which sent the very same enable request as
  "auto" while the read path could only ever report "auto" - so the selection
  snapped back on the next poll;
* the flocculant select wrote ``DOSAGE_floc_use`` but read the ``DOS_6_FLOC``
  output state, so an enabled-but-idle channel showed "off";
* the PV surplus select offered "auto", which the API rewrites to OFF;
* the heater and solar selects reported a target temperature from keys the
  controller does not have.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.select import SelectEntityDescription
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DOMAIN,
    SELECT_CONTROLS,
)
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData
from custom_components.violet_pool_controller.select import (
    MODE_AUTO,
    MODE_OFF,
    MODE_ON,
    VioletSelect,
)

DOSING_DEVICE_KEYS = ("DOS_1_CL", "DOS_2_ELO", "DOS_4_PHM", "DOS_5_PHP")


def _select(hass, device_key: str, data: dict, **kwargs) -> VioletSelect:
    """Build a select entity on a mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"},
    )
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.device_info = {}
    coordinator.device.request_config_refresh = MagicMock()
    coordinator.device.api.set_config = AsyncMock(return_value={"success": True})
    coordinator.device.api.set_dosage_enabled = AsyncMock(return_value={"success": True})
    coordinator.device.api.set_switch_state = AsyncMock(return_value={"success": True})
    coordinator.last_update_success = True
    coordinator.device.available = True
    entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

    description = SelectEntityDescription(key=f"{device_key.lower()}_mode", name=device_key)
    entity = VioletSelect(coordinator, entry, description, device_key, **kwargs)
    entity.async_write_ha_state = MagicMock()
    # The delayed refresh sleeps for half a second in a background task; the
    # tests here are about what is sent, not about when it is confirmed.
    entity._delayed_refresh = AsyncMock()
    return entity


async def _choose(entity: VioletSelect, option: str) -> None:
    """Pick an option and let the scheduled refresh task finish."""
    await entity.async_select_option(option)
    await asyncio.sleep(0)


class TestDosingSelectOptions:
    """A dosing channel is enabled or disabled - there is no "on"."""

    @pytest.mark.parametrize("device_key", DOSING_DEVICE_KEYS)
    def test_options_are_off_and_auto(self, hass, device_key) -> None:
        """Offering "on" produced a selection that always snapped back."""
        entity = _select(hass, device_key, {device_key: "0"})

        assert entity.options == [MODE_OFF, MODE_AUTO]

    def test_enabled_channel_reads_auto(self, hass) -> None:
        """The enable flag is what the select writes, so it is what it reads."""
        entity = _select(hass, "DOS_1_CL", {"DOSAGE_chlorine_use": "1", "DOS_1_CL": "0"})

        assert entity.current_option == MODE_AUTO

    def test_disabled_channel_reads_off(self, hass) -> None:
        """A disabled channel is off even while its output still reports a state."""
        entity = _select(hass, "DOS_1_CL", {"DOSAGE_chlorine_use": "0", "DOS_1_CL": "4"})

        assert entity.current_option == MODE_OFF

    async def test_auto_enables_the_channel(self, hass) -> None:
        """Picking auto enables dosing; picking off disables it."""
        entity = _select(hass, "DOS_4_PHM", {"DOSAGE_phminus_use": "0"})

        await _choose(entity, MODE_AUTO)
        entity.device.api.set_dosage_enabled.assert_awaited_once_with("pH-", enabled=True)

        await _choose(entity, MODE_OFF)
        assert entity.device.api.set_dosage_enabled.await_args.kwargs == {"enabled": False}

    async def test_write_forces_a_config_refresh(self, hass) -> None:
        """getConfig values are cached for a minute; a write must invalidate that."""
        entity = _select(hass, "DOS_4_PHM", {"DOSAGE_phminus_use": "0"})

        await _choose(entity, MODE_AUTO)

        entity.coordinator.device.request_config_refresh.assert_called_once()


class TestFlocculantSelect:
    """The flocculant select is binary and lives entirely in the config flag."""

    def test_enabled_but_idle_reads_on(self, hass) -> None:
        """DOS_6_FLOC is the output state; an idle pump does not mean disabled."""
        entity = _select(
            hass,
            "DOS_6_FLOC",
            {"DOSAGE_floc_use": "1", "DOS_6_FLOC": "0"},
            is_binary=True,
        )

        assert entity.options == [MODE_OFF, MODE_ON]
        assert entity.current_option == MODE_ON

    def test_disabled_reads_off(self, hass) -> None:
        """A cleared flag is off regardless of the output state."""
        entity = _select(
            hass, "DOS_6_FLOC", {"DOSAGE_floc_use": "0", "DOS_6_FLOC": "4"}, is_binary=True
        )

        assert entity.current_option == MODE_OFF

    async def test_write_forces_a_config_refresh(self, hass) -> None:
        """The flag is a getConfig value too."""
        entity = _select(hass, "DOS_6_FLOC", {"DOSAGE_floc_use": "0"}, is_binary=True)

        await _choose(entity, MODE_ON)

        entity.device.api.set_config.assert_awaited_once_with({"DOSAGE_floc_use": "1"})
        entity.coordinator.device.request_config_refresh.assert_called_once()


class TestPvSurplusSelect:
    """PV surplus knows on and off only."""

    def test_declared_binary_in_the_table(self) -> None:
        """The API rewrites AUTO to OFF, so "auto" must not be offered."""
        entry = next(c for c in SELECT_CONTROLS if c["key"] == "pvsurplus_mode")

        assert entry.get("binary") is True

    @pytest.mark.parametrize(("raw", "expected"), [("0", MODE_OFF), ("1", MODE_ON), ("2", MODE_ON)])
    def test_own_state_scheme(self, hass, raw, expected) -> None:
        """0 = off, 1 = on via digital input, 2 = on via HTTP request."""
        entity = _select(hass, "PVSURPLUS", {"PVSURPLUS": raw}, is_binary=True)

        assert entity.current_option == expected


class TestCompositeStates:
    """Composite states carry the state code in their leading part."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("4|PUMP_ANTI_FREEZE", MODE_ON),
            ("6|PUMP_MANUAL", MODE_OFF),
            ("3|PUMP_ANTI_FREEZE", MODE_AUTO),
            ("1", MODE_AUTO),
        ],
    )
    def test_current_option_from_composite_state(self, hass, raw, expected) -> None:
        """A composite state used to fall through into the string branch."""
        entity = _select(hass, "PUMP", {"PUMP": raw})

        assert entity.current_option == expected


class TestExtraStateAttributes:
    """The attributes must read keys the controller actually reports."""

    def test_heater_target_temperature(self, hass) -> None:
        """HEATER_TARGET_TEMP does not exist; the real key is HEATER_set_temp."""
        entity = _select(hass, "HEATER", {"HEATER": "1", "HEATER_set_temp": "38"})

        assert entity.extra_state_attributes["target_temp"] == 38.0

    def test_solar_target_temperature(self, hass) -> None:
        """The controller reports the solar setpoint as SOLAR_maxtemp."""
        entity = _select(hass, "SOLAR", {"SOLAR": "1", "SOLAR_maxtemp": "42.5"})

        assert entity.extra_state_attributes["target_temp"] == 42.5

    def test_unknown_target_temperature_is_not_invented(self, hass) -> None:
        """A missing setpoint must not be reported as a plausible default."""
        entity = _select(hass, "HEATER", {"HEATER": "1"})

        assert entity.extra_state_attributes["target_temp"] is None

    def test_pump_speed_ignores_off_states(self, hass) -> None:
        """PUMP_RPM_n holds a state code: 2, 5 and 6 all mean off."""
        entity = _select(hass, "PUMP", {"PUMP": "1", "PUMP_RPM_2": "6", "PUMP_RPM_1": "0"})

        assert entity.extra_state_attributes["speed"] is None

    def test_pump_speed_reports_the_running_level(self, hass) -> None:
        """A level reporting an on code is the active speed."""
        entity = _select(hass, "PUMP", {"PUMP": "1", "PUMP_RPM_2": "4", "PUMP_RPM_1": "0"})

        assert entity.extra_state_attributes["speed"] == 2
