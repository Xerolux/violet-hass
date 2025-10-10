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

from .const import DOMAIN, BINARY_SENSORS, STATE_MAP, CONF_ACTIVE_FEATURES
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Cover State Constants
COVER_STATE_CLOSED = 2
COVER_STATE_OPEN = 1
COVER_STATE_OPENING = 3
COVER_STATE_CLOSING = 4
COVER_STATE_UNKNOWN = 0

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
    """Repräsentation eines Violet Pool Binary Sensors - OPTIMIZED VERSION."""
    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialisiere den Binary Sensor."""
        super().__init__(coordinator, config_entry, description)
        _LOGGER.debug(
            "Initialisiere Binary Sensor: %s (unique_id=%s)",
            self.entity_id,
            self._attr_unique_id,
        )

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Sensor eingeschaltet ist."""
        state = self._get_sensor_state()
        _LOGGER.debug("Binary Sensor %s state: %s", self.entity_description.key, state)
        return state

    @property
    def icon(self) -> str | None:
        """Gibt das Icon basierend auf dem Zustand zurück."""
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
        """Rufe den aktuellen Sensorzustand ab - OPTIMIZED VERSION."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        _LOGGER.debug(
            "Binary Sensor state check für %s: raw=%s (type=%s)",
            key,
            raw_state,
            type(raw_state).__name__,
        )
        
        if raw_state is None or raw_state == "":
            _LOGGER.debug("Binary Sensor '%s' hat leeren/None Zustand - returning False", key)
            return False
        
        # Try integer interpretation first
        state_int = self._convert_to_int(raw_state)
        if state_int is not None:
            return self._interpret_int_state(state_int, key)
        
        # String interpretation
        return self._interpret_string_state(raw_state, key)

    def _convert_to_int(self, value: Any) -> int | None:
        """Konvertiere Wert zu Integer, wenn möglich."""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str) and value.strip().isdigit():
                return int(value.strip())
        except (ValueError, TypeError):
            pass
        return None

    def _interpret_int_state(self, state_int: int, key: str) -> bool:
        """Interpretiere Integer State-Wert."""
        # Check STATE_MAP first
        if state_int in STATE_MAP:
            result = STATE_MAP[state_int]
            _LOGGER.debug("State %d für %s in STATE_MAP → %s", state_int, key, result)
            return result
        
        # Generic interpretation: 0 = False, non-zero = True
        result = state_int != 0
        _LOGGER.debug("State %d für %s → %s (generic int logic)", state_int, key, result)
        return result

    def _interpret_string_state(self, raw_state: Any, key: str) -> bool:
        """Interpretiere String State-Wert."""
        state_str = str(raw_state).upper().strip()
        
        # Check STATE_MAP
        if state_str in STATE_MAP:
            result = STATE_MAP[state_str]
            _LOGGER.debug("String '%s' für %s in STATE_MAP → %s", state_str, key, result)
            return result
        
        # Known boolean strings
        true_values = {
            "TRUE",
            "ON",
            "1",
            "YES",
            "ACTIVE",
            "RUNNING",
            "ENABLED",
            "OPEN",
            "HIGH",
        }
        false_values = {
            "FALSE",
            "OFF",
            "0",
            "NO",
            "INACTIVE",
            "STOPPED",
            "DISABLED",
            "CLOSED",
            "LOW",
        }
        
        if state_str in true_values:
            _LOGGER.debug("String '%s' für %s → True", state_str, key)
            return True
        
        if state_str in false_values:
            _LOGGER.debug("String '%s' für %s → False", state_str, key)
            return False
        
        # Default: unknown states are False
        _LOGGER.debug("Unbekannter State '%s' für %s → False (default)", state_str, key)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes for debugging."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        return {
            "raw_state": str(raw_state),
            "state_type": type(raw_state).__name__,
            "interpreted_as": "ON" if self.is_on else "OFF",
        }


class CoverIsClosedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor für den Cover-Geschlossen-Status - OPTIMIZED VERSION."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialisiere den Cover-Geschlossen-Sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Cover Geschlossen"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_is_closed"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:window-shutter"
        self._attr_device_info = coordinator.device.device_info
        _LOGGER.debug("Initialisiere Cover-Geschlossen Sensor: %s", self._attr_unique_id)

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn die Abdeckung geschlossen ist."""
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
        """Prüfe ob Cover geschlossen ist - mit Konstanten."""
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
            _LOGGER.debug("Cover state converted to int %d → closed=%s", state_int, is_closed)
            return is_closed
        except (ValueError, TypeError):
            _LOGGER.warning("Unbekannter Cover State Type: %s", type(cover_state))
            return False

    @property
    def icon(self) -> str:
        """Return icon based on cover state."""
        return "mdi:window-shutter" if self.is_on else "mdi:window-shutter-open"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
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
    """Richte Binary Sensors für die Config Entry ein - OPTIMIZED VERSION."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[BinarySensorEntity] = []

    _LOGGER.info("Binary Sensor Setup - Active features: %s", active_features)

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