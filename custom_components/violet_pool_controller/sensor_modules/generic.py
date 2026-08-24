# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util
from violet_poolcontroller_api.const_devices import VioletState

from ..const import DOMAIN
from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity
from .base import (
    _TIME_FORMAT_KEYS,
    _TIMESTAMP_KEYS,
    _TIMESTAMP_SUFFIXES,
    format_seconds_to_readable,
    is_text_sensor,
)

_LOGGER = logging.getLogger(__name__)

_MILLISECONDS_THRESHOLD = 10_000_000_000
_MAX_FUTURE_EVENT_SKEW = timedelta(minutes=5)
_PAST_EVENT_SUFFIXES = (
    "_LAST_ON",
    "_LAST_OFF",
    "_LAST_AUTO_RUN",
    "_LAST_MANUAL_RUN",
    "_LAST_CAN_RESET",
)


def _timestamp_seconds(raw_value: Any) -> float:
    """Return a controller timestamp in seconds.

    The firmware mixes seconds and milliseconds depending on the field.
    """
    timestamp = float(raw_value)
    if timestamp > _MILLISECONDS_THRESHOLD:
        timestamp /= 1000
    return timestamp


def _local_wall_epoch_to_utc(timestamp: float) -> datetime:
    """Decode a Unix-shaped value that actually contains local wall time.

    Violet firmware writes e.g. 15:00 local as if 15:00 were UTC.  Attaching
    Home Assistant's configured timezone to those clock components recovers
    the real instant and also applies the offset valid on the event date.
    """
    wall_time = datetime.fromtimestamp(timestamp, tz=UTC).replace(tzinfo=None)
    return wall_time.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE).astimezone(UTC)


def _controller_uses_local_wall_epoch(data: Mapping[str, Any]) -> bool:
    """Detect whether this controller reports local wall-clock epochs."""
    raw_current = data.get("CURRENT_TIME_UNIX")
    if raw_current is None:
        # This is the format used by current Violet firmware.  The live clock
        # field normally makes the decision below explicit; keep the known
        # firmware convention as the fallback for reduced payloads.
        return dt_util.DEFAULT_TIME_ZONE is not UTC

    try:
        timestamp = _timestamp_seconds(raw_current)
        if timestamp <= 0:
            return dt_util.DEFAULT_TIME_ZONE is not UTC
        as_epoch = datetime.fromtimestamp(timestamp, tz=UTC)
        as_local_wall = _local_wall_epoch_to_utc(timestamp)
    except (ValueError, TypeError, OverflowError, OSError):
        return dt_util.DEFAULT_TIME_ZONE is not UTC

    now = datetime.now(UTC)
    return abs(as_local_wall - now) < abs(as_epoch - now)


def controller_timestamp_to_datetime(
    raw_value: Any,
    key: str,
    data: Mapping[str, Any],
) -> datetime | None:
    """Convert a Violet timestamp to a valid Home Assistant UTC datetime."""
    timestamp = _timestamp_seconds(raw_value)
    # Zero and negative values are firmware sentinels for "never".
    if timestamp <= 0:
        return None

    value = (
        _local_wall_epoch_to_utc(timestamp)
        if _controller_uses_local_wall_epoch(data)
        else datetime.fromtimestamp(timestamp, tz=UTC)
    )

    # LAST_* values describe completed events.  Uninitialised firmware fields
    # can contain far-future sentinels (observed as "in 474 years" in HA).
    if key.upper().endswith(_PAST_EVENT_SUFFIXES) and (
        value > datetime.now(UTC) + _MAX_FUTURE_EVENT_SKEW
    ):
        return None

    return value


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
        """Override state_class for contact sensors to prevent numeric
        conversion errors.

        Contact sensors return string values ('RELEASED', 'TRIGGERED') but
        may have been incorrectly created with state_class='measurement'.
        This property override ensures they always return None, preventing
        Home Assistant from attempting numeric conversion.
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
        # EntityDescription types state_class as SensorStateClass | str | None;
        # every description in this integration uses the enum.
        return cast(SensorStateClass | None, self.entity_description.state_class)

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Returns the native value of the sensor, formatted for Home Assistant."""
        if self.coordinator.data is None:
            return None

        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)

        if raw_value is None:
            return None

        # Check if key indicates a timestamp sensor
        # (by suffix or membership in _TIMESTAMP_KEYS)
        is_timestamp_key = key in _TIMESTAMP_KEYS or any(
            key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES
        )

        if is_timestamp_key and key not in _TIME_FORMAT_KEYS:
            try:
                return controller_timestamp_to_datetime(raw_value, key, self.coordinator.data)
            except (ValueError, TypeError, OverflowError, OSError) as err:
                self._logger.warning(
                    "Timestamp conversion failed for %s with value '%s': %s",
                    key,
                    raw_value,
                    err,
                )
                return None

        if is_text_sensor(key):
            return str(raw_value)

        # Format DI-Rule stopwatch remaining time (seconds) to readable format
        if "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH" in key:
            try:
                return format_seconds_to_readable(float(raw_value))
            except (ValueError, TypeError):
                return str(raw_value)

        try:
            num_value = float(raw_value)

            # Water chemistry values (pH, ORP, Chlorine) -
            # 2 decimal places for precision
            if key in {"pH_value", "orp_value", "pot_value"}:
                return round(num_value, 2)

            # Temperature sensors (all onewire, CPU temps) - 2 decimal places
            # IMPORTANT: Exclude freezecount, faultcount -
            # these are counters, NOT temperatures!
            # ROM-code sensors are excluded via the is_text_sensor() return above.
            if (
                ("temp" in key.lower() or "onewire" in key.lower())
                and "freezecount" not in key.lower()
                and "faultcount" not in key.lower()
            ):
                return round(num_value, 2)

            # Analog sensors (ADC, IMP) - 2 decimal places for precision
            if key.startswith(("ADC", "IMP")):
                return round(num_value, 2)

            # Percentage values - 1 decimal place
            if (
                key.startswith("SYSTEM_")
                or "_" in key
                and key.split("_")[-1] in ["PERCENT", "PERCENTAGE"]
            ):
                return round(num_value, 1)

            # Integer values (counts, RPM, etc.) -
            # round to integer if close to whole number
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
        if raw_value is None:
            return None
        try:
            return VioletState(raw_value, self.entity_description.key).display_mode
        except (ValueError, KeyError, TypeError, AttributeError):
            _LOGGER.warning(
                "VioletState failed for key=%s raw=%s",
                self.entity_description.key,
                raw_value,
            )
            return str(raw_value)

    @property
    def icon(self) -> str | None:
        """Return the icon corresponding to the current status."""
        if self.coordinator.data is None:
            return cast(str | None, super().icon)

        raw_value = self._resolve_raw_value()
        if raw_value is None:
            return cast(str | None, super().icon)
        return cast(str | None, VioletState(raw_value, self.entity_description.key).icon)
