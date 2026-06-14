# =============================================================================
# Violet Pool Controller – Update Entity
# Copyright © 2026 Xerolux
# =============================================================================

"""Update entity for Violet Pool Controller firmware updates."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .update_helper import parse_firmware_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up update entity from config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        [
            VioletPoolControllerUpdateEntity(
                coordinator=coordinator,
                config_entry=config_entry,
            )
        ]
    )


class VioletPoolControllerUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Violet Pool Controller firmware update entity."""

    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize update entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_firmware_update"
        self._attr_name = "System Update"
        self._attr_icon = "mdi:update"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device.device_id)},
            "name": self.coordinator.device.device_name,
            "manufacturer": "PoolDigital GmbH",
            "model": self.coordinator.device.device_model,
        }

    @property
    def installed_version(self) -> str | None:
        """Return installed version."""
        if not self.coordinator.data:
            return None
        firmware_info = parse_firmware_info(self.coordinator.data)
        return firmware_info.installed_version

    @property
    def latest_version(self) -> str | None:
        """Return latest available version."""
        if not self.coordinator.data:
            return None
        firmware_info = parse_firmware_info(self.coordinator.data)
        return firmware_info.available_version or firmware_info.installed_version

    @property
    def release_summary(self) -> str | None:
        """Return release summary/notes."""
        if not self.coordinator.data:
            return None
        firmware_info = parse_firmware_info(self.coordinator.data)
        if firmware_info.update_available:
            return f"Update v{firmware_info.available_version} available\n\n{firmware_info.release_notes_html}"
        return f"System is up to date (v{firmware_info.installed_version})"

    @property
    def in_progress(self) -> bool:
        """Return True if update is in progress."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("SYSTEM_UPDATE_IN_PROGRESS", False)

    async def async_install(
        self, version: str | None = None, backup: bool | None = None
    ) -> None:
        """Install update."""
        try:
            from .http_control import VioletControlClient

            client = VioletControlClient(self.coordinator.device._api)

            _LOGGER.info(
                "Starting firmware update on %s",
                self.coordinator.device.device_name,
            )

            # Send update command to controller
            await client.set_config({"SYSTEM_UPDATE_TRIGGER": 1})

            # Request refresh to update status
            await self.coordinator.async_request_refresh()

            _LOGGER.info(
                "Firmware update initiated on %s. Device will restart in ~30 seconds.",
                self.coordinator.device.device_name,
            )
        except Exception as err:
            _LOGGER.error("Failed to install firmware update: %s", err)
            raise

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        super()._handle_coordinator_update()
        self.async_write_ha_state()
