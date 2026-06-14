# =============================================================================
# Violet Pool Controller – Dynamic Entity Names Helper
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Helper for applying dynamic names from hardware config to all entities."""

from __future__ import annotations

from typing import Any

from .hardware_config import HardwareConfig


class EntityNameResolver:
    """Resolve entity names from hardware configuration."""

    def __init__(self, hw_config: dict[str, Any] | None = None):
        """Initialize with parsed hardware config."""
        self.hw_config = hw_config

    def resolve_entity_name(self, entity_type: str, key: str, default_name: str) -> str:
        """Resolve the actual entity name for any entity type.

        Args:
            entity_type: Type of entity (binary_sensor, switch, climate, etc.)
            key: The entity key (e.g., 'PUMP', 'INPUT1', 'EXT1_1')
            default_name: Fallback name if not found in config

        Returns:
            Resolved entity name from hardware config or default
        """
        if not self.hw_config:
            return default_name

        # Digital inputs
        if key.startswith("INPUT"):
            try:
                di_num = int(key[5:])
                if 1 <= di_num <= 12:
                    di_parser = self.hw_config.get("digital_inputs", {}).get("parser")
                    if di_parser:
                        return di_parser.get_di_friendly_name(di_num)
            except (ValueError, IndexError):
                pass

        # Extension relays
        if key.startswith("EXT"):
            return self._resolve_relay_name(key)

        # DMX scenes
        if key.startswith("LIGHT_SCENE"):
            try:
                scene_num = int(key.split("_")[-1])
                return self._resolve_dmx_scene_name(scene_num)
            except (ValueError, IndexError):
                pass

        # Dosing systems
        if key in ["DOS_1_CL", "DOS_2_ELO", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC"]:
            return self._resolve_dosing_name(key)

        # Main outputs
        if key in ["PUMP", "HEATER", "SOLAR", "COVER", "BACKWASH", "REFILL", "OVERFLOW", "LIGHT", "PVSURPLUS"]:
            return self._resolve_output_name(key)

        return default_name

    def _resolve_relay_name(self, key: str) -> str | None:
        """Resolve extension relay name."""
        if not self.hw_config:
            return None

        relays = self.hw_config.get("extension_relays", {})
        if key in relays:
            return relays[key]["name"]
        return None

    def _resolve_dmx_scene_name(self, scene_num: int) -> str | None:
        """Resolve DMX scene name."""
        if not self.hw_config:
            return None

        scenes = self.hw_config.get("dmx_scenes", {})
        scene_key = f"LIGHT_SCENE_{scene_num}"
        if scene_key in scenes:
            return scenes[scene_key]["name"]
        return None

    def _resolve_dosing_name(self, key: str) -> str | None:
        """Resolve dosing system name."""
        if not self.hw_config:
            return None

        # Map output keys to short names
        mapping = {
            "DOS_1_CL": "CL",
            "DOS_2_ELO": "ELO",
            "DOS_4_PHM": "PHM",
            "DOS_5_PHP": "PHP",
            "DOS_6_FLOC": "FLOC",
        }

        short_name = mapping.get(key)
        if not short_name:
            return None

        systems = self.hw_config.get("dosing_systems", {})
        if short_name in systems:
            return systems[short_name]["name"]
        return None

    def _resolve_output_name(self, key: str) -> str | None:
        """Resolve main output name."""
        if not self.hw_config:
            return None

        outputs = self.hw_config.get("outputs", {})
        if key in outputs:
            return outputs[key]["name"]
        return None

    def get_resolver(self, coordinator) -> EntityNameResolver:
        """Create resolver from coordinator (convenience method)."""
        hw_config = None
        if hasattr(coordinator, "device") and coordinator.device:
            hw_config = coordinator.device.hardware_config

        return EntityNameResolver(hw_config)


def apply_hardware_names(
    entity_configs: list[dict[str, Any]],
    resolver: EntityNameResolver,
    entity_type: str = "switch",
) -> list[dict[str, Any]]:
    """Apply hardware names to a list of entity configs.

    Args:
        entity_configs: List of entity config dicts with 'key' and 'name'
        resolver: EntityNameResolver instance
        entity_type: Type of entity for context

    Returns:
        Updated entity configs with resolved names
    """
    updated = []

    for config in entity_configs:
        updated_config = config.copy()
        key = config.get("key")
        default_name = config.get("name", key)

        if key:
            resolved_name = resolver.resolve_entity_name(entity_type, key, default_name)
            if resolved_name:
                updated_config["name"] = resolved_name

        updated.append(updated_config)

    return updated
