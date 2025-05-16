"""Base entity class for Violet Pool Controller entities."""
import logging
from typing import Any, Optional, Union

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

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
        self._attr_has_entity_name = True
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = coordinator.device.device_info
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")

    @property
    def device(self) -> Any:
        """Gib die Geräteinstanz zurück."""
        return self.coordinator.device

    @property
    def available(self) -> bool:
        """Gib an, ob die Entity verfügbar ist."""
        if not self.device.available or not self.coordinator.data or not self.coordinator.last_update_success:
            return False
        return True

    def _update_from_coordinator(self) -> None:
        """Aktualisiere die Entity aus den Coordinator-Daten.

        Diese Methode sollte von Unterklassen überschrieben werden.
        """
        pass

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entity zu Home Assistant hinzugefügt wird."""
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))
        self._update_from_coordinator()

    def _handle_coordinator_update(self) -> None:
        """Behandle aktualisierte Daten vom Koordinator."""
        self._update_from_coordinator()
        self.async_write_ha_state()

    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """Hole einen Boolean-Wert aus den Coordinator-Daten."""
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
        """Hole einen Integer-Wert aus den Coordinator-Daten."""
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
        """Hole einen Float-Wert aus den Coordinator-Daten."""
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
        """Hole einen String-Wert aus den Coordinator-Daten."""
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, list):
            if not value:
                return default
            return ", ".join(str(item) for item in value)
        return str(value)

    def _get_value(self, key: str) -> Any:
        """Hole einen Wert aus den Coordinator-Daten.

        Behandelt Listenwerte durch Rückgabe des ersten Elements oder einer kommagetrennten Liste.
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