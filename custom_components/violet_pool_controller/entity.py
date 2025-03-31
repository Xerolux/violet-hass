"""Base entity class for Violet Pool Controller entities."""
import logging
from typing import Any, Dict, Optional, List, Union, cast

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import ATTR_ENTITY_ID

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
        # If the parent device is no longer available, we're not available either
        if not self.device.available:
            return False
        
        # Check if feature is active - DEACTIVATED for debugging
        # if hasattr(self.entity_description, "feature_id") and self.entity_description.feature_id:
        #     if not self.device.is_feature_active(self.entity_description.feature_id):
        #         return False
                
        # If the coordinator hasn't fetched data yet, we're not available
        if not self.coordinator.data:
            return False
            
        # Otherwise available if the coordinator's last update was successful
        return self.coordinator.last_update_success
        
    def _update_from_coordinator(self) -> None:
        """Update the entity from the coordinator data.
        
        This method should be overridden by subclasses to update any entity-specific
        properties from the coordinator data.
        """
        # Base implementation does nothing - subclasses should override this
        pass
        
    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        
        # Call update method when coordinator updates
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        
        # Initial update
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
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            return default
            
        if isinstance(value, bool):
            return value
            
        if isinstance(value, (int, float)):
            return bool(value)
            
        if isinstance(value, str):
            return value.lower() in ["true", "1", "on", "yes"]
            
        if isinstance(value, list):
            # If the list is empty, return default
            if not value:
                return default
            # Otherwise, use the first item
            if isinstance(value[0], (bool, int, float, str)):
                if isinstance(value[0], bool):
                    return value[0]
                if isinstance(value[0], (int, float)):
                    return bool(value[0])
                if isinstance(value[0], str):
                    return value[0].lower() in ["true", "1", "on", "yes"]
                
        return default
        
    def get_int_value(self, key: str, default: int = 0) -> int:
        """Get an integer value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            int: The integer value
        """
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            return default
            
        if isinstance(value, int):
            return value
            
        if isinstance(value, float):
            return int(value)
            
        if isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
                    
        if isinstance(value, list):
            # If the list is empty, return default
            if not value:
                return default
            # Otherwise, use the first item
            first_item = value[0]
            if isinstance(first_item, int):
                return first_item
            if isinstance(first_item, float):
                return int(first_item)
            if isinstance(first_item, str):
                try:
                    return int(first_item)
                except (ValueError, TypeError):
                    try:
                        return int(float(first_item))
                    except (ValueError, TypeError):
                        return default
                    
        return default
        
    def get_float_value(self, key: str, default: Optional[float] = 0.0) -> Optional[float]:
        """Get a float value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            Optional[float]: The float value or None
        """
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            return default
            
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
                
        if isinstance(value, list):
            # If the list is empty, return default
            if not value:
                return default
            # Otherwise, use the first item
            first_item = value[0]
            if isinstance(first_item, (int, float)):
                return float(first_item)
            if isinstance(first_item, str):
                try:
                    return float(first_item)
                except (ValueError, TypeError):
                    return default
                
        return default
        
    def get_str_value(self, key: str, default: str = "") -> str:
        """Get a string value from the coordinator data.
        
        Args:
            key: The key in the coordinator data
            default: The default value if key not found
            
        Returns:
            str: The string value
        """
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            return default
            
        # Handle lists properly
        if isinstance(value, list):
            if not value:  # Empty list
                return default
            elif len(value) == 1:  # Single item list
                return str(value[0])
            else:  # Multiple items
                return ", ".join(str(item) for item in value)
                
        return str(value)