# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""This module defines the features and entities available in the integration.

It includes a list of all toggleable features that can be configured by the user,
as well as detailed definitions for binary sensors, switches, and number entities
(setpoints). These definitions are used to dynamically create the correct entities
based on the user's enabled features and the data available from the controller.
"""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.helpers.entity import EntityCategory

_ENTITY_CATEGORY_CONFIG = EntityCategory.CONFIG

# =============================================================================
# AVAILABLE FEATURES
# =============================================================================

AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heater", "default": True},
    {"id": "solar", "name": "Solar Absorber", "default": True},
    {"id": "ph_control", "name": "pH Control", "default": True},
    {"id": "chlorine_control", "name": "Chlorine Control", "default": True},
    {"id": "flocculation", "name": "Flocculant Dosing", "default": True},
    {"id": "cover_control", "name": "Cover Control", "default": True},
    {"id": "backwash", "name": "Backwash", "default": True},
    {"id": "pv_surplus", "name": "PV Surplus", "default": True},
    {"id": "filter_control", "name": "Filter Pump", "default": True},
    {"id": "water_level", "name": "Water Level", "default": False},
    {"id": "water_refill", "name": "Water Refill", "default": False},
    {"id": "led_lighting", "name": "LED Lighting", "default": True},
    {"id": "digital_inputs", "name": "Digital Inputs", "default": False},
    {"id": "extension_outputs", "name": "Extension Outputs", "default": False},
]

# =============================================================================
# BINARY SENSORS
# =============================================================================

BINARY_SENSORS = [
    # Core operational states
    {
        "key": "PUMP",
        "name": "Pump State",
        "translation_key": "pump",
        "icon": "mdi:water-pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "filter_control",
    },
    {
        "key": "SOLAR",
        "name": "Solar State",
        "translation_key": "solar",
        "icon": "mdi:solar-power",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "solar",
    },
    {
        "key": "HEATER",
        "name": "Heater State",
        "translation_key": "heater",
        "icon": "mdi:radiator",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "heating",
    },
    {
        "key": "LIGHT",
        "name": "Light State",
        "translation_key": "light",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
    },
    {
        "key": "BACKWASH",
        "name": "Backwash State",
        "translation_key": "backwash",
        "icon": "mdi:autorenew",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "backwash",
    },
    {
        "key": "REFILL",
        "name": "Refill State",
        "translation_key": "refill",
        "icon": "mdi:water",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "water_refill",
    },
    {"key": "ECO", "name": "ECO Mode", "translation_key": "eco", "icon": "mdi:leaf"},
    {
        "key": "PVSURPLUS",
        "name": "PV Surplus",
        "translation_key": "pvsurplus",
        "icon": "mdi:solar-power",
        "feature_id": "pv_surplus",
    },
    # Diagnostic problem sensors
    {
        "key": "CIRCULATION_STATE",
        "name": "Circulation Issue",
        "translation_key": "circulation_state",
        "icon": "mdi:water-alert",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "ELECTRODE_FLOW_STATE",
        "name": "Electrode Flow Issue",
        "translation_key": "electrode_flow_state",
        "icon": "mdi:water-check",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "PRESSURE_STATE",
        "name": "Pressure Issue",
        "translation_key": "pressure_state",
        "icon": "mdi:gauge",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "CAN_RANGE_STATE",
        "name": "Can Range Issue",
        "translation_key": "can_range_state",
        "icon": "mdi:bottle-tonic",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
]

# Dynamically add digital inputs
for i in range(1, 13):
    BINARY_SENSORS.append(
        {
            "key": f"INPUT{i}",
            "name": f"Digital Input {i}",
            "translation_key": f"input{i}",
            "icon": "mdi:electric-switch",
            "feature_id": "digital_inputs",
            "entity_category": EntityCategory.DIAGNOSTIC,
            "entity_registry_enabled_default": False,
        }
    )
for i in range(1, 5):
    BINARY_SENSORS.append(
        {
            "key": f"INPUT_CE{i}",
            "name": f"Digital Input CE{i}",
            "translation_key": f"input_ce{i}",
            "icon": "mdi:electric-switch",
            "feature_id": "digital_inputs",
            "entity_category": EntityCategory.DIAGNOSTIC,
            "entity_registry_enabled_default": False,
        }
    )

BINARY_SENSORS.extend([
    {
        "key": "HW_BASE_MODULE",
        "name": "Hardware: Base Module",
        "translation_key": "hw_base_module",
        "icon": "mdi:chip",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_DOSING_MODULE",
        "name": "Hardware: Dosing Module",
        "translation_key": "hw_dosing_module",
        "icon": "mdi:flask",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_EXTENSION_MODULE_1",
        "name": "Hardware: Extension Module 1",
        "translation_key": "hw_extension_module_1",
        "icon": "mdi:expansion-card",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_EXTENSION_MODULE_2",
        "name": "Hardware: Extension Module 2",
        "translation_key": "hw_extension_module_2",
        "icon": "mdi:expansion-card",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_STANDALONE_MODE",
        "name": "Hardware: Standalone Dosing Unit",
        "translation_key": "hw_standalone_mode",
        "icon": "mdi:server-network",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_DMX_MODULE",
        "name": "Hardware: DMX Module",
        "translation_key": "hw_dmx_module",
        "icon": "mdi:lightbulb-multiple",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
    {
        "key": "HW_DIRULE_MODULE",
        "name": "Hardware: Digital Rules Module",
        "translation_key": "hw_dirule_module",
        "icon": "mdi:script-text",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "entity_registry_enabled_default": False,
    },
])

# =============================================================================
# SWITCHES
# =============================================================================

SWITCHES = [
    {
        "key": "PUMP",
        "name": "Filter Pump",
        "translation_key": "pump",
        "icon": "mdi:water-pump",
        "feature_id": "filter_control",
        "primary": True,
    },
    {
        "key": "SOLAR",
        "name": "Solar Absorber",
        "translation_key": "solar",
        "icon": "mdi:solar-power",
        "feature_id": "solar",
        "primary": True,
    },
    {
        "key": "HEATER",
        "name": "Heater",
        "translation_key": "heater",
        "icon": "mdi:radiator",
        "feature_id": "heating",
    },
    {
        "key": "LIGHT",
        "name": "Lighting",
        "translation_key": "light",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
    },
    {
        "key": "DOS_5_PHP",
        "name": "Dosing pH+",
        "translation_key": "dos_5_php",
        "icon": "mdi:flask-plus",
        "feature_id": "ph_control",
    },
    {
        "key": "DOS_4_PHM",
        "name": "Dosing pH-",
        "translation_key": "dos_4_phm",
        "icon": "mdi:flask-minus",
        "feature_id": "ph_control",
    },
    {
        "key": "DOS_1_CL",
        "name": "Chlorine Dosing",
        "translation_key": "dos_1_cl",
        "icon": "mdi:flask-outline",
        "feature_id": "chlorine_control",
    },
    {
        "key": "DOS_6_FLOC",
        "name": "Flocculant",
        "translation_key": "dos_6_floc",
        "icon": "mdi:water",
        "feature_id": "flocculation",
    },
    {
        "key": "PVSURPLUS",
        "name": "PV Surplus",
        "translation_key": "pvsurplus",
        "icon": "mdi:solar-power",
        "feature_id": "pv_surplus",
    },
    {
        "key": "BACKWASH",
        "name": "Backwash",
        "translation_key": "backwash",
        "icon": "mdi:autorenew",
        "feature_id": "backwash",
    },
    {
        "key": "BACKWASHRINSE",
        "name": "Rinse",
        "translation_key": "backwashrinse",
        "icon": "mdi:autorenew",
        "feature_id": "backwash",
    },
]

# Dynamically add extension switches
for ext_bank in [1, 2]:
    for i in range(1, 9):
        SWITCHES.append(
            {
                "key": f"EXT{ext_bank}_{i}",
                "name": f"Extension {ext_bank}.{i}",
                "translation_key": f"ext{ext_bank}_{i}",
                "icon": "mdi:toggle-switch-outline",
                "feature_id": "extension_outputs",
                "entity_category": EntityCategory.DIAGNOSTIC,
                "entity_registry_enabled_default": False,
            }
        )
# Dynamically add DMX scenes
for i in range(1, 13):
        SWITCHES.append(
            {
                "key": f"DMX_SCENE{i}",
                "name": f"DMX Scene {i}",
                "translation_key": f"dmx_scene{i}",
                "icon": "mdi:lightbulb-multiple",
                "feature_id": "led_lighting",
                "entity_category": EntityCategory.CONFIG,
                "entity_registry_enabled_default": False,
            }
        )
# Dynamically add digital rules
for i in range(1, 8):
        SWITCHES.append(
            {
                "key": f"DIRULE_{i}",
                "name": f"Switching Rule {i}",
                "translation_key": f"dirule_{i}",
                "icon": "mdi:script-text",
                "feature_id": "digital_inputs",
                "entity_category": EntityCategory.CONFIG,
                "entity_registry_enabled_default": False,
            }
        )

# =============================================================================
# NUMBER ENTITIES (SETPOINTS)
# =============================================================================

SETPOINT_DEFINITIONS = [
    {
        "key": "ph_setpoint",
        "name": "pH Setpoint",
        "translation_key": "ph_setpoint",
        "api_key": "pH",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "default_value": 7.2,
        "icon": "mdi:ph",
        "unit_of_measurement": "pH",
        "device_class": NumberDeviceClass.PH,
        "feature_id": "ph_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_setpoint", "pH_target"],
        "indicator_fields": ["pH_value", "pH_VALUE", "DOS_4_PHM", "DOS_5_PHP"],
    },
    {
        "key": "orp_setpoint",
        "name": "ORP Setpoint",
        "translation_key": "orp_setpoint",
        "api_key": "ORP",
        "min_value": 600,
        "max_value": 800,
        "step": 10,
        "default_value": 700,
        "icon": "mdi:lightning-bolt-circle",
        "unit_of_measurement": "mV",
        "device_class": None,
        "feature_id": "chlorine_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["ORP_SETPOINT", "ORP_setpoint", "ORP_target"],
        "indicator_fields": ["orp_value", "ORP_VALUE", "DOS_1_CL"],
    },
    {
        "key": "chlorine_setpoint",
        "name": "Chlorine Setpoint",
        "translation_key": "chlorine_setpoint",
        "api_key": "MinChlorine",
        "min_value": 0.2,
        "max_value": 2.0,
        "step": 0.1,
        "default_value": 0.6,
        "icon": "mdi:water-plus",
        "unit_of_measurement": "mg/l",
        "device_class": None,
        "feature_id": "chlorine_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["CHLORINE_SETPOINT", "MinChlorine", "pot_setpoint"],
        "indicator_fields": ["pot_value", "POT_VALUE", "DOS_1_CL"],
    },
    {
        "key": "heater_target_temp",
        "name": "Heater Target Temperature",
        "translation_key": "heater_target_temp",
        "api_key": "HEATER_TARGET_TEMP",
        "min_value": 20.0,
        "max_value": 35.0,
        "step": 0.5,
        "default_value": 28.0,
        "icon": "mdi:radiator",
        "unit_of_measurement": "°C",
        "device_class": None,
        "feature_id": "heating",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["HEATER_TARGET_TEMP", "heater_target_temp"],
        "indicator_fields": ["HEATER", "onewire5_value"],
    },
    {
        "key": "solar_target_temp",
        "name": "Solar Target Temperature",
        "translation_key": "solar_target_temp",
        "api_key": "SOLAR_TARGET_TEMP",
        "min_value": 20.0,
        "max_value": 40.0,
        "step": 0.5,
        "default_value": 30.0,
        "icon": "mdi:solar-power",
        "unit_of_measurement": "°C",
        "device_class": None,
        "feature_id": "solar",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["SOLAR_TARGET_TEMP", "solar_target_temp"],
        "indicator_fields": ["SOLAR", "onewire3_value"],
    },
    {
        "key": "pump_speed",
        "name": "Pump Speed",
        "translation_key": "pump_speed",
        "api_key": "PUMP_SPEED",
        "min_value": 1,
        "max_value": 3,
        "step": 1,
        "default_value": 2,
        "icon": "mdi:pump",
        "unit_of_measurement": None,
        "device_class": None,
        "feature_id": "filter_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["PUMP_SPEED", "pump_speed"],
        "indicator_fields": ["PUMP", "PUMP_RPM_2", "PUMP_RPM_2_VALUE"],
    },
    # Dosing Canister Volumes
    {
        "key": "chlorine_canister_volume",
        "name": "Chlorine Canister Volume",
        "translation_key": "chlorine_canister_volume",
        "api_key": "DOS_1_CL_TOTAL_CAN_AMOUNT_ML",
        "min_value": 100,
        "max_value": 50000,
        "step": 100,
        "default_value": 10000,
        "icon": "mdi:barrel",
        "unit_of_measurement": "ml",
        "device_class": None,  # Volume device class not available in HA
        "feature_id": "chlorine_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["DOS_1_CL_TOTAL_CAN_AMOUNT_ML"],
        "indicator_fields": ["DOS_1_CL", "DOS_1_CL_STATE"],
    },
    {
        "key": "ph_minus_canister_volume",
        "name": "pH- Canister Volume",
        "translation_key": "ph_minus_canister_volume",
        "api_key": "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML",
        "min_value": 100,
        "max_value": 50000,
        "step": 100,
        "default_value": 10000,
        "icon": "mdi:barrel",
        "unit_of_measurement": "ml",
        "device_class": None,  # Volume device class not available in HA
        "feature_id": "ph_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["DOS_4_PHM_TOTAL_CAN_AMOUNT_ML"],
        "indicator_fields": ["DOS_4_PHM", "DOS_4_PHM_STATE"],
    },
    {
        "key": "ph_plus_canister_volume",
        "name": "pH+ Canister Volume",
        "translation_key": "ph_plus_canister_volume",
        "api_key": "DOS_5_PHP_TOTAL_CAN_AMOUNT_ML",
        "min_value": 100,
        "max_value": 50000,
        "step": 100,
        "default_value": 20000,
        "icon": "mdi:barrel",
        "unit_of_measurement": "ml",
        "device_class": None,  # Volume device class not available in HA
        "feature_id": "ph_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["DOS_5_PHP_TOTAL_CAN_AMOUNT_ML"],
        "indicator_fields": ["DOS_5_PHP", "DOS_5_PHP_STATE"],
    },
    {
        "key": "flocculant_canister_volume",
        "name": "Flocculant Canister Volume",
        "translation_key": "flocculant_canister_volume",
        "api_key": "DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML",
        "min_value": 100,
        "max_value": 50000,
        "step": 100,
        "default_value": 20000,
        "icon": "mdi:barrel",
        "unit_of_measurement": "ml",
        "device_class": None,  # Volume device class not available in HA
        "feature_id": "flocculation",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML"],
        "indicator_fields": ["DOS_6_FLOC", "DOS_6_FLOC_STATE"],
    },
]

# =============================================================================
# SELECT CONTROLS - ON/OFF/AUTO Control
# =============================================================================

SELECT_CONTROLS = [
    {
        "key": "pump_mode",
        "name": "Pump Mode",
        "translation_key": "pump_mode",
        "device_key": "PUMP",
        "icon": "mdi:water-pump",
        "feature_id": "filter_control",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "heater_mode",
        "name": "Heater Mode",
        "translation_key": "heater_mode",
        "device_key": "HEATER",
        "icon": "mdi:radiator-disabled",
        "feature_id": "heating",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "solar_mode",
        "name": "Solar Mode",
        "translation_key": "solar_mode",
        "device_key": "SOLAR",
        "icon": "mdi:solar-power-variant",
        "feature_id": "solar",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "light_mode",
        "name": "Light Mode",
        "translation_key": "light_mode",
        "device_key": "LIGHT",
        "icon": "mdi:lightbulb-on",
        "feature_id": "led_lighting",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "dos_cl_mode",
        "name": "Chlorine Dosing Mode",
        "translation_key": "dos_cl_mode",
        "device_key": "DOS_1_CL",
        "icon": "mdi:flask-empty-outline",
        "feature_id": "chlorine_control",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "dos_phm_mode",
        "name": "pH- Dosing Mode",
        "translation_key": "dos_phm_mode",
        "device_key": "DOS_4_PHM",
        "icon": "mdi:flask-empty-minus",
        "feature_id": "ph_control",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "dos_php_mode",
        "name": "pH+ Dosing Mode",
        "translation_key": "dos_php_mode",
        "device_key": "DOS_5_PHP",
        "icon": "mdi:flask-plus",
        "feature_id": "ph_control",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "pvsurplus_mode",
        "name": "PV Surplus Mode",
        "translation_key": "pvsurplus_mode",
        "device_key": "PVSURPLUS",
        "icon": "mdi:solar-power-variant",
        "feature_id": "pv_surplus",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "backwash_mode",
        "name": "Backwash Mode",
        "translation_key": "backwash_mode",
        "device_key": "BACKWASH",
        "icon": "mdi:autorenew",
        "feature_id": "backwash",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "backwashrinse_mode",
        "name": "Rinse Mode",
        "translation_key": "backwashrinse_mode",
        "device_key": "BACKWASHRINSE",
        "icon": "mdi:autorenew",
        "feature_id": "backwash",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
    {
        "key": "dos_floc_mode",
        "name": "Flocculant Mode",
        "translation_key": "dos_floc_mode",
        "device_key": "DOS_6_FLOC",
        "icon": "mdi:water",
        "feature_id": "flocculation",
        "entity_category": _ENTITY_CATEGORY_CONFIG,
    },
]

# Dynamically add extension outputs as select (ON/OFF/AUTO)
for _ext_bank in [1, 2]:
    for _i in range(1, 9):
        SELECT_CONTROLS.append(
            {
                "key": f"ext{_ext_bank}_{_i}_mode",
                "name": f"Extension {_ext_bank}.{_i} Mode",
                "translation_key": f"ext{_ext_bank}_{_i}_mode",
                "device_key": f"EXT{_ext_bank}_{_i}",
                "icon": "mdi:toggle-switch-outline",
                "feature_id": "extension_outputs",
                "entity_category": _ENTITY_CATEGORY_CONFIG,
            }
        )
