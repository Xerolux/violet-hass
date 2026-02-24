from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory

from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)


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


class VioletAPIRequestRateSensor(VioletPoolControllerEntity, SensorEntity):
    """Sensor for API request rate (requests per minute)."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the API request rate sensor."""
        description = SensorEntityDescription(
            key="api_request_rate",
            translation_key="api_request_rate",
            name="API Request Rate",
            icon="mdi:network",
            native_unit_of_measurement="req/min",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the API request rate."""
        return round(self.coordinator.device.api_request_rate, 1)


class VioletAverageLatencySensor(VioletPoolControllerEntity, SensorEntity):
    """Sensor for average connection latency."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the average latency sensor."""
        description = SensorEntityDescription(
            key="average_latency",
            translation_key="average_latency",
            name="Average Latency",
            icon="mdi:speedometer",
            native_unit_of_measurement="ms",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the average connection latency."""
        return round(self.coordinator.device.average_latency, 0)


