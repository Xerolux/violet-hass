# =============================================================================
# Violet Pool Controller – Update Entity
# Copyright © 2026 Xerolux
# =============================================================================

"""Update entity for Violet Pool Controller firmware updates."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from violet_poolcontroller_api import VioletPoolAPIError

from .device import VioletPoolDataUpdateCoordinator
from .entity_cleanup import track_provided_entities
from .update_helper import parse_firmware_info

# CoordinatorEntity is generic in the type stubs but not subscriptable at runtime.
if TYPE_CHECKING:
    _VioletCoordinatorEntity = CoordinatorEntity[VioletPoolDataUpdateCoordinator]
else:
    _VioletCoordinatorEntity = CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

# Entity updates are driven by the coordinator, so no per-entity throttling.
PARALLEL_UPDATES = 0

_PROGRESS_RE = re.compile(r"(\d+)\s*%")


def _parse_update_progress(state: str) -> int | None:
    """Extract a best-effort percentage from an update-state string.

    The controller writes progress lines to /home/violet/log/update.log.
    Returns an int in [0, 100] if a percentage is found, else None.
    """
    match = _PROGRESS_RE.search(state)
    if not match:
        return None
    value = int(match.group(1))
    if value > 100:
        return 100
    return value


# Substrings (lowercased) that indicate an actively-running update log.
# Stale completed logs ("Update complete.", "Rebooting.") are intentionally
# absent so a leftover update.log is not mistaken for a running update.
_ACTIVE_UPDATE_KEYWORDS = (
    "download",
    "install",
    "extract",
    "unpack",
    "verify",
    "flash",
    "writing",
    "updating",
    "preparing",
    "fetching",
)


def _looks_like_active_update(state: str) -> bool:
    """Heuristic: does this update-state string indicate an active update?

    Returns True when the state contains a progress percentage or a recognized
    active-update keyword. Used to avoid mistaking a stale completed update log
    (or any non-STANDBY idle response) for an in-progress update at startup.
    """
    if not state:
        return False
    if _parse_update_progress(state) is not None:
        return True
    lowered = state.lower()
    return any(keyword in lowered for keyword in _ACTIVE_UPDATE_KEYWORDS)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up update entity from config entry."""
    coordinator = config_entry.runtime_data.coordinator

    entities = [
        VioletPoolControllerUpdateEntity(
            coordinator=coordinator,
            config_entry=config_entry,
        )
    ]

    track_provided_entities(hass, config_entry, Platform.UPDATE, entities)
    async_add_entities(entities)


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
    # How often (seconds) the polling task re-reads the firmware version to see
    # whether the install already landed while the state string stayed stale.
    _UPDATE_VERSION_REFRESH_INTERVAL = 30
    _UPDATE_MAX_LIFETIME = 600  # 10 minutes
    # Abort progress tracking if the reported state is byte-identical for this
    # many consecutive polls — a static state means the update log is either
    # leftover from a previous run or the update is genuinely stuck.
    _UPDATE_STALE_LIMIT = 12

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
        # Version checkpoints are a fallback for controllers that keep the final
        # update.log contents instead of returning STANDBY after a successful
        # reboot: a changed installed version proves the update finished.
        self._update_start_version: str | None = None
        self._update_target_version: str | None = None

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

    def _remember_update_versions(self, target_version: str | None = None) -> None:
        """Store the firmware versions used to confirm completion after a reboot."""
        if not self.coordinator.data:
            self._update_start_version = None
            self._update_target_version = target_version
            return

        info = parse_firmware_info(self.coordinator.data)
        self._update_start_version = info.installed_version
        self._update_target_version = target_version or info.available_version

    def _firmware_version_confirms_completion(self) -> bool:
        """Return True when refreshed firmware data proves the update completed."""
        if not self.coordinator.data:
            return False

        current_version = parse_firmware_info(self.coordinator.data).installed_version
        if not current_version:
            return False

        if self._update_target_version and current_version == self._update_target_version:
            return True

        return bool(
            self._update_start_version and current_version != self._update_start_version
        )

    def _controller_state_is_stale(self) -> bool:
        """Return True when a non-STANDBY state belongs to an already installed update.

        The raw readings are used on purpose: parse_firmware_info drops the
        available version once it equals the installed one, which is exactly the
        signal needed here. When the controller advertises an available version
        and it matches what is installed, nothing is left to install, so a
        lingering update.log is leftover output rather than a running update.

        An empty available version is not treated as stale — the controller may
        simply not have reached the update server yet, and suppressing a genuine
        in-progress update would be worse than tracking one extra log.
        """
        data = self.coordinator.data
        if not data:
            return False

        installed = str(data.get("SYSTEM_swversion", "") or "").strip() or str(
            data.get("SW_VERSION", "") or ""
        ).strip()
        available = str(data.get("SYSTEM_availableversion", "") or "").strip() or str(
            data.get("SW_UPDATE_AVAILABLE", "") or ""
        ).strip()

        return bool(installed and available and installed == available)

    def _clear_update_tracking(self) -> None:
        """Reset local update progress and version checkpoints."""
        self._update_in_progress = False
        self._update_progress = None
        self._update_status_text = None
        self._update_start_version = None
        self._update_target_version = None
        self.async_write_ha_state()

    async def _refresh_firmware_data(self) -> bool:
        """Refresh coordinator data without failing update progress tracking."""
        try:
            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Could not refresh firmware version while tracking update on %s: %s",
                self.coordinator.device.device_name,
                err,
            )
            return False
        return True

    async def _poll_update_state(self) -> None:
        """Poll update status until STANDBY, a version change, or timeout.

        Runs as a background task after async_install or after startup detection.
        Updates _update_in_progress, _update_progress, and _update_status_text
        and writes HA state on each iteration. Resilient to transient errors.

        Some controllers never return to STANDBY after a successful reboot and
        keep serving the final update.log instead. The periodic version refresh
        catches that case: once the installed firmware version has changed (or
        reached the target version), the update is complete regardless of what
        the state string still says.
        """
        interval = self._UPDATE_POLL_INTERVAL
        version_refresh_interval = max(self._UPDATE_VERSION_REFRESH_INTERVAL, interval)
        next_version_refresh = version_refresh_interval
        elapsed = 0
        last_state: str | None = None
        unchanged = 0

        while elapsed <= self._UPDATE_MAX_LIFETIME:
            try:
                state = await self.coordinator.device.api.get_update_state()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                # Controller is briefly unreachable during its restart — keep polling.
                _LOGGER.debug(
                    "Transient error polling update state on %s: %s",
                    self.coordinator.device.device_name,
                    err,
                )
                await asyncio.sleep(interval)
                elapsed += interval
                continue

            normalized = (state or "").strip()
            if normalized.upper() == "STANDBY":
                await self._refresh_firmware_data()
                self._clear_update_tracking()
                return

            # Stale detection: a static, never-changing state means the update
            # log is either leftover from a previous run or genuinely stuck.
            # Stop tracking early instead of polling for the full lifetime.
            if normalized == last_state:
                unchanged += 1
                if unchanged >= self._UPDATE_STALE_LIMIT:
                    _LOGGER.info(
                        "Update state on %s unchanged for %d polls (%ds); "
                        "assuming stale or finished, stopping progress tracking "
                        "(last state: %r)",
                        self.coordinator.device.device_name,
                        unchanged,
                        unchanged * interval,
                        (last_state or "")[:120],
                    )
                    await self._refresh_firmware_data()
                    self._clear_update_tracking()
                    return
            else:
                unchanged = 0

            last_state = normalized
            self._update_in_progress = True
            self._update_progress = _parse_update_progress(normalized)
            self._update_status_text = normalized
            self.async_write_ha_state()

            if elapsed >= next_version_refresh:
                if (
                    await self._refresh_firmware_data()
                    and self._firmware_version_confirms_completion()
                ):
                    _LOGGER.info(
                        "Firmware update on %s completed; installed version changed "
                        "although the update state remained %r",
                        self.coordinator.device.device_name,
                        normalized[:120],
                    )
                    self._clear_update_tracking()
                    return
                next_version_refresh += version_refresh_interval

            await asyncio.sleep(interval)
            elapsed += interval

        # Safety net: exceeded max lifetime. Do one final version check before
        # declaring failure — the install may have landed on a controller that
        # never clears its update state.
        if (
            await self._refresh_firmware_data()
            and self._firmware_version_confirms_completion()
        ):
            _LOGGER.info(
                "Firmware update on %s completed before the timeout; ignoring "
                "stale update state %r",
                self.coordinator.device.device_name,
                (last_state or "")[:120],
            )
            self._clear_update_tracking()
            return

        _LOGGER.warning(
            "Firmware update on %s did not reach STANDBY within %d seconds; "
            "aborting progress tracking (last state: %r)",
            self.coordinator.device.device_name,
            self._UPDATE_MAX_LIFETIME,
            (last_state or "")[:120],
        )
        self._clear_update_tracking()

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to HA.

        Probe the controller once: if an update is already in progress (e.g.
        after an HA restart or integration reload mid-update), start polling.
        """
        await super().async_added_to_hass()
        try:
            state = await self.coordinator.device.api.get_update_state()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Could not probe update state at startup for %s: %s",
                self.coordinator.device.device_name,
                err,
            )
            return

        normalized = (state or "").strip()
        if normalized.upper() == "STANDBY":
            return

        if not _looks_like_active_update(normalized):
            # Non-STANDBY but no progress percentage or active keyword — most
            # likely a stale log from a previous update (the controller did not
            # clear /home/violet/log/update.log) or an unexpected idle response.
            # Do NOT start 10 minutes of pointless polling.
            _LOGGER.debug(
                "Update state on %s is non-STANDBY (%s) but does not look like "
                "an active update; treating as idle (likely a stale log)",
                self.coordinator.device.device_name,
                normalized[:120],
            )
            return

        if self._controller_state_is_stale():
            _LOGGER.debug(
                "Ignoring stale firmware update state on %s at startup (%s): the "
                "installed version already matches the available one",
                self.coordinator.device.device_name,
                normalized[:120],
            )
            return

        _LOGGER.info(
            "Detected in-progress firmware update on %s at startup (state=%s); "
            "resuming progress tracking",
            self.coordinator.device.device_name,
            normalized,
        )
        self._remember_update_versions()
        self._update_in_progress = True
        self._update_status_text = normalized
        self._update_progress = _parse_update_progress(normalized)
        self.async_write_ha_state()
        self._update_task = asyncio.create_task(self._poll_update_state())

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is removed from HA. Cancel any running polling task."""
        task = self._update_task
        if task is not None and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._update_in_progress = False
        await super().async_will_remove_from_hass()

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
        Refuses to start a second install while one is already running.
        """
        # Guard 1: already tracking a local install.
        if self._update_in_progress:
            raise HomeAssistantError(
                "Update läuft bereits auf der Steuerung"
            )

        try:
            # Guard 2: an update may have been started externally (another client,
            # a previous crashed task). Probe the controller before triggering.
            current_state = await self.coordinator.device.api.get_update_state()
            normalized_state = (current_state or "").strip()
            if normalized_state.upper() != "STANDBY" and not self._controller_state_is_stale():
                _LOGGER.warning(
                    "Update on %s already in progress (state=%s); starting progress tracking",
                    self.coordinator.device.device_name,
                    current_state,
                )
                self._remember_update_versions(version)
                self._update_in_progress = True
                self._update_status_text = normalized_state
                self._update_progress = _parse_update_progress(normalized_state)
                self.async_write_ha_state()
                self._update_task = asyncio.create_task(self._poll_update_state())
                raise HomeAssistantError(
                    "Update läuft bereits auf der Steuerung"
                )

            if normalized_state.upper() != "STANDBY":
                _LOGGER.debug(
                    "Ignoring stale firmware update state on %s before install: %s",
                    self.coordinator.device.device_name,
                    normalized_state[:120],
                )

            _LOGGER.info(
                "Triggering firmware update on %s",
                self.coordinator.device.device_name,
            )

            self._remember_update_versions(version or self.latest_version)
            response = await self.coordinator.device.api.init_update()

            if response and response != "STARTING":
                _LOGGER.warning("Unexpected update response: %s", response)

            _LOGGER.info(
                "Firmware update initiated on %s. Device will restart in ~30 seconds.",
                self.coordinator.device.device_name,
            )

            self._update_in_progress = True
            self._update_status_text = "initiiert"
            self._update_progress = None
            self.async_write_ha_state()
            self._update_task = asyncio.create_task(self._poll_update_state())

            await self.coordinator.async_request_refresh()

        except HomeAssistantError:
            raise
        except Exception as err:
            self._update_start_version = None
            self._update_target_version = None
            _LOGGER.error("Failed to initiate firmware update: %s", err)
            raise HomeAssistantError(f"Firmware update failed: {err}") from err

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        super()._handle_coordinator_update()
        self.async_write_ha_state()
