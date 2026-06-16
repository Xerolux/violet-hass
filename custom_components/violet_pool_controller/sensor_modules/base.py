# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory

from ..const import (
    NO_UNIT_SENSORS,
    UNIT_MAP,
)

_LOGGER = logging.getLogger(__name__)


_PRECISION_MAP: dict[str, int] = {
    "°C": 1,
    "pH": 2,
    "mV": 0,
    "mg/l": 2,
    "bar": 2,
    "m³/h": 2,
    "cm": 1,
    "V": 1,
    "RPM": 0,
    "cm/s": 1,
    "%": 0,
    "W": 0,
    "ml": 0,
    "s": 0,
}

_KEYS_DISABLED_BY_DEFAULT: frozenset[str] = frozenset(
    {
        "FW",
        "CURRENT_TIME_UNIX",
    }
)

_KEY_PREFIXES_DISABLED_BY_DEFAULT: frozenset[str] = frozenset(
    {
        "SYSTEM_",
        "PUMP_RPM_",
    }
)

_KEY_SUFFIXES_DISABLED_BY_DEFAULT: frozenset[str] = frozenset(
    {
        "_LAST_ON",
        "_LAST_OFF",
        "_LAST_AUTO_RUN",
        "_LAST_MANUAL_RUN",
        "_LAST_CAN_RESET",
        "_TIMESTAMP",
        "_RUNTIME",
        "_faultcount",
        "_freezecount",
    }
)

_TIMESTAMP_SUFFIXES = (
    "_LAST_ON",
    "_LAST_OFF",
    "_LAST_AUTO_RUN",
    "_LAST_MANUAL_RUN",
    "_LAST_CAN_RESET",
    "_TIMESTAMP",
)
_TIMESTAMP_KEYS = {"CURRENT_TIME_UNIX"} | {
    key
    for key in UNIT_MAP
    if any(key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES)
}

_BOOLEAN_VALUE_KEYS = {
    "OVERFLOW_REFILL_STATE",
    "OVERFLOW_DRYRUN_STATE",
    "OVERFLOW_OVERFILL_STATE",
    "BACKWASH_OMNI_MOVING",
    "BACKWASH_DELAY_RUNNING",
    "BATHING_AI_SURVEILLANCE_STATE",
    "BATHING_AI_PUMP_STATE",
    "HW_BASE_MODULE",
    "HW_DOSING_MODULE",
    "HW_EXTENSION_MODULE_1",
    "HW_EXTENSION_MODULE_2",
    "HW_STANDALONE_MODE",
    "HW_DMX_MODULE",
    "HW_DIRULE_MODULE",
} | {f"onewire{i}_state" for i in range(1, 13)}

_RUNTIME_KEYS = (
    {
        "ECO_RUNTIME",
        "LIGHT_RUNTIME",
        "PUMP_RUNTIME",
        "BACKWASH_RUNTIME",
        "BACKWASHRINSE_RUNTIME",
        "SOLAR_RUNTIME",
        "HEATER_RUNTIME",
        "DOS_1_CL_RUNTIME",
        "DOS_2_ELO_RUNTIME",
        "DOS_3_ELO_REV_RUNTIME",
        "DOS_4_PHM_RUNTIME",
        "DOS_5_PHP_RUNTIME",
        "DOS_6_FLOC_RUNTIME",
        "REFILL_RUNTIME",
        "REFILL_TIMEOUT",
        "RUNTIME",
        "POSTRUN_TIME",
    }
    | {f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)}
    | {f"OMNI_DC{i}_RUNTIME" for i in range(6)}
    | {f"PUMP_RPM_{i}_RUNTIME" for i in range(4)}
)

_TIME_FORMAT_KEYS = (
    {
        "HEATER_POSTRUN_TIME",
        "SOLAR_POSTRUN_TIME",
        "DEVICE_UPTIME",
    }
    | {f"PUMP_RPM_{i}_LAST_ON" for i in range(4)}
    | {f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)}
)

