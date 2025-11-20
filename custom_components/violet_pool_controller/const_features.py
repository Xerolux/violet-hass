"""Feature- und Entity-bezogene Konstanten für die Violet Pool Controller Integration."""

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

# =============================================================================
# AVAILABLE FEATURES
# =============================================================================

AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heizung", "default": True, "platforms": ["climate", "switch", "binary_sensor"]},
    {"id": "solar", "name": "Solarabsorber", "default": True, "platforms": ["climate", "switch", "binary_sensor"]},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True, "platforms": ["number", "sensor", "switch"]},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True, "platforms": ["number", "sensor", "switch"]},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True, "platforms": ["cover", "binary_sensor"]},
    {"id": "backwash", "name": "Rückspülung", "default": True, "platforms": ["switch", "binary_sensor"]},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True, "platforms": ["switch", "binary_sensor"]},
    {
        "id": "filter_control", "name": "Filterpumpe", "default": True,
        "platforms": ["switch", "binary_sensor", "sensor"]
    },
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch", "binary_sensor"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False, "platforms": ["binary_sensor", "switch"]},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False, "platforms": ["switch"]},
]

# =============================================================================
# BINARY SENSORS with 3-STATE SUPPORT
# =============================================================================

BINARY_SENSORS = [
    {
        "name": "Pump State",
        "key": "PUMP",
        "icon": "mdi:water-pump",
        "feature_id": "filter_control",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "supports_3_state": True,
    },
    {
        "name": "Solar State",
        "key": "SOLAR",
        "icon": "mdi:solar-power",
        "feature_id": "solar",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "supports_3_state": True,
    },
    {
        "name": "Heater State",
        "key": "HEATER",
        "icon": "mdi:radiator",
        "feature_id": "heating",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "supports_3_state": True,
    },
    {
        "name": "Light State",
        "key": "LIGHT",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
        "supports_3_state": True,
    },
    {
        "name": "Backwash State",
        "key": "BACKWASH",
        "icon": "mdi:valve",
        "feature_id": "backwash",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "supports_3_state": True,
    },
    {
        "name": "Refill State",
        "key": "REFILL",
        "icon": "mdi:water",
        "feature_id": "water_refill",
        "device_class": BinarySensorDeviceClass.RUNNING,
    },
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"},
    {
        "name": "PV Surplus",
        "key": "PVSURPLUS",
        "icon": "mdi:solar-power-variant",
        "feature_id": "pv_surplus",
        "supports_3_state": True,
    },
    {
        "name": "Circulation Issue",
        "key": "CIRCULATION_STATE",
        "icon": "mdi:water-alert",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "name": "Electrode Flow Issue",
        "key": "ELECTRODE_FLOW_STATE",
        "icon": "mdi:water-check",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "name": "Pressure Issue",
        "key": "PRESSURE_STATE",
        "icon": "mdi:gauge",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "name": "Can Range Issue",
        "key": "CAN_RANGE_STATE",
        "icon": "mdi:bottle-tonic",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]

# Add digital inputs
for i in range(1, 13):
    BINARY_SENSORS.append({
        "name": f"Digital Input {i}",
        "key": f"INPUT{i}",
        "icon": "mdi:electric-switch",
        "feature_id": "digital_inputs",
        "entity_category": EntityCategory.DIAGNOSTIC,
    })

# Add digital CE inputs
for i in range(1, 5):
    BINARY_SENSORS.append({
        "name": f"Digital Input CE{i}",
        "key": f"INPUT_CE{i}",
        "icon": "mdi:electric-switch",
        "feature_id": "digital_inputs",
        "entity_category": EntityCategory.DIAGNOSTIC,
    })

# =============================================================================
# SWITCHES with 3-STATE SUPPORT
# =============================================================================

SWITCHES = [
    {
        "name": "Filterpumpe",
        "key": "PUMP",
        "icon": "mdi:water-pump",
        "feature_id": "filter_control",
        "supports_3_state": True,
        "supports_speed": True,
    },
    {
        "name": "Solarabsorber",
        "key": "SOLAR",
        "icon": "mdi:solar-power",
        "feature_id": "solar",
        "supports_3_state": True,
    },
    {
        "name": "Heizung",
        "key": "HEATER",
        "icon": "mdi:radiator",
        "feature_id": "heating",
        "supports_3_state": True,
    },
    {
        "name": "Beleuchtung",
        "key": "LIGHT",
        "icon": "mdi:lightbulb",
        "feature_id": "led_lighting",
        "supports_3_state": True,
        "supports_color_pulse": True,
    },
    {
        "name": "Dosierung pH+",
        "key": "DOS_5_PHP",
        "icon": "mdi:flask-plus",
        "feature_id": "ph_control",
        "supports_3_state": True,
        "supports_timer": True,
    },
    {
        "name": "Dosierung pH-",
        "key": "DOS_4_PHM",
        "icon": "mdi:flask-minus",
        "feature_id": "ph_control",
        "supports_3_state": True,
        "supports_timer": True,
    },
    {
        "name": "Chlor-Dosierung",
        "key": "DOS_1_CL",
        "icon": "mdi:flask",
        "feature_id": "chlorine_control",
        "supports_3_state": True,
        "supports_timer": True,
    },
    {
        "name": "Flockmittel",
        "key": "DOS_6_FLOC",
        "icon": "mdi:flask",
        "feature_id": "chlorine_control",
        "supports_3_state": True,
        "supports_timer": True,
    },
    {
        "name": "PV-Überschuss",
        "key": "PVSURPLUS",
        "icon": "mdi:solar-power-variant",
        "feature_id": "pv_surplus",
        "supports_3_state": True,
        "supports_speed": True,
    },
    {
        "name": "Rückspülung",
        "key": "BACKWASH",
        "icon": "mdi:valve",
        "feature_id": "backwash",
        "supports_3_state": True,
    },
    {
        "name": "Nachspülung",
        "key": "BACKWASHRINSE",
        "icon": "mdi:valve",
        "feature_id": "backwash",
        "supports_3_state": True,
    },
]

# Add extension switches
for ext_bank in [1, 2]:
    for i in range(1, 9):
        SWITCHES.append({
            "name": f"Extension {ext_bank}.{i}",
            "key": f"EXT{ext_bank}_{i}",
            "icon": "mdi:toggle-switch-outline",
            "feature_id": "extension_outputs",
            "supports_3_state": True,
        })

# Add DMX scenes
for scene_num in range(1, 13):
    SWITCHES.append({
        "name": f"DMX Szene {scene_num}",
        "key": f"DMX_SCENE{scene_num}",
        "icon": "mdi:lightbulb-multiple",
        "feature_id": "led_lighting",
        "supports_3_state": True,
    })

# Add digital rules
for rule_num in range(1, 8):
    SWITCHES.append({
        "name": f"Schaltregel {rule_num}",
        "key": f"DIRULE_{rule_num}",
        "icon": "mdi:script-text",
        "feature_id": "digital_inputs",
        "supports_3_state": True,
    })

# =============================================================================
# SETPOINT DEFINITIONS
# =============================================================================

SETPOINT_DEFINITIONS = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH",
        "feature_id": "ph_control",
        "unit_of_measurement": "pH",
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
        "default_value": 7.2,
        "setpoint_fields": ["pH_setpoint", "pH_target", "pH"],
        "indicator_fields": ["pH_value", "ph_value"],
    },
    {
        "key": "orp_setpoint",
        "name": "Redox Sollwert",
        "min_value": 600,
        "max_value": 800,
        "step": 10,
        "icon": "mdi:flash",
        "api_key": "ORP",
        "feature_id": "chlorine_control",
        "unit_of_measurement": "mV",
        "entity_category": EntityCategory.CONFIG,
        "default_value": 700,
        "setpoint_fields": ["ORP_setpoint", "ORP_target", "ORP"],
        "indicator_fields": ["orp_value", "ORP_value"],
    },
    {
        "key": "chlorine_setpoint",
        "name": "Chlor Sollwert",
        "min_value": 0.2,
        "max_value": 2.0,
        "step": 0.1,
        "icon": "mdi:test-tube",
        "api_key": "MinChlorine",
        "feature_id": "chlorine_control",
        "unit_of_measurement": "mg/l",
        "entity_category": EntityCategory.CONFIG,
        "default_value": 0.6,
        "setpoint_fields": ["MinChlorine", "chlorine_target", "chlorine_setpoint"],
        "indicator_fields": ["pot_value", "chlorine_value"],
    },
]

__all__ = [
    "AVAILABLE_FEATURES",
    "BINARY_SENSORS",
    "SWITCHES",
    "SETPOINT_DEFINITIONS",
]
