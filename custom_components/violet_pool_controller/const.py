"""Konstanten für die Violet Pool Controller Integration - OPTIMIZED VERSION."""
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

# =============================================================================
# INTEGRATION INFO
# =============================================================================

DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "0.2.0-beta.1"
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# =============================================================================
# CONFIGURATION KEYS
# =============================================================================

CONF_API_URL = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_ACTIVE_FEATURES = "active_features"
CONF_SELECTED_SENSORS = "selected_sensors"
CONF_POOL_SIZE = "pool_size"
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"

# Default Values
DEFAULT_POLLING_INTERVAL = 10  # Sekunden
DEFAULT_TIMEOUT_DURATION = 10  # Sekunden
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_USE_SSL = False
DEFAULT_DEVICE_NAME = "Violet Pool Controller"
DEFAULT_POOL_SIZE = 50  # m³
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

# =============================================================================
# API ENDPOINTS
# =============================================================================

API_READINGS = "/getReadings"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"
API_SET_DOSING_PARAMETERS = "/setDosingParameters"
API_SET_TARGET_VALUES = "/setTargetValues"
API_GET_CONFIG = "/getConfig"
API_SET_CONFIG = "/setConfig"
API_GET_CALIB_RAW_VALUES = "/getCalibRawValues"
API_GET_CALIB_HISTORY = "/getCalibHistory"
API_RESTORE_CALIBRATION = "/restoreOldCalib"
API_SET_OUTPUT_TESTMODE = "/setOutputTestmode"
API_GET_HISTORY = "/getHistory"
API_GET_WEATHER_DATA = "/getWeatherdata"
API_GET_OVERALL_DOSING = "/getOverallDosing"
API_GET_OUTPUT_STATES = "/getOutputstates"

# Default reading optimisation settings
SPECIFIC_READING_GROUPS = (
    "ADC",
    "DOSAGE",
    "RUNTIMES",
    "PUMPPRIOSTATE",
    "BACKWASH",
    "SYSTEM",
    "INPUT1",
    "INPUT2",
    "INPUT3",
    "INPUT4",
    "date",
    "time",
)
SPECIFIC_FULL_REFRESH_INTERVAL = 10

# =============================================================================
# POOL CONFIGURATION
# =============================================================================

POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# =============================================================================
# STATE MAPPINGS - CRITICAL FOR 3-STATE SUPPORT
# =============================================================================

# Device State Mapping - Extended state information with State 4
DEVICE_STATE_MAPPING = {
    # String-based states
    "ON": {"mode": "manual", "active": True, "priority": 80},
    "OFF": {"mode": "manual", "active": False, "priority": 70},
    "AUTO": {"mode": "auto", "active": None, "priority": 60},
    "MAN": {"mode": "manual", "active": True, "priority": 80},
    "MANUAL": {"mode": "manual", "active": True, "priority": 80},
    # Numeric states (as documented in API)
    "0": {"mode": "auto", "active": False, "priority": 50, "desc": "AUTO - Standby"},
    "1": {"mode": "manual", "active": True, "priority": 80, "desc": "Manuell EIN"},
    "2": {"mode": "auto", "active": True, "priority": 60, "desc": "AUTO - Aktiv"},
    "3": {"mode": "auto", "active": True, "priority": 65, "desc": "AUTO - Aktiv (Zeitsteuerung)"},
    "4": {"mode": "manual", "active": True, "priority": 85, "desc": "Manuell EIN (forciert)"},
    "5": {"mode": "auto", "active": False, "priority": 55, "desc": "AUTO - Wartend"},
    "6": {"mode": "manual", "active": False, "priority": 70, "desc": "Manuell AUS"},
    # Additional states
    "STOPPED": {"mode": "manual", "active": False, "priority": 75},
    "ERROR": {"mode": "error", "active": False, "priority": 100},
    "MAINTENANCE": {"mode": "maintenance", "active": False, "priority": 90},
}

