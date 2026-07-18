# =============================================================================
# Violet Pool Controller – Update Entity
# Copyright © 2026 Xerolux
# =============================================================================

"""Update entity for Violet Pool Controller firmware updates."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from violet_poolcontroller_api import VioletPoolAPIError

from .const import DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .update_helper import parse_firmware_info

# CoordinatorEntity is generic in the type stubs but not subscriptable at runtime.
if TYPE_CHECKING:
    _VioletCoordinatorEntity = CoordinatorEntity[VioletPoolDataUpdateCoordinator]
else:
    _VioletCoordinatorEntity = CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up update entity from config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            VioletPoolControllerUpdateEntity(
                coordinator=coordinator,
                config_entry=config_entry,
            )
        ]
    )


class VioletPoolControllerUpdateEntity(_VioletCoordinatorEntity, UpdateEntity):
    """Violet Pool Controller firmware update entity."""

    _attr_supported_features = (
        UpdateEntityFeature.INSTALL
        | UpdateEntityFeature.RELEASE_NOTES
        | UpdateEntityFeature.PROGRESS
    )
    _attr_icon = "mdi:update"
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    # Show the update entity in the main device view instead of hiding it under
    # the "Configuration" section, so users can actually find it.
    _attr_entity_category = None
    # Update-state polling cadence (seconds) and maximum task lifetime before
    # the safety net aborts. Exposed as class constants so tests can shrink them.
    _UPDATE_POLL_INTERVAL = 5
    _UPDATE_MAX_LIFETIME = 600  # 10 minutes

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize update entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_firmware_update"
        self._attr_has_entity_name = True
        self._attr_name = "System Update"
        self._release_notes_cache: str = ""
        # Live update state — driven by the polling task in _poll_update_state.
        self._update_in_progress: bool = False
        self._update_progress: int | None = None
        self._update_status_text: str | None = None
        self._update_task: asyncio.Task[None] | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.coordinator.device.device_info

    @property
    def installed_version(self) -> str | None:
        """Return installed firmware version."""
        if not self.coordinator.data:
            return None
        info = parse_firmware_info(self.coordinator.data)
        _LOGGER.debug(
            "Firmware installed version for %s: %s (raw keys: SYSTEM_swversion=%s, SW_VERSION=%s)",
            self.coordinator.device.device_name,
            info.installed_version,
            self.coordinator.data.get("SYSTEM_swversion"),
            self.coordinator.data.get("SW_VERSION"),
        )
        return info.installed_version

    @property
    def latest_version(self) -> str | None:
        """Return latest available version.

        When no update is available, return the installed version (system is up-to-date).
        When an update is available, return the available version.
        """
        if not self.coordinator.data:
            return None
        info = parse_firmware_info(self.coordinator.data)
        # If there's an available update, show that version; otherwise show installed
        latest = info.available_version or info.installed_version
        _LOGGER.debug(
            "Firmware latest version for %s: %s (available=%s, installed=%s, update_available=%s)",
            self.coordinator.device.device_name,
            latest,
            info.available_version,
            info.installed_version,
            info.update_available,
        )
        return latest

    @property
    def release_summary(self) -> str | None:
        """Return brief update status.

        While a firmware update is in progress, return the live status text
        from the controller. Otherwise return the update description (release
        notes are fetched on demand in async_release_notes).
        """
        if self._update_in_progress and self._update_status_text:
            return f"Update läuft: {self._update_status_text}"
        if not self.coordinator.data:
            return None
        info = parse_firmware_info(self.coordinator.data)
        return info.update_description

    @property
    def in_progress(self) -> bool:
        """Return True while a firmware update is being installed.

        Driven by the entity-local _update_in_progress flag, which is set by
        async_install and refreshed by the _poll_update_state task.
        """
        return self._update_in_progress

    async def async_release_notes(self) -> str | None:
        """Fetch and return HTML release notes from the controller."""
        try:
            notes = await self.coordinator.device.api.get_update_history()
            if notes:
                self._release_notes_cache = notes
        except (VioletPoolAPIError, TimeoutError) as err:
            _LOGGER.debug("Could not fetch release notes: %s", err)

        return self._release_notes_cache or None

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        """Trigger firmware update on the controller.

        The controller downloads and installs the update via
        GET /initUpdate and then restarts (~30 seconds offline).
        """
        try:
            _LOGGER.info(
                "Triggering firmware update on %s",
                self.coordinator.device.device_name,
            )

            response = await self.coordinator.device.api.init_update()

            if response and response != "STARTING":
                _LOGGER.warning("Unexpected update response: %s", response)

            _LOGGER.info(
                "Firmware update initiated on %s. Device will restart in ~30 seconds.",
                self.coordinator.device.device_name,
            )

            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Failed to initiate firmware update: %s", err)
            raise HomeAssistantError(f"Firmware update failed: {err}") from err

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        super()._handle_coordinator_update()
        self.async_write_ha_state()
