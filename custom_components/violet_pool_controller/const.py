"""Konstanten für die Violet Pool Controller Integration."""
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

# Integration
DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "0.1.0.1"
MANUFACTURER = "PoolDigital GmbH & Co. KG"
LOGGER_NAME = f"{DOMAIN}_logger"

# Konfigurationsschlüssel
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
CONF_POOL_SIZE = "pool_size"
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"

# Standardwerte
DEFAULT_POLLING_INTERVAL = 10  # Sekunden
DEFAULT_TIMEOUT_DURATION = 10  # Sekunden
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_USE_SSL = False
DEFAULT_DEVICE_NAME = "Violet Pool Controller"
DEFAULT_POOL_SIZE = 50  # m³
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

# API-Endpunkte
API_READINGS = "/getReadings"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"
API_SET_DOSING_PARAMETERS = "/setDosingParameters"
API_SET_TARGET_VALUES = "/setTargetValues"

# Optionen
POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# Verfügbare Features
AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heizung", "default": True, "platforms": ["climate"]},
    {"id": "solar", "name": "Solarabsorber", "default": True, "platforms": ["climate"]},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True, "platforms": ["cover"]},
    {"id": "backwash", "name": "Rückspülung", "default": True, "platforms": ["switch"]},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True, "platforms": ["switch"]},
    {"id": "filter_control", "name": "Filterpumpe", "default": True, "platforms": ["switch", "binary_sensor"]},
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch", "binary_sensor"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False, "platforms": ["binary_sensor"]},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False, "platforms": ["switch"]},
]

# API-Schlüssel
# API-Schlüssel - Python 3.13 kompatibel
_EXT1_RELAYS = {f"EXT1_{i}": f"Relais 1-{i}" for i in range(1, 9)}
_EXT2_RELAYS = {f"EXT2_{i}": f"Relais 2-{i}" for i in range(1, 9)}
_DMX_SCENES = {f"DMX_SCENE{i}": f"DMX Szene {i}" for i in range(1, 13)}
_DIRULES = {f"DIRULE_{i}": f"Schaltregel {i}" for i in range(1, 8)}
_OMNI_DCS = {f"OMNI_DC{i}": f"Omni DC{i}" for i in range(6)}

SWITCH_FUNCTIONS = {
    "PUMP": "Pumpe", 
    "SOLAR": "Absorber", 
    "HEATER": "Heizung", 
    "LIGHT": "Licht",
    "ECO": "Eco-Modus", 
    "BACKWASH": "Rückspülung", 
    "BACKWASHRINSE": "Nachspülung",
    "REFILL": "Nachfüllen",
    "PVSURPLUS": "PV-Überschuss",
}

# Add generated mappings
SWITCH_FUNCTIONS.update(_EXT1_RELAYS)
SWITCH_FUNCTIONS.update(_EXT2_RELAYS) 
SWITCH_FUNCTIONS.update(_DMX_SCENES)
SWITCH_FUNCTIONS.update(_DIRULES)
SWITCH_FUNCTIONS.update(_OMNI_DCS)

COVER_FUNCTIONS = {
    "OPEN": "COVER_OPEN", "CLOSE": "COVER_CLOSE", "STOP": "COVER_STOP",
}

DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM", "pH+": "DOS_5_PHP", "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO", "Flockmittel": "DOS_6_FLOC",
}

# Zustandsmapping
STATE_MAP = {
    # Numeric states
    **{i: bool(i in {1, 3, 4}) for i in range(7)},
    **{str(i): bool(i in {"1", "3", "4"}) for i in range(7)},
    # String states
    "ON": True, "OFF": False, "AUTO": False, "TRUE": True, "FALSE": False,
    "OPEN": True, "CLOSED": False, "OPENING": True, "CLOSING": True, "STOPPED": False,
}

# Sensoren
TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Absorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
}

WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": "pH"},
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}

ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Füllstand", "icon": "mdi:water-percent", "unit": "cm"},
    "IMP1_value": {"name": "Messwasser-Durchfluss", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Förderleistung", "icon": "mdi:pump", "unit": "m³/h"},
}

