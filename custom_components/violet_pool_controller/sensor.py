"""Sensor integration for the Violet Pool Controller.

This module defines the sensor entities for the integration, including
generic sensors, status sensors, and specialized sensors for error codes and
flow rates. It also handles the logic for creating and configuring these
sensors based on the user's settings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ANALOG_SENSORS,
    CONF_ACTIVE_FEATURES,
    CONF_SELECTED_SENSORS,
    DOMAIN,
    NO_UNIT_SENSORS,
    SENSOR_FEATURE_MAP,
    STATUS_SENSORS,
    TEMP_SENSORS,
    UNIT_MAP,
    WATER_CHEM_SENSORS,
    VioletState,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity
from .error_codes import get_error_info

_LOGGER = logging.getLogger(__name__)

# --- Sensor Categorization ---

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
} | {f"onewire{i}_state" for i in range(1, 13)}

_RUNTIME_KEYS = (
    {
        "ECO_RUNTIME",
        "LIGHT_RUNTIME",
        "PUMP_RUNTIME",
        "BACKWASH_RUNTIME",
        "SOLAR_RUNTIME",
        "HEATER_RUNTIME",
        "DOS_1_CL_RUNTIME",
        "DOS_4_PHM_RUNTIME",
        "DOS_5_PHP_RUNTIME",
        "DOS_6_FLOC_RUNTIME",
        "REFILL_TIMEOUT",
        "RUNTIME",
        "POSTRUN_TIME",
    }
    | {f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)}
    | {f"OMNI_DC{i}_RUNTIME" for i in range(1, 6)}
    | {f"PUMP_RPM_{i}_RUNTIME" for i in range(4)}
)

_TIME_FORMAT_KEYS = (
    {
        "HEATER_POSTRUN_TIME",
        "SOLAR_POSTRUN_TIME",
        "CPU_UPTIME",
        "DEVICE_UPTIME",
    }
    | {f"PUMP_RPM_{i}_LAST_ON" for i in range(4)}
    | {f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)}
)

_TEXT_VALUE_KEYS = {
    "DOS_1_CL_STATE",
    "DOS_4_PHM_STATE",
    "DOS_5_PHP_STATE",
    "HEATERSTATE",
    "SOLARSTATE",
    "PUMPSTATE",
    "BACKWASHSTATE",
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
    "LOAD_AVG",
    "pump_rs485_pwr",
    "SYSTEM_carrier_alive_count",
    "SYSTEM_carrier_alive_faultcount",
    "SYSTEM_dosagemodule_alive_count",
    "SYSTEM_dosagemodule_alive_faultcount",
    "SYSTEM_ext1module_alive_count",
    "SYSTEM_ext1module_alive_faultcount",
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


class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Represents a generic Violet Pool Controller sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initializes the sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
            description: The entity description for the sensor.
        """
        super().__init__(coordinator, config_entry, description)
        self._logger = logging.getLogger(f"{DOMAIN}.sensor.{description.key}")
        _LOGGER.debug(
            "Sensor initialized: %s (Key: %s, Class: %s)",
            description.name or description.translation_key,
            description.key,
            description.device_class,
        )

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Returns the native value of the sensor, formatted for Home Assistant."""
        if self.coordinator.data is None:
            return None

        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)

        if raw_value is None:
            return None

        if key in _TIMESTAMP_KEYS and key not in _TIME_FORMAT_KEYS:
            try:
                return datetime.fromtimestamp(float(raw_value), tz=timezone.utc)
            except (ValueError, TypeError) as err:
                self._logger.warning(
                    "Timestamp conversion failed for %s with value '%s': %s",
                    key,
                    raw_value,
                    err,
                )
                return None

        if key in _ALL_TEXT_SENSORS:
            return str(raw_value)

        try:
            num_value = float(raw_value)
            if key == "pH_value":
                return round(num_value, 2)
            if "temp" in key.lower() or "onewire" in key.lower():
                return round(num_value, 1)
            return int(num_value) if num_value.is_integer() else num_value
        except (ValueError, TypeError):
            # Explicitly cast to string to match return type
            return str(raw_value)


class VioletStatusSensor(VioletSensor):
    """Represents a sensor for status values that use VioletState."""

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the display string for the status."""
        if self.coordinator.data is None:
            return None

        raw_value = self.coordinator.data.get(self.entity_description.key)
        return (
            VioletState(raw_value, self.entity_description.key).display_mode
            if raw_value is not None
            else None
        )

    @property
    def icon(self) -> str | None:
        """Return the icon corresponding to the current status."""
        if self.coordinator.data is None:
            return super().icon

        raw_value = self.coordinator.data.get(self.entity_description.key)
        if raw_value is None:
            return super().icon
        return VioletState(raw_value, self.entity_description.key).icon


