"""Button platform for Violet Pool Controller."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .entity import VioletPoolControllerEntity
from .error_handler import get_enhanced_error_handler

_LOGGER = logging.getLogger(__name__)

BUTTON_TYPES: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="test_pump",
        translation_key="test_pump",
        icon="mdi:pump",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonEntityDescription(
        key="test_heater",
        translation_key="test_heater",
        icon="mdi:heating-coil",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonEntityDescription(
        key="test_solar",
        translation_key="test_solar",
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonEntityDescription(
        key="clear_error_history",
        translation_key="clear_error_history",
        icon="mdi:delete-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VioletDiagnosticButton(coordinator, description)
        for description in BUTTON_TYPES
    ]

    async_add_entities(entities)


from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class VioletDiagnosticButton(VioletPoolControllerEntity, ButtonEntity):
    """Button to clear the error history of the integration."""

    def __init__(self, coordinator: DataUpdateCoordinator[Any], description: ButtonEntityDescription) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device.device_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "clear_error_history":
            _LOGGER.info("Clearing error history for %s via button press", self.device.device_name)
            error_handler = get_enhanced_error_handler()
            error_handler.clear_history()
        elif self.entity_description.key.startswith("test_"):
            output_name = self.entity_description.key.split("_")[1].upper()
            _LOGGER.info("Activating test mode for %s on %s via button press", output_name, self.device.device_name)
            try:
                result = await self.coordinator.device.api.set_output_test_mode(
                    output=output_name,
                    mode="SWITCH",
                    duration=120,
                )
                if result.get("success") is not True:
                    _LOGGER.warning(
                        "Test mode could not be activated for %s: %s",
                        self.device.device_name,
                        result.get("response", result),
                    )
            except Exception as err:
                _LOGGER.error("Test mode error (%s): %s", self.device.device_name, err)

            await self.coordinator.async_request_refresh()
