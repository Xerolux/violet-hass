"""Base entity class for Violet Pool Controller entities."""
import logging
import re
from typing import Any, Optional

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityDescription
from homeassistant.config_entries import ConfigEntry

from .const import STATE_MAP
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


# =============================================================================
# SHARED UTILITY FUNCTIONS
# =============================================================================

def convert_to_int(value: Any) -> int | None:
    """
    Convert value to integer if possible.

    Args:
        value: Value to convert.

    Returns:
        Integer value or None if conversion fails.
    """
    try:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    except (ValueError, TypeError):
        pass
    return None


def interpret_state_as_bool(raw_state: Any, key: str = "") -> bool:
    """
    Interpret raw state value as boolean.

    Supports:
    - Integer states (via STATE_MAP)
    - String states (ON/OFF, TRUE/FALSE, etc.)

    Args:
        raw_state: Raw state value from API.
        key: Entity key for logging.

    Returns:
        Boolean interpretation of the state.
    """
    if raw_state is None or raw_state == "":
        return False

    # Try integer interpretation first
    state_int = convert_to_int(raw_state)

    # ✅ Robust handling for composite strings like "3|PUMP_ANTI_FREEZE"
    if state_int is None and isinstance(raw_state, str):
        numeric_prefix = re.match(r"\s*(-?\d+)", raw_state)
        if numeric_prefix:
            state_int = int(numeric_prefix.group(1))
    if state_int is not None:
        # Check STATE_MAP first
        if state_int in STATE_MAP:
            return STATE_MAP[state_int]
        # Generic interpretation: 0 = False, non-zero = True
        return state_int != 0

    # String interpretation
    state_str = str(raw_state).upper().strip()

    # Check STATE_MAP for string states
    if state_str in STATE_MAP:
        return STATE_MAP[state_str]

    # Known boolean strings
    true_values = {
        "TRUE", "ON", "1", "YES", "ACTIVE", "RUNNING",
        "ENABLED", "OPEN", "HIGH", "MANUAL", "MAN"
    }
    false_values = {
        "FALSE", "OFF", "0", "NO", "INACTIVE", "STOPPED",
        "DISABLED", "CLOSED", "LOW"
    }

    if state_str in true_values:
        return True

    if state_str in false_values:
        return False

    # Default: unknown states are False
    _LOGGER.debug("Unknown state '%s' for %s -> False (default)", state_str, key)
    return False


class VioletPoolControllerEntity(CoordinatorEntity):
    """Basis-Entity-Klasse für alle Violet Pool Controller Entities."""

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry, 
        entity_description: EntityDescription
    ) -> None:
        """
        Initialize the entity.
        
        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            entity_description: The entity description.
        """
        super().__init__(coordinator)
        
        self.config_entry = config_entry
        self.entity_description = entity_description
        
        # Entity Attribute
        self._attr_has_entity_name = True
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = coordinator.device.device_info
        
        _LOGGER.debug(
            "Entity initialisiert: %s (Key: %s, ID: %s)",
            entity_description.name,
            entity_description.key,
            self._attr_unique_id
        )

    @property
    def device(self) -> Any:
        """Return the device instance."""
        return self.coordinator.device

    @property
    def available(self) -> bool:
        """
        Return whether the entity is available.
        
        Entity is available if:
        - The last coordinator update was successful AND
        - The device itself is available.

        Returns:
            True if available, False otherwise.
        """
        is_available = (
            self.coordinator.last_update_success and 
            self.device.available
        )
        
        if not is_available:
            _LOGGER.debug(
                "Entity '%s' nicht verfügbar (coordinator_success: %s, device_available: %s)",
                self.name,
                self.coordinator.last_update_success,
                self.device.available
            )
        
        return is_available

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from coordinator data.
        
        Args:
            key: The data key.
            default: Default value if key does not exist.
            
        Returns:
            The value or the default.
        """
        if not self.coordinator.data:
            _LOGGER.debug("Keine Coordinator-Daten verfügbar für Key '%s'", key)
            return default
        
        value = self.coordinator.data.get(key, default)
        
        if value is None and default is not None:
            _LOGGER.debug(
                "Key '%s' nicht in Daten gefunden, verwende default: %s", 
                key, 
                default
            )
        
        return value

    def get_str_value(self, key: str, default: str = "") -> str:
        """
        Get a string value from coordinator data.
        
        Args:
            key: The data key.
            default: Default value if key does not exist.
            
        Returns:
            String value or default.
        """
        value = self.get_value(key, default)
        
        if value is None:
            return default
        
        return str(value)

    def get_int_value(self, key: str, default: int = 0) -> int:
        """
        Get an integer value from coordinator data.
        
        Args:
            key: The data key.
            default: Default value if key does not exist or conversion fails.
            
        Returns:
            Integer value or default.
        """
        value = self.get_value(key, default)
        
        if value is None:
            return default
        
        try:
            # Unterstützt auch Float → Int Konvertierung
            return int(float(value))
        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Konvertierung zu int fehlgeschlagen für Key '%s' (Wert: %s): %s",
                key, value, err
            )
            return default

    def get_float_value(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get a float value from coordinator data.
        
        Args:
            key: The data key.
            default: Default value if key does not exist or conversion fails.
            
        Returns:
            Float value or default.
        """
        value = self.get_value(key, default)
        
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Konvertierung zu float fehlgeschlagen für Key '%s' (Wert: %s): %s",
                key, value, err
            )
            return default

    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean value from coordinator data.
        
        Supports various formats:
        - Boolean: True/False
        - String: "TRUE", "ON", "1", "YES" (case-insensitive)
        - Integer: 0 = False, anything else = True
        
        Args:
            key: The data key.
            default: Default value if key does not exist or conversion fails.
            
        Returns:
            Boolean value or default.
        """
        value = self.get_value(key, default)
        
        if value is None:
            return default
        
        # Direkter Boolean
        if isinstance(value, bool):
            return value
        
        # String-Werte
        if isinstance(value, str):
            return value.upper() in ("TRUE", "ON", "1", "YES", "ENABLED")
        
        # Numerische Werte
        try:
            return bool(int(float(value)))
        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Konvertierung zu bool fehlgeschlagen für Key '%s' (Wert: %s): %s",
                key, value, err
            )
            return default

    def has_value(self, key: str) -> bool:
        """
        Check if a key exists in coordinator data.
        
        Args:
            key: The data key.
            
        Returns:
            True if the key exists, False otherwise.
        """
        if not self.coordinator.data:
            return False

        return key in self.coordinator.data
