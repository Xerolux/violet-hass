# =============================================================================
# Violet Pool Controller – Digital Input Configuration Helper
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Helper for reading and parsing digital input configurations from controller."""

from __future__ import annotations

from typing import Any


class DigitalInputConfig:
    """Parse and manage digital input (DI) configuration from controller."""

    def __init__(self, config_data: dict[str, Any]):
        """Initialize with config data from getConfig."""
        self.config = config_data
        self._di_configs = self._parse_di_configs()

    def _parse_di_configs(self) -> dict[int, dict[str, Any]]:
        """Parse all DI configurations from config data.

        Reads:
        - NAMES_digitalinput1-12: Display names
        - SWITCHINGRULE_prog*_function: What the DI triggers
        - SWITCHINGRULE_prog*_outputindex: Which output gets controlled
        """
        di_configs = {}

        for di_num in range(1, 13):  # DI 1-12
            name_key = f"NAMES_digitalinput{di_num}"
            name = self.config.get(name_key, f"Digital Input {di_num}")

            # Parse switching rule if exists (usually 1-8 for first 8 DIs)
            if di_num <= 8:
                rule_num = di_num
                function_key = f"SWITCHINGRULE_prog{rule_num}_function"
                output_key = f"SWITCHINGRULE_prog{rule_num}_outputindex"

                function = self.config.get(function_key, "unknown")
                output_index = self.config.get(output_key, None)

                di_configs[di_num] = {
                    "number": di_num,
                    "name": name,
                    "function": function,
                    "output_index": output_index,
                    "enabled": bool(function and function != "unknown"),
                    "description": self._get_description(function, output_index),
                }
            else:
                # DI 9-12 might not have switching rules
                di_configs[di_num] = {
                    "number": di_num,
                    "name": name,
                    "function": None,
                    "output_index": None,
                    "enabled": False,
                    "description": "No switching rule assigned",
                }

        return di_configs

    @staticmethod
    def _get_description(function: str | None, output_index: Any) -> str:
        """Get human-readable description of DI function."""
        if not function or function == "unknown":
            return "No function assigned"

        output_map = {
            0: "Pump",
            1: "Heater",
            2: "Solar",
            3: "Chlorine Dosing",
            4: "Backwash",
            5: "Refill",
            6: "Overflow",
            7: "Light/DMX",
        }

        output_name = output_map.get(output_index, f"Output {output_index}")

        function_lower = str(function).lower()

        if "pulse" in function_lower or "toggle" in function_lower:
            return f"Toggle {output_name}"
        elif "on" in function_lower or "active" in function_lower:
            return f"Activate {output_name}"
        elif "off" in function_lower:
            return f"Deactivate {output_name}"
        else:
            return f"Control {output_name} ({function})"

    def get_all_di_configs(self) -> dict[int, dict[str, Any]]:
        """Get all DI configurations.

        Returns:
            Dict mapping DI number (1-12) to config dict with:
            - number: DI number
            - name: Display name
            - function: Switching function
            - output_index: Controlled output index
            - enabled: Whether DI has a function
            - description: Human-readable description
        """
        return self._di_configs

    def get_di_config(self, di_num: int) -> dict[str, Any] | None:
        """Get config for specific DI.

        Args:
            di_num: DI number (1-12)

        Returns:
            DI config dict or None if invalid DI number
        """
        if not 1 <= di_num <= 12:
            return None
        return self._di_configs.get(di_num)

    def get_enabled_dis(self) -> dict[int, dict[str, Any]]:
        """Get only enabled DIs (those with switching rules assigned).

        Returns:
            Dict of enabled DI configurations
        """
        return {k: v for k, v in self._di_configs.items() if v["enabled"]}

    def get_di_by_name(self, name: str) -> dict[str, Any] | None:
        """Find DI config by display name.

        Args:
            name: DI display name

        Returns:
            DI config dict or None if not found
        """
        for di_config in self._di_configs.values():
            if di_config["name"].lower() == name.lower():
                return di_config
        return None

    def get_di_entity_id(
        self, di_num: int, prefix: str = "binary_sensor"
    ) -> str:
        """Generate HA entity ID for a DI.

        Args:
            di_num: DI number (1-12)
            prefix: Entity type prefix (default: binary_sensor)

        Returns:
            Entity ID like "binary_sensor.violet_pool_controller_digital_input_1"
        """
        if not 1 <= di_num <= 12:
            return ""

        di_config = self._di_configs[di_num]
        # Use friendly name or fallback to number
        name_suffix = di_config["name"].lower().replace(" ", "_")[:20]
        # Don't hardcode domain prefix - let HA handle it via device info
        return f"{prefix}.{name_suffix}"

    def get_di_friendly_name(self, di_num: int) -> str:
        """Get friendly name for display in HA.

        Args:
            di_num: DI number (1-12)

        Returns:
            Friendly name like "Filterstatus" or "Digital Input 3"
        """
        if not 1 <= di_num <= 12:
            return f"Digital Input {di_num}"
        return str(self._di_configs[di_num]["name"])

    def should_expose_di(self, di_num: int) -> bool:
        """Determine if DI should be exposed as HA entity.

        Only expose DIs that have a switching rule configured (enabled).

        Args:
            di_num: DI number (1-12)

        Returns:
            True if DI should be exposed, False otherwise
        """
        if not 1 <= di_num <= 12:
            return False

        di_config = self._di_configs[di_num]
        return bool(di_config["enabled"])

    @staticmethod
    def parse_digital_input_state(state_str: str | int | None) -> bool:
        """Parse digital input state to boolean.

        Args:
            state_str: State from getReadings (usually "0" or "1")

        Returns:
            True if input is active, False otherwise
        """
        if state_str is None:
            return False

        # Handle string "0"/"1" or int 0/1
        state_str = str(state_str).strip().lower()
        return state_str in ("1", "true", "active", "on", "high")
