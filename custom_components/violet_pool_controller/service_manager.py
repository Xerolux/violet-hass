"""Coordinator and safety-lock management for Violet services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service import async_extract_config_entry_ids

from .runtime_data import async_get_coordinator
from .safety_guard import SafetyGuard, create_safety_guard

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall


def _config_entry_ids(device: object) -> tuple[str, ...]:
    """Return the config entry ids a device belongs to.

    Home Assistant 2026.8 restricted a device to a single config entry and
    deprecated ``DeviceEntry.config_entries`` in favour of
    ``DeviceEntry.config_entry_id``; 2026.9 warns about the old attribute. The
    integration supports Home Assistant from 2026.1, so read whichever the
    running release provides.

    The parameter is untyped on purpose: a registry lookup returns a plain
    ``DeviceEntry`` before 2026.9 and ``DeviceEntry | ChildDeviceEntry`` from
    2026.9 on, and only the two attributes read below are needed from either.
    """
    entry_id = getattr(device, "config_entry_id", None)
    if entry_id is not None:
        return (entry_id,)
    return tuple(getattr(device, "config_entries", ()))


class VioletServiceManager:
    """Manages all Violet Pool Controller services."""

    def __init__(self, hass):
        """Initialize the service manager."""
        self.hass = hass
        # Centralised safety enforcement (cooldown locks + restart-safe
        # auto-stop timers).  Replaces the former _safety_locks dict.
        self.safety_guard: SafetyGuard = create_safety_guard(hass)

    async def async_setup_safety(self) -> None:
        """Load persisted safety deadlines and re-arm active timers."""
        await self.safety_guard.async_setup()

    async def get_coordinator_for_device(self, device_id: str):
        """Get coordinator for device ID.

        ``device_id`` is either a config entry id or a device registry id.
        """
        if (coordinator := async_get_coordinator(self.hass, device_id)) is not None:
            return coordinator

        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(device_id)

        if device:
            for config_entry_id in _config_entry_ids(device):
                coordinator = async_get_coordinator(self.hass, config_entry_id)
                if coordinator is not None:
                    return coordinator

        return None

    async def get_coordinators_for_call(self, call: ServiceCall) -> list[Any]:
        """Return the coordinators a service call addresses.

        Resolution is delegated to Home Assistant's own target extraction, so
        every target kind the schemas accept actually reaches a controller:
        entity, device, area, floor and label.  The hand-rolled lookup this
        replaces read only ``entity_id`` and ``device_id``, so an
        area-targeted call matched nothing and the handler reported success
        without having done anything.
        """
        try:
            entry_ids = await async_extract_config_entry_ids(call)
        except HomeAssistantError:
            # Raised for an unknown or ambiguous target; treat it as "nothing
            # matched" so the caller reports it uniformly.
            entry_ids = set()

        coordinators: list[Any] = []
        for entry_id in entry_ids:
            coordinator = async_get_coordinator(self.hass, entry_id)
            if coordinator is not None and coordinator not in coordinators:
                coordinators.append(coordinator)

        return coordinators

    def set_safety_lock(self, entry_id: str, device_key: str, duration: int) -> None:
        """Set safety lock for a device on one controller (delegates to SafetyGuard)."""
        self.safety_guard.set_lock(entry_id, device_key, duration)