# CRITICAL FIX: STATE_MAP with State 4
STATE_MAP = {
    # Numeric states as integer (direct API values)
    0: False,  # AUTO-Standby (OFF)
    1: True,   # Manuell EIN
    2: True,   # AUTO-Aktiv (ON)
    3: True,   # AUTO-Zeitsteuerung (ON)
    4: True,   # ⭐ Manuell forciert EIN (ON) - CRITICAL FIX!
    5: False,  # AUTO-Wartend (OFF)
    6: False,  # Manuell AUS
    # Numeric states as string (if API delivers as string)
    "0": False,
    "1": True,
    "2": True,
    "3": True,
    "4": True,  # ⭐ CRITICAL FIX!
    "5": False,
    "6": False,
    # String-based states
    "ON": True,
    "OFF": False,
    "AUTO": False,
    "TRUE": True,
    "FALSE": False,
    "OPEN": True,
    "CLOSED": False,
    "OPENING": True,
    "CLOSING": True,
    "STOPPED": False,
    "MAN": True,
    "MANUAL": True,
    "ACTIVE": True,
    "RUNNING": True,
    "IDLE": False,
}

# COVER_STATE_MAP with string states
COVER_STATE_MAP = {
    # Numeric states
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
    "4": "stopped",
    # String states (recognized from API)
    "OPEN": "open",
    "CLOSED": "closed",
    "OPENING": "opening",
    "CLOSING": "closing",
    "STOPPED": "stopped",
}

# =============================================================================
# STATE VISUALIZATION
# =============================================================================

STATE_ICONS = {
    "PUMP": {
        "auto_active": "mdi:water-pump",
        "auto_inactive": "mdi:water-pump-off",
        "manual_on": "mdi:water-pump",
        "manual_off": "mdi:water-pump-off",
        "error": "mdi:water-pump-alert",
        "maintenance": "mdi:water-pump-wrench",
    },
    "HEATER": {
        "auto_active": "mdi:radiator",
        "auto_inactive": "mdi:radiator-disabled",
        "manual_on": "mdi:radiator",
        "manual_off": "mdi:radiator-off",
        "error": "mdi:radiator-alert",
        "maintenance": "mdi:radiator-wrench",
    },
    "SOLAR": {
        "auto_active": "mdi:solar-power",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power",
        "manual_off": "mdi:solar-power-off",
        "error": "mdi:solar-power-alert",
    },
    "LIGHT": {
        "auto_active": "mdi:lightbulb-on",
        "auto_inactive": "mdi:lightbulb-auto",
        "manual_on": "mdi:lightbulb-on",
        "manual_off": "mdi:lightbulb-off",
        "color_pulse": "mdi:lightbulb-multiple",
    },
    "DOS_1_CL": {
        "auto_active": "mdi:flask",
        "auto_inactive": "mdi:flask-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off",
    },
    "DOS_4_PHM": {
        "auto_active": "mdi:flask-minus",
        "auto_inactive": "mdi:flask-minus-outline",
        "manual_on": "mdi:flask-minus",
        "manual_off": "mdi:flask-off",
    },
    "DOS_5_PHP": {
        "auto_active": "mdi:flask-plus",
        "auto_inactive": "mdi:flask-plus-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off",
    },
    "BACKWASH": {
        "auto_active": "mdi:valve-open",
        "auto_inactive": "mdi:valve",
        "manual_on": "mdi:valve-open",
        "manual_off": "mdi:valve-closed",
    },
    "PVSURPLUS": {
        "auto_active": "mdi:solar-power-variant",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power-variant",
        "manual_off": "mdi:solar-power-variant-outline",
    },
}

STATE_COLORS = {
    "auto_active": "#4CAF50",     # Grün
    "auto_inactive": "#2196F3",   # Blau
    "manual_on": "#FF9800",       # Orange
    "manual_off": "#F44336",      # Rot
    "error": "#9C27B0",           # Lila
    "maintenance": "#607D8B",     # Grau
}

