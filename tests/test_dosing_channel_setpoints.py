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
    active_dosing_channels,
)
from custom_components.violet_pool_controller.number import VioletNumber, electrolysis_twin

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
            # Both channels in use: the chlorine channel stays the primary
            # one - the electrolysis setpoint gets a second entity instead of
            # replacing this one (see TestBothChannelsActive).
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


class TestBothChannelsActive:
    """An electrolysis cell and a chlorine pump on the same pool.

    Raised on the forum for 2.5.4: "es können aber auch beide Optionen
    simultan benutzt werden". The controller then keeps two independent
    setpoints. Reporting a single channel would leave one of them unreachable
    in Home Assistant - there is no entity that reads or writes it.
    """

    BOTH = {"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "1"}

    def test_both_channels_are_reported(self) -> None:
        """Neither channel may be dropped when both are enabled."""
        assert active_dosing_channels(self.BOTH) == (CHANNEL_CHLORINE, CHANNEL_ELECTROLYSIS)

    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ({"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "0"}, (CHANNEL_CHLORINE,)),
            (
                {"DOSAGE_chlorine_use": "0", "DOSAGE_electrolysis_use": "1"},
                (CHANNEL_ELECTROLYSIS,),
            ),
            # Nothing flagged - the chlorine channel is what the integration
            # used before the flags were read at all.
            ({}, (CHANNEL_CHLORINE,)),
            ({"DOSAGE_chlorine_use": "0", "DOSAGE_electrolysis_use": "0"}, (CHANNEL_CHLORINE,)),
        ],
    )
    def test_single_channel_setups_are_unchanged(self, data: dict, expected: tuple) -> None:
        """One channel enabled must still report exactly that one."""
        assert active_dosing_channels(data) == expected

    def test_missing_data(self) -> None:
        """No data at all must not raise."""
        assert active_dosing_channels(None) == (CHANNEL_CHLORINE,)

    def test_the_primary_entity_keeps_the_chlorine_setpoint(self) -> None:
        """The entity that already exists must not change what it shows."""
        number = _make_number(
            ORP_SETPOINT,
            {
                **self.BOTH,
                "DOSAGE_chlorine_setpoint_orp": 770,
                "DOSAGE_electrolysis_setpoint_orp": 710,
            },
        )
        assert number.native_value == 770

    def test_the_second_entity_reads_the_electrolysis_setpoint(self) -> None:
        """The pinned entity always reports its own channel."""
        number = _make_number(
            {**ORP_SETPOINT, "pinned_to_electrolysis": True},
            {
                **self.BOTH,
                "DOSAGE_chlorine_setpoint_orp": 770,
                "DOSAGE_electrolysis_setpoint_orp": 710,
            },
        )
        assert number.native_value == 710

    async def test_the_second_entity_writes_the_electrolysis_key(self) -> None:
        """A write from the second entity must not land on the chlorine key."""
        number = _make_number(
            {**ORP_SETPOINT, "pinned_to_electrolysis": True},
            {**self.BOTH, "DOSAGE_electrolysis_setpoint_orp": 710},
        )
        api = number.device.api
        api.set_target_value = AsyncMock(return_value={"success": True})
        api.set_orp_target = AsyncMock(return_value={"success": True})
        number._delayed_refresh = AsyncMock()
        number.async_write_ha_state = MagicMock()

        await number.async_set_native_value(720)
        await asyncio.sleep(0)

        api.set_target_value.assert_awaited_once_with("DOSAGE_electrolysis_setpoint_orp", 720)
        api.set_orp_target.assert_not_awaited()

    def test_the_chlorine_setpoint_gets_a_second_entity_too(self) -> None:
        """Both setpoints are per channel, not just the ORP one."""
        number = _make_number(
            {**CHLORINE_SETPOINT, "pinned_to_electrolysis": True},
            {
                **self.BOTH,
                "DOSAGE_chlorine_lowerval_cl": 0.1,
                "DOSAGE_electrolysis_setpoint_chlorine": 0.6,
            },
        )
        assert number.native_value == 0.6


class TestElectrolysisTwin:
    """electrolysis_twin() - whether the second entity gets created at all."""

    BOTH = {"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "1"}

    def test_dual_dosing_produces_a_twin(self) -> None:
        """Both channels enabled: the setpoint needs a second entity."""
        twin = electrolysis_twin(ORP_SETPOINT, self.BOTH)

        assert twin is not None
        assert twin["key"] == "orp_setpoint_electrolysis"
        assert twin["translation_key"] == "orp_setpoint_electrolysis"
        assert twin["pinned_to_electrolysis"] is True
        # The twin must keep the range and unit of the setpoint it copies.
        assert twin["min_value"] == ORP_SETPOINT["min_value"]
        assert twin["max_value"] == ORP_SETPOINT["max_value"]

    def test_the_twin_has_its_own_unique_id(self) -> None:
        """Two entities sharing a key would collide in the registry."""
        twin = electrolysis_twin(ORP_SETPOINT, self.BOTH)

        assert twin is not None
        assert twin["key"] != ORP_SETPOINT["key"]

    @pytest.mark.parametrize(
        "data",
        [
            {"DOSAGE_chlorine_use": "1", "DOSAGE_electrolysis_use": "0"},
            {"DOSAGE_chlorine_use": "0", "DOSAGE_electrolysis_use": "1"},
            {},
            None,
        ],
    )
    def test_a_single_channel_gets_no_twin(self, data: dict | None) -> None:
        """One channel is served by the entity that already exists."""
        assert electrolysis_twin(ORP_SETPOINT, data) is None

    def test_setpoints_without_a_counterpart_get_no_twin(self) -> None:
        """The pH setpoint is not kept per dosing channel."""
        ph = next(item for item in SETPOINT_DEFINITIONS if item["key"] == "ph_setpoint")

        assert electrolysis_twin(ph, self.BOTH) is None

    @pytest.mark.parametrize("language", ["de", "en"])
    def test_the_twin_names_are_translated(self, language: str) -> None:
        """An untranslated key falls back to a name built from the key."""
        import json
        from pathlib import Path

        path = (
            Path(__file__).parent.parent
            / "custom_components"
            / "violet_pool_controller"
            / "translations"
            / f"{language}.json"
        )
        names = json.loads(path.read_text(encoding="utf-8"))["entity"]["number"]

        for setpoint in (ORP_SETPOINT, CHLORINE_SETPOINT):
            twin = electrolysis_twin(setpoint, self.BOTH)
            assert twin is not None
            assert twin["translation_key"] in names
