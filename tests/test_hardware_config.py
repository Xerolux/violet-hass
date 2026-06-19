"""Tests for HardwareConfig and DigitalInputConfig parsers."""
import pytest

from custom_components.violet_pool_controller.digital_input_helper import (
    DigitalInputConfig,
)
from custom_components.violet_pool_controller.hardware_config import HardwareConfig

# ============================================================
# Sample config data
# ============================================================

SAMPLE_CONFIG = {
    # Digital inputs
    "NAMES_digitalinput1": "Filterstatus",
    "NAMES_digitalinput2": "Water Level",
    "SWITCHINGRULE_prog1_function": "toggle",
    "SWITCHINGRULE_prog1_outputindex": 0,
    "SWITCHINGRULE_prog2_function": "on_off",
    "SWITCHINGRULE_prog2_outputindex": 4,
    # Extension relays
    "NAMES_ext1relay1": "Pool Light",
    "EXT1_1_use": 1,
    "EXT1_2_use": 0,
    "NAMES_ext2relay1": "Aux Relay",
    "EXT2_1_use": 1,
    # DMX scenes
    "LIGHT_prog1_name": "Party Mode",
    "LIGHT_prog1_use": 1,
    "LIGHT_prog2_name": "Relax",
    "LIGHT_prog2_use": 0,
    # Dosing systems
    "DOSAGE_chlorine_name": "Chlor Pump",
    "DOSAGE_chlorine_use": 1,
    "DOSAGE_chlorine_set_value": 7.0,
    "DOSAGE_phminus_use": 0,
    # Temperature sensors
    "NAMES_onewire1": "Pool Water",
    "onewire1_deviceid": "28-000001234",
    "NAMES_onewire2": "Solar Panel",
    "onewire2_deviceid": "28-000005678",
    # Analog inputs
    "NAMES_analoginput1": "pH Probe",
    "AI1_use": 1,
    "AI2_use": 0,
    # Outputs
    "NAMES_pump": "Hauptpumpe",
    "PUMP_control_use": 1,
    "HEATER_control_use": 1,
    "SOLAR_control_use": 0,
    # Pool config
    "POOL_type": "indoor",
    "POOL_size": 40,
    "POOL_disinfection_method": "salt",
    "NAMES_controller": "My Pool Controller",
}


# ============================================================
# DigitalInputConfig tests
# ============================================================


