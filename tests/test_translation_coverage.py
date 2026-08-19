"""Every value the controller documents must reach the user in his language.

Reported on the forum for 2.5.4: "die Übersetzung der Entitätsnamen ist nicht
konsistent/vollständig, teilweise sind die noch englisch bei deutscher HA".
Keys without a translation fall back to a name built from the key itself
("MEMORY_USED" -> "Memory Used"), which is what a German installation showed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from custom_components.violet_pool_controller import const_sensors
from custom_components.violet_pool_controller.sensor import _HARDWARE_FLAG_KEYS
from custom_components.violet_pool_controller.sensor_modules import romcode_sensor_index

COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"
SPEC = Path(__file__).parent / "getReadings_spec.json"

# Predefined tables the sensor platform merges before falling back to the key.
_PREDEFINED_TABLES = (
    "TEMP_SENSORS",
    "WATER_CHEM_SENSORS",
    "ONEWIRE_ROMCODE_SENSORS",
    "ANALOG_SENSORS",
    "STATUS_SENSORS",
    "RUNTIME_SENSORS",
    "DOSING_STATS_SENSORS",
    "SYSTEM_SENSORS",
    "DOSING_STATE_SENSORS",
    "COMPOSITE_STATE_SENSORS",
    "EXTRA_DIAGNOSTIC_SENSORS",
    "ANALOG_RULE_SENSORS",
    "TEMP_RULE_SENSORS",
)

# Values the controller reports but ``getReadings_spec.json`` does not list.
# They come from the reference payload of the API package and from what users
# reported seeing in Home Assistant.
UNDOCUMENTED_KEYS = (
    "MEMORY_USED",
    "CONFIGCHANGEMARKER",
    "CURRENT_TIME_UNIX",
    "HW_SERIAL_CARRIER",
    "HW_VERSION_CARRIER",
    "INPUTz1z2",
    "LIGHTSTATE",
    "PUMPPRIOSTATE",
    "REFILL_STATE",
    "SW_UPDATE_AVAILABLE",
    "SYSTEM_carrier_alive_count",
    "SYSTEM_dosagemodule_alive_count",
    "SYSTEM_ext1module_alive_count",
    "HEATER_set_temp",
    "SOLAR_maxtemp",
)

# The sensor platform never creates these.
_SKIPPED_KEYS = frozenset({f"onewire{i}_state" for i in range(1, 13)}) | _HARDWARE_FLAG_KEYS


def _predefined() -> dict[str, dict]:
    """Return the merged predefined sensor tables."""
    merged: dict[str, dict] = {}
    for table in _PREDEFINED_TABLES:
        merged.update(getattr(const_sensors, table))
    return merged


def _expand(key: str) -> set[str]:
    """Return every key a documented family stands for.

    The specification lists one member per family ("all other DOS_4_PHM options
    are the same as DOS_1_CL") - the controller reports all of them.
    """
    keys = {key}
    if match := re.match(r"^onewire(?:1|12)_(.*)$", key):
        keys |= {f"onewire{i}_{match.group(1)}" for i in range(1, 13)}
    if match := re.match(r"^DOS_1_CL(_.*)?$", key):
        suffix = match.group(1) or ""
        keys |= {
            f"DOS_{number}_{name}{suffix}"
            for number, name in ((1, "CL"), (2, "ELO"), (4, "PHM"), (5, "PHP"), (6, "FLOC"))
        }
    if match := re.match(r"^(DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE(?:_STOPWATCH)?)\d$", key):
        keys |= {f"{match.group(1)}{i}" for i in range(1, 9)}
    if match := re.match(r"^EXT1_\d(_.*)?$", key):
        suffix = match.group(1) or ""
        keys |= {f"EXT{bank}_{i}{suffix}" for bank in (1, 2) for i in range(1, 9)}
    if match := re.match(r"^PUMP_RPM_\d(_.*)?$", key):
        suffix = match.group(1) or ""
        keys |= {f"PUMP_RPM_{i}{suffix}" for i in range(4)}
    return keys


def _controller_keys() -> set[str]:
    """Return every controller key the integration can turn into a sensor."""
    documented = set()
    for entry in json.loads(SPEC.read_text(encoding="utf-8")):
        key = str(entry["key"]).strip()
        if re.match(r"^[A-Za-z]", key):
            documented |= _expand(key)
    return (documented | set(UNDOCUMENTED_KEYS)) - _SKIPPED_KEYS


def _translation_key(key: str, predefined: dict[str, dict]) -> str:
    """Return the translation key the sensor platform uses for a reading."""
    index = romcode_sensor_index(key)
    if index is not None:
        return f"onewire{index}_romcode"
    entry = predefined.get(key)
    if entry and entry.get("translation_key"):
        return str(entry["translation_key"])
    return key.lower()


def _names(language: str) -> dict[str, dict]:
    """Return the sensor names of one translation file."""
    path = COMPONENT_DIR / "translations" / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))["entity"]["sensor"]


@pytest.mark.parametrize("language", ["de", "en"])
def test_every_documented_reading_has_a_name(language: str) -> None:
    """No reading may fall back to a name built from its raw key."""
    predefined = _predefined()
    names = _names(language)

    missing = sorted(
        f"{key} -> {_translation_key(key, predefined)}"
        for key in _controller_keys()
        if _translation_key(key, predefined) not in names
    )

    assert not missing, f"{language}.json has no name for: {missing}"


def test_german_covers_every_english_name() -> None:
    """A key translated in English must not stay English in German."""
    english = _names("en")
    german = _names("de")

    missing = sorted(set(english) - set(german))

    assert not missing, f"de.json is missing: {missing}"


def test_the_reported_keys_are_translated() -> None:
    """The names the forum report named explicitly."""
    german = _names("de")

    assert german["memory_used"]["name"] == "Belegter Arbeitsspeicher"
    assert german["onewire1_romcode"]["name"] == "OneWire-ROM-Code 1"
    # "Bathing AI" watches the overflow tank; the name now says so.
    assert "Überlaufbehälter" in german["bathing_ai_last_level"]["name"]