# Binary Sensoren - Dictionary Format für einfachere Verwendung
_DIGITAL_INPUTS = [{"name": f"Digital Input {i}", "key": f"INPUT{i}", "icon": "mdi:electric-switch", "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC} for i in range(1, 13)]
_DIGITAL_CE_INPUTS = [{"name": f"Digital Input CE{i}", "key": f"INPUT_CE{i}", "icon": "mdi:electric-switch", "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC} for i in range(1, 5)]

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump", "feature_id": "filter_control", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power", "feature_id": "solar", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator", "feature_id": "heating", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb", "feature_id": "led_lighting"},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:valve", "feature_id": "backwash", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "Refill State", "key": "REFILL", "icon": "mdi:water", "feature_id": "water_refill", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "PV Surplus", "key": "PVSURPLUS", "icon": "mdi:solar-power-variant", "feature_id": "pv_surplus"},
    {"name": "Digital Input Z1Z2", "key": "INPUTz1z2", "icon": "mdi:electric-switch", "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC},
    # Cover Controls
    {"name": "Cover Open Contact", "key": "OPEN_CONTACT", "icon": "mdi:window-open-variant", "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
    {"name": "Cover Stop Contact", "key": "STOP_CONTACT", "icon": "mdi:stop-circle-outline", "feature_id": "cover_control"},
    {"name": "Cover Close Contact", "key": "CLOSE_CONTACT", "icon": "mdi:window-closed-variant", "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
]

# Add generated digital inputs
BINARY_SENSORS.extend(_DIGITAL_INPUTS)
BINARY_SENSORS.extend(_DIGITAL_CE_INPUTS)

# Switches - Python 3.13 kompatibel
_EXT1_SWITCHES = [{"name": f"Extension 1.{i}", "key": f"EXT1_{i}", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"} for i in range(1, 9)]
_EXT2_SWITCHES = [{"name": f"Extension 2.{i}", "key": f"EXT2_{i}", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"} for i in range(1, 9)]
_OMNI_SWITCHES = [{"name": f"Omni DC{i} Output", "key": f"OMNI_DC{i}", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"} for i in range(6)]

SWITCHES = [
    {"name": "Pumpe", "key": "PUMP", "icon": "mdi:water-pump", "feature_id": "filter_control"},
    {"name": "Absorber", "key": "SOLAR", "icon": "mdi:solar-power", "feature_id": "solar"},
    {"name": "Heizung", "key": "HEATER", "icon": "mdi:radiator", "feature_id": "heating"},
    {"name": "Licht", "key": "LIGHT", "icon": "mdi:lightbulb", "feature_id": "led_lighting"},
    {"name": "Dosierung Chlor", "key": "DOS_1_CL", "icon": "mdi:flask", "feature_id": "chlorine_control"},
    {"name": "Dosierung pH-", "key": "DOS_4_PHM", "icon": "mdi:flask", "feature_id": "ph_control"},
    {"name": "Eco-Modus", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Rückspülung", "key": "BACKWASH", "icon": "mdi:valve", "feature_id": "backwash"},
    {"name": "Nachspülung", "key": "BACKWASHRINSE", "icon": "mdi:water-sync", "feature_id": "backwash"},
    {"name": "Dosierung pH+", "key": "DOS_5_PHP", "icon": "mdi:flask", "feature_id": "ph_control"},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask", "feature_id": "chlorine_control"},
    {"name": "PV-Überschuss", "key": "PVSURPLUS", "icon": "mdi:solar-power-variant", "feature_id": "pv_surplus"},
]

# Add generated switches
SWITCHES.extend(_EXT1_SWITCHES)
SWITCHES.extend(_EXT2_SWITCHES)
SWITCHES.extend(_OMNI_SWITCHES)

# Setpoint-Definitionen
SETPOINT_DEFINITIONS = [
    {
        "key": "ph_setpoint", "name": "pH Sollwert", "min_value": 6.8, "max_value": 7.8, "step": 0.1,
        "icon": "mdi:flask", "api_key": "pH", "feature_id": "ph_control", "unit_of_measurement": "pH",
        "device_class": NumberDeviceClass.PH, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_TARGET", "TARGET_PH"],
        "indicator_fields": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"], "default_value": 7.2
    },
    {
        "key": "orp_setpoint", "name": "Redox Sollwert", "min_value": 600, "max_value": 800, "step": 10,
        "icon": "mdi:flash", "api_key": "ORP", "feature_id": "chlorine_control", "unit_of_measurement": "mV",
        "device_class": None, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["ORP_SETPOINT", "ORP_TARGET", "TARGET_ORP"],
        "indicator_fields": ["orp_value"], "default_value": 700
    },
    {
        "key": "chlorine_setpoint", "name": "Chlor Sollwert", "min_value": 0.2, "max_value": 2.0, "step": 0.1,
        "icon": "mdi:test-tube", "api_key": "MinChlorine", "feature_id": "chlorine_control", "unit_of_measurement": "mg/l",
        "device_class": None, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["CHLORINE_SETPOINT", "MIN_CHLORINE", "TARGET_MIN_CHLORINE"],
        "indicator_fields": ["pot_value", "DOS_1_CL"], "default_value": 0.6
    },
]

# Unit mappings für dynamische Sensoren - Kompatibel mit Python 3.13
_ONEWIRE_TEMPS = {f"onewire{i}_value": "°C" for i in range(1, 13)}
_PUMP_RPMS = {f"PUMP_RPM_{i}": "RPM" for i in range(4)}
_PUMP_RPM_VALUES = {f"PUMP_RPM_{i}_VALUE": "RPM" for i in range(4)}

UNIT_MAP = {
    # Temperature sensors
    "water_temp": "°C", 
    "air_temp": "°C", 
    "temp_value": "°C",
    "SYSTEM_cpu_temperature": "°C", 
    "SYSTEM_carrier_cpu_temperature": "°C",
    # Water chemistry
    "pH_value": "pH", 
    "orp_value": "mV", 
    "pot_value": "mg/l",
    # Analog values
    "ADC1_value": "bar", 
    "ADC2_value": "cm", 
    "IMP1_value": "cm/s", 
    "IMP2_value": "m³/h",
    # System values
    "CPU_UPTIME": "s", 
    "DEVICE_UPTIME": "s", 
    "RUNTIME": "s",
}

# Add generated mappings
UNIT_MAP.update(_ONEWIRE_TEMPS)
UNIT_MAP.update(_PUMP_RPMS)
UNIT_MAP.update(_PUMP_RPM_VALUES)

# Sensors without units
_DOS_CL_STATES = {f"DOS_{i}_CL_STATE" for i in range(1, 7)}
_DOS_PHM_STATES = {f"DOS_{i}_PHM_STATE" for i in range(1, 7)}
_DOS_PHP_STATES = {f"DOS_{i}_PHP_STATE" for i in range(1, 7)}
_DOS_CL_RANGES = {f"DOS_{i}_CL_REMAINING_RANGE" for i in range(1, 7)}
_DOS_PHM_RANGES = {f"DOS_{i}_PHM_REMAINING_RANGE" for i in range(1, 7)}
_DOS_PHP_RANGES = {f"DOS_{i}_PHP_REMAINING_RANGE" for i in range(1, 7)}
_DOS_FLOC_RANGES = {f"DOS_{i}_FLOC_REMAINING_RANGE" for i in range(1, 7)}

NO_UNIT_SENSORS = {
    "FW", "SW_VERSION", "HW_VERSION", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS",
    "VERSION", "VERSION_INFO", "HARDWARE_VERSION", "CPU_GOV", "HW_SERIAL_CARRIER",
    "SW_VERSION_CARRIER", "HW_VERSION_CARRIER", "ERROR_CODE", "LAST_ERROR",
    "CHECKSUM", "RULE_RESULT", "DISPLAY_MODE", "OPERATING_MODE", "MAINTENANCE_MODE",
    "HEATERSTATE", "SOLARSTATE", "PUMPSTATE", "BACKWASHSTATE", "OMNI_STATE",
    "BACKWASH_OMNI_STATE", "SOLAR_STATE", "HEATER_STATE", "PUMP_STATE", "FILTER_STATE",
    "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE", "HEATER_MODE", "LAST_MOVING_DIRECTION",
    "COVER_DIRECTION", "BATHING_AI_SURVEILLANCE_STATE", "BATHING_AI_PUMP_STATE",
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", "BACKWASH_STATE", "REFILL_STATE",
    "time", "TIME", "CURRENT_TIME"
} | _DOS_CL_STATES | _DOS_PHM_STATES | _DOS_PHP_STATES | _DOS_CL_RANGES | _DOS_PHM_RANGES | _DOS_PHP_RANGES | _DOS_FLOC_RANGES

# Sensor feature mapping erweitert - Python 3.13 kompatibel
_DOS_CL_FEATURE_MAP = {f"DOS_{i}_CL_STATE": "chlorine_control" for i in range(1, 7)}
_DOS_PHM_FEATURE_MAP = {f"DOS_{i}_PHM_STATE": "ph_control" for i in range(1, 7)}
_DOS_PHP_FEATURE_MAP = {f"DOS_{i}_PHP_STATE": "ph_control" for i in range(1, 7)}
_DOS_CL_RUNTIME_MAP = {f"DOS_{i}_CL_RUNTIME": "chlorine_control" for i in range(1, 7)}
_DOS_PHM_RUNTIME_MAP = {f"DOS_{i}_PHM_RUNTIME": "ph_control" for i in range(1, 7)}
_DOS_PHP_RUNTIME_MAP = {f"DOS_{i}_PHP_RUNTIME": "ph_control" for i in range(1, 7)}
_EXT1_RUNTIME_MAP = {f"EXT1_{i}_RUNTIME": "extension_outputs" for i in range(1, 9)}
_EXT2_RUNTIME_MAP = {f"EXT2_{i}_RUNTIME": "extension_outputs" for i in range(1, 9)}
_OMNI_RUNTIME_MAP = {f"OMNI_DC{i}_RUNTIME": "extension_outputs" for i in range(1, 6)}

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
    # Analog sensors
    "ADC1_value": "filter_control",
    "ADC2_value": "water_level",
    "IMP1_value": "filter_control",
    "IMP2_value": "filter_control",
    # Runtime sensors
    "PUMP_RUNTIME": "filter_control",
    "SOLAR_RUNTIME": "solar",
    "HEATER_RUNTIME": "heating",
    "LIGHT_RUNTIME": "led_lighting",
    "BACKWASH_RUNTIME": "backwash",
}

# Add generated mappings
SENSOR_FEATURE_MAP.update(_DOS_CL_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHM_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHP_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_CL_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHM_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHP_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_EXT1_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_EXT2_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_OMNI_RUNTIME_MAP)

# API-Aktionen
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
QUERY_ALL = "ALL"
TARGET_PH = "pH"
TARGET_ORP = "ORP"
TARGET_MIN_CHLORINE = "MinChlorine"
KEY_MAINTENANCE = "MAINTENANCE"
KEY_PVSURPLUS = "PVSURPLUS"
