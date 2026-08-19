"""One ROM code per OneWire probe, and never a temperature.

Reported on the forum for 2.5.4: "Es gibt die OneWireRomCode-Entitäten 2 mal.
Einmal richtig mit der ID und einmal fälschlicherweise als Temperatur." The
controller reports the same ROM code under two spellings; only the documented
``onewireN_rcode`` was recognised, so the second one fell through to the
"anything with onewire in its key is a temperature" default and was published
as a second sensor reading 0.0 °C.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.violet_pool_controller.const_sensors import ONEWIRE_ROMCODE_SENSORS
from custom_components.violet_pool_controller.sensor import (
    _create_standard_sensors,
    _select_romcode_keys,
)
from custom_components.violet_pool_controller.sensor_modules import (
    _build_sensor_description,
    romcode_sensor_index,
)

ROM_CODE = "282A71C5C3230681"
SECOND_CODE = "2818701CC124067C"


def _coordinator(data: dict) -> MagicMock:
    """Return a coordinator stub carrying the given readings."""
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}
    coordinator.device.device_name = "Violet Pool Controller"
    coordinator.device.controller_name = "Violet Pool Controller"
    return coordinator


def _config_entry() -> MagicMock:
    """Return a config entry stub."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.title = "Test Pool"
    entry.options.get.side_effect = lambda key, default=None: default
    entry.data.get.side_effect = lambda key, default=None: default
    return entry


def _standard_sensors(data: dict) -> list:
    """Run the standard sensor factory over the given readings."""
    return _create_standard_sensors(
        _coordinator(data),
        _config_entry(),
        {"active_features": set(), "selected_sensors": set(), "create_all": True},
        handled_keys=set(),
    )


class TestRomcodeKeyRecognition:
    """romcode_sensor_index() – every spelling names the same probe."""

    @pytest.mark.parametrize(
        ("key", "index"),
        [
            ("onewire1_rcode", 1),
            ("onewire1_romcode", 1),
            ("onewire1romcode", 1),
            ("Onewire1Romcode", 1),
            ("ONEWIRE12_RCODE", 12),
            ("onewire12_romcode", 12),
        ],
    )
    def test_spellings_resolve_to_the_probe(self, key: str, index: int) -> None:
        """All spellings the firmware uses map onto the probe number."""
        assert romcode_sensor_index(key) == index

    @pytest.mark.parametrize(
        "key",
        [
            "onewire1_value",
            "onewire1_state",
            "onewire13_rcode",  # the controller has 12 probes
            "onewire0_rcode",
            "romcode",
            "CPU_TEMP",
            "",
        ],
    )
    def test_other_keys_are_not_rom_codes(self, key: str) -> None:
        """Nothing else may be swallowed by the ROM-code handling."""
        assert romcode_sensor_index(key) is None


class TestRomcodeDescription:
    """A ROM code identifies the probe; it is not a reading."""

    @pytest.mark.parametrize("key", ["onewire1_rcode", "onewire1_romcode", "onewire1romcode"])
    def test_no_temperature_for_any_spelling(self, key: str) -> None:
        """The unrecognised spelling used to arrive as 0.0 °C."""
        description = _build_sensor_description(key, ROM_CODE, ONEWIRE_ROMCODE_SENSORS)

        assert description.native_unit_of_measurement is None
        assert description.device_class is None
        assert description.state_class is None
        assert description.icon == "mdi:identifier"
        assert description.name == "OneWire ROM Code 1"


class TestOneEntityPerProbe:
    """Several spellings in one payload must not produce several entities."""

    def test_both_spellings_yield_one_sensor(self) -> None:
        """The forum report: the ROM code showed up twice."""
        sensors = _standard_sensors(
            {"onewire1_rcode": ROM_CODE, "onewire1romcode": "0"},
        )
        romcode_sensors = [
            sensor
            for sensor in sensors
            if romcode_sensor_index(sensor.entity_description.key) is not None
        ]

        assert len(romcode_sensors) == 1
        assert romcode_sensors[0].entity_description.key == "onewire1_rcode"
        assert romcode_sensors[0].entity_description.translation_key == "onewire1_romcode"

    def test_the_spelling_carrying_the_code_wins(self) -> None:
        """An empty documented key must not hide the code the controller sent."""
        keys = _select_romcode_keys({"onewire1_rcode": "0", "onewire1_romcode": ROM_CODE})

        assert keys == {1: "onewire1_romcode"}

    def test_the_documented_spelling_breaks_a_tie(self) -> None:
        """With a code under both spellings the documented key is published."""
        keys = _select_romcode_keys(
            {"onewire1romcode": ROM_CODE, "onewire1_rcode": ROM_CODE},
        )

        assert keys == {1: "onewire1_rcode"}

    def test_probes_stay_apart(self) -> None:
        """Deduplication is per probe, not across probes."""
        sensors = _standard_sensors(
            {
                "onewire1_rcode": ROM_CODE,
                "onewire1_romcode": ROM_CODE,
                "onewire2_rcode": SECOND_CODE,
            },
        )
        keys = {
            sensor.entity_description.key
            for sensor in sensors
            if romcode_sensor_index(sensor.entity_description.key) is not None
        }

        assert keys == {"onewire1_rcode", "onewire2_rcode"}

    def test_the_value_stays_the_rom_code(self) -> None:
        """The published sensor shows the code, not a number."""
        sensors = _standard_sensors({"onewire7_romcode": ROM_CODE})
        sensor = next(
            sensor
            for sensor in sensors
            if romcode_sensor_index(sensor.entity_description.key) is not None
        )

        assert sensor.native_value == ROM_CODE
        assert sensor.entity_description.translation_key == "onewire7_romcode"


class TestSensorSelection:
    """A stored selection survives the deduplication."""

    def test_a_selected_losing_spelling_keeps_the_sensor(self) -> None:
        """The user picked the spelling that is no longer published."""
        sensors = _create_standard_sensors(
            _coordinator({"onewire1_rcode": ROM_CODE, "onewire1romcode": "0"}),
            _config_entry(),
            {
                "active_features": set(),
                "selected_sensors": {"onewire1romcode"},
                "create_all": False,
            },
            handled_keys=set(),
        )

        assert [sensor.entity_description.key for sensor in sensors] == ["onewire1_rcode"]

    def test_an_unselected_probe_stays_unselected(self) -> None:
        """Deduplication must not smuggle in a sensor nobody selected."""
        sensors = _create_standard_sensors(
            _coordinator({"onewire1_rcode": ROM_CODE, "onewire1romcode": "0"}),
            _config_entry(),
            {"active_features": set(), "selected_sensors": set(), "create_all": False},
            handled_keys=set(),
        )

        assert sensors == []

    def test_the_selection_list_offers_one_entry_per_probe(self) -> None:
        """The config flow must not ask which spelling the user wants."""
        from custom_components.violet_pool_controller.config_flow_utils import group_sensor_keys

        grouped = group_sensor_keys(["onewire1_rcode", "onewire1romcode", "CPU_TEMP"])
        offered = {key for keys in grouped.values() for key in keys}

        assert offered == {"onewire1_rcode", "CPU_TEMP"}


class TestHardwareFlagsStayBinarySensors:
    """The synthesised HW_* flags are binary sensors, not text sensors."""

    def test_no_duplicate_text_sensor(self) -> None:
        """"Hw Base Module" was an untranslated copy of the binary sensor."""
        sensors = _standard_sensors({"HW_BASE_MODULE": True, "HW_DOSING_MODULE": False})

        assert sensors == []
