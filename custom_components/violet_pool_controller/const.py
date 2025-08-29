"""Erweiterte Konstanten für die Violet Pool Controller Integration - 3-STATE SUPPORT."""
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

# Integration
DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "0.2.0.0"  # Updated for 3-state support
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

# Pool-Typen und Desinfektionsmethoden
POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# ═══════════════════════════════════════════════════════════════════════════════
# 3-STATE SUPPORT - ERWEITERTE ZUSTANDSMAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Basierend auf API-Dokumentation Kapitel 26.2.1: Filterpumpe States 0-6
DEVICE_STATE_MAPPING = {
    # String-basierte Zustände (häufigste Form)
    "ON": {"mode": "manual", "active": True, "priority": 80},
    "OFF": {"mode": "manual", "active": False, "priority": 70},
    "AUTO": {"mode": "auto", "active": None, "priority": 60},  # None = abhängig von Bedingungen
    "MAN": {"mode": "manual", "active": True, "priority": 80},
    "MANUAL": {"mode": "manual", "active": True, "priority": 80},
    
    # Numerische Zustände (wie in API-Doku beschrieben)
    "0": {"mode": "auto", "active": False, "priority": 50, "desc": "AUTO - Standby"},
    "1": {"mode": "manual", "active": True, "priority": 80, "desc": "Manuell EIN"},
    "2": {"mode": "auto", "active": True, "priority": 60, "desc": "AUTO - Aktiv"},
    "3": {"mode": "auto", "active": True, "priority": 65, "desc": "AUTO - Aktiv (Zeitsteuerung)"},
    "4": {"mode": "manual", "active": True, "priority": 85, "desc": "Manuell EIN (forciert)"},
    "5": {"mode": "auto", "active": False, "priority": 55, "desc": "AUTO - Wartend"},
    "6": {"mode": "manual", "active": False, "priority": 70, "desc": "Manuell AUS"},
    
    # Zusätzliche Zustände
    "STOPPED": {"mode": "manual", "active": False, "priority": 75},
    "ERROR": {"mode": "error", "active": False, "priority": 100},
    "MAINTENANCE": {"mode": "maintenance", "active": False, "priority": 90},
}

# Gerätespezifische Parameter basierend auf API-Dokumentation
DEVICE_PARAMETERS = {
    "PUMP": {
        "supports_speed": True,
        "supports_timer": True,
        "supports_force_off": True,
        "speeds": {1: "Eco (Niedrig)", 2: "Normal (Mittel)", 3: "Boost (Hoch)"},
        "default_on_speed": 2,
        "force_off_duration": 600,  # 10 Minuten wie in Doku
        "activity_sensors": ["PUMP_RPM_1_VALUE", "PUMP_RUNTIME"],
        "activity_threshold": {"PUMP_RPM_1_VALUE": 100},  # Minimum RPM für "aktiv"
        "api_template": "PUMP,{action},{duration},{speed}"
    },
    "HEATER": {
        "supports_timer": True,
        "supports_temperature": True,
        "default_on_duration": 0,  # Permanent
        "activity_sensors": ["onewire5_value", "onewire1_value", "HEATER_RUNTIME"],
        "activity_threshold": {"temp_diff": 2.0},  # 2°C Differenz = aktiv
        "api_template": "HEATER,{action},{duration},0"
    },
    "SOLAR": {
        "supports_timer": True,
        "default_on_duration": 0,  # Permanent
        "activity_sensors": ["onewire3_value", "onewire1_value", "SOLAR_RUNTIME"],
        "activity_threshold": {"temp_diff": 5.0},  # 5°C Differenz = aktiv
        "api_template": "SOLAR,{action},{duration},0"
    },
    "LIGHT": {
        "supports_color_pulse": True,
        "color_pulse_duration": 150,  # 150ms wie in Doku
        "api_template": "LIGHT,{action},0,0",
        "color_pulse_template": "LIGHT,COLOR,0,0"
    },
    "DOS_1_CL": {
        "supports_timer": True,
        "dosing_type": "Chlor",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,  # 5 Minuten Pause zwischen Dosierungen
        "activity_sensors": ["DOS_1_CL_RUNTIME", "DOS_1_CL_STATE"],
        "api_template": "DOS_1_CL,{action},{duration},0"
    },
    "DOS_4_PHM": {
        "supports_timer": True,
        "dosing_type": "pH-",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_4_PHM_RUNTIME", "DOS_4_PHM_STATE"],
        "api_template": "DOS_4_PHM,{action},{duration},0"
    },
    "DOS_5_PHP": {
        "supports_timer": True,
        "dosing_type": "pH+",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_5_PHP_RUNTIME", "DOS_5_PHP_STATE"],
        "api_template": "DOS_5_PHP,{action},{duration},0"
    },
    "DOS_6_FLOC": {
        "supports_timer": True,
        "dosing_type": "Flockmittel",
        "default_dosing_duration": 60,
        "max_dosing_duration": 600,
        "safety_interval": 600,
        "activity_sensors": ["DOS_6_FLOC_RUNTIME"],
        "api_template": "DOS_6_FLOC,{action},{duration},0"
    },
    "BACKWASH": {
        "supports_timer": True,
        "default_duration": 180,  # 3 Minuten Standard-Rückspülung
        "max_duration": 900,
        "activity_sensors": ["BACKWASH_RUNTIME", "BACKWASHSTATE"],
        "api_template": "BACKWASH,{action},{duration},0"
    },
    "BACKWASHRINSE": {
        "supports_timer": True,
        "default_duration": 60,  # 1 Minute Standard-Nachspülung
        "max_duration": 300,
        "activity_sensors": ["BACKWASH_RUNTIME"],
        "api_template": "BACKWASHRINSE,{action},{duration},0"
    },
}

# Erweiterungsrelais: EXT1_1 bis EXT1_8, EXT2_1 bis EXT2_8
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "default_on_duration": 3600,  # 1 Stunde wie in Doku
            "max_duration": 86400,
            "activity_sensors": [f"EXT{ext_bank}_{relay_num}_RUNTIME"],
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0"
        }

# Digital Rules: DIRULE_1 bis DIRULE_7
for rule_num in range(1, 8):
    key = f"DIRULE_{rule_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_lock": True,
        "action_type": "PUSH",
        "pulse_duration": 500,  # 500ms wie in Doku
        "api_template": f"DIRULE_{rule_num},{{action}},0,0"
    }

# DMX Scenes: DMX_SCENE1 bis DMX_SCENE12
for scene_num in range(1, 13):
    key = f"DMX_SCENE{scene_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_group_control": True,
        "group_actions": ["ALLON", "ALLOFF", "ALLAUTO"],
        "api_template": f"DMX_SCENE{scene_num},{{action}},0,0"
    }

# PV-Überschuss (Kapitel 26.3)
DEVICE_PARAMETERS["PVSURPLUS"] = {
    "supports_speed": True,
    "speeds": {1: "Eco", 2: "Normal", 3: "Boost"},
    "default_speed": 2,
    "api_template": "PVSURPLUS,{action},{speed},0"
}

