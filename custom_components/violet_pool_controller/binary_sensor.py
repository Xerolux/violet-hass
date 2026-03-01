
"""Binary sensor platform for Violet Pool Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SENSORS, CONF_ACTIVE_FEATURES, DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity, interpret_state_as_bool

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# Feature mapping für Binary Sensors
BINARY_SENSOR_FEATURE_MAP = {
    "PUMP": "filter_control",
    "HEATER": "heating",
    "SOLAR": "solar",
    "LIGHT": "led_lighting",
    "BACKWASH": "backwash",
    "BACKWASHRINSE": "backwash",
    "DOS_1_CL": "chlorine_control",
    "DOS_4_PHM": "ph_control",
    "DOS_5_PHP": "ph_control",
    "DOS_6_FLOC": "chlorine_control",
    "REFILL": "water_refill",
    "PVSURPLUS": "pv_surplus",
}


class VioletBinarySensor(VioletPoolControllerEntity, BinarySensorEntity):
    """Representation of a Violet Pool binary sensor."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """
        Initialize the binary sensor.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The binary sensor entity description.
        """
        super().__init__(coordinator, config_entry, description)
        _LOGGER.debug(
            "Initializing Binary Sensor: %s (unique_id=%s)",
            self.entity_id,
            self._attr_unique_id,
        )

    @property
    def is_on(self) -> bool:
        """
        Return True if the sensor is on.

        Returns:
            True if on, False otherwise.
        """
        return self._get_sensor_state()

    @property
    def icon(self) -> str | None:
        """
        Return the icon based on state.

        Returns:
            The icon string.
        """
        base_icon = self.entity_description.icon

        if not base_icon:
            return None

        # Handle outline icons
        if base_icon.endswith("-outline"):
            return base_icon.replace("-outline", "") if self.is_on else base_icon

        # Add -off suffix for inactive state
        if not self.is_on and not base_icon.endswith("-off"):
            return f"{base_icon}-off"

        return base_icon

    def _get_sensor_state(self) -> bool:
        """
        Get the current sensor state.

        Returns:
            The boolean state of the sensor.
        """
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        return interpret_state_as_bool(raw_state, key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return additional state attributes for debugging.

        Returns:
            A dictionary of attributes.
        """
        key = self.entity_description.key
        raw_state = self.get_value(key, "")

        return {
            "raw_state": str(raw_state),
            "state_type": type(raw_state).__name__,
            "interpreted_as": "ON" if self.is_on else "OFF",
        }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up binary sensors for the config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[BinarySensorEntity] = []

    _LOGGER.info("Binary Sensor Setup - Active features: %s", active_features)

    # None-check for coordinator.data
    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator data is None for '%s'. "
            "Binary sensors will not be created.",
            config_entry.title,
        )
        return

    # Diagnose für verfügbare Daten
    if coordinator.data:
        _LOGGER.debug(
            "Coordinator data keys: %d - %s",
            len(coordinator.data.keys()),
            list(coordinator.data.keys())[:10],  # First 10 keys for brevity
        )

    # Create binary sensor descriptions from BINARY_SENSORS constant
    for sensor_config in BINARY_SENSORS:
        if not isinstance(sensor_config, dict):
            _LOGGER.warning("Invalid sensor config: %s", sensor_config)
            continue

        # Use proper BinarySensorEntityDescription
        description = BinarySensorEntityDescription(
            key=sensor_config["key"],
            name=sensor_config["name"],
            icon=sensor_config.get("icon"),  # type: ignore[arg-type]
            device_class=sensor_config.get("device_class"),  # type: ignore[arg-type]
            entity_category=sensor_config.get("entity_category"),  # type: ignore[arg-type]
        )

        feature_id = BINARY_SENSOR_FEATURE_MAP.get(description.key)

        # Check if feature is active (if feature_id is specified)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Skipping binary sensor %s: feature %s not active",
                description.key,
                feature_id,
            )
            continue

        # Check if data is available for this sensor
        # Allow INPUT sensors even without data (they might be populated later)
        if (
            coordinator.data
            and description.key not in coordinator.data
            and not description.key.startswith("INPUT")
        ):
            _LOGGER.debug(
                "Skipping binary sensor %s: no data available",
                description.key,
            )
            continue

        _LOGGER.debug("Creating binary sensor: %s", description.name)
        entities.append(VioletBinarySensor(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "%d binary sensors added: %s",
            len(entities),
            [e.name for e in entities],
        )
    else:
        _LOGGER.warning("No binary sensors were set up")