STATE_TRANSLATIONS = {
    "de": {
        "auto_active": "Automatik (Aktiv)",
        "auto_inactive": "Automatik (Bereit)",
        "manual_on": "Manuell Ein",
        "manual_off": "Manuell Aus",
        "error": "Fehler",
        "maintenance": "Wartung",
        "unknown": "Unbekannt",
    },
    "en": {
        "auto_active": "Auto (Active)",
        "auto_inactive": "Auto (Ready)",
        "manual_on": "Manual On",
        "manual_off": "Manual Off",
        "error": "Error",
        "maintenance": "Maintenance",
        "unknown": "Unknown",
    },
}

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
# API FUNCTIONS AND KEYS
# =============================================================================

# Base Switch Functions
SWITCH_FUNCTIONS = {
    "PUMP": "Filterpumpe",
    "SOLAR": "Solarabsorber",
    "HEATER": "Heizung",
    "LIGHT": "Beleuchtung",
    "ECO": "Eco-Modus",
    "BACKWASH": "Rückspülung",
    "BACKWASHRINSE": "Nachspülung",
    "REFILL": "Wassernachfüllung",
    "PVSURPLUS": "PV-Überschuss",  # ⭐ FIX: PVSURPLUS added
}

# Add extension relays
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        SWITCH_FUNCTIONS[f"EXT{ext_bank}_{relay_num}"] = f"Erweiterung {ext_bank}.{relay_num}"

# Add DMX scenes
for scene_num in range(1, 13):
    SWITCH_FUNCTIONS[f"DMX_SCENE{scene_num}"] = f"DMX Szene {scene_num}"

# Add digital rules
for rule_num in range(1, 8):
    SWITCH_FUNCTIONS[f"DIRULE_{rule_num}"] = f"Schaltregel {rule_num}"

# Add Omni DCs
for dc_num in range(6):
    SWITCH_FUNCTIONS[f"OMNI_DC{dc_num}"] = f"Omni DC{dc_num}"

COVER_FUNCTIONS = {
    "OPEN": "COVER_OPEN",
    "CLOSE": "COVER_CLOSE",
    "STOP": "COVER_STOP",
}

DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO",
    "Flockmittel": "DOS_6_FLOC",
}

# =============================================================================
# API ACTIONS
# =============================================================================

ACTION_ON = "ON"
ACTION_OFF = "OFF"
ACTION_AUTO = "AUTO"
ACTION_PUSH = "PUSH"
ACTION_MAN = "MAN"
ACTION_COLOR = "COLOR"
ACTION_ALLON = "ALLON"
ACTION_ALLOFF = "ALLOFF"
ACTION_ALLAUTO = "ALLAUTO"
ACTION_LOCK = "LOCK"
ACTION_UNLOCK = "UNLOCK"

# Query and Target Parameters
QUERY_ALL = "ALL"
TARGET_PH = "pH"
TARGET_ORP = "ORP"
TARGET_MIN_CHLORINE = "MinChlorine"
KEY_MAINTENANCE = "MAINTENANCE"
KEY_PVSURPLUS = "PVSURPLUS"

# =============================================================================
# DEVICE PARAMETERS - Extended Configuration
# =============================================================================