# ═══════════════════════════════════════════════════════════════════════════════
# ERWEITERTE ICON-MAPPINGS FÜR 3-STATE VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

STATE_ICONS = {
    "PUMP": {
        "auto_active": "mdi:water-pump",
        "auto_inactive": "mdi:water-pump-off",
        "manual_on": "mdi:water-pump",
        "manual_off": "mdi:water-pump-off",
        "error": "mdi:water-pump-alert",
        "maintenance": "mdi:water-pump-wrench"
    },
    "HEATER": {
        "auto_active": "mdi:radiator",
        "auto_inactive": "mdi:radiator-disabled",
        "manual_on": "mdi:radiator",
        "manual_off": "mdi:radiator-off",
        "error": "mdi:radiator-alert",
        "maintenance": "mdi:radiator-wrench"
    },
    "SOLAR": {
        "auto_active": "mdi:solar-power",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power",
        "manual_off": "mdi:solar-power-off",
        "error": "mdi:solar-power-alert"
    },
    "LIGHT": {
        "auto_active": "mdi:lightbulb-on",
        "auto_inactive": "mdi:lightbulb-auto",
        "manual_on": "mdi:lightbulb-on",
        "manual_off": "mdi:lightbulb-off",
        "color_pulse": "mdi:lightbulb-multiple"
    },
    "DOS_1_CL": {
        "auto_active": "mdi:flask",
        "auto_inactive": "mdi:flask-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off"
    },
    "DOS_4_PHM": {
        "auto_active": "mdi:flask-minus",
        "auto_inactive": "mdi:flask-minus-outline",
        "manual_on": "mdi:flask-minus",
        "manual_off": "mdi:flask-off"
    },
    "DOS_5_PHP": {
        "auto_active": "mdi:flask-plus",
        "auto_inactive": "mdi:flask-plus-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off"
    },
    "BACKWASH": {
        "auto_active": "mdi:valve-open",
        "auto_inactive": "mdi:valve",
        "manual_on": "mdi:valve-open",
        "manual_off": "mdi:valve-closed"
    },
    "PVSURPLUS": {
        "auto_active": "mdi:solar-power-variant",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power-variant",
        "manual_off": "mdi:solar-power-variant-outline"
    }
}

# Farb-Codes für UI-Anzeige
STATE_COLORS = {
    "auto_active": "#4CAF50",     # Grün - Automatik aktiv
    "auto_inactive": "#2196F3",   # Blau - Automatik bereit
    "manual_on": "#FF9800",       # Orange - Manuell ein
    "manual_off": "#F44336",      # Rot - Manuell/Forciert aus
    "error": "#9C27B0",           # Lila - Fehler
    "maintenance": "#607D8B"      # Grau - Wartung
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERFÜGBARE FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heizung", "default": True, "platforms": ["climate", "switch", "binary_sensor"]},
    {"id": "solar", "name": "Solarabsorber", "default": True, "platforms": ["climate", "switch", "binary_sensor"]},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True, "platforms": ["number", "sensor", "switch"]},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True, "platforms": ["number", "sensor", "switch"]},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True, "platforms": ["cover", "binary_sensor"]},
    {"id": "backwash", "name": "Rückspülung", "default": True, "platforms": ["switch", "binary_sensor"]},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True, "platforms": ["switch", "binary_sensor"]},
    {"id": "filter_control", "name": "Filterpumpe", "default": True, "platforms": ["switch", "binary_sensor", "sensor"]},
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch", "binary_sensor"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False, "platforms": ["binary_sensor", "switch"]},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False, "platforms": ["switch"]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# API-SCHLÜSSEL UND FUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════════════

# Dynamische Generierung von Mappings (Python 3.13 kompatibel)
_EXT1_RELAYS = {f"EXT1_{i}": f"Relais 1-{i}" for i in range(1, 9)}
_EXT2_RELAYS = {f"EXT2_{i}": f"Relais 2-{i}" for i in range(1, 9)}
_DMX_SCENES = {f"DMX_SCENE{i}": f"DMX Szene {i}" for i in range(1, 13)}
_DIRULES = {f"DIRULE_{i}": f"Schaltregel {i}" for i in range(1, 8)}
_OMNI_DCS = {f"OMNI_DC{i}": f"Omni DC{i}" for i in range(6)}

SWITCH_FUNCTIONS = {
    "PUMP": "Filterpumpe",
    "SOLAR": "Solarabsorber",
    "HEATER": "Heizung",
    "LIGHT": "Beleuchtung",
    "ECO": "Eco-Modus",
    "BACKWASH": "Rückspülung",
    "BACKWASHRINSE": "Nachspülung",
    "REFILL": "Wassernachfüllung",
    "PVSURPLUS": "PV-Überschuss",
}

# Generierte Mappings hinzufügen
SWITCH_FUNCTIONS.update(_EXT1_RELAYS)
SWITCH_FUNCTIONS.update(_EXT2_RELAYS)
SWITCH_FUNCTIONS.update(_DMX_SCENES)
SWITCH_FUNCTIONS.update(_DIRULES)
SWITCH_FUNCTIONS.update(_OMNI_DCS)

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

# ═══════════════════════════════════════════════════════════════════════════════
# ERWEITERTE ZUSTANDSMAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Legacy State Map (für Rückwärtskompatibilität)
STATE_MAP = {
    # Numeric states
    **{i: bool(i in {1, 3, 4}) for i in range(7)},
    **{str(i): bool(i in {"1", "3", "4"}) for i in range(7)},
    # String states
    "ON": True, "OFF": False, "AUTO": False, "TRUE": True, "FALSE": False,
    "OPEN": True, "CLOSED": False, "OPENING": True, "CLOSING": True, "STOPPED": False,
}

# Erweiterte State-to-Mode Mappings für 3-State-Unterstützung
def get_device_state_info(raw_state: str, device_key: str = None) -> dict:
    """
    Ermittle erweiterte Zustandsinformationen für ein Gerät.
    
    Args:
        raw_state: Roher Zustandswert aus API
        device_key: Geräteschlüssel für spezifische Behandlung
        
    Returns:
        Dict mit mode, active, priority, description
    """
    if not raw_state:
        return {"mode": "auto", "active": False, "priority": 50, "desc": "Unknown"}
        
    upper_state = str(raw_state).upper().strip()
    
    # Prüfe Device-State-Mapping
    if upper_state in DEVICE_STATE_MAPPING:
        return DEVICE_STATE_MAPPING[upper_state]
    
    # Fallback für unbekannte Zustände
    return {"mode": "auto", "active": None, "priority": 10, "desc": f"Unknown state: {raw_state}"}

# ═══════════════════════════════════════════════════════════════════════════════
# SENSOREN
# ═══════════════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════════════
# BINARY SENSOREN MIT 3-STATE UNTERSTÜTZUNG
# ═══════════════════════════════════════════════════════════════════════════════

