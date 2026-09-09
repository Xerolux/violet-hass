"""State codes belong on the platform that models them, and only there.

The controller reports a digital input, a DMX scene, a switching rule and a
dosing channel's configured flag as small integers. The sensor platform turned
each of them into a numeric sensor with ``state_class = measurement``, so Home
Assistant recorded long-term statistics for values where the arithmetic is
meaningless - the mean of scene 3 and scene 7 is scene 5.

2.7.0 removed the state class, which made Home Assistant raise a repair issue
per entity ("... no longer has a state class"): 41 of them on a fully equipped
controller. 2.7.1 removes the entities instead, because every one of those
readings already had an entity of the right type on another platform.

Removing a duplicate must change a reading's *type*, never make it disappear,
so the pairing below is what this module holds: for every key the sensor
platform drops, another platform declares it, and declares it enabled.
"""

from __future__ import annotations

import pytest

from custom_components.violet_pool_controller.const_features import (
    BINARY_SENSORS,
    DMX_LIGHTS,
    SWITCHES,
)
from custom_components.violet_pool_controller.entity import interpret_state_as_bool
from custom_components.violet_pool_controller.feature_keys import feature_for_key
from custom_components.violet_pool_controller.sensor import _STATE_CODE_DUPLICATE_KEYS
from custom_components.violet_pool_controller.sensor_modules.base import (
    determine_state_class,
    is_state_code_key,
)

# The reading, and the entry that has to carry it once the sensor is gone. A
# switching rule is spelled out in full in getReadings and abbreviated in the
# entity tables, which is why the two columns differ for DIRULE.
COUNTERPARTS: dict[str, tuple[str, str]] = {
    **{f"INPUT{i}": ("binary_sensor", f"INPUT{i}") for i in range(1, 13)},
    **{f"INPUT_CE{i}": ("binary_sensor", f"INPUT_CE{i}") for i in range(1, 5)},
    **{f"DMX_SCENE{i}": ("light", f"DMX_SCENE{i}") for i in range(1, 13)},
    **{
        f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_{i}": ("switch", f"DIRULE_{i}")
        for i in range(1, 9)
    },
    "DOS_1_CL_USE": ("binary_sensor", "DOS_1_CL_USE"),
    "DOS_2_ELO_USE": ("binary_sensor", "DOS_2_ELO_USE"),
    "DOS_4_PHM_USE": ("binary_sensor", "DOS_4_PHM_USE"),
    "DOS_5_PHP_USE": ("binary_sensor", "DOS_5_PHP_USE"),
    "DOS_6_FLOC_USE": ("binary_sensor", "DOS_6_FLOC_USE"),
}

TABLES = {"binary_sensor": BINARY_SENSORS, "light": DMX_LIGHTS, "switch": SWITCHES}


def _entry(platform: str, key: str) -> dict:
    """Return the table entry a platform declares for a key."""
    matches = [entry for entry in TABLES[platform] if entry.get("key") == key]
    assert len(matches) == 1, f"{platform} declares {key} {len(matches)} times"
    return matches[0]


def test_the_removed_keys_are_exactly_the_documented_ones() -> None:
    """The skip set and this module's table describe the same readings."""
    assert set(_STATE_CODE_DUPLICATE_KEYS) == set(COUNTERPARTS)


@pytest.mark.parametrize("key", sorted(COUNTERPARTS))
def test_every_removed_sensor_has_a_counterpart(key: str) -> None:
    """A dropped reading is declared by exactly one other platform."""
    platform, counterpart_key = COUNTERPARTS[key]

    _entry(platform, counterpart_key)


@pytest.mark.parametrize("key", sorted(COUNTERPARTS))
def test_the_counterpart_is_enabled_by_default(key: str) -> None:
    """Nothing may become invisible: the sensors this replaces were enabled.

    ``DMX_LIGHTS`` is the odd one out - the light platform builds its
    descriptions without reading the flag at all, so its entities are enabled
    whatever the table says.
    """
    platform, counterpart_key = COUNTERPARTS[key]
    if platform == "light":
        pytest.skip("the light platform does not read entity_registry_enabled_default")

    entry = _entry(platform, counterpart_key)

    assert entry.get("entity_registry_enabled_default") is True, (
        f"{platform}.{counterpart_key} is disabled by default, so removing "
        f"sensor {key} would hide the reading instead of retyping it"
    )


@pytest.mark.parametrize("key", sorted(COUNTERPARTS))
def test_the_counterpart_is_reachable_wherever_the_sensor_was(key: str) -> None:
    """The counterpart may not be gated behind a feature the sensor ignored.

    ``feature_for_key`` is what the sensor platform used, so it is the rule the
    replacement has to match. A stricter gate would drop the reading for anyone
    who has that feature switched off.
    """
    platform, counterpart_key = COUNTERPARTS[key]
    if platform == "light":
        pytest.skip("lights are gated by DMX_LIGHTS, checked by test_light.py")

    assert _entry(platform, counterpart_key).get("feature_id") == feature_for_key(key)


@pytest.mark.parametrize("key", sorted(COUNTERPARTS))
def test_a_removed_key_never_carried_a_state_class(key: str) -> None:
    """The statistics that produced the repair issues cannot come back."""
    assert is_state_code_key(key)
    assert determine_state_class(key) is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0", False), ("1", True), ("2", True), (0, False), (1, True), ("", None), (None, None)],
)
def test_a_dosing_use_flag_is_read_as_a_flag(raw: object, expected: bool | None) -> None:
    """DOS_*_USE is not one of the 0-6 output states.

    Under the shared mapping a 2 means "blocked by a control rule" and reads as
    off. For this key any non-zero value means the channel is configured, which
    is also how the dosing switch fills its ``dosing_configured`` attribute.
    """
    assert interpret_state_as_bool(raw, "DOS_1_CL_USE") is expected


def test_the_stopwatch_readings_are_not_removed() -> None:
    """DIGITALINPUTRULE_STATE_..._STOPWATCH* is a duration, not a state code."""
    stopwatches = {
        f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{i}" for i in range(1, 9)
    }

    assert not (stopwatches & set(_STATE_CODE_DUPLICATE_KEYS))