DEVICE_PARAMETERS = {
    "PUMP": {
        "supports_speed": True,
        "supports_timer": True,
        "supports_force_off": True,
        "speeds": {1: "Eco (Niedrig)", 2: "Normal (Mittel)", 3: "Boost (Hoch)"},
        "default_on_speed": 2,
        "force_off_duration": 600,
        "activity_sensors": ["PUMP_RPM_1_VALUE", "PUMP_RUNTIME"],
        "activity_threshold": {"PUMP_RPM_1_VALUE": 100},
        "api_template": "PUMP,{action},{duration},{speed}",
    },
    "HEATER": {
        "supports_timer": True,
        "supports_temperature": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire5_value", "onewire1_value", "HEATER_RUNTIME"],
        "activity_threshold": {"temp_diff": 2.0},
        "api_template": "HEATER,{action},{duration},0",
    },
    "SOLAR": {
        "supports_timer": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire3_value", "onewire1_value", "SOLAR_RUNTIME"],
        "activity_threshold": {"temp_diff": 5.0},
        "api_template": "SOLAR,{action},{duration},0",
    },
    "LIGHT": {
        "supports_color_pulse": True,
        "color_pulse_duration": 150,
        "api_template": "LIGHT,{action},0,0",
        "color_pulse_template": "LIGHT,COLOR,0,0",
    },
    "DOS_1_CL": {
        "supports_timer": True,
        "dosing_type": "Chlor",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_1_CL_RUNTIME", "DOS_1_CL_STATE"],
        "api_template": "DOS_1_CL,{action},{duration},0",
    },
    "DOS_4_PHM": {
        "supports_timer": True,
        "dosing_type": "pH-",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_4_PHM_RUNTIME", "DOS_4_PHM_STATE"],
        "api_template": "DOS_4_PHM,{action},{duration},0",
    },
    "DOS_5_PHP": {
        "supports_timer": True,
        "dosing_type": "pH+",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_5_PHP_RUNTIME", "DOS_5_PHP_STATE"],
        "api_template": "DOS_5_PHP,{action},{duration},0",
    },
    "DOS_6_FLOC": {
        "supports_timer": True,
        "dosing_type": "Flockmittel",
        "default_dosing_duration": 60,
        "max_dosing_duration": 600,
        "safety_interval": 600,
        "activity_sensors": ["DOS_6_FLOC_RUNTIME"],
        "api_template": "DOS_6_FLOC,{action},{duration},0",
    },
    "BACKWASH": {
        "supports_timer": True,
        "default_duration": 180,
        "max_duration": 900,
        "activity_sensors": ["BACKWASH_RUNTIME", "BACKWASHSTATE"],
        "api_template": "BACKWASH,{action},{duration},0",
    },
    "BACKWASHRINSE": {
        "supports_timer": True,
        "default_duration": 60,
        "max_duration": 300,
        "activity_sensors": ["BACKWASH_RUNTIME"],
        "api_template": "BACKWASHRINSE,{action},{duration},0",
    },
    "PVSURPLUS": {  # ⭐ FIX: PVSURPLUS added
        "supports_speed": True,
        "speeds": {1: "Eco", 2: "Normal", 3: "Boost"},
        "default_speed": 2,
        "activity_sensors": ["PVSURPLUS"],
        "activity_threshold": {"PVSURPLUS": 1},
        "api_template": "PVSURPLUS,{action},{speed},0",
    },
}

# Extension relays with runtime sensors
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "default_on_duration": 3600,
            "max_duration": 86400,
            "activity_sensors": [f"EXT{ext_bank}_{relay_num}_RUNTIME"],
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0",
        }

# Digital Rules
for rule_num in range(1, 8):
    key = f"DIRULE_{rule_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_lock": True,
        "action_type": "PUSH",
        "pulse_duration": 500,
        "api_template": f"DIRULE_{rule_num},{{action}},0,0",
    }

# DMX Scenes
for scene_num in range(1, 13):
    key = f"DMX_SCENE{scene_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_group_control": True,
        "group_actions": ["ALLON", "ALLOFF", "ALLAUTO"],
        "api_template": f"DMX_SCENE{scene_num},{{action}},0,0",
    }

# =============================================================================
# SENSORS - Temperature, Chemistry, Analog, System
# =============================================================================

TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Solarabsorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
}

WATER_CHEM_SENSORS = {
    # IMPORTANT: pH sensor has NO unit per Home Assistant specification
    # This is intentional and correct behavior:
    # - pH Sensor (this): No unit - displays raw measurement value
    # - pH Number (setpoint): Has "pH" unit - for user input/setpoints
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": None},  # pH ohne unit
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}

ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Überlaufbehälter", "icon": "mdi:water-percent", "unit": "cm"},
    "ADC3_value": {"name": "Durchflussmesser (4-20mA)", "icon": "mdi:pump", "unit": "m³/h"},
    "ADC4_value": {"name": "Analogsensor 4 (4-20mA)", "icon": "mdi:gauge", "unit": None},
    "ADC5_value": {"name": "Analogsensor 5 (0-10V)", "icon": "mdi:gauge", "unit": "V"},
    "IMP1_value": {"name": "Flow-Switch", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Pumpen-Durchfluss", "icon": "mdi:pump", "unit": "m³/h"},
}

