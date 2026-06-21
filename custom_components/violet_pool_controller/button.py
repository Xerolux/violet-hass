# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Button platform for Violet Pool Controller error management."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0


class VioletResetBlockingButton(VioletPoolControllerEntity, ButtonEntity):
    """Button to reset error blockings on the pool controller.

    Equivalent to clicking "Reset" on the controller's web UI error page.
    Clears fault-induced blockings (e.g. BLOCKED_BY_ESC from empty-canister
    alarms) so dosing and other outputs resume after the underlying issue
    has been fixed.
    """

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the reset blockings button."""
        description = ButtonEntityDescription(
            key="reset_blocking",
            translation_key="reset_errors",
            name="Reset Error Blockings",
            icon="mdi:restart-alert",
            entity_category=EntityCategory.CONFIG,
        )
        super().__init__(coordinator, config_entry, description)

    async def async_press(self) -> None:
        """Handle button press - reset error blockings on the controller."""
        try:
            _LOGGER.info(
                "Resetting error blockings for controller '%s'",
                self.config_entry.title,
            )

            result = await self.coordinator.device.api.reset_blocking()

            _LOGGER.info(
                "Error blockings reset successfully for '%s': %s",
                self.config_entry.title,
                result,
            )

            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to reset error blockings: %s", err)
            raise HomeAssistantError(f"Reset failed: {err}") from err


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Violet Pool Controller error management buttons."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    buttons = [
        VioletResetBlockingButton(coordinator, config_entry),
    ]

    async_add_entities(buttons)
    _LOGGER.debug("Error management buttons added for '%s'", config_entry.title)
