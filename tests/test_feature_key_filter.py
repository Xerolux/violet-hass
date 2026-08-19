"""Disabling a feature must hide everything that belongs to it.

Reported on the forum for 2.5.3: after deselecting Solar under
"enable/disable features", every ``SOLAR*`` reading was still offered under
"select sensors" and had to be deselected a second time. Only the handful of
keys listed in ``SENSOR_FEATURE_MAP`` carried a feature id; the rest of the
controller's key space counted as feature-independent.
"""

from __future__ import annotations

import pytest

from custom_components.violet_pool_controller.config_flow_utils import group_sensor_keys
from custom_components.violet_pool_controller.const import AVAILABLE_FEATURES
from custom_components.violet_pool_controller.feature_keys import (
    FEATURE_KEY_PATTERNS,
    feature_for_key,
    is_key_feature_active,
)

ALL_FEATURES = [str(feature["id"]) for feature in AVAILABLE_FEATURES]


class TestFeatureForKey:
    """feature_for_key() – the key space beyond the curated table."""

    @pytest.mark.parametrize(
        ("key", "feature"),
        [
            # Curated table entries keep their mapping.
            ("onewire3_value", "solar"),
            ("ECO", "eco_mode"),
            ("DMX_SCENE1", "dmx_scenes"),
            # Keys the table never listed.
            ("SOLAR", "solar"),
            ("SOLAR_LAST_ON", "solar"),
            ("HEATER_set_temp", "heating"),
            ("LIGHT_SCENE_2", "led_lighting"),
            ("COVER_OPEN", "cover_control"),
            ("BACKWASHRINSE", "backwash"),
            ("REFILL_TIMEOUT", "water_refill"),
            ("PVSURPLUS_RUNTIME", "pv_surplus"),
            ("EXT1_3", "extension_outputs"),
            ("DIRULE_4", "digital_inputs"),
            ("DOS_2_ELO_RUNTIME", "chlorine_control"),
            ("DOS_5_PHP_LAST_ON", "ph_control"),
            ("DOS_6_FLOC_STATE", "flocculation"),
            ("PUMP_RPM_1", "filter_control"),
        ],
    )
    def test_key_resolves_to_its_feature(self, key: str, feature: str) -> None:
        """Each key must name the feature that switches it off."""
        assert feature_for_key(key) == feature

    @pytest.mark.parametrize(
        "key",
        [
            "onewire1_value",
            "CPU_TEMP",
            "SYSTEM_swversion",
            # Generic inputs stay usable no matter which features are on.
            "ADC1",
            "IMP1_value",
            "INPUT1",
            "",
        ],
    )
    def test_feature_independent_keys(self, key: str) -> None:
        """Keys without an owning feature must never be filtered away."""
        assert feature_for_key(key) is None
        assert is_key_feature_active(key, [])

    def test_patterns_only_reference_known_features(self) -> None:
        """A typo in a pattern would silently hide entities forever."""
        unknown = {feature for _, feature in FEATURE_KEY_PATTERNS if feature not in ALL_FEATURES}
        assert not unknown, f"unknown features in FEATURE_KEY_PATTERNS: {sorted(unknown)}"


class TestSensorSelectionList:
    """group_sensor_keys() – what the "select sensors" step offers."""

    KEYS = [
        "onewire1_value",
        "onewire3_value",
        "SOLAR",
        "SOLAR_RUNTIME",
        "SOLAR_LAST_ON",
        "PUMP_RUNTIME",
        "CPU_TEMP",
    ]

    def test_disabled_feature_is_not_offered(self) -> None:
        """Solar off → no solar key survives, not even the uncurated ones."""
        active = [feature for feature in ALL_FEATURES if feature != "solar"]
        offered = {key for keys in group_sensor_keys(self.KEYS, active).values() for key in keys}

        assert not any(key.startswith("SOLAR") for key in offered)
        assert "onewire3_value" not in offered
        assert {"onewire1_value", "PUMP_RUNTIME", "CPU_TEMP"} <= offered

    def test_enabled_feature_is_offered(self) -> None:
        """With solar enabled the list is unchanged."""
        offered = {
            key for keys in group_sensor_keys(self.KEYS, ALL_FEATURES).values() for key in keys
        }
        assert offered == set(self.KEYS)

    def test_empty_groups_are_dropped(self) -> None:
        """A group whose keys all vanished must not show an empty selector."""
        active = [feature for feature in ALL_FEATURES if feature != "solar"]
        assert "SOLAR" not in group_sensor_keys(["SOLAR", "SOLAR_RUNTIME"], active)

    def test_legacy_entries_without_features_keep_every_key(self) -> None:
        """No feature list stored → no filtering, same list as before."""
        offered = {key for keys in group_sensor_keys(self.KEYS, None).values() for key in keys}
        assert offered == set(self.KEYS)
