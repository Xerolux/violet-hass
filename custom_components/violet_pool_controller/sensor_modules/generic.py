from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry

from ..const import DOMAIN
from ..const_devices import VioletState
from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity
from .base import (
    _ALL_TEXT_SENSORS,
    _TIMESTAMP_KEYS,
    _TIMESTAMP_SUFFIXES,
    _TIME_FORMAT_KEYS,
)

_LOGGER = logging.getLogger(__name__)


class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Represents a generic Violet Pool Controller sensor."""

    entity_description: SensorEntityDescription
    coordinator: VioletPoolDataUpdateCoordinator

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
    def state_class(self) -> SensorStateClass | None:
        """Override state_class for contact sensors to prevent numeric conversion errors.

        Contact sensors return string values ('RELEASED', 'TRIGGERED') but may have been
        incorrectly created with state_class='measurement'. This property override
        ensures they always return None, preventing Home Assistant from attempting
        numeric conversion.
        """
        # Force state_class to None for contact sensors
        if "contact" in self.entity_description.key.lower():
            # Only log if we're actually overriding a non-None value
            if self.entity_description.state_class is not None:
                _LOGGER.debug(
                    "Overriding state_class to None for contact sensor: %s",
                    self.entity_description.key,
                )
            return None
        return self.entity_description.state_class

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Returns the native value of the sensor, formatted for Home Assistant."""
        if self.coordinator.data is None:
            return None

        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)

        if raw_value is None:
            return None

        # Check if key indicates a timestamp sensor (by suffix or membership in _TIMESTAMP_KEYS)
        is_timestamp_key = key in _TIMESTAMP_KEYS or any(
            key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES
        )

        if is_timestamp_key and key not in _TIME_FORMAT_KEYS:
            try:
                timestamp = float(raw_value)
                # Handle milliseconds: if timestamp > 10000000000, it's in milliseconds
                # (10000000000 ms = September 2001, in seconds since 1970)
                if timestamp > 10000000000:
                    timestamp = timestamp / 1000
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
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

            # Water chemistry values (pH, ORP, Chlorine) - 2 decimal places for precision
            if key in {"pH_value", "orp_value", "pot_value"}:
                return round(num_value, 2)

            # Temperature sensors (all onewire, CPU temps) - 2 decimal places
            # IMPORTANT: Exclude freezecount, faultcount - these are counters, NOT temperatures!
            if ("temp" in key.lower() or "onewire" in key.lower()) and "freezecount" not in key.lower() and "faultcount" not in key.lower():
                return round(num_value, 2)

            # Analog sensors (ADC, IMP) - 2 decimal places for precision
            if key.startswith(("ADC", "IMP")):
                return round(num_value, 2)

            # Percentage values - 1 decimal place
            if key.startswith(("SYSTEM_")) or "_" in key and key.split("_")[-1] in ["PERCENT", "PERCENTAGE"]:
                return round(num_value, 1)

            # Integer values (counts, RPM, etc.) - round to integer if close to whole number
            if num_value.is_integer():
                return int(num_value)

            # All other numeric values - 2 decimal places for consistency
            return round(num_value, 2)

        except (ValueError, TypeError):
            # Explicitly cast to string to match return type
            return str(raw_value)


class VioletStatusSensor(VioletSensor):
    """Represents a sensor for status values that use VioletState."""

    def _resolve_raw_value(self) -> Any | None:
        """Resolve the best raw value, preferring *STATE key with fallback."""
        key = self.entity_description.key
        state_key = f"{key}STATE"

        # Prefer *STATE field (e.g., PUMPSTATE = "3|PUMP_ANTI_FREEZE")
        raw_value = self.coordinator.data.get(state_key)

        # Skip empty/useless *STATE values (e.g., SOLARSTATE = "[]")
        if raw_value is not None and str(raw_value).strip() in ("", "[]", "{}"):
            raw_value = None

        if raw_value is None:
            raw_value = self.coordinator.data.get(key)

        return raw_value

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the display string for the status."""
        if self.coordinator.data is None:
            return None

        raw_value = self._resolve_raw_value()
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

        raw_value = self._resolve_raw_value()
        if raw_value is None:
            return super().icon
        return VioletState(raw_value, self.entity_description.key).icon