_TEXT_VALUE_KEYS = {
    "DOS_1_CL_STATE",
    "DOS_2_ELO_STATE",
    "DOS_4_PHM_STATE",
    "DOS_5_PHP_STATE",
    "DOS_6_FLOC_STATE",
    "HEATERSTATE",
    "SOLARSTATE",
    "PUMPSTATE",
    "BACKWASHSTATE",
    # STATUS_SENSORS - these return text values like "Automatik (Bereit)", "Ein", "Aus"
    "BACKWASH",
    "BACKWASHRINSE",
    "PUMP",
    "HEATER",
    "SOLAR",
    "LIGHT",
    "ECO",
    "REFILL",
    "PVSURPLUS",
    # Other STATE sensors
    "OMNI_STATE",
    "BACKWASH_OMNI_STATE",
    "SOLAR_STATE",
    "HEATER_STATE",
    "PUMP_STATE",
    "FILTER_STATE",
    "OMNI_MODE",
    "FILTER_MODE",
    "SOLAR_MODE",
    "HEATER_MODE",
    "DISPLAY_MODE",
    "OPERATING_MODE",
    "MAINTENANCE_MODE",
    "ERROR_CODE",
    "LAST_ERROR",
    "VERSION_CODE",
    "CHECKSUM",
    "RULE_RESULT",
    "LAST_MOVING_DIRECTION",
    "COVER_STATE",
    "COVER_DIRECTION",
    "SW_VERSION",
    "SW_VERSION_CARRIER",
    "HW_VERSION_CARRIER",
    "FW",
    "fw",
    "VERSION",
    "VERSION_INFO",
    "HARDWARE_VERSION",
    "CPU_GOV",
    "HW_SERIAL_CARRIER",
    "SERIAL_NUMBER",
    "MAC_ADDRESS",
    "IP_ADDRESS",
    "DOS_1_CL_REMAINING_RANGE",
    "DOS_2_ELO_REMAINING_RANGE",
    "DOS_3_ELO_REV_REMAINING_RANGE",
    "DOS_4_PHM_REMAINING_RANGE",
    "DOS_5_PHP_REMAINING_RANGE",
    "DOS_6_FLOC_REMAINING_RANGE",
    "BACKWASH_OMNI_MOVING",
    "BACKWASH_DELAY_RUNNING",
    "BACKWASH_STATE",
    "REFILL_STATE",
    "BATHING_AI_SURVEILLANCE_STATE",
    "BATHING_AI_PUMP_STATE",
    "OVERFLOW_REFILL_STATE",
    "OVERFLOW_DRYRUN_STATE",
    "OVERFLOW_OVERFILL_STATE",
    "time",
    "TIME",
    "CURRENT_TIME",
    "date",  # Date value, not numeric
    "LOAD_AVG",
    "pump_rs485_pwr",
    "SYSTEM_carrier_alive_count",
    "SYSTEM_carrier_alive_faultcount",
    "SYSTEM_dosagemodule_alive_count",
    "SYSTEM_dosagemodule_alive_faultcount",
    "SYSTEM_ext1module_alive_count",
    "SYSTEM_ext1module_alive_faultcount",
    # Cover contact sensors - these return string values ("RELEASED"/"TRIGGERED")
    "CLOSE_CONTACT",
    "OPEN_CONTACT",
    "ERROR_CONTACT",
}

_ALL_TEXT_SENSORS = (
    _TEXT_VALUE_KEYS | _RUNTIME_KEYS | _BOOLEAN_VALUE_KEYS | _TIME_FORMAT_KEYS
)

_NON_TEMPERATURE_ONEWIRE_KEYS = {
    f"onewire{i}_{suffix}"
    for i in range(1, 13)
    for suffix in ("rcode", "romcode", "state")
}
_FLOW_RATE_SOURCE_KEYS = {"ADC3_value", "IMP2_value"}
_ERROR_CODE_KEYS = {"LAST_ERROR_CODE", "ERROR_CODE", "LAST_ERROR"}


def _is_boolean_value(value: Any) -> bool:
    """Checks if a value can be interpreted as a boolean."""
    return str(value).lower().strip() in (
        "true",
        "false",
        "1",
        "0",
        "on",
        "off",
        "yes",
        "no",
    )


