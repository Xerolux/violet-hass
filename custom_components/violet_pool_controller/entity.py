"""Base entity class for Violet Pool Controller entities."""
import logging
from typing import Any, Optional

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerEntity(CoordinatorEntity):
    """Basis-Entity-Klasse für Violet Pool Controller."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, entity_description) -> None:
        """Initialisiere die Entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = entity_description
        self._attr_has_entity_name = True
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = coordinator.device.device_info

    @property
    def device(self) -> Any:
        """Return device instance."""
        return self.coordinator.device

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.device.available

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get value from coordinator data."""
        if not self.coordinator.data:
            return default
        return self.coordinator.data.get(key, default)

    def get_str_value(self, key: str, default: str = "") -> str:
        """Get string value from coordinator data."""
        value = self.get_value(key, default)
        return str(value) if value is not None else default

    def get_int_value(self, key: str, default: int = 0) -> int:
        """Get integer value from coordinator data."""
        value = self.get_value(key, default)
        try:
            return int(float(value)) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_float_value(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """Get float value from coordinator data."""
        value = self.get_value(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """Get boolean value from coordinator data."""
        value = self.get_value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.upper() in ("TRUE", "ON", "1", "YES")
        try:
            return bool(int(value)) if value is not None else default
        except (ValueError, TypeError):
            return default
