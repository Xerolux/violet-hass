"""Base entity class with performance optimizations for Violet Pool Controller."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# =============================================================================
# SHARED UTILITY FUNCTIONS
# =============================================================================

# Boolean State Mapping (used by switches and other boolean entities)
STATE_MAP = {
    0: False,  # Off
    1: True,  # On
    2: True,  # Auto (usually means on with automatic control)
    3: True,  # Auto with timer
    4: True,  # Manual forced on
    5: False,  # Auto waiting
    6: False,  # Manual forced off
}


# Pre-compiled numeric pattern for performance
NUMERIC_PATTERN = re.compile(r"^-?\d+$")


def convert_to_int(value: Any) -> int | None:
    """
    Convert value to integer if possible.

    Args:
        value: Value to convert.

    Returns:
        Integer value or None if conversion fails.
    """
    # Fast path for common cases
    if isinstance(value, int):
        return value
    if isinstance(value, str) and NUMERIC_PATTERN.match(value.strip()):
        return int(value.strip())

    # Fallback for complex cases
    try:
        if isinstance(value, (int, float)):
            return int(value)
        return int(float(value)) if "." in str(value) else int(value)
    except (ValueError, TypeError):
        return None


def interpret_state_as_bool(raw_state: Any, key: str = "") -> bool:
    """
    Interpret raw state value as boolean.

    Args:
        raw_state: Raw state value from API.
        key: Entity key for logging.

    Returns:
        Boolean interpretation.
    """
    # Priority 1: Check STATE_MAP first (most common)
    state_int = convert_to_int(raw_state)
    if state_int is not None:
        if state_int in STATE_MAP:
            return STATE_MAP[state_int]
        # Generic interpretation: 0 = False, non-zero = True
        return state_int != 0

    # Optimized string interpretation with pre-compiled patterns
    state_str = str(raw_state).upper().strip()

    # Handle composite states like "5|AUTO_WAIT"
    if "|" in state_str:
        prefix = state_str.split("|")[0]
        state_int = convert_to_int(prefix)
        if state_int is not None:
            if state_int in STATE_MAP:
                return STATE_MAP[state_int]
            return state_int != 0

    # Pre-compiled patterns for performance
    TRUE_PATTERN = re.compile(r"^(TRUE|ON|1|YES|ACTIVE|ENABLED)$")
    FALSE_PATTERN = re.compile(r"^(FALSE|OFF|0|NO|INACTIVE|DISABLED)$")
    NUMERIC_PATTERN = re.compile(r"^-?\d+$")

    # Fast boolean string checks using pre-compiled patterns
    if TRUE_PATTERN.match(state_str):
        return True
    if FALSE_PATTERN.match(state_str):
        return False

    # Fast numeric check
    if NUMERIC_PATTERN.match(state_str):
        return int(state_str) != 0

    # Default: non-empty/valid numeric = True
    return bool(raw_state) and raw_state != ""


# =============================================================================
# BASE ENTITY CLASS
# =============================================================================


class VioletPoolControllerEntity(CoordinatorEntity):
    """Basis-Entity-Klasse für alle Violet Pool Controller Entities."""

    coordinator: VioletPoolDataUpdateCoordinator

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description,
    ) -> None:
        """
        Initialize entity with intelligent caching.

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
        # If translation_key is set, name should be None to let HA handle it.
        # But if it is not set, we use name from description.
        if entity_description.translation_key:
            self._attr_name = None
        else:
            self._attr_name = entity_description.name

        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = cast(DeviceInfo, coordinator.device.device_info)

        # Performance optimization: Entity-level caching
        self._value_cache: dict[str, Any] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 1.0  # 1 second cache

        _LOGGER.debug(
            "Entity initialisiert: %s (Key: %s, ID: %s)",
            entity_description.name or entity_description.translation_key,
            entity_description.key,
            self._attr_unique_id,
        )

    @property
    def device(self) -> Any:
        """Return device instance."""
        return self.coordinator.device

    @property
    def available(self) -> bool:
        """
        Return whether entity is available.

        Entity is available if:
            - The last coordinator update was successful AND
            - The device itself is available.

        Returns:
            True if available, False otherwise.
        """
        is_available = self.coordinator.last_update_success and self.device.available

        if not is_available:
            _LOGGER.debug(
                "Entity '%s' nicht verfügbar (coordinator_success: %s, device_available: %s)",
                self.name or self.entity_description.key,
                self.coordinator.last_update_success,
                self.device.available,
            )

        return is_available

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get value with intelligent caching.

        Args:
            key: The data key.
            default: Default value if key does not exist.

        Returns:
            The value or default.
        """
        current_time = asyncio.get_event_loop().time()

        # Check cache validity
        if (current_time - self._cache_timestamp) > self._cache_ttl:
            self._value_cache.clear()
            self._cache_timestamp = current_time

        # Use cached value if available
        if key not in self._value_cache:
            if not self.coordinator.data:
                self._value_cache[key] = default
            else:
                self._value_cache[key] = self.coordinator.data.get(key, default)

        return self._value_cache[key]

    def get_float_value(self, key: str, default: Any = None) -> float | None:
        """
        Get float value from coordinator data.

        Args:
            key: The data key.
            default: Default value if key does not exist or conversion fails.

        Returns:
            Float value or None.
        """
        value = self.get_value(key, default)

        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            _LOGGER.debug(
                "Konvertierung zu Float für Key '%s' fehlgeschlagen: %s", key, value
            )
            return default if default is not None else 0.0

    def get_bool_value(self, key: str, default: Any = None) -> bool:
        """
        Get boolean value from coordinator data.

        Args:
            key: The data key.
            default: Default value if key does not exist.

        Returns:
            Boolean interpretation.
        """
        value = self.get_value(key, default)

        # Use interpretation function
        return interpret_state_as_bool(value, key)

    def get_str_value(self, key: str, default: str | None = None) -> str | None:
        """
        Get string value from coordinator data.

        Args:
            key: The data key.
            default: Default value if key does not exist.

        Returns:
            String value or None.
        """
        value = self.get_value(key, default)

        if value is None:
            return None
        return str(value)

    def get_int_value(self, key: str, default: int | None = None) -> int | None:
        """
        Get integer value from coordinator data.

        Args:
            key: The data key.
            default: Default value if key does not exist or conversion fails.

        Returns:
            Integer value or None.
        """
        value = self.get_value(key, default)
        return convert_to_int(value) if value is not None else default
