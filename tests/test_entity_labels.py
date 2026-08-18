"""Entity labels must say what the value actually is.

Reported on the forum after 2.4.0: the electrolysis channel showed
"Elektrolyse Kanisterinhalt (ml)" while the controller reports the remaining
runtime of the electrolysis cell in hours there - the channel has no canister
at all. The audit that followed turned up two more classes of wrong label:
readings named after something they are not (a 0/1 configuration flag called
"Verbrauch"), and entities whose translation key does not exist, so every user
saw the German fallback name regardless of their language.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from custom_components.violet_pool_controller import const_features, const_sensors
from custom_components.violet_pool_controller.sensor_modules.base import (
    _build_sensor_description,
)

COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"

# Tables of entity definitions, by the platform their translations live under.
SENSOR_TABLES = {
    name: table
    for name, table in vars(const_sensors).items()
    if name.endswith("_SENSORS") and isinstance(table, dict)
}
PLATFORM_TABLES = {
    "binary_sensor": const_features.BINARY_SENSORS,
    "select": const_features.SELECT_CONTROLS,
    "switch": const_features.SWITCHES,
    "light": const_features.DMX_LIGHTS,
}

# Languages that are expected to carry every entity name. The remaining files
# are partial on purpose; Home Assistant falls back to English for those.
COMPLETE_LANGUAGES = ("de", "en")


def load(language: str) -> dict:
    """Return the entity section of one translation file."""
    path = COMPONENT_DIR / "translations" / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8")).get("entity", {})


def sensor_keys() -> set[str]:
    """Return every translation key the sensor platform asks for."""
    return {
        entry["translation_key"]
        for table in SENSOR_TABLES.values()
        for entry in table.values()
        if isinstance(entry, dict) and entry.get("translation_key")
    }


class TestEveryTranslationKeyResolves:
    """A key without a translation silently falls back to the German name."""

    @pytest.mark.parametrize("language", COMPLETE_LANGUAGES)
    def test_sensor_keys_are_translated(self, language: str) -> None:
        """Every sensor definition must find its name in de and en."""
        missing = sorted(sensor_keys() - set(load(language).get("sensor", {})))

        assert not missing, f"{language}.json is missing sensor names: {missing}"

    @pytest.mark.parametrize("language", COMPLETE_LANGUAGES)
    @pytest.mark.parametrize("platform", sorted(PLATFORM_TABLES))
    def test_other_platform_keys_are_translated(self, language: str, platform: str) -> None:
        """The same guarantee for the control platforms."""
        used = {
            entry["translation_key"]
            for entry in PLATFORM_TABLES[platform]
            if entry.get("translation_key")
        }
        missing = sorted(used - set(load(language).get(platform, {})))

        assert not missing, f"{language}.json is missing {platform} names: {missing}"

    def test_remaining_range_keys_keep_their_prefix(self) -> None:
        """These were generated as "1_cl_remaining_range" and never resolved."""
        for channel in ("1_cl", "2_elo", "4_phm", "5_php", "6_floc"):
            key = f"DOS_{channel.upper()}_REMAINING_RANGE"
            assert const_sensors.EXTRA_DIAGNOSTIC_SENSORS[key]["translation_key"] == (
                f"dos_{channel}_remaining_range"
            )


class TestElectrolysisCellIsNotACanister:
    """The forum report: the ELO channel has no canister."""

    def test_cell_runtime_is_reported_in_hours(self) -> None:
        """The value is the cell's remaining runtime, so it is a duration."""
        description = _build_sensor_description(
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML",
            1234,
            const_sensors.DOSING_STATS_SENSORS,
            translation_key="dos_2_elo_total_can",
        )

        assert description.native_unit_of_measurement == "h"
        assert description.device_class == "duration"

    def test_millilitres_stay_on_the_liquid_channels(self) -> None:
        """Chlorine, pH and flocculant really do dose out of a canister."""
        for channel in ("DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC"):
            assert const_sensors.UNIT_MAP[f"{channel}_TOTAL_CAN_AMOUNT_ML"] == "ml"

    def test_daily_electrolysis_figure_claims_no_unit(self) -> None:
        """It is a cell figure, not millilitres of liquid."""
        assert "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML" not in const_sensors.UNIT_MAP

    @pytest.mark.parametrize("language", COMPLETE_LANGUAGES)
    @pytest.mark.parametrize(
        "key", ["dos_2_elo_total_can", "dos_2_elo_daily", "dos_2_elo_last_can_reset"]
    )
    def test_no_canister_wording_on_the_electrolysis_channel(
        self, language: str, key: str
    ) -> None:
        """Nothing on this channel may be called a canister."""
        name = load(language)["sensor"][key]["name"].lower()

        assert "kanister" not in name
        assert "canister" not in name
        assert "(ml)" not in name


class TestNamesMatchTheReading:
    """Labels that described something other than the value behind them."""

    @pytest.mark.parametrize("language", COMPLETE_LANGUAGES)
    @pytest.mark.parametrize(
        "key", ["dos_1_cl_use", "dos_2_elo_use", "dos_4_phm_use", "dos_5_php_use", "dos_6_floc_use"]
    )
    def test_use_flags_are_not_called_consumption(self, language: str, key: str) -> None:
        """DOS_*_USE is a 0/1 "configured in the system" flag, not a consumption."""
        name = load(language)["sensor"][key]["name"].lower()

        assert "verbrauch" not in name
        assert "usage" not in name

    @pytest.mark.parametrize("language", COMPLETE_LANGUAGES)
    def test_carrier_board_entity_names_the_temperature(self, language: str) -> None:
        """CPU_TEMP_CARRIER is a temperature, not "the carrier board"."""
        name = load(language)["sensor"]["cpu_temp_carrier"]["name"].lower()

        assert "temperatur" in name or "temperature" in name