SYSTEM_SENSORS = {
    "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:chip", "unit": "°C"},
    "CPU_TEMP_CARRIER": {"name": "Carrier Board", "icon": "mdi:expansion-card", "unit": "°C"},
    "CPU_UPTIME": {"name": "System Uptime", "icon": "mdi:clock", "unit": None},
}

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
# RUNTIME AND TIMESTAMP SENSORS
# =============================================================================

RUNTIME_SENSORS = {
    "PUMP_RUNTIME": {"name": "Pumpe Laufzeit", "icon": "mdi:timer", "unit": None},
    "SOLAR_RUNTIME": {"name": "Solar Laufzeit", "icon": "mdi:timer", "unit": None},
    "HEATER_RUNTIME": {"name": "Heizung Laufzeit", "icon": "mdi:timer", "unit": None},
    "LIGHT_RUNTIME": {"name": "Beleuchtung Laufzeit", "icon": "mdi:timer", "unit": None},
    "BACKWASH_RUNTIME": {"name": "Rückspülung Laufzeit", "icon": "mdi:timer", "unit": None},
}

# Runtime for dosing
DOSING_RUNTIME_KEYS = [
    ("DOS_1_CL", "Chlor"),
    ("DOS_4_PHM", "pH-Minus"),
    ("DOS_5_PHP", "pH-Plus"),
    ("DOS_6_FLOC", "Flockmittel")
]
for dos_key, name in DOSING_RUNTIME_KEYS:
    RUNTIME_SENSORS[f"{dos_key}_RUNTIME"] = {
        "name": f"{name} Laufzeit", "icon": "mdi:timer", "unit": None
    }

# Runtime for extensions
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}_RUNTIME"
        RUNTIME_SENSORS[key] = {
            "name": f"Ext {ext_bank}.{relay_num} Laufzeit",
            "icon": "mdi:timer",
            "unit": None,
        }

TIMESTAMP_SENSORS = {
    "PUMP_LAST_ON": {"name": "Pumpe letzte Einschaltung"},
    "PUMP_LAST_OFF": {"name": "Pumpe letzte Ausschaltung"},
    "BACKWASH_LAST_AUTO_RUN": {"name": "Letzte automatische Rückspülung"},
    "BACKWASH_LAST_MANUAL_RUN": {"name": "Letzte manuelle Rückspülung"},
}

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

# =============================================================================
# UNIT MAPPINGS
# =============================================================================

UNIT_MAP = {
    # Temperature sensors
    "water_temp": "°C",
    "air_temp": "°C",
    "temp_value": "°C",
    "CPU_TEMP": "°C",
    "CPU_TEMP_CARRIER": "°C",
    # Water chemistry (pH WITHOUT unit!)
    "orp_value": "mV",
    "pot_value": "mg/l",
    # Analog values
    "ADC1_value": "bar",
    "ADC2_value": "cm",
    "ADC3_value": "m³/h",
    "ADC5_value": "V",
    "IMP1_value": "cm/s",
    "IMP2_value": "m³/h",
}

# Add OneWire temperatures
for i in range(1, 13):
    UNIT_MAP[f"onewire{i}_value"] = "°C"

# Add Pump RPMs
for i in range(4):
    UNIT_MAP[f"PUMP_RPM_{i}"] = "RPM"
    UNIT_MAP[f"PUMP_RPM_{i}_VALUE"] = "RPM"

# Sensors without units
NO_UNIT_SENSORS = {
    "FW", "SW_VERSION", "HW_VERSION", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS",
    "VERSION", "CPU_UPTIME", "BACKWASH_STATE", "PUMP_STATE", "HEATER_STATE",
    "SOLAR_STATE", "LIGHT_STATE", "time", "TIME", "CURRENT_TIME",
}

