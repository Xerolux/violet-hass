"""Coordinator and safety-lock management for Violet services."""

from __future__ import annotations

import time
from typing import Any

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN


class VioletServiceManager:
    """Manages all Violet Pool Controller services."""

    def __init__(self, hass):
        """Initialize the service manager."""
        self.hass = hass
        self._safety_locks: dict[str, float] = {}

    async def get_coordinator_for_device(self, device_id: str):
        """Get coordinator for device ID."""
        domain_data = self.hass.data.get(DOMAIN, {})

        for coordinator in domain_data.values():
            if (
                hasattr(coordinator, "device")
                and coordinator.device
                and str(coordinator.config_entry.entry_id) == device_id
            ):
                return coordinator

        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(device_id)

        if device:
            for config_entry_id in device.config_entries:
                coordinator = domain_data.get(config_entry_id)
                if coordinator and hasattr(coordinator, "device") and coordinator.device:
                    return coordinator

        return None

    async def get_coordinators_for_entities(self, entity_ids: list[str]) -> list[Any]:
        """Get coordinators for entity IDs."""
        coordinators = []
        entity_reg = er.async_get(self.hass)

        for entity_id in entity_ids:
            entity = entity_reg.async_get(entity_id)
            if entity and entity.config_entry_id:
                domain_data = self.hass.data.get(DOMAIN, {})
                coordinator = domain_data.get(entity.config_entry_id)
                if coordinator and coordinator not in coordinators:
                    coordinators.append(coordinator)

        return coordinators

    def extract_device_key(self, entity_id: str) -> str:
        """Extract device key from entity ID."""
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError(f"Invalid entity_id: {entity_id}")
        if "." not in entity_id:
            raise ValueError(
                f"Entity ID must contain domain separator '.': {entity_id}"
            )

        parts = entity_id.split(".")[-1].split("_")
        parts = [part for part in parts if part not in ("violet", "pool")]
        if not parts:
            raise ValueError(
                f"Cannot extract device key from {entity_id}: no parts remaining"
            )
        return "_".join(parts).upper()

    def check_safety_lock(self, device_key: str) -> bool:
        """Check if device has active safety lock."""
        if device_key not in self._safety_locks:
            return False
        return time.time() < self._safety_locks[device_key]

    def set_safety_lock(self, device_key: str, duration: int) -> None:
        """Set safety lock for device."""
        self._safety_locks[device_key] = time.time() + duration

    def get_remaining_lock_time(self, device_key: str) -> int:
        """Get remaining lock time in seconds."""
        if not self.check_safety_lock(device_key):
            return 0
        return int(self._safety_locks[device_key] - time.time())
