"""Base entity class for Violet Pool Controller entities."""
import logging
from typing import Any, Optional, Union

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class VioletPoolControllerEntity(CoordinatorEntity):
    """Basis-Entity-Klasse für Violet Pool Controller."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: Any,
    ) -> None:
        """Initialisiere die Entity.

        Args:
            coordinator: Daten-Koordinator.
            config_entry: Config Entry.
            entity_description: Entity-Beschreibung.
        """
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = entity_description
        
        # Modern entity naming - device name is automatically added by HA
        self._attr_has_entity_name = True
        self._attr_name = entity_description.name
        
        # Unique ID should not include device name as it's automatically handled
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        
        # Device info is provided by coordinator
        self._attr_device_info = coordinator.device.device_info