"""Setpoints must come from the dosing channel that is actually in charge.

Reported on the forum after 2.5.3: a controller configured to 710 mV showed
770 mV in Home Assistant, and the chlorine setpoint was equally wrong. The pool
produces its chlorine with an electrolysis cell, so the controller keeps the
setpoints under ``DOSAGE_electrolysis_*`` while the integration read the
untouched ``DOSAGE_chlorine_*`` copies.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.number import NumberEntityDescription

from custom_components.violet_pool_controller.const_features import SETPOINT_DEFINITIONS
from custom_components.violet_pool_controller.dosing_channel import (
    CHANNEL_CHLORINE,
    CHANNEL_ELECTROLYSIS,
    active_dosing_channel,
)
from custom_components.violet_pool_controller.number import VioletNumber

ORP_SETPOINT = next(item for item in SETPOINT_DEFINITIONS if item["key"] == "orp_setpoint")
CHLORINE_SETPOINT = next(
    item for item in SETPOINT_DEFINITIONS if item["key"] == "chlorine_setpoint"
)


def _make_number(setpoint_config: dict, data: dict) -> VioletNumber:
    """Build a number entity on top of a mocked coordinator."""
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.available = True
    coordinator.device.device_info = {}
    coordinator.device.device_name = "Violet"
    coordinator.device.controller_name = "Violet"
    coordinator.last_update_success = True

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"

    description = NumberEntityDescription(
        key=setpoint_config["key"],
        name=setpoint_config["name"],
        native_unit_of_measurement=setpoint_config["unit_of_measurement"],
    )
    return VioletNumber(coordinator, config_entry, description, setpoint_config)


class TestActiveDosingChannel:
    """active_dosing_channel() – which channel owns the setpoints."""

    def test_electrolysis_only_switches_channel(self) -> None:
        """Electrolysis on, chlorine pump off → the electrolysis channel."""
        data = {"DOSAGE_chlorine_use": "0", "DOSAGE_electrolysis_use": "1"}
        assert active_dosing_channel(data) == CHANNEL_ELECTROLYSIS

    def test_readings_flags_are_used_as_fallback(self) -> None:
        """Before the first getConfig fetch the DOS_*_USE readings decide."""
        data = {"DOS_1_CL_USE": "0", "DOS_2_ELO_USE": "1"}
        assert active_dosing_channel(data) == CHANNEL_ELECTROLYSIS

    def test_numeric_flags(self) -> None:
        """The controller may report the flags as numbers instead of strings."""
        data = {"DOSAGE_chlorine_use": 0, "DOSAGE_electrolysis_use": 1}
        assert active_dosing_channel(data) == CHANNEL_ELECTROLYSIS

    @pytest.mark.parametrize(
        "data",
        [
            {},
            {"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "0"},
            # Both channels in use: the chlorine keys stay authoritative,
            # which is what the integration has always done.
            {"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "1"},
        ],
    )
    def test_chlorine_stays_the_default(self, data: dict) -> None:
        """Anything but electrolysis-only keeps the chlorine channel."""
        assert active_dosing_channel(data) == CHANNEL_CHLORINE

    def test_missing_data(self) -> None:
        """No data at all must not raise."""
        assert active_dosing_channel(None) == CHANNEL_CHLORINE


class TestSetpointReading:
    """VioletNumber.native_value – the forum report, end to end."""

    def test_orp_reads_the_electrolysis_setpoint(self) -> None:
        """710 mV on the electrolysis channel, not the chlorine channel's 770."""
        number = _make_number(
            ORP_SETPOINT,
            {
                "DOSAGE_chlorine_use": "0",
                "DOSAGE_electrolysis_use": "1",
                "DOSAGE_chlorine_setpoint_orp": 770,
                "DOSAGE_electrolysis_setpoint_orp": 710,
            },
        )
        assert number.native_value == 710

    def test_orp_keeps_the_chlorine_setpoint_for_chlorine_pools(self) -> None:
        """A chlorine-dosing pool must be unaffected by the fix."""
        number = _make_number(
            ORP_SETPOINT,
            {
                "DOSAGE_chlorine_use": "1",
                "DOSAGE_electrolysis_use": "0",
                "DOSAGE_chlorine_setpoint_orp": 770,
                "DOSAGE_electrolysis_setpoint_orp": 710,
            },
        )
        assert number.native_value == 770

    def test_chlorine_reads_the_electrolysis_setpoint(self) -> None:
        """The mg/l setpoint follows the same channel as the ORP one."""
        number = _make_number(
            CHLORINE_SETPOINT,
            {
                "DOSAGE_chlorine_use": "0",
                "DOSAGE_electrolysis_use": "1",
                "DOSAGE_chlorine_lowerval_cl": 0.1,
                "DOSAGE_electrolysis_setpoint_chlorine": 0.6,
            },
        )
        assert number.native_value == 0.6

    def test_falls_back_to_the_chlorine_keys_when_absent(self) -> None:
        """Firmware without the electrolysis keys keeps the old behaviour."""
        number = _make_number(
            ORP_SETPOINT,
            {
                "DOSAGE_chlorine_use": "0",
                "DOSAGE_electrolysis_use": "1",
                "DOSAGE_chlorine_setpoint_orp": 770,
            },
        )
        assert number.native_value == 770


class TestSetpointWriting:
    """Writes must land on the channel the value was read from."""

    async def test_orp_write_targets_the_electrolysis_key(self) -> None:
        """set_orp_target() would write the unused chlorine key."""
        number = _make_number(
            ORP_SETPOINT,
            {
                "DOSAGE_chlorine_use": "0",
                "DOSAGE_electrolysis_use": "1",
                "DOSAGE_electrolysis_setpoint_orp": 710,
            },
        )
        api = number.device.api
        api.set_target_value = AsyncMock(return_value={"success": True})
        number._delayed_refresh = AsyncMock()
        number.async_write_ha_state = MagicMock()

        await number.async_set_native_value(720)
        await asyncio.sleep(0)  # let the follow-up refresh task finish

        api.set_target_value.assert_awaited_once_with("DOSAGE_electrolysis_setpoint_orp", 720)

    async def test_orp_write_keeps_the_api_helper_for_chlorine_pools(self) -> None:
        """Chlorine pools keep using the dedicated ORP helper."""
        number = _make_number(
            ORP_SETPOINT,
            {
                "DOSAGE_chlorine_use": "1",
                "DOSAGE_electrolysis_use": "0",
                "DOSAGE_chlorine_setpoint_orp": 770,
            },
        )
        api = number.device.api
        api.set_orp_target = AsyncMock(return_value={"success": True})
        number._delayed_refresh = AsyncMock()
        number.async_write_ha_state = MagicMock()

        await number.async_set_native_value(720)
        await asyncio.sleep(0)  # let the follow-up refresh task finish

        api.set_orp_target.assert_awaited_once_with(720.0)