def format_seconds_to_readable(seconds: float) -> str:
    """Convert seconds to readable format (e.g., '1d 2h 30m 45s')."""
    try:
        total_seconds = int(seconds)
        if total_seconds < 0:
            return "0s"

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)
    except (ValueError, TypeError):
        return "0s"


def determine_device_class(
    key: str, unit: str | None, raw_value: Any
) -> SensorDeviceClass | None:
    """Determines the appropriate device class for a sensor."""
    if key in _BOOLEAN_VALUE_KEYS or (
        _is_boolean_value(raw_value) and key not in UNIT_MAP
    ):
        return None
    if key == "pH_value":
        return SensorDeviceClass.PH
    # Temperature device class only for actual temperature sensors (not counters)
    if (
        (unit == "°C" or ("temp" in key.lower() and unit is not None))
        and "freezecount" not in key.lower()
        and "faultcount" not in key.lower()
    ):
        return SensorDeviceClass.TEMPERATURE
    if unit == "%":
        return SensorDeviceClass.HUMIDITY
    if unit == "bar":
        return SensorDeviceClass.PRESSURE
    if unit in {"mV", "V"}:
        return SensorDeviceClass.VOLTAGE
    if unit == "W":
        return SensorDeviceClass.POWER
    if unit == "s":
        return SensorDeviceClass.DURATION
    # Check if key indicates a timestamp sensor
    # (by suffix or membership in _TIMESTAMP_KEYS)
    is_timestamp_key = key in _TIMESTAMP_KEYS or any(
        key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES
    )
    if is_timestamp_key and key not in _TIME_FORMAT_KEYS:
        return SensorDeviceClass.TIMESTAMP
    return None


def determine_state_class(key: str) -> SensorStateClass | None:
    """Determines the appropriate state class for a sensor."""
    # Check if key indicates a timestamp sensor
    # (by suffix or membership in _TIMESTAMP_KEYS)
    is_timestamp_key = key in _TIMESTAMP_KEYS or any(
        key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES
    )

    # Explicitly force None for remaining range sensors (text/string values like ">99d")
    if key.endswith("_REMAINING_RANGE"):
        return None

    # DI-Rule stopwatch sensors return formatted strings like "1d 2h 30m 45s"
    if "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH" in key:
        return None

    if key in _ALL_TEXT_SENSORS or is_timestamp_key or key in NO_UNIT_SENSORS:
        return None
    # Handle contact sensors (e.g., CLOSE_CONTACT) which return
    # string values like "RELEASED"/"TRIGGERED"
    if "contact" in key.lower():
        return None
    # Count/fault sensors should not have state_class
    # (they are counters, not measurements)
    if "freezecount" in key.lower() or "faultcount" in key.lower():
        return None
    # Dosing can amount sensors (DOS_*_TOTAL_CAN_AMOUNT_ML) can decrease on refill
    if "dos_" in key.lower() and "_total_can_amount_" in key.lower():
        return SensorStateClass.MEASUREMENT
    if "total" in key.lower() or "daily" in key.lower():
        return SensorStateClass.TOTAL_INCREASING
    return SensorStateClass.MEASUREMENT


def get_icon(key: str, unit: str | None, raw_value: Any) -> str:
    """Determin a sensor."""
    if key.startswith("EXT1_") or key.startswith("EXT2_"):
        return "mdi:electric-switch"
    if key.startswith("OMNI_DC"):
        return "mdi:electric-switch"
    if key.startswith("DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_"):
        return "mdi:script-text"
    if key.startswith("PUMP_RPM_") and key.endswith(("_LAST_ON", "_LAST_OFF")) is False:
        return "mdi:speedometer"
    if key in _BOOLEAN_VALUE_KEYS or (
        _is_boolean_value(raw_value) and key not in UNIT_MAP
    ):
        return "mdi:toggle-switch"
    if key == "pH_value":
        return "mdi:flask"
    if "flow" in key.lower():
        return "mdi:pump"
    if unit == "°C":
        return "mdi:thermometer"
    if unit == "bar":
        return "mdi:gauge"
    if unit in {"mV", "V"}:
        return "mdi:flash"
    if key in _TIMESTAMP_KEYS:
        return "mdi:clock"
    return "mdi:information"


