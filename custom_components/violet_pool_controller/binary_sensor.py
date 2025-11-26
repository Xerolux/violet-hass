"""Binary Sensor Integration für den Violet Pool Controller - OPTIMIZED VERSION."""

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSORS, CONF_ACTIVE_FEATURES
from .entity import VioletPoolControllerEntity, interpret_state_as_bool
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Cover State Constants
COVER_STATE_CLOSED = 2

# String representations of cover states
COVER_CLOSED_STRINGS = {"CLOSED", "2", "GESCHLOSSEN"}
COVER_OPEN_STRINGS = {"OPEN", "1", "OFFEN"}

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
    "COVER_OPEN": "cover_control",
    "COVER_CLOSE": "cover_control",
    "COVER_STATE": "cover_control",
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
        state = self._get_sensor_state()
        _LOGGER.debug("Binary Sensor %s state: %s", self.entity_description.key, state)
        return state

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

        _LOGGER.debug(
            "Binary Sensor state check für %s: raw=%s (type=%s)",
            key,
            raw_state,
            type(raw_state).__name__,
        )

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


class CoverIsClosedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor indicating if the cover is closed."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """
        Initialize the cover closed sensor.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
        """
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Cover Geschlossen"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_is_closed"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:window-shutter"
        self._attr_device_info = coordinator.device.device_info
        _LOGGER.debug(
            "Initialisiere Cover-Geschlossen Sensor: %s", self._attr_unique_id
        )

    @property
    def available(self) -> bool:
        """
        Return whether the entity is available.

        Returns:
            True if available, False otherwise.
        """
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """
        Return True if the cover is closed.

        Returns:
            True if closed, False otherwise.
        """
        if not self.coordinator.data:
            _LOGGER.debug("Cover-Geschlossen Sensor: Keine Daten verfügbar")
            return False

        cover_state = self.coordinator.data.get("COVER_STATE")
        _LOGGER.debug(
            "Cover-Geschlossen Sensor: COVER_STATE=%s (type=%s)",
            cover_state,
            type(cover_state).__name__,
        )

        return self._is_cover_closed(cover_state)

    def _is_cover_closed(self, cover_state: Any) -> bool:
        """
        Check if the cover is closed.

        Args:
            cover_state: The raw cover state.

        Returns:
            True if closed, False otherwise.
        """
        if cover_state is None:
            return False

        # Integer check
        if isinstance(cover_state, int):
            is_closed = cover_state == COVER_STATE_CLOSED
            _LOGGER.debug("Cover state integer %d → closed=%s", cover_state, is_closed)
            return is_closed

        # String check
        if isinstance(cover_state, str):
            state_upper = cover_state.upper().strip()
            is_closed = state_upper in COVER_CLOSED_STRINGS
            _LOGGER.debug("Cover state string '%s' → closed=%s", state_upper, is_closed)
            return is_closed

        # Try conversion
        try:
            state_int = int(cover_state)
            is_closed = state_int == COVER_STATE_CLOSED
            _LOGGER.debug(
                "Cover state converted to int %d → closed=%s", state_int, is_closed
            )
            return is_closed
        except (ValueError, TypeError):
            _LOGGER.warning("Unbekannter Cover State Type: %s", type(cover_state))
            return False

    @property
    def icon(self) -> str:
        """
        Return icon based on cover state.

        Returns:
            The icon string.
        """
        return "mdi:window-shutter" if self.is_on else "mdi:window-shutter-open"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return additional state attributes.

        Returns:
            A dictionary of attributes.
        """
        if not self.coordinator.data:
            return {}

        cover_state = self.coordinator.data.get("COVER_STATE")
        return {
            "raw_state": str(cover_state),
            "state_type": type(cover_state).__name__,
            "is_closed": self.is_on,
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

    # None-Check für coordinator.data
    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator-Daten sind None für '%s'. "
            "Binary Sensors werden nicht erstellt.",
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
            _LOGGER.warning("Ungültige Sensor-Config: %s", sensor_config)
            continue

        # Use proper BinarySensorEntityDescription
        description = BinarySensorEntityDescription(
            key=sensor_config["key"],
            name=sensor_config["name"],
            icon=sensor_config.get("icon"),
            device_class=sensor_config.get("device_class"),
            entity_category=sensor_config.get("entity_category"),
        )

        feature_id = BINARY_SENSOR_FEATURE_MAP.get(description.key)

        # Check if feature is active (if feature_id is specified)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe Binary Sensor %s: Feature %s nicht aktiv",
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
                "Überspringe Binary Sensor %s: Keine Daten verfügbar",
                description.key,
            )
            continue

        _LOGGER.debug("Erstelle Binary Sensor: %s", description.name)
        entities.append(VioletBinarySensor(coordinator, config_entry, description))

    # Add cover closed sensor if cover control is active
    if "cover_control" in active_features:
        _LOGGER.debug("Erstelle Cover-Geschlossen Sensor")
        entities.append(CoverIsClosedBinarySensor(coordinator, config_entry))

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "✓ %d Binary Sensors erfolgreich eingerichtet: %s",
            len(entities),
            [e.name for e in entities],
        )
    else:
        _LOGGER.warning("⚠ Keine Binary Sensors eingerichtet")