_DIGITAL_INPUTS = [
    {"name": f"Digital Input {i}", "key": f"INPUT{i}", "icon": "mdi:electric-switch", 
     "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC} 
    for i in range(1, 13)
]
_DIGITAL_CE_INPUTS = [
    {"name": f"Digital Input CE{i}", "key": f"INPUT_CE{i}", "icon": "mdi:electric-switch",
     "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC}
    for i in range(1, 5)
]

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump", 
     "feature_id": "filter_control", "device_class": BinarySensorDeviceClass.RUNNING,
     "supports_3_state": True},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power", 
     "feature_id": "solar", "device_class": BinarySensorDeviceClass.RUNNING,
     "supports_3_state": True},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator", 
     "feature_id": "heating", "device_class": BinarySensorDeviceClass.RUNNING,
     "supports_3_state": True},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb", 
     "feature_id": "led_lighting", "supports_3_state": True},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:valve", 
     "feature_id": "backwash", "device_class": BinarySensorDeviceClass.RUNNING,
     "supports_3_state": True},
    {"name": "Refill State", "key": "REFILL", "icon": "mdi:water", 
     "feature_id": "water_refill", "device_class": BinarySensorDeviceClass.RUNNING},
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "PV Surplus", "key": "PVSURPLUS", "icon": "mdi:solar-power-variant", 
     "feature_id": "pv_surplus", "supports_3_state": True},
    {"name": "Digital Input Z1Z2", "key": "INPUTz1z2", "icon": "mdi:electric-switch", 
     "feature_id": "digital_inputs", "entity_category": EntityCategory.DIAGNOSTIC},
    # Cover Controls
    {"name": "Cover Open Contact", "key": "OPEN_CONTACT", "icon": "mdi:window-open-variant", 
     "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
    {"name": "Cover Stop Contact", "key": "STOP_CONTACT", "icon": "mdi:stop-circle-outline", 
     "feature_id": "cover_control"},
    {"name": "Cover Close Contact", "key": "CLOSE_CONTACT", "icon": "mdi:window-closed-variant", 
     "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
]

# Generierte Digital Inputs hinzufügen
BINARY_SENSORS.extend(_DIGITAL_INPUTS)
BINARY_SENSORS.extend(_DIGITAL_CE_INPUTS)

# ═══════════════════════════════════════════════════════════════════════════════
# SWITCHES MIT 3-STATE UNTERSTÜTZUNG
# ═══════════════════════════════════════════════════════════════════════════════

_EXT1_SWITCHES = [
    {"name": f"Extension 1.{i}", "key": f"EXT1_{i}", "icon": "mdi:toggle-switch-outline", 
     "feature_id": "extension_outputs", "supports_3_state": True} 
    for i in range(1, 9)
]
_EXT2_SWITCHES = [
    {"name": f"Extension 2.{i}", "key": f"EXT2_{i}", "icon": "mdi:toggle-switch-outline", 
     "feature_id": "extension_outputs", "supports_3_state": True}
    for i in range(1, 9)
]
_OMNI_SWITCHES = [
    {"name": f"Omni DC{i} Output", "key": f"OMNI_DC{i}", "icon": "mdi:electric-switch", 
     "feature_id": "extension_outputs", "supports_3_state": True}
    for i in range(6)
]

SWITCHES = [
    {"name": "Filterpumpe", "key": "PUMP", "icon": "mdi:water-pump", 
     "feature_id": "filter_control", "supports_3_state": True, "supports_speed": True},
    {"name": "Solarabsorber", "key": "SOLAR", "icon": "mdi:solar-power", 
     "feature_id": "solar", "supports_3_state": True},
    {"name": "Heizung", "key": "HEATER", "icon": "mdi:radiator", 
     "feature_id": "heating", "supports_3_state": True},
    {"name": "Beleuchtung", "key": "LIGHT", "icon": "mdi:lightbulb", 
     "feature_id": "led_lighting", "supports_3_state": True, "supports_color_pulse": True},
    {"name": "Dosierung pH+", "key": "DOS_5_PHP", "icon": "mdi:flask-plus", 
     "feature_id": "ph_control", "supports_3_state": True, "supports_timer": True},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask", 
     "feature_id": "chlorine_control", "supports_3_state": True, "supports_timer": True},
    {"name": "PV-Überschuss", "key": "PVSURPLUS", "icon": "mdi:solar-power-variant", 
     "feature_id": "pv_surplus", "supports_3_state": True, "supports_speed": True},
]

# Generierte Switches hinzufügen
SWITCHES.extend(_EXT1_SWITCHES)
SWITCHES.extend(_EXT2_SWITCHES)
SWITCHES.extend(_OMNI_SWITCHES)

# ═══════════════════════════════════════════════════════════════════════════════
# SETPOINT-DEFINITIONEN MIT ERWEITERTER VALIDIERUNG
# ═══════════════════════════════════════════════════════════════════════════════