def should_skip_sensor(key: str, raw_value: Any) -> bool:
    """Determines if a sensor should be skipped and not created."""
    return (
        raw_value is None
        or str(raw_value).strip() in ("[]", "{}", "")
        or key in _NON_TEMPERATURE_ONEWIRE_KEYS
        or key.startswith("_")
    )


def _build_sensor_description(
    key: str,
    raw_value: Any,
    predefined: dict[str, Any],
    *,
    translation_key: str | None = None,
) -> SensorEntityDescription:
    """Builds a SensorEntityDescription for a given sensor key."""
    predefined_info = predefined.get(key)
    # Prefer translation key logic if implemented fully,
    # but for dynamic sensors derived from API keys, we need dynamic names.
    # We stick to name here but could use key as translation key
    # if we updated strings.json
    name = predefined_info["name"] if predefined_info else key.replace("_", " ").title()
    icon = predefined_info.get("icon") if predefined_info else None

    unit = UNIT_MAP.get(key) if key not in NO_UNIT_SENSORS else None
    if _is_boolean_value(raw_value) and key not in UNIT_MAP:
        unit = None

    # Force no unit for count/fault sensors (they are counters, not measurements)
    if "freezecount" in key.lower() or "faultcount" in key.lower():
        unit = None

    # Force no unit for DI-Rule stopwatch (formatted value includes time units)
    if "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH" in key:
        unit = None

    if unit is None and key not in NO_UNIT_SENSORS:
        for suffix in [
            "_min",
            "_max",
            "_setpoint",
            "_target",
            "_faultcount",
            "_freezecount",
        ]:
            if key.endswith(suffix):
                base_key = key[: -len(suffix)]
                # IMPORTANT: Don't inherit unit for count/fault sensors
                if suffix not in ["_faultcount", "_freezecount"] and UNIT_MAP.get(
                    base_key
                ):
                    unit = UNIT_MAP[base_key]
                    break
        # Default temperature unit for onewire/temp sensors (but not for counters or non-temp keys!)
        if (
            unit is None
            and ("temp" in key.lower() or "onewire" in key.lower())
            and "freezecount" not in key.lower()
            and "faultcount" not in key.lower()
            and key not in _NON_TEMPERATURE_ONEWIRE_KEYS
        ):
            unit = "°C"

    # Determine state class
    state_class = determine_state_class(key)
    # Force state_class to None for contact sensors (they return string values)
    if "contact" in key.lower():
        state_class = None

    # Entity category: DIAGNOSTIC for system/internal sensors, otherwise
    # allow the predefined dict to override (e.g. for extra diagnostic
    # sensors that don't start with SYSTEM_).
    predefined_category = (predefined_info or {}).get("entity_category")
    if predefined_category == "diagnostic":
        category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    elif predefined_category == "config":
        category = EntityCategory.CONFIG
    elif key.startswith("SYSTEM_"):
        category = EntityCategory.DIAGNOSTIC
    else:
        category = None

    return SensorEntityDescription(
        key=key,
        name=name,
        icon=icon or get_icon(key, unit, raw_value),
        native_unit_of_measurement=unit,
        device_class=determine_device_class(key, unit, raw_value),
        state_class=state_class,
        entity_category=category,
        translation_key=translation_key,
        entity_registry_enabled_default=_should_enable_by_default(key),
        suggested_display_precision=_PRECISION_MAP.get(unit) if unit else None,
    )


def _should_enable_by_default(key: str) -> bool:
    if key in _KEYS_DISABLED_BY_DEFAULT:
        return False
    for prefix in _KEY_PREFIXES_DISABLED_BY_DEFAULT:
        if key.startswith(prefix):
            if key in (
                "PUMP_RPM_0_VALUE",
                "PUMP_RPM_1_VALUE",
                "PUMP_RPM_2_VALUE",
                "PUMP_RPM_3_VALUE",
            ):
                continue
            return False
    key_upper = key.upper()
    for suffix in _KEY_SUFFIXES_DISABLED_BY_DEFAULT:
        if key_upper.endswith(suffix.upper()):
            return False
    return True
