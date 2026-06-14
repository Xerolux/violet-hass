# =============================================================================
# Violet Pool Controller – Complete Hardware Configuration Helper
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Complete hardware configuration reader - reads ALL configurable names, functions, and parameters."""

from __future__ import annotations

from typing import Any

from .digital_input_helper import DigitalInputConfig


class HardwareConfig:
    """Read and parse complete hardware configuration from controller.

    Covers all configurable elements:
    - Digital Inputs (DI1-12) with names and switching rules
    - Extension Relays (EXT1_1-8, EXT2_1-8)
    - DMX Scenes (LIGHT_SCENE_1-12)
    - Dosing Systems (Chlorine, pH±, Flocculant, Electrolysis, H2O2)
    - Temperature Sensors (1-8)
    - Analog Inputs (AI1-8)
    - Output Parameters (Pump, Heater, Solar, Cover, Backwash, Refill, Overflow)
    """

    def __init__(self, config_data: dict[str, Any]):
        """Initialize with config data from getConfig."""
        self.config = config_data
        self._parsed_configs = {}
        self._parse_all_configs()

    def _parse_all_configs(self) -> None:
        """Parse all hardware configuration sections."""
        self._parsed_configs["digital_inputs"] = self._parse_digital_inputs()
        self._parsed_configs["extension_relays"] = self._parse_extension_relays()
        self._parsed_configs["dmx_scenes"] = self._parse_dmx_scenes()
        self._parsed_configs["dosing_systems"] = self._parse_dosing_systems()
        self._parsed_configs["temperature_sensors"] = self._parse_temp_sensors()
        self._parsed_configs["analog_inputs"] = self._parse_analog_inputs()
        self._parsed_configs["outputs"] = self._parse_outputs()
        self._parsed_configs["pool_config"] = self._parse_pool_config()

    def _parse_digital_inputs(self) -> dict[str, Any]:
        """Parse digital input (DI1-12) configuration."""
        di_config = DigitalInputConfig(self.config)
        return {
            "all": di_config.get_all_di_configs(),
            "enabled": di_config.get_enabled_dis(),
            "parser": di_config,
        }

    def _parse_extension_relays(self) -> dict[str, Any]:
        """Parse extension relay configuration (EXT1_1-8, EXT2_1-8)."""
        relays = {}

        # EXT1: 8 relays
        for relay_num in range(1, 9):
            # Relays might have NAMES_* keys or just use defaults
            name_key = f"NAMES_ext1relay{relay_num}"
            name = self.config.get(name_key, f"Relay EXT1-{relay_num}")

            # Check if relay is enabled
            enable_key = f"EXT1_{relay_num}_use"
            enabled = bool(self.config.get(enable_key, 0))

            relays[f"EXT1_{relay_num}"] = {
                "number": relay_num,
                "module": 1,
                "name": name,
                "enabled": enabled,
                "entity_id": f"switch.violet_pool_controller_ext1_{relay_num}",
            }

        # EXT2: 8 relays
        for relay_num in range(1, 9):
            name_key = f"NAMES_ext2relay{relay_num}"
            name = self.config.get(name_key, f"Relay EXT2-{relay_num}")

            enable_key = f"EXT2_{relay_num}_use"
            enabled = bool(self.config.get(enable_key, 0))

            relays[f"EXT2_{relay_num}"] = {
                "number": relay_num,
                "module": 2,
                "name": name,
                "enabled": enabled,
                "entity_id": f"switch.violet_pool_controller_ext2_{relay_num}",
            }

        return relays

    def _parse_dmx_scenes(self) -> dict[str, Any]:
        """Parse DMX/Light scene configuration (LIGHT_SCENE_1-12)."""
        scenes = {}

        for scene_num in range(1, 13):
            # Scene names: LIGHT_prog*_name or use defaults
            name_key = f"LIGHT_prog{scene_num}_name"
            name = self.config.get(name_key, f"Scene {scene_num}")

            # Check if scene is enabled
            enable_key = f"LIGHT_prog{scene_num}_use"
            enabled = bool(self.config.get(enable_key, 0))

            scenes[f"LIGHT_SCENE_{scene_num}"] = {
                "number": scene_num,
                "name": name,
                "enabled": enabled,
                "entity_id": f"switch.violet_pool_controller_light_scene_{scene_num}",
            }

        return scenes

    def _parse_dosing_systems(self) -> dict[str, Any]:
        """Parse dosing system configuration (6 systems)."""
        systems = {}

        dosing_systems = [
            ("Chlorine", "DOS_1_CL", "chlorine", "CL"),
            ("Electrolysis", "DOS_2_ELO", "electrolysis", "ELO"),
            ("pH Minus", "DOS_4_PHM", "phminus", "PHM"),
            ("pH Plus", "DOS_5_PHP", "phplus", "PHP"),
            ("Flocculant", "DOS_6_FLOC", "floc", "FLOC"),
            ("H2O2", "DOS_1_CL", "h2o2", "H2O2"),
        ]

        for display_name, output_name, config_prefix, short_name in dosing_systems:
            # Get custom name if configured
            name_key = f"DOSAGE_{config_prefix}_name"
            name = self.config.get(name_key, display_name)

            # Check if enabled
            enable_key = f"DOSAGE_{config_prefix}_use"
            enabled = bool(self.config.get(enable_key, 0))

            # Get setpoint and limits
            setpoint_key = f"DOSAGE_{config_prefix}_set_value"
            setpoint = self.config.get(setpoint_key, 0)

            systems[short_name] = {
                "name": name,
                "output": output_name,
                "config_prefix": config_prefix,
                "enabled": enabled,
                "setpoint": setpoint,
                "entity_id": f"switch.violet_pool_controller_dosing_{config_prefix}",
            }

        return systems

    def _parse_temp_sensors(self) -> dict[str, Any]:
        """Parse temperature sensor configuration (onewire 1-8)."""
        sensors = {}

        sensor_names = [
            (1, "Pool Temperature"),
            (2, "Solar Collector"),
            (3, "Solar Return"),
            (4, "Heater Boiler"),
            (5, "Auxiliary 1"),
            (6, "Auxiliary 2"),
            (7, "Auxiliary 3"),
            (8, "Auxiliary 4"),
        ]

        for sensor_num, default_name in sensor_names:
            # Try to get configured name
            name_key = f"NAMES_onewire{sensor_num}"
            name = self.config.get(name_key, default_name)

            # Check if connected (has device ID)
            device_key = f"onewire{sensor_num}_deviceid"
            connected = bool(self.config.get(device_key))

            sensors[f"TEMP_{sensor_num}"] = {
                "number": sensor_num,
                "name": name,
                "connected": connected,
                "entity_id": f"sensor.violet_pool_controller_temperature_{sensor_num}",
            }

        return sensors

    def _parse_analog_inputs(self) -> dict[str, Any]:
        """Parse analog input configuration (AI1-8)."""
        inputs = {}

        analog_inputs = [
            (1, "Analog Input 1", "ADC Input 1"),
            (2, "Analog Input 2", "ADC Input 2"),
            (3, "Analog Input 3", "ADC Input 3"),
            (4, "Analog Input 4", "ADC Input 4"),
            (5, "Analog Input 5", "ADC Input 5"),
            (6, "Analog Input 6", "ADC Input 6"),
            (7, "Analog Input 7", "ADC Input 7"),
            (8, "Analog Input 8", "ADC Input 8"),
        ]

        for ai_num, default_name, description in analog_inputs:
            # Get configured name
            name_key = f"NAMES_analoginput{ai_num}"
            name = self.config.get(name_key, default_name)

            # Check if enabled
            enable_key = f"AI{ai_num}_use"
            enabled = bool(self.config.get(enable_key, 0))

            inputs[f"AI{ai_num}"] = {
                "number": ai_num,
                "name": name,
                "description": description,
                "enabled": enabled,
                "entity_id": f"sensor.violet_pool_controller_analog_input_{ai_num}",
            }

        return inputs

    def _parse_outputs(self) -> dict[str, Any]:
        """Parse output (control) configuration - Pump, Heater, Solar, etc."""
        outputs = {}

        output_definitions = [
            ("PUMP", "Pump", "water-pump", True),
            ("HEATER", "Heater", "radiator", True),
            ("SOLAR", "Solar", "solar-power", True),
            ("BACKWASH", "Backwash", "autorenew", False),
            ("REFILL", "Refill", "water", False),
            ("OVERFLOW", "Overflow", "water-alert", False),
            ("COVER", "Cover", "window-closed", False),
            ("LIGHT", "Light", "lightbulb", True),
            ("PVSURPLUS", "PV Surplus", "solar-power", False),
        ]

        for output_key, default_name, icon, default_enabled in output_definitions:
            # Get custom name
            name_key = f"NAMES_{output_key.lower()}"
            name = self.config.get(name_key, default_name)

            # Check if enabled
            enable_key = f"{output_key}_control_use"
            enabled = self.config.get(enable_key, 1 if default_enabled else 0)

            outputs[output_key] = {
                "name": name,
                "icon": icon,
                "enabled": bool(enabled),
                "entity_id": f"switch.violet_pool_controller_{output_key.lower()}",
            }

        return outputs

    def _parse_pool_config(self) -> dict[str, Any]:
        """Parse pool configuration - type, size, disinfection method."""
        return {
            "pool_type": self.config.get("POOL_type", "outdoor"),
            "pool_size": self.config.get("POOL_size", 50),
            "disinfection_method": self.config.get("POOL_disinfection_method", "chlorine"),
            "controller_name": self.config.get("NAMES_controller", "Violet Pool Controller"),
        }

    def get_all_configs(self) -> dict[str, Any]:
        """Get all parsed hardware configurations."""
        return self._parsed_configs

    def get_digital_input_config(self, di_num: int) -> dict[str, Any] | None:
        """Get specific digital input configuration."""
        parser = self._parsed_configs["digital_inputs"].get("parser")
        if parser:
            return parser.get_di_config(di_num)
        return None

    def get_di_friendly_name(self, di_num: int) -> str:
        """Get friendly name for digital input."""
        parser = self._parsed_configs["digital_inputs"].get("parser")
        if parser:
            return parser.get_di_friendly_name(di_num)
        return f"Digital Input {di_num}"

    def get_extension_relay_name(self, relay_key: str) -> str:
        """Get friendly name for extension relay (e.g., 'EXT1_1')."""
        relays = self._parsed_configs["extension_relays"]
        if relay_key in relays:
            return relays[relay_key]["name"]
        return relay_key

    def get_dmx_scene_name(self, scene_num: int) -> str:
        """Get friendly name for DMX scene."""
        scenes = self._parsed_configs["dmx_scenes"]
        scene_key = f"LIGHT_SCENE_{scene_num}"
        if scene_key in scenes:
            return scenes[scene_key]["name"]
        return f"Scene {scene_num}"

    def get_dosing_system_name(self, system_short: str) -> str:
        """Get friendly name for dosing system (e.g., 'CL', 'PHM')."""
        systems = self._parsed_configs["dosing_systems"]
        if system_short in systems:
            return systems[system_short]["name"]
        return system_short

    def get_temp_sensor_name(self, sensor_num: int) -> str:
        """Get friendly name for temperature sensor."""
        sensors = self._parsed_configs["temperature_sensors"]
        sensor_key = f"TEMP_{sensor_num}"
        if sensor_key in sensors:
            return sensors[sensor_key]["name"]
        return f"Temperature {sensor_num}"

    def get_analog_input_name(self, ai_num: int) -> str:
        """Get friendly name for analog input."""
        inputs = self._parsed_configs["analog_inputs"]
        ai_key = f"AI{ai_num}"
        if ai_key in inputs:
            return inputs[ai_key]["name"]
        return f"Analog Input {ai_num}"

    def get_output_name(self, output_key: str) -> str:
        """Get friendly name for output (e.g., 'PUMP', 'HEATER')."""
        outputs = self._parsed_configs["outputs"]
        if output_key in outputs:
            return outputs[output_key]["name"]
        return output_key

    def get_enabled_features(self) -> dict[str, list[str]]:
        """Get all enabled features grouped by type."""
        enabled = {
            "digital_inputs": [
                f"DI{k['number']}" for k in
                self._parsed_configs["digital_inputs"]["enabled"].values()
            ],
            "extension_relays": [
                k for k, v in self._parsed_configs["extension_relays"].items()
                if v["enabled"]
            ],
            "dmx_scenes": [
                f"Scene {v['number']}" for v in
                self._parsed_configs["dmx_scenes"].values()
                if v["enabled"]
            ],
            "dosing_systems": [
                v["name"] for v in
                self._parsed_configs["dosing_systems"].values()
                if v["enabled"]
            ],
            "outputs": [
                k for k, v in self._parsed_configs["outputs"].items()
                if v["enabled"]
            ],
        }
        return enabled

    def summary(self) -> str:
        """Get human-readable summary of hardware configuration."""
        lines = []
        lines.append(f"Pool: {self._parsed_configs['pool_config']['pool_size']}m³ "
                    f"({self._parsed_configs['pool_config']['pool_type']})")

        enabled = self.get_enabled_features()

        if enabled["outputs"]:
            lines.append(f"Outputs: {', '.join(enabled['outputs'])}")
        if enabled["digital_inputs"]:
            lines.append(f"Digital Inputs: {len(enabled['digital_inputs'])} active")
        if enabled["extension_relays"]:
            lines.append(f"Extension Relays: {len(enabled['extension_relays'])} active")
        if enabled["dosing_systems"]:
            lines.append(f"Dosing: {', '.join(enabled['dosing_systems'])}")

        return "\n".join(lines)