SETPOINT_DEFINITIONS = [
    {
        "key": "ph_setpoint", "name": "pH Sollwert", "min_value": 6.8, "max_value": 7.8, "step": 0.1,
        "icon": "mdi:flask", "api_key": "pH", "feature_id": "ph_control", "unit_of_measurement": "pH",
        "device_class": NumberDeviceClass.PH, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_TARGET", "TARGET_PH"],
        "indicator_fields": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"], 
        "default_value": 7.2, "validation_range": (6.5, 8.0)
    },
    {
        "key": "orp_setpoint", "name": "Redox Sollwert", "min_value": 600, "max_value": 800, "step": 10,
        "icon": "mdi:flash", "api_key": "ORP", "feature_id": "chlorine_control", "unit_of_measurement": "mV",
        "device_class": None, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["ORP_SETPOINT", "ORP_TARGET", "TARGET_ORP"],
        "indicator_fields": ["orp_value"], "default_value": 700, "validation_range": (500, 900)
    },
    {
        "key": "chlorine_setpoint", "name": "Chlor Sollwert", "min_value": 0.2, "max_value": 2.0, "step": 0.1,
        "icon": "mdi:test-tube", "api_key": "MinChlorine", "feature_id": "chlorine_control", "unit_of_measurement": "mg/l",
        "device_class": None, "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["CHLORINE_SETPOINT", "MIN_CHLORINE", "TARGET_MIN_CHLORINE"],
        "indicator_fields": ["pot_value", "DOS_1_CL"], "default_value": 0.6, "validation_range": (0.1, 3.0)
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# UNIT MAPPINGS UND SENSOREN
# ═══════════════════════════════════════════════════════════════════════════════

# Dynamische Unit-Mappings (Python 3.13 kompatibel)
_ONEWIRE_TEMPS = {f"onewire{i}_value": "°C" for i in range(1, 13)}
_PUMP_RPMS = {f"PUMP_RPM_{i}": "RPM" for i in range(4)}
_PUMP_RPM_VALUES = {f"PUMP_RPM_{i}_VALUE": "RPM" for i in range(4)}

UNIT_MAP = {
    # Temperature sensors
    "water_temp": "°C", "air_temp": "°C", "temp_value": "°C",
    "SYSTEM_cpu_temperature": "°C", "SYSTEM_carrier_cpu_temperature": "°C",
    # Water chemistry
    "pH_value": "pH", "orp_value": "mV", "pot_value": "mg/l",
    # Analog values
    "ADC1_value": "bar", "ADC2_value": "cm", "IMP1_value": "cm/s", "IMP2_value": "m³/h",
    # System values
    "CPU_UPTIME": "s", "DEVICE_UPTIME": "s", "RUNTIME": "s",
}

# Generierte Mappings hinzufügen
UNIT_MAP.update(_ONEWIRE_TEMPS)
UNIT_MAP.update(_PUMP_RPMS)
UNIT_MAP.update(_PUMP_RPM_VALUES)

# Sensoren ohne Einheiten
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

# Feature-Mapping für Sensoren (erweitert)
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

# Generierte Mappings hinzufügen
SENSOR_FEATURE_MAP.update(_DOS_CL_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHM_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHP_FEATURE_MAP)
SENSOR_FEATURE_MAP.update(_DOS_CL_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHM_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_DOS_PHP_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_EXT1_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_EXT2_RUNTIME_MAP)
SENSOR_FEATURE_MAP.update(_OMNI_RUNTIME_MAP)

# ═══════════════════════════════════════════════════════════════════════════════
# API-AKTIONEN UND ERWEITERTE SERVICE-DEFINITIONEN
# ═══════════════════════════════════════════════════════════════════════════════

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

# Query und Target-Parameter
QUERY_ALL = "ALL"
TARGET_PH = "pH"
TARGET_ORP = "ORP"
TARGET_MIN_CHLORINE = "MinChlorine"
KEY_MAINTENANCE = "MAINTENANCE"
KEY_PVSURPLUS = "PVSURPLUS"

# API-Request-Templates basierend auf Dokumentation
API_REQUEST_TEMPLATES = {
    "pump_speed": "PUMP,{action},{duration},{speed}",
    "pump_force_off": "PUMP,OFF,{duration},0", 
    "pump_auto": "PUMP,AUTO,0,0",
    "dosing_manual": "{key},MAN,{duration},0",
    "extension_timed": "{key},ON,{duration},0",
    "light_color_pulse": "LIGHT,COLOR,0,0",
    "dirule_trigger": "{key},PUSH,0,0",
    "dirule_lock": "{key},LOCK,0,0",
    "dirule_unlock": "{key},UNLOCK,0,0",
    "dmx_all_control": "DMX_SCENE1,{action},0,0",
    "pv_surplus": "PVSURPLUS,{action},{speed},0"
}

# ═══════════════════════════════════════════════════════════════════════════════
# ERWEITERTE SERVICE-DEFINITIONEN FÜR 3-STATE SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════

ENHANCED_SERVICES = {
    "set_auto_mode": {
        "name": "AUTO-Modus aktivieren",
        "description": "Setzt Switch(es) in automatischen Betriebsmodus",
        "target": "entity",
        "fields": {
            "restore_after": {
                "selector": {"number": {"min": 0, "max": 86400, "unit_of_measurement": "seconds"}},
                "required": False,
                "default": 0,
                "description": "Nach X Sekunden zu vorherigem Zustand zurück (0 = permanent)"
            }
        }
    },
    "set_pump_speed": {
        "name": "Pumpengeschwindigkeit setzen",
        "description": "Stellt die Filterpumpen-Drehzahl ein",
        "target": "entity",
        "fields": {
            "speed": {
                "selector": {"select": {"options": ["1", "2", "3"]}},
                "required": True,
                "description": "Drehzahlstufe (1=Eco, 2=Normal, 3=Boost)"
            },
            "duration": {
                "selector": {"number": {"min": 0, "max": 86400, "unit_of_measurement": "seconds"}},
                "required": False,
                "default": 0,
                "description": "Laufzeit in Sekunden (0 = permanent)"
            }
        }
    },
    "manual_dosing": {
        "name": "Manuelle Dosierung",
        "description": "Startet manuelle Dosierung für angegebene Dauer",
        "target": "entity",
        "fields": {
            "duration": {
                "selector": {"number": {"min": 5, "max": 300, "unit_of_measurement": "seconds"}},
                "required": True,
                "description": "Dosierungsdauer in Sekunden"
            },
            "safety_override": {
                "selector": {"boolean": {}},
                "required": False,
                "default": False,
                "description": "Sicherheitsintervall überschreiben (mit Vorsicht verwenden)"
            }
        }
    },
    "set_extension_timer": {
        "name": "Erweiterungsrelais-Timer",
        "description": "Aktiviert Erweiterungsrelais für bestimmte Zeit",
        "target": "entity",
        "fields": {
            "duration": {
                "selector": {"number": {"min": 60, "max": 86400, "unit_of_measurement": "seconds"}},
                "required": True,
                "description": "Aktivierungsdauer in Sekunden"
            }
        }
    },
    "force_off": {
        "name": "Zwangsabschaltung",
        "description": "Schaltet Gerät zwangsweise aus mit Sperrzeit",
        "target": "entity",
        "fields": {
            "lock_duration": {
                "selector": {"number": {"min": 60, "max": 3600, "unit_of_measurement": "seconds"}},
                "required": True,
                "description": "Sperrdauer in Sekunden"
            }
        }
    },
    "trigger_light_color_pulse": {
        "name": "Licht-Farbpuls",
        "description": "Löst Farbwechsel-Puls für einfache LED-Leuchten aus",
        "target": "entity",
        "fields": {}
    },
    "control_all_dmx_scenes": {
        "name": "Alle DMX-Szenen steuern",
        "description": "Steuert alle DMX-Lichtszenen gleichzeitig",
        "target": "device",
        "fields": {
            "action": {
                "selector": {"select": {"options": ["ALLON", "ALLOFF", "ALLAUTO"]}},
                "required": True,
                "description": "Aktion für alle DMX-Szenen"
            }
        }
    },
    "manage_digital_rule": {
        "name": "Digitale Regel verwalten",
        "description": "Sperrt/entsperrt oder löst digitale Eingaberegeln aus",
        "target": "device",
        "fields": {
            "rule": {
                "selector": {"select": {"options": [f"DIRULE_{i}" for i in range(1, 8)]}},
                "required": True,
                "description": "Zu verwaltende digitale Eingaberegel"
            },
            "action": {
                "selector": {"select": {"options": ["TRIGGER", "LOCK", "UNLOCK"]}},
                "required": True,
                "description": "Auszuführende Aktion"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# COVER-KONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

COVER_CONFIG = {
    "states": {
        "CLOSED": {"numeric": "2", "position": 0, "description": "Vollständig geschlossen"},
        "OPEN": {"numeric": "0", "position": 100, "description": "Vollständig geöffnet"},
        "OPENING": {"numeric": "1", "position": None, "description": "Öffnet sich"},
        "CLOSING": {"numeric": "3", "position": None, "description": "Schließt sich"},
        "STOPPED": {"numeric": "4", "position": None, "description": "Angehalten"}
    },
    "movement_timeout": 120,  # Maximum Zeit für Öffnen/Schließen in Sekunden
    "position_update_interval": 5  # Aktualisierungsintervall während Bewegung
}

# ═══════════════════════════════════════════════════════════════════════════════
# PV-ÜBERSCHUSS KONFIGURATION (KAPITEL 26.3)
# ═══════════════════════════════════════════════════════════════════════════════

PV_SURPLUS_CONFIG = {
    "activation_modes": {
        "digital_input": 1,  # Aktiviert durch Digital-Input
        "http_request": 2    # Aktiviert durch HTTP-Request
    },
    "pump_speeds": {
        1: {"name": "Eco", "description": "Minimale Drehzahl für PV-Überschuss"},
        2: {"name": "Normal", "description": "Standard-Drehzahl für PV-Überschuss"}, 
        3: {"name": "Boost", "description": "Maximale Drehzahl für PV-Überschuss"}
    },
    "default_speed": 2,
    "api_template": "PVSURPLUS,{state},{speed},0"
}

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDIERUNG UND MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

# Gerätespezifische Validierungsregeln
DEVICE_VALIDATION_RULES = {
    "PUMP": {
        "min_speed": 1, "max_speed": 3, 
        "min_off_duration": 60, "max_off_duration": 3600,
        "rpm_thresholds": {"min_active": 100, "max_normal": 3000}
    },
    "HEATER": {
        "min_temp": 20.0, "max_temp": 40.0, "temp_step": 0.5,
        "max_temp_diff": 50.0  # Maximum erlaubte Temperaturdifferenz
    },
    "DOS_1_CL": {
        "min_dosing": 5, "max_dosing": 300,
        "safety_interval": 300, "max_daily_runtime": 1800
    },
    "DOS_4_PHM": {
        "min_dosing": 5, "max_dosing": 300,
        "safety_interval": 300, "max_daily_runtime": 1800
    },
    "DOS_5_PHP": {
        "min_dosing": 5, "max_dosing": 300,
        "safety_interval": 300, "max_daily_runtime": 1800
    }
}

# Erweiterte Monitoring-Konfiguration
MONITORING_CONFIG = {
    "critical_devices": ["PUMP", "HEATER", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP"],
    "monitoring_intervals": {
        "critical": 10,    # Sekunden - Pumpe, Heizung, Dosierungen
        "normal": 30,      # Sekunden - Solar, Licht, Standard-Funktionen
        "background": 120  # Sekunden - Erweiterungen, System-Sensoren
    },
    "alert_thresholds": {
        "pump_rpm_min": 100,           # Minimum RPM für laufende Pumpe
        "temp_diff_max": 50,           # Maximum Temperaturdifferenz in °C
        "dosing_runtime_max": 300,     # Maximum Dosierungszeit in Sekunden
        "ph_deviation_max": 0.5,       # Maximum pH-Abweichung vom Sollwert
        "orp_deviation_max": 100,      # Maximum Redox-Abweichung in mV
        "pressure_max": 2.5,           # Maximum Filterdruck in bar
        "temp_sensor_timeout": 300     # Timeout für Temperatursensoren in Sekunden
    },
    "error_recovery": {
        "max_retries": 3,
        "retry_delay": 5,  # Sekunden
        "fallback_to_auto": True
    }
}

# Fehlercodes und -behandlung
ERROR_CODES = {
    # API-Antwort-Codes
    "OK": {"severity": "info", "message": "Operation successful", "action": "none"},
    "ERROR": {"severity": "error", "message": "General error occurred", "action": "retry"},
    
    # HTTP-spezifische Fehler
    "HTTP_401": {"severity": "error", "message": "Authentication required - check credentials", "action": "check_auth"},
    "HTTP_404": {"severity": "error", "message": "API endpoint not found", "action": "check_url"},
    "HTTP_500": {"severity": "error", "message": "Controller overloaded", "action": "wait_retry"},
    "HTTP_TIMEOUT": {"severity": "warning", "message": "Request timeout", "action": "retry"},
    
    # Validierungsfehler
    "INVALID_SPEED": {"severity": "error", "message": "Pump speed must be 1-3", "action": "validate_input"},
    "INVALID_DURATION": {"severity": "error", "message": "Duration outside valid range", "action": "validate_input"},
    "DOSING_SAFETY": {"severity": "warning", "message": "Dosing safety interval not met", "action": "enforce_delay"},
    "DEVICE_LOCKED": {"severity": "warning", "message": "Device in maintenance mode", "action": "wait_maintenance"},
    "TEMP_SENSOR_FAULT": {"severity": "error", "message": "Temperature sensor malfunction", "action": "disable_temp_control"}
}

# Status-Prioritäten für Anzeige-Logik
STATUS_PRIORITIES = {
    "error": 100,
    "maintenance": 90,
    "manual_on": 80,
    "manual_off": 70,
    "auto_active": 60,
    "auto_inactive": 50,
    "unknown": 10
}

# Lokalisierung für Zustandsanzeigen
STATE_TRANSLATIONS = {
    "de": {
        "auto_active": "Automatik (Aktiv)",
        "auto_inactive": "Automatik (Bereit)", 
        "manual_on": "Manuell Ein",
        "manual_off": "Manuell Aus",
        "error": "Fehler",
        "maintenance": "Wartung",
        "unknown": "Unbekannt"
    },
    "en": {
        "auto_active": "Auto (Active)",
        "auto_inactive": "Auto (Ready)",
        "manual_on": "Manual On", 
        "manual_off": "Manual Off",
        "error": "Error",
        "maintenance": "Maintenance",
        "unknown": "Unknown"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS FOR 3-STATE SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════

def get_device_mode_from_state(raw_state: str, device_key: str = None) -> str:
    """
    Ermittle den Gerätemodus aus dem rohen Zustandswert.
    
    Args:
        raw_state: Roher Zustandswert aus der API
        device_key: Geräteschlüssel für gerätespezifische Behandlung
        
    Returns:
        String: auto, manual_on, manual_off, error, maintenance, unknown
    """
    state_info = get_device_state_info(raw_state, device_key)
    mode = state_info.get("mode", "auto")
    active = state_info.get("active")
    
    if mode == "manual":
        return "manual_on" if active else "manual_off"
    elif mode == "auto":
        return "auto_active" if active else "auto_inactive"
    else:
        return mode  # error, maintenance, etc.

def get_device_icon(device_key: str, mode: str) -> str:
    """
    Ermittle das passende Icon für ein Gerät basierend auf Modus.
    
    Args:
        device_key: Geräteschlüssel (z.B. PUMP, HEATER)
        mode: Gerätemodus (auto_active, manual_on, etc.)
        
    Returns:
        String: MDI-Icon-Name
    """
    if device_key in STATE_ICONS:
        return STATE_ICONS[device_key].get(mode, STATE_ICONS[device_key].get("auto_inactive", "mdi:help"))
    
    # Fallback-Icons
    fallback_icons = {
        "auto_active": "mdi:auto-mode",
        "auto_inactive": "mdi:auto-mode-outline",
        "manual_on": "mdi:power-on",
        "manual_off": "mdi:power-off",
        "error": "mdi:alert-circle",
        "maintenance": "mdi:wrench"
    }
    
    return fallback_icons.get(mode, "mdi:help")

def get_device_color(mode: str) -> str:
    """
    Ermittle die Anzeigefarbe für einen Gerätemodus.
    
    Args:
        mode: Gerätemodus
        
    Returns:
        String: Hex-Farbcode
    """
    return STATE_COLORS.get(mode, "#9E9E9E")  # Grau als Fallback

def validate_device_parameter(device_key: str, parameter: str, value: any) -> tuple[bool, str]:
    """
    Validiere einen Geräteparameter.
    
    Args:
        device_key: Geräteschlüssel
        parameter: Parameter-Name (speed, duration, etc.)
        value: Zu validierender Wert
        
    Returns:
        Tuple: (is_valid: bool, error_message: str)
    """
    if device_key not in DEVICE_VALIDATION_RULES:
        return True, ""
    
    rules = DEVICE_VALIDATION_RULES[device_key]
    
    if parameter == "speed" and "min_speed" in rules:
        if not (rules["min_speed"] <= int(value) <= rules["max_speed"]):
            return False, f"Speed must be between {rules['min_speed']} and {rules['max_speed']}"
    elif parameter == "duration" and "max_off_duration" in rules:
        if int(value) > rules["max_off_duration"]:
            return False, f"Duration cannot exceed {rules['max_off_duration']} seconds"
    elif parameter == "dosing_duration" and "max_dosing" in rules:
        if not (rules["min_dosing"] <= int(value) <= rules["max_dosing"]):
            return False, f"Dosing duration must be between {rules['min_dosing']} and {rules['max_dosing']} seconds"
    
    return True, ""

def build_api_request(device_key: str, action: str, **params) -> str:
    """
    Erstelle API-Request-String basierend auf Geräteparametern.
    
    Args:
        device_key: Geräteschlüssel
        action: API-Aktion (ON, OFF, AUTO, etc.)
        **params: Zusätzliche Parameter (duration, speed, etc.)
        
    Returns:
        String: Formatierter API-Request
    """
    if device_key not in DEVICE_PARAMETERS:
        # Fallback für unbekannte Geräte
        duration = params.get("duration", 0)
        value = params.get("value", 0)
        return f"{device_key},{action},{duration},{value}"
    
    device_config = DEVICE_PARAMETERS[device_key]
    template = device_config.get("api_template", "{key},{action},0,0")
    
    # Parameter für Template vorbereiten
    template_params = {
        "key": device_key,
        "action": action,
        "duration": params.get("duration", 0),
        "speed": params.get("speed", device_config.get("default_on_speed", 0)),
        "value": params.get("value", 0)
    }
    
    return template.format(**template_params)

def is_device_activity_detected(device_key: str, coordinator_data: dict) -> bool:
    """
    Prüfe, ob ein Gerät tatsächlich aktiv ist (für AUTO-Modus).
    
    Args:
        device_key: Geräteschlüssel
        coordinator_data: Daten vom Koordinator
        
    Returns:
        bool: True wenn Gerät aktiv läuft
    """
    if device_key not in DEVICE_PARAMETERS:
        return False
    
    device_config = DEVICE_PARAMETERS[device_key]
    activity_sensors = device_config.get("activity_sensors", [])
    thresholds = device_config.get("activity_threshold", {})
    
    # Gerätespezifische Aktivitätserkennung
    if device_key == "PUMP":
        rpm = coordinator_data.get("PUMP_RPM_1_VALUE", 0)
        try:
            return int(float(rpm)) > thresholds.get("PUMP_RPM_1_VALUE", 100)
        except (ValueError, TypeError):
            return False
            
    elif device_key in ["HEATER", "SOLAR"]:
        # Temperaturdifferenz prüfen
        if device_key == "HEATER":
            device_temp = coordinator_data.get("onewire5_value")  # Heizer-Temperatur
        else:
            device_temp = coordinator_data.get("onewire3_value")  # Absorber-Temperatur
            
        water_temp = coordinator_data.get("onewire1_value")  # Wasser-Temperatur
        
        if device_temp is not None and water_temp is not None:
            try:
                temp_diff = float(device_temp) - float(water_temp)
                required_diff = thresholds.get("temp_diff", 2.0)
                return temp_diff > required_diff
            except (ValueError, TypeError):
                return False
                
    elif device_key.startswith("DOS_"):
        # Dosierung: Prüfe Runtime
        runtime = coordinator_data.get(f"{device_key}_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
        # Alternativ: Prüfe State
        state = coordinator_data.get(f"{device_key}_STATE", "")
        return str(state).upper() in ["ON", "ACTIVE", "DOSING", "1"]
        
    elif device_key.startswith("EXT"):
        # Erweiterungsrelais: Prüfe Runtime
        runtime = coordinator_data.get(f"{device_key}_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
    elif device_key == "LIGHT":
        # Licht: Prüfe Runtime oder State
        runtime = coordinator_data.get("LIGHT_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
    elif device_key == "BACKWASH":
        # Rückspülung: Prüfe State oder Runtime
        state = coordinator_data.get("BACKWASHSTATE", "")
        runtime = coordinator_data.get("BACKWASH_RUNTIME", "")
        
        if str(state).upper() in ["ON", "ACTIVE", "RUNNING", "1"]:
            return True
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
    
    # Fallback: Prüfe alle activity_sensors
    for sensor_key in activity_sensors:
        value = coordinator_data.get(sensor_key)
        if value is not None:
            if sensor_key in thresholds:
                try:
                    return float(value) > thresholds[sensor_key]
                except (ValueError, TypeError):
                    continue
            elif str(value).upper() in ["ON", "ACTIVE", "RUNNING", "1", "TRUE"]:
                return True
    
    return False

def get_enhanced_switch_attributes(device_key: str, coordinator_data: dict) -> dict:
    """
    Erstelle erweiterte Attribute für einen 3-State-Switch.
    
    Args:
        device_key: Geräteschlüssel
        coordinator_data: Daten vom Koordinator
        
    Returns:
        dict: Erweiterte Attribute
    """
    raw_state = coordinator_data.get(device_key, "")
    state_info = get_device_state_info(raw_state, device_key)
    mode = get_device_mode_from_state(raw_state, device_key)
    
    attributes = {
        "mode": state_info.get("mode", "auto"),
        "active": state_info.get("active"),
        "priority": state_info.get("priority", 50),
        "description": state_info.get("desc", ""),
        "raw_state": str(raw_state),
        "display_mode": STATE_TRANSLATIONS.get("de", {}).get(mode, mode),
        "supports_3_state": True
    }
    
    # Gerätespezifische Attribute hinzufügen
    if device_key == "PUMP":
        rpm = coordinator_data.get("PUMP_RPM_1_VALUE")
        if rpm is not None:
            try:
                attributes["pump_rpm"] = int(float(rpm))
            except (ValueError, TypeError):
                pass
                
        runtime = coordinator_data.get("PUMP_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        # Verfügbare Geschwindigkeiten
        if device_key in DEVICE_PARAMETERS:
            speeds = DEVICE_PARAMETERS[device_key].get("speeds", {})
            attributes["available_speeds"] = list(speeds.keys())
            attributes["speed_names"] = speeds
            
    elif device_key.startswith("DOS_"):
        # Dosierungs-spezifische Attribute
        runtime = coordinator_data.get(f"{device_key}_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        remaining = coordinator_data.get(f"{device_key}_REMAINING_RANGE")
        if remaining:
            attributes["remaining_range"] = remaining
            
        state = coordinator_data.get(f"{device_key}_STATE")
        if state:
            attributes["dosing_state"] = state
            
        # Dosierungsparameter
        if device_key in DEVICE_PARAMETERS:
            dosing_config = DEVICE_PARAMETERS[device_key]
            attributes["dosing_type"] = dosing_config.get("dosing_type", "")
            attributes["max_duration"] = dosing_config.get("max_dosing_duration", 300)
            attributes["safety_interval"] = dosing_config.get("safety_interval", 300)
            
    elif device_key in ["HEATER", "SOLAR"]:
        # Temperatur-spezifische Attribute
        if device_key == "HEATER":
            temp_sensor = "onewire5_value"
        else:
            temp_sensor = "onewire3_value"
            
        device_temp = coordinator_data.get(temp_sensor)
        water_temp = coordinator_data.get("onewire1_value")
        
        if device_temp is not None:
            try:
                attributes["device_temperature"] = round(float(device_temp), 1)
            except (ValueError, TypeError):
                pass
                
        if water_temp is not None:
            try:
                attributes["water_temperature"] = round(float(water_temp), 1)
            except (ValueError, TypeError):
                pass
                
        if device_temp is not None and water_temp is not None:
            try:
                temp_diff = float(device_temp) - float(water_temp)
                attributes["temperature_difference"] = round(temp_diff, 1)
            except (ValueError, TypeError):
                pass
                
        runtime = coordinator_data.get(f"{device_key}_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
    elif device_key.startswith("EXT"):
        # Erweiterungsrelais-Attribute
        runtime = coordinator_data.get(f"{device_key}_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        # Timer-Informationen
        if device_key in DEVICE_PARAMETERS:
            ext_config = DEVICE_PARAMETERS[device_key]
            attributes["default_duration"] = ext_config.get("default_on_duration", 3600)
            attributes["max_duration"] = ext_config.get("max_duration", 86400)
            
    elif device_key == "LIGHT":
        runtime = coordinator_data.get("LIGHT_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        # Licht-spezifische Funktionen
        if device_key in DEVICE_PARAMETERS:
            light_config = DEVICE_PARAMETERS[device_key]
            attributes["supports_color_pulse"] = light_config.get("supports_color_pulse", False)
            attributes["color_pulse_duration"] = light_config.get("color_pulse_duration", 150)
            
    elif device_key == "PVSURPLUS":
        # PV-Überschuss Attribute
        pv_status = coordinator_data.get("PVSURPLUS")
        if pv_status is not None:
            try:
                pv_code = int(pv_status)
                if pv_code == 0:
                    attributes["pv_mode"] = "inactive"
                elif pv_code == 1:
                    attributes["pv_mode"] = "digital_input"
                elif pv_code == 2:
                    attributes["pv_mode"] = "http_request"
                else:
                    attributes["pv_mode"] = "unknown"
            except (ValueError, TypeError):
                pass
                
        # Verfügbare Geschwindigkeiten
        if device_key in DEVICE_PARAMETERS:
            speeds = DEVICE_PARAMETERS[device_key].get("speeds", {})
            attributes["available_speeds"] = list(speeds.keys())
            attributes["speed_names"] = speeds
    
    # Unterstützte Aktionen basierend auf Gerätekonfiguration
    if device_key in DEVICE_PARAMETERS:
        device_config = DEVICE_PARAMETERS[device_key]
        supported_actions = ["ON", "OFF", "AUTO"]
        
        if device_config.get("supports_speed"):
            supported_actions.append("SPEED_CONTROL")
        if device_config.get("supports_timer"):
            supported_actions.append("TIMER")
        if device_config.get("supports_color_pulse"):
            supported_actions.append("COLOR_PULSE")
        if device_config.get("supports_lock"):
            supported_actions.extend(["LOCK", "UNLOCK"])
        if device_config.get("supports_force_off"):
            supported_actions.append("FORCE_OFF")
            
        attributes["supported_actions"] = supported_actions
    
    return attributes

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE-ZU-SWITCH MAPPINGS FÜR UI-ORGANIZATION
# ═══════════════════════════════════════════════════════════════════════════════

SWITCH_FEATURE_MAP = {
    "PUMP": "filter_control",
    "SOLAR": "solar", 
    "HEATER": "heating",
    "LIGHT": "led_lighting",
    "DOS_1_CL": "chlorine_control",
    "DOS_4_PHM": "ph_control",
    "DOS_5_PHP": "ph_control",
    "DOS_6_FLOC": "chlorine_control",
    "BACKWASH": "backwash",
    "BACKWASHRINSE": "backwash",
    "PVSURPLUS": "pv_surplus",
    "REFILL": "water_refill",
    **{f"EXT1_{i}": "extension_outputs" for i in range(1, 9)},
    **{f"EXT2_{i}": "extension_outputs" for i in range(1, 9)},
    **{f"DMX_SCENE{i}": "led_lighting" for i in range(1, 13)},
    **{f"DIRULE_{i}": "digital_inputs" for i in range(1, 8)},
    **{f"OMNI_DC{i}": "extension_outputs" for i in range(6)},
}

BINARY_SENSOR_FEATURE_MAP = {
    "PUMP": "filter_control",
    "HEATER": "heating",
    "SOLAR": "solar",
    "LIGHT": "led_lighting",
    "BACKWASH": "backwash",
    "BACKWASHRINSE": "backwash", 
    "DOS_1_CL": "chlorine_control",
    "DOS_4_PHM": "ph_control",
    "DOS_5_PHP": "ph_control",
    "DOS_6_FLOC": "chlorine_control",
    "COVER_OPEN": "cover_control",
    "COVER_CLOSE": "cover_control",
    "COVER_STATE": "cover_control",
    "REFILL": "water_refill",
    "PVSURPLUS": "pv_surplus",
    **{f"INPUT{i}": "digital_inputs" for i in range(1, 13)},
    **{f"INPUT_CE{i}": "digital_inputs" for i in range(1, 5)},
}

# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED ERROR HANDLING UND LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

class VioletState:
    """Erweiterte Zustandsklasse für 3-State-Support."""
    
    def __init__(self, raw_state: str, device_key: str = None):
        self.raw_state = str(raw_state).strip()
        self.device_key = device_key
        self._state_info = get_device_state_info(self.raw_state, device_key)
        
    @property
    def mode(self) -> str:
        """Gerätemodus: auto, manual, error, maintenance."""
        return self._state_info.get("mode", "auto")
        
    @property
    def is_active(self) -> bool:
        """Ist das Gerät aktiv? None = abhängig von externen Faktoren."""
        return self._state_info.get("active")
        
    @property
    def priority(self) -> int:
        """Anzeigepriorität für UI-Sortierung."""
        return self._state_info.get("priority", 50)
        
    @property
    def description(self) -> str:
        """Menschenlesbare Beschreibung des Zustands."""
        return self._state_info.get("desc", f"State: {self.raw_state}")
        
    @property
    def display_mode(self) -> str:
        """Anzeigename für UI."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return STATE_TRANSLATIONS.get("de", {}).get(mode_key, mode_key)
        
    @property
    def icon(self) -> str:
        """Passendes Icon für aktuellen Zustand."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_icon(self.device_key, mode_key)
        
    @property
    def color(self) -> str:
        """Anzeigefarbe für aktuellen Zustand."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_color(mode_key)
        
    def is_manual_mode(self) -> bool:
        """Ist das Gerät im manuellen Modus?"""
        return self.mode == "manual"
        
    def is_auto_mode(self) -> bool:
        """Ist das Gerät im automatischen Modus?"""
        return self.mode == "auto"
        
    def is_error_state(self) -> bool:
        """Ist das Gerät in einem Fehlerzustand?"""
        return self.mode in ["error", "maintenance"]
        
    def __str__(self) -> str:
        return f"VioletState({self.device_key}): {self.display_mode} ({self.raw_state})"
        
    def __repr__(self) -> str:
        return f"VioletState(raw_state='{self.raw_state}', device_key='{self.device_key}', mode='{self.mode}', active={self.is_active})"

# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def legacy_is_on_state(raw_state: str) -> bool:
    """
    Legacy-Funktion für einfache On/Off-Prüfung.
    Für Rückwärtskompatibilität mit bestehenden Binary Sensors.
    
    Args:
        raw_state: Roher Zustandswert
        
    Returns:
        bool: True wenn "eingeschaltet"
    """
    if not raw_state:
        return False
        
    upper_state = str(raw_state).upper().strip()
    
    # Nutze erweiterte Zustandsinformationen
    state_info = get_device_state_info(raw_state)
    
    # Wenn explizit aktiv/inaktiv definiert
    if state_info.get("active") is not None:
        return state_info.get("active")
    
    # Fallback zu Legacy-Mapping
    return STATE_MAP.get(upper_state, False)

# Rückwärtskompatible Funktionen
def get_legacy_icon(device_key: str, is_on: bool) -> str:
    """Legacy Icon-Funktion."""
    if device_key in STATE_ICONS:
        return STATE_ICONS[device_key].get("manual_on" if is_on else "manual_off", "mdi:help")
    return "mdi:power" if is_on else "mdi:power-off"

# ═══════════════════════════════════════════════════════════════════════════════
# KONFIGURATIONSDEFINITIONEN FÜR CONFIG FLOW
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_FLOW_SCHEMAS = {
    "user": {
        "required": [CONF_API_URL],
        "optional": [
            CONF_USERNAME, CONF_PASSWORD, CONF_USE_SSL, CONF_DEVICE_ID,
            CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS, CONF_DEVICE_NAME
        ]
    },
    "pool_setup": {
        "required": [CONF_POOL_SIZE, CONF_POOL_TYPE, CONF_DISINFECTION_METHOD],
        "optional": []
    },
    "feature_selection": {
        "features": AVAILABLE_FEATURES
    }
}

OPTIONS_FLOW_SCHEMA = {
    "advanced": [
        CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS,
        CONF_POOL_SIZE, CONF_POOL_TYPE, CONF_DISINFECTION_METHOD
    ],
    "features": AVAILABLE_FEATURES
}

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL EXPORTS UND VERSION INFO
# ═══════════════════════════════════════════════════════════════════════════════

# Version und Changelog
VERSION_INFO = {
    "version": INTEGRATION_VERSION,
    "release_date": "2024-12-19",
    "major_features": [
        "3-State Switch Support (AUTO/MANUAL ON/MANUAL OFF)",
        "Enhanced Device Parameter Control",
        "Improved Visual State Representation", 
        "Extended API Parameter Support",
        "Advanced Error Handling and Validation"
    ],
    "breaking_changes": [
        "Switch entities now support 3-state mode",
        "New attribute structure for enhanced devices",
        "Modified service call parameters for better API alignment"
    ],
    "migration_notes": [
        "Existing automations may need attribute name updates",
        "New service parameters available for advanced control",
        "Legacy binary switch behavior preserved for compatibility"
    ]
}

# Exportierte Hauptkonstanten (für __init__.py imports)
__all__ = [
    # Core constants
    "DOMAIN", "INTEGRATION_VERSION", "MANUFACTURER",
    
    # Configuration
    "CONF_API_URL", "CONF_USERNAME", "CONF_PASSWORD", "CONF_ACTIVE_FEATURES",
    "DEFAULT_POLLING_INTERVAL", "DEFAULT_TIMEOUT_DURATION", "DEFAULT_RETRY_ATTEMPTS",
    
    # API
    "API_READINGS", "API_SET_FUNCTION_MANUALLY", "ACTION_ON", "ACTION_OFF", "ACTION_AUTO",
    
    # 3-State Support  
    "DEVICE_STATE_MAPPING", "STATE_ICONS", "STATE_COLORS", "get_device_state_info",
    "get_device_mode_from_state", "is_device_activity_detected", "VioletState",
    
    # Device Configuration
    "DEVICE_PARAMETERS", "SWITCHES", "BINARY_SENSORS", "AVAILABLE_FEATURES",
    "SWITCH_FUNCTIONS", "ENHANCED_SERVICES",
    
    # Utilities
    "validate_device_parameter", "build_api_request", "get_enhanced_switch_attributes",
    "legacy_is_on_state", "VERSION_INFO"
]

DEBUG_INFO = {
    "integration_version": "0.2.0.0",
    "total_switches": 50,                    # Alle Haupt- und Erweiterungsschalter
    "total_binary_sensors": 25,              # Mit digitalen Eingängen
    "total_device_parameters": 70,           # Alle Geräte-Konfigurationen
    "total_state_mappings": 15,               # 3-State-Mappings
    "supported_features": 13,                 # Pool-Features
    "enhanced_services": 9,                   # Erweiterte Services
    "3_state_devices": 30,                   # Geräte mit 3-State-Support
    "api_templates": 60,                     # API-Request-Templates
    "temperature_sensors": 6,                 # OneWire-Basis-Sensoren
    "water_chemistry_sensors": 3,             # pH, ORP, Chlor
    "analog_sensors": 4,                      # ADC/IMP-Sensoren
    "setpoint_definitions": 4,                # Sollwert-Definitionen
    "unit_mappings": 50,                     # Unit-Zuordnungen
    "no_unit_sensors": 100,                  # Text/Status-Sensoren
    "sensor_feature_mappings": 80,           # Feature-Zuordnungen
    "state_icons": 40,                       # Icon-Variationen
    "validation_rules": 5,                    # Validierungsregeln
    "error_codes": 15,                       # Fehlercode-Definitionen
    "extension_relais": 16,                   # EXT1_1-8 + EXT2_1-8
    "dmx_scenes": 12,                         # DMX_SCENE1-12
    "digital_rules": 7,                       # DIRULE_1-7
    "api_request_templates": 15              # Template-Variationen
}
