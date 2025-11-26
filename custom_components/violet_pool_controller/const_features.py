"""This module defines the features and entities available in the integration.

It includes a list of all toggleable features that can be configured by the user,
as well as detailed definitions for binary sensors, switches, and number entities
(setpoints). These definitions are used to dynamically create the correct entities
based on the user's enabled features and the data available from the controller.
"""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.helpers.entity import EntityCategory

# =============================================================================
# AVAILABLE FEATURES
# =============================================================================

AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heizung", "default": True},
    {"id": "solar", "name": "Solarabsorber", "default": True},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True},
    {"id": "backwash", "name": "Rückspülung", "default": True},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True},
    {"id": "filter_control", "name": "Filterpumpe", "default": True},
    {"id": "water_level", "name": "Wasserstand", "default": False},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True},
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False},
]

# =============================================================================
# BINARY SENSORS
# =============================================================================

BINARY_SENSORS = [
    # Core operational states
    {
        "key": "PUMP",
        "name": "Pump State",
        "icon": "mdi:water-pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "filter_control",
    },
    {
        "key": "SOLAR",
        "name": "Solar State",
        "icon": "mdi:solar-power",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "solar",
    },
    {
        "key": "HEATER",
        "name": "Heater State",
        "icon": "mdi:radiator",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "heating",
    },
    {
        "key": "LIGHT",
        "name": "Light State",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
    },
    {
        "key": "BACKWASH",
        "name": "Backwash State",
        "icon": "mdi:valve",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "backwash",
    },
    {
        "key": "REFILL",
        "name": "Refill State",
        "icon": "mdi:water",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "feature_id": "water_refill",
    },
    {"key": "ECO", "name": "ECO Mode", "icon": "mdi:leaf"},
    {
        "key": "PVSURPLUS",
        "name": "PV Surplus",
        "icon": "mdi:solar-power-variant",
        "feature_id": "pv_surplus",
    },
    # Diagnostic problem sensors
    {
        "key": "CIRCULATION_STATE",
        "name": "Circulation Issue",
        "icon": "mdi:water-alert",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "ELECTRODE_FLOW_STATE",
        "name": "Electrode Flow Issue",
        "icon": "mdi:water-check",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "PRESSURE_STATE",
        "name": "Pressure Issue",
        "icon": "mdi:gauge",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "CAN_RANGE_STATE",
        "name": "Can Range Issue",
        "icon": "mdi:bottle-tonic",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]

# Dynamically add digital inputs
for i in range(1, 13):
    BINARY_SENSORS.append(
        {
            "key": f"INPUT{i}",
            "name": f"Digital Input {i}",
            "icon": "mdi:electric-switch",
            "feature_id": "digital_inputs",
            "entity_category": EntityCategory.DIAGNOSTIC,
        }
    )
for i in range(1, 5):
    BINARY_SENSORS.append(
        {
            "key": f"INPUT_CE{i}",
            "name": f"Digital Input CE{i}",
            "icon": "mdi:electric-switch",
            "feature_id": "digital_inputs",
            "entity_category": EntityCategory.DIAGNOSTIC,
        }
    )

# =============================================================================
# SWITCHES
# =============================================================================

SWITCHES = [
    {
        "key": "PUMP",
        "name": "Filterpumpe",
        "icon": "mdi:water-pump",
        "feature_id": "filter_control",
    },
    {
        "key": "SOLAR",
        "name": "Solarabsorber",
        "icon": "mdi:solar-power",
        "feature_id": "solar",
    },
    {
        "key": "HEATER",
        "name": "Heizung",
        "icon": "mdi:radiator",
        "feature_id": "heating",
    },
    {
        "key": "LIGHT",
        "name": "Beleuchtung",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
    },
    {
        "key": "DOS_5_PHP",
        "name": "Dosierung pH+",
        "icon": "mdi:flask-plus",
        "feature_id": "ph_control",
    },
    {
        "key": "DOS_4_PHM",
        "name": "Dosierung pH-",
        "icon": "mdi:flask-minus",
        "feature_id": "ph_control",
    },
    {
        "key": "DOS_1_CL",
        "name": "Chlor-Dosierung",
        "icon": "mdi:flask",
        "feature_id": "chlorine_control",
    },
    {
        "key": "DOS_6_FLOC",
        "name": "Flockmittel",
        "icon": "mdi:flask",
        "feature_id": "chlorine_control",
    },
    {
        "key": "PVSURPLUS",
        "name": "PV-Überschuss",
        "icon": "mdi:solar-power-variant",
        "feature_id": "pv_surplus",
    },
    {
        "key": "BACKWASH",
        "name": "Rückspülung",
        "icon": "mdi:valve",
        "feature_id": "backwash",
    },
    {
        "key": "BACKWASHRINSE",
        "name": "Nachspülung",
        "icon": "mdi:valve",
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
                "icon": "mdi:toggle-switch-outline",
                "feature_id": "extension_outputs",
            }
        )
# Dynamically add DMX scenes
for i in range(1, 13):
    SWITCHES.append(
        {
            "key": f"DMX_SCENE{i}",
            "name": f"DMX Szene {i}",
            "icon": "mdi:lightbulb-multiple",
            "feature_id": "led_lighting",
        }
    )
# Dynamically add digital rules
for i in range(1, 8):
    SWITCHES.append(
        {
            "key": f"DIRULE_{i}",
            "name": f"Schaltregel {i}",
            "icon": "mdi:script-text",
            "feature_id": "digital_inputs",
        }
    )

# =============================================================================
# NUMBER ENTITIES (SETPOINTS)
# =============================================================================

SETPOINT_DEFINITIONS = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "api_key": "pH",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "default_value": 7.2,
        "icon": "mdi:flask",
        "unit_of_measurement": "pH",
        "device_class": NumberDeviceClass.PH,
        "feature_id": "ph_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_setpoint", "pH_target"],
        "indicator_fields": ["pH_value", "pH_VALUE", "DOS_4_PHM", "DOS_5_PHP"],
    },
    {
        "key": "orp_setpoint",
        "name": "Redox Sollwert",
        "api_key": "ORP",
        "min_value": 600,
        "max_value": 800,
        "step": 10,
        "default_value": 700,
        "icon": "mdi:flash",
        "unit_of_measurement": "mV",
        "device_class": None,
        "feature_id": "chlorine_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["ORP_SETPOINT", "ORP_setpoint", "ORP_target"],
        "indicator_fields": ["orp_value", "ORP_VALUE", "DOS_1_CL"],
    },
    {
        "key": "chlorine_setpoint",
        "name": "Chlor Sollwert",
        "api_key": "MinChlorine",
        "min_value": 0.2,
        "max_value": 2.0,
        "step": 0.1,
        "default_value": 0.6,
        "icon": "mdi:test-tube",
        "unit_of_measurement": "mg/l",
        "device_class": None,
        "feature_id": "chlorine_control",
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["CHLORINE_SETPOINT", "MinChlorine", "pot_setpoint"],
        "indicator_fields": ["pot_value", "POT_VALUE", "DOS_1_CL"],
    },
    {
        "key": "heater_target_temp",
        "name": "Heizung Zieltemperatur",
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
        "name": "Solar Zieltemperatur",
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
        "name": "Pumpengeschwindigkeit",
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
        "setpoint_fields": ["PUMP_RPM_2", "PUMP_SPEED", "pump_speed"],
        "indicator_fields": ["PUMP", "PUMP_RPM_2", "PUMP_RPM_2_VALUE"],
    },
]
