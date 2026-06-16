# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Sensor integration for the Violet Pool Controller.

This module defines the sensor setup and entity creation logic for the integration.
Sensor classes are split into submodules for better organization.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ANALOG_RULE_SENSORS,
    ANALOG_SENSORS,
    COMPOSITE_STATE_SENSORS,
    CONF_ACTIVE_FEATURES,
    CONF_SELECTED_SENSORS,
    DOMAIN,
    DOSING_STATE_SENSORS,
    DOSING_STATS_SENSORS,
    EXTRA_DIAGNOSTIC_SENSORS,
    ONEWIRE_ROMCODE_SENSORS,
    RUNTIME_SENSORS,
    SENSOR_FEATURE_MAP,
    STATUS_SENSORS,
    SYSTEM_SENSORS,
    TEMP_RULE_SENSORS,
    TEMP_SENSORS,
    WATER_CHEM_SENSORS,
)
from .device import VioletPoolDataUpdateCoordinator

# Import sensor classes from submodules
from .sensor_modules import (
    VioletActiveErrorsSensor,
    VioletAPIRequestRateSensor,
    VioletAverageLatencySensor,
    VioletConnectionLatencySensor,
    VioletDosingStateSensor,
    VioletErrorCodeSensor,
    VioletFlowRateSensor,
    VioletHealthSensor,
    VioletLastEventAgeSensor,
    VioletPumpPowerSensor,
    VioletSensor,
    VioletStatusSensor,
    VioletSystemHealthSensor,
    _build_sensor_description,
    should_skip_sensor,
)

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# Additional constants for sensor classification
_ERROR_CODE_KEYS = {"LAST_ERROR_CODE", "ERROR_CODE", "LAST_ERROR"}
_FLOW_RATE_SOURCE_KEYS = {"ADC3_value", "IMP2_value"}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sets up the Violet Pool Controller sensors from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # None-check for coordinator.data
    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator data is None for '%s'. Sensors will not be created.",
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
        _LOGGER.debug("%d sensors added for '%s'", len(sensors), config_entry.title)
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
        _LOGGER.debug(
            "No sensor selection found (legacy config). Creating all available sensors."
        )
    else:
        _LOGGER.debug("Creating %d selected sensors.", len(selected_sensors_raw or []))

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
    """Creates special sensors that are not part of the standard sensor sets."""
    sensors: list[SensorEntity] = []
    handled_keys: set[str] = set()

    # System Health & Monitoring Sensors
    sensors.extend(
        [
            VioletSystemHealthSensor(coordinator, config_entry),
            VioletConnectionLatencySensor(coordinator, config_entry),
            VioletLastEventAgeSensor(coordinator, config_entry),
            VioletAPIRequestRateSensor(coordinator, config_entry),
            VioletAverageLatencySensor(coordinator, config_entry),
        ]
    )
    handled_keys.update(
        {
            "system_health",
            "connection_latency",
            "last_event_age",
            "api_request_rate",
            "average_latency",
        }
    )
    _LOGGER.debug(
        "Diagnostic sensors created (System Health, Connection Latency,"
        " Last Event Age, API Request Rate, Average Latency)"
    )

    # Error Code Sensors
    for key in _ERROR_CODE_KEYS:
        if key in coordinator.data and (
            config["create_all"] or key in config["selected_sensors"]
        ):
            sensors.append(VioletErrorCodeSensor(coordinator, config_entry, key))
            handled_keys.add(key)
            _LOGGER.debug("Error code sensor created for %s", key)

    # Active Errors Sensor (shows all active errors at once)
    sensors.append(VioletActiveErrorsSensor(coordinator, config_entry))
    _LOGGER.debug("Active errors sensor created")

    # Pool Health Sensor (aggregate state: ok / warning / error / offline)
    sensors.append(VioletHealthSensor(coordinator, config_entry))
    _LOGGER.debug("Pool health sensor created")

    # Flow Rate Sensor
    flow_keys_present = any(key in coordinator.data for key in _FLOW_RATE_SOURCE_KEYS)
    flow_selected = (
        config["create_all"] or "flow_rate_adc3_priority" in config["selected_sensors"]
    )
    if flow_keys_present and flow_selected:
        sensors.append(VioletFlowRateSensor(coordinator, config_entry))
        handled_keys.update(_FLOW_RATE_SOURCE_KEYS)
        _LOGGER.debug("Priority flow rate sensor created.")

    # Pump Power Estimation Sensor
    if "filter_control" in config["active_features"] or config["create_all"]:
        sensors.append(VioletPumpPowerSensor(coordinator, config_entry))
        _LOGGER.debug("Pump power estimation sensor created.")

    # Dosing State Array Sensors
    for key, sensor_config in DOSING_STATE_SENSORS.items():
        if key in coordinator.data:
            # Check if feature is enabled
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in config["active_features"]:
                continue

            # Check if sensor is selected
            if not config["create_all"] and key not in config["selected_sensors"]:
                continue

            sensors.append(
                VioletDosingStateSensor(
                    coordinator,
                    config_entry,
                    key,
                    sensor_config["name"],
                    sensor_config["icon"],
                    translation_key=sensor_config.get("translation_key"),
                )
            )
            handled_keys.add(key)
            _LOGGER.debug("Dosing state sensor created for %s", key)

    # Composite State Sensors (PUMPSTATE, HEATERSTATE, SOLARSTATE, etc.)
    for key, sensor_config in COMPOSITE_STATE_SENSORS.items():
        if key in coordinator.data:
            # Check if feature is enabled
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in config["active_features"]:
                continue

            # Check if sensor is selected
            if not config["create_all"] and key not in config["selected_sensors"]:
                continue

            sensors.append(
                VioletDosingStateSensor(  # Reuse same class, handles both types
                    coordinator,
                    config_entry,
                    key,
                    sensor_config["name"],
                    sensor_config["icon"],
                    translation_key=sensor_config.get("translation_key"),
                )
            )
            handled_keys.add(key)
            _LOGGER.debug("Composite state sensor created for %s", key)

    # Runtime Sensors (PUMP_RUNTIME, SOLAR_RUNTIME, etc.)
    for key, sensor_config in RUNTIME_SENSORS.items():
        if key in coordinator.data:
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in config["active_features"]:
                continue
            if not config["create_all"] and key not in config["selected_sensors"]:
                continue

            sensors.append(
                VioletSensor(
                    coordinator,
                    config_entry,
                    _build_sensor_description(
                        key,
                        coordinator.data.get(key),
                        RUNTIME_SENSORS,
                        translation_key=sensor_config.get(
                            "translation_key", key.lower()
                        ),
                    ),
                )
            )
            handled_keys.add(key)
            _LOGGER.debug("Runtime sensor created for %s", key)

    # Dosing Statistics Sensors
    for key, sensor_config in DOSING_STATS_SENSORS.items():
        if key in coordinator.data:
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in config["active_features"]:
                continue
            if not config["create_all"] and key not in config["selected_sensors"]:
                continue

            sensors.append(
                VioletSensor(
                    coordinator,
                    config_entry,
                    _build_sensor_description(
                        key,
                        coordinator.data.get(key),
                        DOSING_STATS_SENSORS,
                        translation_key=sensor_config.get(
                            "translation_key", key.lower()
                        ),
                    ),
                )
            )
            handled_keys.add(key)
            _LOGGER.debug("Dosing stats sensor created for %s", key)

    # Extra Diagnostic Sensors (POLARITY, REMAINING_RANGE, last_error_id,
    # OmniTronic valve state, backwash last-run timestamps, etc.)
    for key, sensor_config in EXTRA_DIAGNOSTIC_SENSORS.items():
        if key in coordinator.data:
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in config["active_features"]:
                continue
            if not config["create_all"] and key not in config["selected_sensors"]:
                continue

            sensors.append(
                VioletSensor(
                    coordinator,
                    config_entry,
                    _build_sensor_description(
                        key,
                        coordinator.data.get(key),
                        EXTRA_DIAGNOSTIC_SENSORS,
                        translation_key=sensor_config.get(
                            "translation_key", key.lower()
                        ),
                    ),
                )
            )
            handled_keys.add(key)
            _LOGGER.debug("Extra diagnostic sensor created for %s", key)

    # Analog + Temperature switching-rule states (0/1 active flag per rule)
    for source in (ANALOG_RULE_SENSORS, TEMP_RULE_SENSORS):
        for key, sensor_config in source.items():
            if key not in coordinator.data:
                continue
            sensors.append(
                VioletSensor(
                    coordinator,
                    config_entry,
                    _build_sensor_description(
                        key,
                        coordinator.data.get(key),
                        source,
                        translation_key=sensor_config.get(
                            "translation_key", key.lower()
                        ),
                    ),
                )
            )
            handled_keys.add(key)

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
        **ONEWIRE_ROMCODE_SENSORS,
        **ANALOG_SENSORS,
        **STATUS_SENSORS,
        **RUNTIME_SENSORS,
        **DOSING_STATS_SENSORS,
        **SYSTEM_SENSORS,
    }

    for key in sorted(coordinator.data.keys()):
        if key in handled_keys or should_skip_sensor(key, coordinator.data.get(key)):
            continue

        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in config["active_features"]:
            continue

        if not config["create_all"] and key not in config["selected_sensors"]:
            continue

        predefined_info = all_predefined.get(key)
        tk = predefined_info.get("translation_key") if predefined_info else key.lower()

        description = _build_sensor_description(
            key,
            coordinator.data.get(key),
            all_predefined,
            translation_key=tk,
        )

        SensorClass = (
            VioletStatusSensor
            if key in STATUS_SENSORS and key not in ["fw", "FW"]
            else VioletSensor
        )
        sensors.append(SensorClass(coordinator, config_entry, description))

    return sensors