class TestDigitalInputConfig:
    """Test DigitalInputConfig parser."""

    def test_parses_di_names(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        di1 = config.get_di_config(1)
        assert di1["name"] == "Filterstatus"

    def test_parses_switching_rule(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        di1 = config.get_di_config(1)
        assert di1["function"] == "toggle"
        assert di1["output_index"] == 0
        assert di1["enabled"] is True

    def test_di_without_rule_disabled(self):
        """DI with 'unknown' function is disabled."""
        config = DigitalInputConfig({})
        di3 = config.get_di_config(3)
        assert di3["enabled"] is False
        assert di3["function"] == "unknown"

    def test_di_9_to_12_have_no_rules(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        di9 = config.get_di_config(9)
        assert di9["enabled"] is False
        assert di9["function"] is None

    def test_invalid_di_number(self):
        config = DigitalInputConfig({})
        assert config.get_di_config(0) is None
        assert config.get_di_config(13) is None

    def test_get_all_di_configs(self):
        config = DigitalInputConfig({})
        all_dis = config.get_all_di_configs()
        assert len(all_dis) == 12
        assert 1 in all_dis
        assert 12 in all_dis

    def test_get_enabled_dis(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        enabled = config.get_enabled_dis()
        assert 1 in enabled  # has toggle rule
        assert 2 in enabled  # has on_off rule
        assert 3 not in enabled  # no rule

    def test_get_enabled_dis_all_disabled(self):
        config = DigitalInputConfig({})
        enabled = config.get_enabled_dis()
        assert enabled == {}

    def test_get_di_by_name(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        result = config.get_di_by_name("Filterstatus")
        assert result is not None
        assert result["number"] == 1

    def test_get_di_by_name_case_insensitive(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        result = config.get_di_by_name("FILTERSTATUS")
        assert result is not None

    def test_get_di_by_name_not_found(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        assert config.get_di_by_name("Nonexistent") is None

    def test_get_di_entity_id(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        entity_id = config.get_di_entity_id(1)
        assert "filterstatus" in entity_id

    def test_get_di_entity_id_invalid(self):
        config = DigitalInputConfig({})
        assert config.get_di_entity_id(0) == ""
        assert config.get_di_entity_id(99) == ""

    def test_get_di_friendly_name(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        assert config.get_di_friendly_name(1) == "Filterstatus"

    def test_get_di_friendly_name_default(self):
        config = DigitalInputConfig({})
        assert config.get_di_friendly_name(5) == "Digital Input 5"

    def test_get_di_friendly_name_invalid(self):
        config = DigitalInputConfig({})
        assert "Digital Input" in config.get_di_friendly_name(99)

    def test_should_expose_di(self):
        config = DigitalInputConfig(SAMPLE_CONFIG)
        assert config.should_expose_di(1) is True
        assert config.should_expose_di(3) is False

    def test_should_expose_di_invalid(self):
        config = DigitalInputConfig({})
        assert config.should_expose_di(0) is False
        assert config.should_expose_di(99) is False

    def test_description_toggle(self):
        desc = DigitalInputConfig._get_description("toggle", 0)
        assert "Toggle" in desc
        assert "Pump" in desc

    def test_description_on(self):
        desc = DigitalInputConfig._get_description("on", 1)
        assert "Activate" in desc

    def test_description_off(self):
        desc = DigitalInputConfig._get_description("off", 2)
        assert "Deactivate" in desc

    def test_description_unknown_function(self):
        desc = DigitalInputConfig._get_description(None, 0)
        assert desc == "No function assigned"

    def test_description_unknown_output(self):
        desc = DigitalInputConfig._get_description("pulse", 99)
        assert "Output 99" in desc


class TestParseDigitalInputState:
    """Test parse_digital_input_state static method."""

    @pytest.mark.parametrize(
        "state,expected",
        [
            ("1", True),
            ("0", False),
            (1, True),
            (0, False),
            ("true", True),
            ("false", False),
            ("on", True),
            ("off", False),
            ("active", True),
            ("high", True),
            (None, False),
            ("", False),
        ],
    )
    def test_state_parsing(self, state, expected):
        assert DigitalInputConfig.parse_digital_input_state(state) is expected


# ============================================================
# HardwareConfig tests
# ============================================================


class TestHardwareConfig:
    """Test HardwareConfig parser."""

    @pytest.fixture
    def hw(self):
        return HardwareConfig(SAMPLE_CONFIG)

    def test_get_all_configs(self, hw):
        configs = hw.get_all_configs()
        assert "digital_inputs" in configs
        assert "extension_relays" in configs
        assert "dmx_scenes" in configs
        assert "dosing_systems" in configs
        assert "temperature_sensors" in configs
        assert "analog_inputs" in configs
        assert "outputs" in configs
        assert "pool_config" in configs

    def test_digital_input_config(self, hw):
        result = hw.get_digital_input_config(1)
        assert result is not None
        assert result["name"] == "Filterstatus"

    def test_digital_input_config_invalid(self, hw):
        assert hw.get_digital_input_config(0) is None

    def test_di_friendly_name(self, hw):
        assert hw.get_di_friendly_name(1) == "Filterstatus"

    def test_extension_relay_name(self, hw):
        assert hw.get_extension_relay_name("EXT1_1") == "Pool Light"

    def test_extension_relay_name_not_found(self, hw):
        assert hw.get_extension_relay_name("EXT9_1") == "EXT9_1"

    def test_dmx_scene_name(self, hw):
        assert hw.get_dmx_scene_name(1) == "Party Mode"

    def test_dmx_scene_name_default(self, hw):
        assert "Scene" in hw.get_dmx_scene_name(5)

    def test_dosing_system_name(self, hw):
        assert hw.get_dosing_system_name("CL") == "Chlor Pump"

    def test_dosing_system_name_not_found(self, hw):
        assert hw.get_dosing_system_name("UNKNOWN") == "UNKNOWN"

    def test_temp_sensor_name(self, hw):
        assert hw.get_temp_sensor_name(1) == "Pool Water"

    def test_temp_sensor_name_default(self, hw):
        assert hw.get_temp_sensor_name(5) == "Auxiliary 1"

    def test_analog_input_name(self, hw):
        assert hw.get_analog_input_name(1) == "pH Probe"

    def test_analog_input_name_default(self, hw):
        assert "Analog Input" in hw.get_analog_input_name(5)

    def test_output_name(self, hw):
        assert hw.get_output_name("PUMP") == "Hauptpumpe"

    def test_output_name_not_found(self, hw):
        assert hw.get_output_name("UNKNOWN") == "UNKNOWN"

    def test_enabled_features(self, hw):
        enabled = hw.get_enabled_features()
        assert "PUMP" in enabled["outputs"]
        assert "HEATER" in enabled["outputs"]
        assert "SOLAR" not in enabled["outputs"]
        assert len(enabled["digital_inputs"]) > 0
        assert "EXT1_1" in enabled["extension_relays"]
        assert "EXT1_2" not in enabled["extension_relays"]

    def test_summary(self, hw):
        summary = hw.summary()
        assert "40" in summary
        assert "indoor" in summary

    def test_empty_config(self):
        """Empty config uses all defaults."""
        hw = HardwareConfig({})
        configs = hw.get_all_configs()
        assert len(configs["extension_relays"]) == 16  # EXT1_1-8 + EXT2_1-8
        assert len(configs["dmx_scenes"]) == 12
        assert len(configs["outputs"]) == 9

    def test_pool_config_defaults(self):
        hw = HardwareConfig({})
        pool = hw.get_all_configs()["pool_config"]
        assert pool["pool_type"] == "outdoor"
        assert pool["pool_size"] == 50

    def test_pool_config_custom(self, hw):
        pool = hw.get_all_configs()["pool_config"]
        assert pool["pool_type"] == "indoor"
        assert pool["pool_size"] == 40
        assert pool["controller_name"] == "My Pool Controller"