class VioletErrorCodeSensor(VioletSensor):
    """A specialized sensor that resolves error codes to descriptive text."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        value_key: str,
    ) -> None:
        """Initializes the error code sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
            value_key: The key in the coordinator data that holds the error code.
        """
        description = SensorEntityDescription(
            key=value_key,
            translation_key="last_error_code",
            name="Last Error Code",
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> str | None:
        """Return the descriptive subject of the error code."""
        if self.coordinator.data is None:
            return None

        code = str(self.coordinator.data.get(self.entity_description.key, "")).strip()
        return get_error_info(code)["subject"] if code else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed information about the error code as attributes."""
        if self.coordinator.data is None:
            return {}

        code = str(self.coordinator.data.get(self.entity_description.key, "")).strip()
        if not code:
            return {}
        info = get_error_info(code)
        return {
            "code": code,
            "type": info.get("type"),
            "severity": info.get("severity"),
            "description": info.get("description"),
        }


class VioletSystemHealthSensor(VioletPoolControllerEntity, SensorEntity):
    """Diagnostic sensor for system health percentage (0-100)."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the system health sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
        """
        description = SensorEntityDescription(
            key="system_health",
            translation_key="system_health",
            name="System Health",
            icon="mdi:heart-pulse",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the system health percentage."""
        return round(self.coordinator.device.system_health, 0)


class VioletConnectionLatencySensor(VioletPoolControllerEntity, SensorEntity):
    """Diagnostic sensor for connection latency in milliseconds."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the connection latency sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
        """
        description = SensorEntityDescription(
            key="connection_latency",
            translation_key="connection_latency",
            name="Connection Latency",
            icon="mdi:speedometer",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement="ms",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            suggested_display_precision=0,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the connection latency in milliseconds."""
        return round(self.coordinator.device.connection_latency, 0)


class VioletLastEventAgeSensor(VioletPoolControllerEntity, SensorEntity):
    """Diagnostic sensor for seconds since last successful update."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the last event age sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
        """
        description = SensorEntityDescription(
            key="last_event_age",
            translation_key="last_event_age",
            name="Last Event Age",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement="s",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            suggested_display_precision=0,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return seconds since last successful update."""
        return round(self.coordinator.device.last_event_age, 0)


class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """A specialized sensor for flow rate that prioritizes ADC3 over IMP2."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initializes the flow rate sensor."""
        description = SensorEntityDescription(
            key="flow_rate_adc3_priority",
            translation_key="flow_rate",
            name="Flow Rate",
            icon="mdi:pump",
            native_unit_of_measurement="m³/h",
            device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the flow rate, prioritizing the ADC3 value."""
        if self.coordinator.data is None:
            return None

        for key in ["ADC3_value", "IMP2_value"]:
            raw_value = self.coordinator.data.get(key)
            if raw_value is not None:
                try:
                    return round(float(raw_value), 2)
                except (ValueError, TypeError):
                    continue
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the raw source values for debugging purposes."""
        if self.coordinator.data is None:
            return {"data_source": "None"}

        adc3 = self.coordinator.data.get("ADC3_value", "N/A")
        imp2 = self.coordinator.data.get("IMP2_value", "N/A")
        source = "ADC3" if adc3 != "N/A" else "IMP2" if imp2 != "N/A" else "None"
        return {
            "adc3_raw_value": str(adc3),
            "imp2_raw_value": str(imp2),
            "data_source": source,
        }

    @property
    def available(self) -> bool:
        """The sensor is available if either of its data sources is present."""
        if self.coordinator.data is None:
            return False

        return super().available and any(
            self.coordinator.data.get(key) is not None for key in _FLOW_RATE_SOURCE_KEYS
        )


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


def determine_device_class(
    key: str, unit: str | None, raw_value: Any
) -> SensorDeviceClass | None:
    """Determines the appropriate device class for a sensor."""
    if key in _BOOLEAN_VALUE_KEYS or _is_boolean_value(raw_value):
        return None
    if key == "pH_value":
        return SensorDeviceClass.PH
    if unit == "°C" or ("temp" in key.lower() and unit is not None):
        return SensorDeviceClass.TEMPERATURE
    if unit == "%":
        return SensorDeviceClass.HUMIDITY
    if unit == "bar":
        return SensorDeviceClass.PRESSURE
    if unit in {"mV", "V"}:
        return SensorDeviceClass.VOLTAGE
    if unit == "W":
        return SensorDeviceClass.POWER
    if key in _TIMESTAMP_KEYS and key not in _TIME_FORMAT_KEYS:
        return SensorDeviceClass.TIMESTAMP
    return None


def determine_state_class(key: str) -> SensorStateClass | None:
    """Determines the appropriate state class for a sensor."""
    if key in _ALL_TEXT_SENSORS or key in _TIMESTAMP_KEYS or key in NO_UNIT_SENSORS:
        return None
    if "total" in key.lower() or "daily" in key.lower():
        return SensorStateClass.TOTAL_INCREASING
    return SensorStateClass.MEASUREMENT


def get_icon(key: str, unit: str | None, raw_value: Any) -> str:
    """Determin a sensor."""
    if key in _BOOLEAN_VALUE_KEYS or _is_boolean_value(raw_value):
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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sets up the Violet Pool Controller sensors from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # None-Check für coordinator.data
    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator-Daten sind None für '%s'. Sensoren werden nicht erstellt.",
            config_entry.title,
        )
        return

    config = _get_sensor_config(config_entry)

    sensors: list[SensorEntity] = []
    handled_keys: set[str] = set()

    special_sensors, special_keys = _create_special_sensors(
        coordinator, config_entry, config
    )
    sensors.extend(special_sensors)
    handled_keys.update(special_keys)

    standard_sensors = _create_standard_sensors(
        coordinator, config_entry, config, handled_keys
    )
    sensors.extend(standard_sensors)

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d sensors added for '%s'", len(sensors), config_entry.title)
    else:
        _LOGGER.warning(
            "No sensors were added for '%s'. "
            "Check the sensor selection in the configuration menu.",
            config_entry.title,
        )


def _get_sensor_config(config_entry: ConfigEntry) -> dict[str, Any]:
    """Extracts sensor-specific configuration from the config entry."""
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    selected_sensors_raw = config_entry.options.get(
        CONF_SELECTED_SENSORS, config_entry.data.get(CONF_SELECTED_SENSORS)
    )
    create_all = selected_sensors_raw is None

    if create_all:
        _LOGGER.info(
            "No sensor selection found (legacy config). Creating all available sensors."
        )
    else:
        _LOGGER.info("Creating %d selected sensors.", len(selected_sensors_raw or []))

    return {
        "active_features": set(active_features),
        "selected_sensors": set(selected_sensors_raw or []),
        "create_all": create_all,
    }


def _create_special_sensors(
    coordinator: VioletPoolDataUpdateCoordinator,
    config_entry: ConfigEntry,
    config: dict[str, Any],
) -> tuple[list[SensorEntity], set[str]]:
    """Creates specialized sensors like error codes, flow rate, and diagnostics."""
    sensors: list[SensorEntity] = []
    handled_keys: set[str] = set()

    # ✅ DIAGNOSTIC SENSORS: Always create system monitoring sensors
    sensors.append(VioletSystemHealthSensor(coordinator, config_entry))
    sensors.append(VioletConnectionLatencySensor(coordinator, config_entry))
    sensors.append(VioletLastEventAgeSensor(coordinator, config_entry))
    handled_keys.update({"system_health", "connection_latency", "last_event_age"})
    _LOGGER.debug(
        "Diagnostic sensors created "
        "(System Health, Connection Latency, Last Event Age)"
    )

    for key in _ERROR_CODE_KEYS:
        if key in coordinator.data and (
            config["create_all"] or key in config["selected_sensors"]
        ):
            sensors.append(VioletErrorCodeSensor(coordinator, config_entry, key))
            handled_keys.add(key)
            _LOGGER.debug("Error code sensor created for %s", key)

    flow_keys_present = any(key in coordinator.data for key in _FLOW_RATE_SOURCE_KEYS)
    flow_selected = (
        config["create_all"] or "flow_rate_adc3_priority" in config["selected_sensors"]
    )
    if flow_keys_present and flow_selected:
        sensors.append(VioletFlowRateSensor(coordinator, config_entry))
        handled_keys.update(_FLOW_RATE_SOURCE_KEYS)
        _LOGGER.debug("Priority flow rate sensor created.")

    return sensors, handled_keys


def _create_standard_sensors(
    coordinator: VioletPoolDataUpdateCoordinator,
    config_entry: ConfigEntry,
    config: dict[str, Any],
    handled_keys: set[str],
) -> list[SensorEntity]:
    """Creates all standard sensors based on coordinator data and user configuration."""
    sensors: list[SensorEntity] = []
    all_predefined = {
        **TEMP_SENSORS,
        **WATER_CHEM_SENSORS,
        **ANALOG_SENSORS,
        **STATUS_SENSORS,
    }

    for key in sorted(coordinator.data.keys()):
        if key in handled_keys or should_skip_sensor(key, coordinator.data.get(key)):
            continue

        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in config["active_features"]:
            continue

        if not config["create_all"] and key not in config["selected_sensors"]:
            continue

        description = _build_sensor_description(
            key, coordinator.data.get(key), all_predefined
        )

        SensorClass = (
            VioletStatusSensor
            if key in STATUS_SENSORS and key not in ["fw", "FW"]
            else VioletSensor
        )
        sensors.append(SensorClass(coordinator, config_entry, description))

    return sensors


def _build_sensor_description(
    key: str, raw_value: Any, predefined: dict[str, Any]
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
    if _is_boolean_value(raw_value):
        unit = None  # Booleans should not have a unit

    if unit is None and key not in NO_UNIT_SENSORS and not _is_boolean_value(raw_value):
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
                if UNIT_MAP.get(base_key):
                    unit = UNIT_MAP[base_key]
                    break
        if unit is None and ("temp" in key.lower() or "onewire" in key.lower()):
            unit = "°C"

    return SensorEntityDescription(
        key=key,
        name=name,
        icon=icon or get_icon(key, unit, raw_value),
        native_unit_of_measurement=unit,
        device_class=determine_device_class(key, unit, raw_value),
        state_class=determine_state_class(key),
        entity_category=EntityCategory.DIAGNOSTIC
        if key.startswith("SYSTEM_")
        else None,
    )
