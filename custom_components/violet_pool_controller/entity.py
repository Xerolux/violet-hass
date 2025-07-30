"""Base entity class for Violet Pool Controller entities."""
import logging

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
