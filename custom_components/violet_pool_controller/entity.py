"""Base entity class for Violet Pool Controller entities."""
import logging
from typing import Any, Optional, Union

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, MANUFACTURER
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerEntity(CoordinatorEntity):
    """Base entity class for Violet Pool Controller entities."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: Any,
    ) -> None:
        """Initialize the entity.
        
        Args:
            coordinator: The data update coordinator
            config_entry: The config entry
            entity_description: The entity description
        """
        super().__init__(coordinator)
        
        self.config_entry = config_entry
        self.entity_description = entity_description
        
        # Set up entity_id and unique_id
        self._attr_has_entity_name = True
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        
        # Set up device info
        self._attr_device_info = coordinator.device.device_info
        
        # Create a logger for this entity
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")
        
    @property
    def device(self) -> Any:
        """Return the device instance."""
        return self.coordinator.device
        
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.device.available:
            return False
        if not self.coordinator.data:
            return False
        return self.coordinator.last_update_success
        
    def _update_from_coordinator(self) -> None:
        """Update the entity from the coordinator data.
        
        This method should be overridden by subclasses to update any entity-specific
        properties from the coordinator data.
        """
        pass
        
    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        self._update_from_coordinator()
        
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_coordinator()
        self.async_write_ha_state()
        
    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """Get a boolean value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            bool: The boolean value
        """
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ["true", "1", "on", "yes"]
        return default
        
    def get_int_value(self, key: str, default: int = 0) -> int:
        """Get an integer value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            int: The integer value
        """
        value = self._get_value(key)
        if value is None:
            return default
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                return int(float(value))
        except (ValueError, TypeError):
            pass
        return default
        
    def get_float_value(self, key: str, default: Optional[float] = 0.0) -> Optional[float]:
        """Get a float value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            Optional[float]: The float value or None
        """
        value = self._get_value(key)
        if value is None:
            return default
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                return float(value)
        except (ValueError, TypeError):
            pass
        return default
        
    def get_str_value(self, key: str, default: str = "") -> str:
        """Get a string value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            str: The string value
        """
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, list):
            if not value:
                return default
            return ", ".join(str(item) for item in value)
        return str(value)
        
    def _get_value(self, key: str) -> Any:
        """Helper method to get value from coordinator data.
        
        Handles list values by returning the first item if the list has one item,
        or a comma-separated string if multiple items.
        
        Args:
            key: The key in the coordinator data
            
        Returns:
            Any: The value from the coordinator data
        """
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get(key)
        if isinstance(value, list):
            if len(value) == 1:
                return value[0]
            elif len(value) > 1:
                return ", ".join(str(item) for item in value)
        return value