# =============================================================================
# FEATURE MAPPINGS
# =============================================================================

SENSOR_FEATURE_MAP = {
    # Temperature sensors
    "onewire1_value": None,  # Always show water temperature
    "onewire2_value": None,  # Always show air temperature
    "onewire3_value": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
    # Water chemistry
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    # System sensors
    "CPU_TEMP": None,
    "CPU_TEMP_CARRIER": None,
    "CPU_UPTIME": None,
}

# =============================================================================
# VALIDATION AND MONITORING
# =============================================================================

DEVICE_VALIDATION_RULES = {
    "PUMP": {
        "min_speed": 1,
        "max_speed": 3,
        "min_off_duration": 60,
        "max_off_duration": 3600,
        "rpm_thresholds": {"min_active": 100, "max_normal": 3000},
    },
    "HEATER": {
        "min_temp": 20.0,
        "max_temp": 40.0,
        "temp_step": 0.5,
        "max_temp_diff": 50.0,
    },
    "DOS_1_CL": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
    "DOS_4_PHM": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
    "DOS_5_PHP": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_device_state_info(raw_state: str, device_key: str = None) -> dict:
    """Get extended state information for a device."""
    if not raw_state:
        return {"mode": "auto", "active": False, "priority": 50, "desc": "Unknown"}

    upper_state = str(raw_state).upper().strip()

    if upper_state in DEVICE_STATE_MAPPING:
        return DEVICE_STATE_MAPPING[upper_state]

    return {"mode": "auto", "active": None, "priority": 10, "desc": f"Unknown state: {raw_state}"}


def legacy_is_on_state(raw_state: str) -> bool:
    """Legacy function for simple On/Off check."""
    if not raw_state:
        return False

    # Test integer values directly
    try:
        int_state = int(raw_state) if isinstance(raw_state, (int, float)) else int(str(raw_state))
        if int_state in STATE_MAP:
            return STATE_MAP[int_state]
    except (ValueError, TypeError):
        pass

    # Then string values
    upper_state = str(raw_state).upper().strip()
    if upper_state in STATE_MAP:
        return STATE_MAP[upper_state]

    # Fallback to extended state information
    state_info = get_device_state_info(raw_state)
    if state_info.get("active") is not None:
        return state_info.get("active")

    return False


def get_device_mode_from_state(raw_state: str, device_key: str = None) -> str:
    """Get device mode from raw state value."""
    state_info = get_device_state_info(raw_state, device_key)
    mode = state_info.get("mode", "auto")
    active = state_info.get("active")

    if mode == "manual":
        return "manual_on" if active else "manual_off"
    elif mode == "auto":
        return "auto_active" if active else "auto_inactive"
    else:
        return mode


def get_device_icon(device_key: str, mode: str) -> str:
    """Get appropriate icon for a device based on mode."""
    if device_key in STATE_ICONS:
        return STATE_ICONS[device_key].get(
            mode, STATE_ICONS[device_key].get("auto_inactive", "mdi:help")
        )

    fallback_icons = {
        "auto_active": "mdi:auto-mode",
        "auto_inactive": "mdi:auto-mode-outline",
        "manual_on": "mdi:power-on",
        "manual_off": "mdi:power-off",
        "error": "mdi:alert-circle",
        "maintenance": "mdi:wrench",
    }

    return fallback_icons.get(mode, "mdi:help")


def get_device_color(mode: str) -> str:
    """Get display color for a device mode."""
    return STATE_COLORS.get(mode, "#9E9E9E")


# =============================================================================
# VIOLET STATE CLASS
# =============================================================================


class VioletState:
    """Extended state class for 3-State support."""

    def __init__(self, raw_state: str, device_key: str = None):
        self.raw_state = str(raw_state).strip()
        self.device_key = device_key
        self._state_info = get_device_state_info(self.raw_state, device_key)

    @property
    def mode(self) -> str:
        """Device mode: auto, manual, error, maintenance."""
        return self._state_info.get("mode", "auto")

    @property
    def is_active(self) -> bool:
        """Is the device active? None = depends on external factors."""
        return self._state_info.get("active")

    @property
    def priority(self) -> int:
        """Display priority for UI sorting."""
        return self._state_info.get("priority", 50)

    @property
    def description(self) -> str:
        """Human-readable description of the state."""
        return self._state_info.get("desc", f"State: {self.raw_state}")

    @property
    def display_mode(self) -> str:
        """Display name for UI."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return STATE_TRANSLATIONS.get("de", {}).get(mode_key, mode_key)

    @property
    def icon(self) -> str:
        """Appropriate icon for current state."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_icon(self.device_key, mode_key)

    @property
    def color(self) -> str:
        """Display color for current state."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_color(mode_key)

    def is_manual_mode(self) -> bool:
        """Is the device in manual mode?"""
        return self.mode == "manual"

    def is_auto_mode(self) -> bool:
        """Is the device in automatic mode?"""
        return self.mode == "auto"

    def is_error_state(self) -> bool:
        """Is the device in an error state?"""
        return self.mode in ["error", "maintenance"]

    def __str__(self) -> str:
        return f"VioletState({self.device_key}): {self.display_mode} ({self.raw_state})"

    def __repr__(self) -> str:
        return (
            f"VioletState(raw_state='{self.raw_state}', "
            f"device_key='{self.device_key}', mode='{self.mode}', "
            f"active={self.is_active})"
        )


# =============================================================================
# VERSION INFO AND EXPORTS
# =============================================================================

VERSION_INFO = {
    "version": INTEGRATION_VERSION,
    "release_date": "2025-11-20",
    "major_features": [
        "Complete 3-State Switch Support with State 4 Fix",
        "PVSURPLUS Parameter Support",
        "Cover String-State Handling",
        "Extended Sensor Coverage (147 API Parameters)",
        "Enhanced DMX Scene Control (12 Scenes)",
        "Complete Extension Relay Support (EXT1/EXT2)",
        "Semantic Versioning Adoption (SemVer 2.0.0)",
    ],
    "critical_fixes": [
        "STATE_MAP now includes State 4 (Manual Forced ON)",
        "PVSURPLUS added to SWITCH_FUNCTIONS",
        "COVER_STATE_MAP supports string states",
        "Migrated to clean Semantic Versioning",
    ],
}

# Main exports
__all__ = [
    # Core
    "DOMAIN",
    "INTEGRATION_VERSION",
    "MANUFACTURER",
    # Configuration
    "CONF_API_URL",
    "CONF_USERNAME",
    "CONF_PASSWORD",
    "CONF_ACTIVE_FEATURES",
    "CONF_SELECTED_SENSORS",
    "DEFAULT_POLLING_INTERVAL",
    "DEFAULT_TIMEOUT_DURATION",
    # API
    "API_READINGS",
    "API_SET_FUNCTION_MANUALLY",
    "API_GET_HISTORY",
    "API_GET_WEATHER_DATA",
    "API_GET_OVERALL_DOSING",
    "API_GET_OUTPUT_STATES",
    "ACTION_ON",
    "ACTION_OFF",
    "ACTION_AUTO",
    # State Support
    "DEVICE_STATE_MAPPING",
    "STATE_MAP",
    "COVER_STATE_MAP",
    "STATE_ICONS",
    "STATE_COLORS",
    "get_device_state_info",
    "get_device_mode_from_state",
    "VioletState",
    "legacy_is_on_state",
    # Devices
    "DEVICE_PARAMETERS",
    "SWITCHES",
    "BINARY_SENSORS",
    "SWITCH_FUNCTIONS",
    "AVAILABLE_FEATURES",
    # Sensors
    "TEMP_SENSORS",
    "WATER_CHEM_SENSORS",
    "ANALOG_SENSORS",
    "SYSTEM_SENSORS",
    "RUNTIME_SENSORS",
    "TIMESTAMP_SENSORS",
    # Utilities
    "UNIT_MAP",
    "NO_UNIT_SENSORS",
    "SENSOR_FEATURE_MAP",
    # Version
    "VERSION_INFO",
]
