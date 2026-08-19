# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Resolve which configurable feature a raw controller key belongs to.

The controller reports several hundred keys, while :data:`SENSOR_FEATURE_MAP`
only names the curated ones. Everything the table does not list used to count
as "belongs to no feature", so turning a feature off in the config flow left
its remaining readings behind – both as entities and as entries in the sensor
selection list (reported for Solar: disabling the feature still offered every
``SOLAR*`` reading under "select sensors").

The prefix patterns below close that gap. They only cover key spaces that
unambiguously belong to a single feature; generic inputs (``ADC*``, ``IMP*``,
``INPUT*``) stay unmapped on purpose, because they are useful independently of
any feature.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from .const_sensors import SENSOR_FEATURE_MAP

# Matched in order against the raw controller key. The first hit wins, so the
# more specific dosing prefixes come before the broader ones.
FEATURE_KEY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # --- Dosing channels ---
    (re.compile(r"^DOS_1_CL|^DOS_2_ELO|^DOSAGE_chlorine|^DOSAGE_electrolysis"), "chlorine_control"),
    (re.compile(r"^DOS_4_PHM|^DOS_5_PHP|^DOSAGE_phminus|^DOSAGE_phplus"), "ph_control"),
    (re.compile(r"^DOS_6_FLOC|^DOSAGE_floc"), "flocculation"),
    (re.compile(r"^orp_|^ORP_|^pot_|^POT_"), "chlorine_control"),
    (re.compile(r"^pH_|^PH_"), "ph_control"),
    # --- Circulation, heating, solar ---
    (re.compile(r"^PUMP(_|$)|^pump_|^PUMPSTATE"), "filter_control"),
    (re.compile(r"^HEATER"), "heating"),
    (re.compile(r"^SOLAR"), "solar"),
    # --- Lighting (DMX before the broader LIGHT prefix) ---
    (re.compile(r"^DMX_"), "dmx_scenes"),
    (re.compile(r"^LIGHT"), "led_lighting"),
    # --- Cover, backwash, refill, PV, ECO ---
    (re.compile(r"^COVER"), "cover_control"),
    (re.compile(r"^BACKWASH|^RINSE"), "backwash"),
    (re.compile(r"^REFILL"), "water_refill"),
    (re.compile(r"^PVSURPLUS"), "pv_surplus"),
    (re.compile(r"^ECO(_|$)"), "eco_mode"),
    # --- I/O modules ---
    (re.compile(r"^EXT\d_|^OMNI_DC"), "extension_outputs"),
    (re.compile(r"^DIRULE_|^DIGITALINPUTRULE|^SWITCHINGRULE"), "digital_inputs"),
)


def feature_for_key(key: str) -> str | None:
    """Return the feature id a controller key belongs to.

    Args:
        key: The raw controller key.

    Returns:
        The feature id, or ``None`` when the key belongs to no feature and is
        therefore always available.
    """
    if not key:
        return None

    # The curated table wins: it also marks keys as feature-independent by
    # mapping them to None explicitly.
    if key in SENSOR_FEATURE_MAP:
        feature = SENSOR_FEATURE_MAP[key]
        return str(feature) if feature else None

    for pattern, feature_id in FEATURE_KEY_PATTERNS:
        if pattern.match(key):
            return feature_id

    return None


def is_key_feature_active(key: str, active_features: Iterable[str]) -> bool:
    """Return whether a controller key belongs to an enabled feature.

    Args:
        key: The raw controller key.
        active_features: The features enabled for the config entry.

    Returns:
        True when the key has no feature or its feature is enabled.
    """
    feature_id = feature_for_key(key)
    if feature_id is None:
        return True
    return feature_id in set(active_features)
