"""Konstanten für die Violet Pool Controller Integration."""
from homeassistant.components.number import NumberDeviceClass
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
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch", "binary_sensor"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False, "platforms": ["binary_sensor"]},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False, "platforms": ["switch"]},
]

# API-Schlüssel
SWITCH_FUNCTIONS = {
    "PUMP": "Pumpe", "SOLAR": "Absorber", "HEATER": "Heizung", "LIGHT": "Licht",
    "ECO": "Eco-Modus", "BACKWASH": "Rückspülung", "BACKWASHRINSE": "Nachspülung",
    **{f"EXT1_{i}": f"Relais 1-{i}" for i in range(1, 9)},
    **{f"EXT2_{i}": f"Relais 2-{i}" for i in range(1, 9)},
    **{f"DMX_SCENE{i}": f"DMX Szene {i}" for i in range(1, 13)},
    "REFILL": "Nachfüllen",
    **{f"DIRULE_{i}": f"Schaltregel {i}" for i in range(1, 8)},
    "PVSURPLUS": "PV-Überschuss",
    **{f"OMNI_DC{i}": f"Omni DC{i}" for i in range(6)},
}

COVER_FUNCTIONS = {
    "OPEN": "COVER_OPEN", "CLOSE": "COVER_CLOSE", "STOP": "COVER_STOP",
}

DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM", "pH+": "DOS_5_PHP", "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO", "Flockmittel": "DOS_6_FLOC",
}

# Zustandsmapping
STATE_MAP = {
    **{i: bool(i in {1, 3, 4}) for i in range(7)},
    **{str(i): bool(i in {"1", "3", "4"}) for i in range(7)},
    "ON": True, "OFF": False, "AUTO": False, "TRUE": True, "FALSE": False,
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

# Binary Sensoren
BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump", "feature_id": "filter_control"},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power", "feature_id": "solar"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator", "feature_id": "heating"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb", "feature_id": "led_lighting"},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:valve", "feature_id": "backwash"},
    {"name": "Refill State", "key": "REFILL", "icon": "mdi:water", "feature_id": "water_refill"},
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"},
    *[{"name": f"Digital Input {i}", "key": f"INPUT{i}", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"} for i in range(1, 13)],
    {"name": "Digital Input Z1Z2", "key": "INPUTz1z2", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    *[{"name": f"Digital Input CE{i}", "key": f"INPUT_CE{i}", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"} for i in range(1, 5)],
    {"name": "Cover Open Contact", "key": "OPEN_CONTACT", "icon": "mdi:window-open-variant", "feature_id": "cover_control"},
    {"name": "Cover Stop Contact", "key": "STOP_CONTACT", "icon": "mdi:stop-circle-outline", "feature_id": "cover_control"},
    {"name": "Cover Close Contact", "key": "CLOSE_CONTACT", "icon": "mdi:window-closed-variant", "feature_id": "cover_control"},
]

# Switches
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
    *[{"name": f"Extension 1.{i}", "key": f"EXT1_{i}", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"} for i in range(1, 9)],
    *[{"name": f"Extension 2.{i}", "key": f"EXT2_{i}", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"} for i in range(1, 9)],
    *[{"name": f"Omni DC{i} Output", "key": f"OMNI_DC{i}", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"} for i in range(6)],
]

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
