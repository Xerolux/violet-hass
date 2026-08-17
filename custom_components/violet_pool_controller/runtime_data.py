# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Per-config-entry runtime state.

Everything a loaded config entry needs at runtime lives on
``entry.runtime_data`` instead of in ``hass.data[DOMAIN][entry_id]``: the
coordinator, the option snapshot the entities were built from, the registry
ids of the pre-created devices, the unique ids each platform reported, and the
manual saturation-index inputs.

Home Assistant deletes ``runtime_data`` when the entry is unloaded, so nothing
here has to be cleaned up by hand - and unlike a shared dict keyed by strings,
the per-entry state cannot be confused with integration-wide objects such as
the service manager (which stays in ``hass.data[DOMAIN]``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

if TYPE_CHECKING:
    from .device import VioletPoolDataUpdateCoordinator

# Key under which the integration-wide service manager lives in hass.data.
SERVICE_MANAGER_KEY = "service_manager"


@dataclass(slots=True)
class VioletRuntimeData:
    """State of one loaded Violet Pool Controller config entry."""

    coordinator: VioletPoolDataUpdateCoordinator
    # Options that decide *which* entities exist; a change forces a reload.
    structural_options: dict[str, Any] = field(default_factory=dict)
    # Registry ids of the pre-created controller and sub-devices, so entities
    # can link to their parent regardless of platform setup order.
    device_ids: dict[str, str] = field(default_factory=dict)
    # Unique ids each platform reported, used to drop orphaned registry entries.
    provided_unique_ids: dict[str, set[str]] = field(default_factory=dict)
    # Manually entered saturation-index values, per input group.
    calculator_inputs: dict[str, dict[str, Any]] = field(default_factory=dict)


type VioletConfigEntry = ConfigEntry[VioletRuntimeData]


@callback
def get_runtime_data(entry: ConfigEntry) -> VioletRuntimeData | None:
    """Return the runtime data of a config entry, or None if it is not loaded.

    ``runtime_data`` is absent before setup and after unload, and tests may
    hand in entries that never went through setup at all.
    """
    runtime_data = getattr(entry, "runtime_data", None)
    return runtime_data if isinstance(runtime_data, VioletRuntimeData) else None


@callback
def async_loaded_entries(hass: HomeAssistant) -> list[VioletConfigEntry]:
    """Return every config entry of this integration that is currently loaded."""
    return [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if get_runtime_data(entry) is not None
    ]


@callback
def async_get_coordinator(
    hass: HomeAssistant, entry_id: str
) -> VioletPoolDataUpdateCoordinator | None:
    """Return the coordinator of a loaded config entry id, or None."""
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None:
        return None
    runtime_data = get_runtime_data(entry)
    return runtime_data.coordinator if runtime_data else None


@callback
def async_all_coordinators(hass: HomeAssistant) -> list[VioletPoolDataUpdateCoordinator]:
    """Return the coordinators of all loaded config entries."""
    return [
        runtime_data.coordinator
        for entry in hass.config_entries.async_entries(DOMAIN)
        if (runtime_data := get_runtime_data(entry)) is not None
    ]
