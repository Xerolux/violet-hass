"""Coordinator and safety-lock management for Violet services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .runtime_data import async_get_coordinator
from .safety_guard import SafetyGuard, create_safety_guard

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall


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
            for config_entry_id in device.config_entries:
                coordinator = async_get_coordinator(self.hass, config_entry_id)
                if coordinator is not None:
                    return coordinator

        return None

    async def get_coordinators_for_entities(self, entity_ids: list[str]) -> list[Any]:
        """Get coordinators for entity IDs."""
        coordinators = []
        entity_reg = er.async_get(self.hass)

        for entity_id in entity_ids:
            entity = entity_reg.async_get(entity_id)
            if entity and entity.config_entry_id:
                coordinator = async_get_coordinator(self.hass, entity.config_entry_id)
                if coordinator and coordinator not in coordinators:
                    coordinators.append(coordinator)

        return coordinators

    async def get_coordinators_for_call(self, call: ServiceCall) -> list[Any]:
        """Get coordinators from a service call (entity_id or device_id)."""
        coordinators: list[Any] = []
        entity_reg = er.async_get(self.hass)
        device_reg = dr.async_get(self.hass)

        entity_ids: list[str] = call.data.get(ATTR_ENTITY_ID, [])
        device_ids: list[str] = call.data.get(ATTR_DEVICE_ID, [])

        for eid in entity_ids:
            entity = entity_reg.async_get(eid)
            if entity and entity.config_entry_id:
                coord = async_get_coordinator(self.hass, entity.config_entry_id)
                if coord and coord not in coordinators:
                    coordinators.append(coord)

        for did in device_ids:
            device = device_reg.async_get(did)
            if device and device.config_entries:
                for entry_id in device.config_entries:
                    coord = async_get_coordinator(self.hass, entry_id)
                    if coord and coord not in coordinators:
                        coordinators.append(coord)

        return coordinators

    def extract_device_key(self, entity_id: str) -> str:
        """Extract device key from entity ID."""
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError(f"Invalid entity_id: {entity_id}")
        if "." not in entity_id:
            raise ValueError(f"Entity ID must contain domain separator '.': {entity_id}")

        parts = entity_id.split(".")[-1].split("_")
        parts = [part for part in parts if part not in ("violet", "pool")]
        if not parts:
            raise ValueError(f"Cannot extract device key from {entity_id}: no parts remaining")
        return "_".join(parts).upper()

    def check_safety_lock(self, device_key: str) -> bool:
        """Check if device has active safety lock (delegates to SafetyGuard)."""
        return self.safety_guard.check_lock(device_key)

    def set_safety_lock(self, device_key: str, duration: int) -> None:
        """Set safety lock for device (delegates to SafetyGuard)."""
        self.safety_guard.set_lock(device_key, duration)

    def get_remaining_lock_time(self, device_key: str) -> int:
        """Get remaining lock time in seconds (delegates to SafetyGuard)."""
        return self.safety_guard.remaining_lock_time(device_key)
