"""Erweiterte Konstanten für die Violet Pool Controller Integration - VOLLSTÄNDIGE VERSION MIT ALLEN FIXES."""
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

# Integration
DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "0.1.0.4"  # Updated with all fixes
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

# DEVICE_STATE_MAPPING - Erweiterte State-Mappings mit State 4
DEVICE_STATE_MAPPING = {
    # String-basierte Zustände (häufigste Form)
    "ON": {"mode": "manual", "active": True, "priority": 80},
    "OFF": {"mode": "manual", "active": False, "priority": 70},
    "AUTO": {"mode": "auto", "active": None, "priority": 60},
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

# ⭐ KRITISCHER FIX: STATE_MAP mit State 4
STATE_MAP = {
    # Numeric states als Integer (direkte API-Werte)
    0: False,    # AUTO-Standby (OFF)
    1: True,     # Manuell EIN
    2: True,     # AUTO-Aktiv (ON)
    3: True,     # AUTO-Zeitsteuerung (ON)
    4: True,     # ⭐ Manuell forciert EIN (ON) - KRITISCHER FIX!
    5: False,    # AUTO-Wartend (OFF)
    6: False,    # Manuell AUS
    
    # Numeric states als String (falls API als String liefert)
    "0": False,
    "1": True,
    "2": True,
    "3": True,
    "4": True,   # ⭐ KRITISCHER FIX!
    "5": False,
    "6": False,
    
    # String-basierte States
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

# ⭐ FIX: COVER_STATE_MAP mit String-States
COVER_STATE_MAP = {
    # Numerische States
    "0": "open", 
    "1": "opening", 
    "2": "closed", 
    "3": "closing", 
    "4": "stopped",
    
    # ⭐ String-States hinzufügen (aus API erkannt)
    "OPEN": "open", 
    "CLOSED": "closed", 
    "OPENING": "opening", 
    "CLOSING": "closing",
    "STOPPED": "stopped"
}

# Gerätespezifische Parameter
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
        "api_template": "PUMP,{action},{duration},{speed}"
    },
    "HEATER": {
        "supports_timer": True,
        "supports_temperature": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire5_value", "onewire1_value", "HEATER_RUNTIME"],
        "activity_threshold": {"temp_diff": 2.0},
        "api_template": "HEATER,{action},{duration},0"
    },
    "SOLAR": {
        "supports_timer": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire3_value", "onewire1_value", "SOLAR_RUNTIME"],
        "activity_threshold": {"temp_diff": 5.0},
        "api_template": "SOLAR,{action},{duration},0"
    },
    "LIGHT": {
        "supports_color_pulse": True,
        "color_pulse_duration": 150,
        "api_template": "LIGHT,{action},0,0",
        "color_pulse_template": "LIGHT,COLOR,0,0"
    },
    "DOS_1_CL": {
        "supports_timer": True,
        "dosing_type": "Chlor",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
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
        "default_duration": 180,
        "max_duration": 900,
        "activity_sensors": ["BACKWASH_RUNTIME", "BACKWASHSTATE"],
        "api_template": "BACKWASH,{action},{duration},0"
    },
    "BACKWASHRINSE": {
        "supports_timer": True,
        "default_duration": 60,
        "max_duration": 300,
        "activity_sensors": ["BACKWASH_RUNTIME"],
        "api_template": "BACKWASHRINSE,{action},{duration},0"
    },
    # ⭐ FIX: PVSURPLUS hinzugefügt
    "PVSURPLUS": {
        "supports_speed": True,
        "speeds": {1: "Eco", 2: "Normal", 3: "Boost"},
        "default_speed": 2,
        "activity_sensors": ["PVSURPLUS"],
        "activity_threshold": {"PVSURPLUS": 1},
        "api_template": "PVSURPLUS,{action},{speed},0"
    }
}

# Erweiterungsrelais mit Runtime-Sensoren
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "default_on_duration": 3600,
            "max_duration": 86400,
            "activity_sensors": [f"EXT{ext_bank}_{relay_num}_RUNTIME"],
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0"
        }

# Digital Rules
for rule_num in range(1, 8):
    key = f"DIRULE_{rule_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_lock": True,
        "action_type": "PUSH",
        "pulse_duration": 500,
        "api_template": f"DIRULE_{rule_num},{{action}},0,0"
    }

# DMX Scenes
for scene_num in range(1, 13):
    key = f"DMX_SCENE{scene_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_group_control": True,
        "group_actions": ["ALLON", "ALLOFF", "ALLAUTO"],
        "api_template": f"DMX_SCENE{scene_num},{{action}},0,0"
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

STATE_COLORS = {
    "auto_active": "#4CAF50",     # Grün
    "auto_inactive": "#2196F3",   # Blau
    "manual_on": "#FF9800",       # Orange
    "manual_off": "#F44336",      # Rot
    "error": "#9C27B0",           # Lila
    "maintenance": "#607D8B"      # Grau
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

# Basis Switch-Funktionen
SWITCH_FUNCTIONS = {
    "PUMP": "Filterpumpe",
    "SOLAR": "Solarabsorber",
    "HEATER": "Heizung",
    "LIGHT": "Beleuchtung",
    "ECO": "Eco-Modus",
    "BACKWASH": "Rückspülung",
    "BACKWASHRINSE": "Nachspülung",
    "REFILL": "Wassernachfüllung",
    "PVSURPLUS": "PV-Überschuss",  # ⭐ FIX: PVSURPLUS hinzugefügt
}

# Erweiterungsrelais hinzufügen
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        SWITCH_FUNCTIONS[f"EXT{ext_bank}_{relay_num}"] = f"Erweiterung {ext_bank}.{relay_num}"

# DMX-Szenen hinzufügen
for scene_num in range(1, 13):
    SWITCH_FUNCTIONS[f"DMX_SCENE{scene_num}"] = f"DMX Szene {scene_num}"

# Digitale Regeln hinzufügen
for rule_num in range(1, 8):
    SWITCH_FUNCTIONS[f"DIRULE_{rule_num}"] = f"Schaltregel {rule_num}"

# Omni DCs hinzufügen
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

# ═══════════════════════════════════════════════════════════════════════════════
# SENSOREN - ERWEITERT
# ═══════════════════════════════════════════════════════════════════════════════

# ⭐ Erweiterte Temperatur-Sensoren
TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Solarabsorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
}

WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": None},  # pH ohne unit
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}

# ⭐ Erweiterte Analog-Sensoren
ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Überlaufbehälter", "icon": "mdi:water-percent", "unit": "cm"},
    "ADC3_value": {"name": "Durchflussmesser (4-20mA)", "icon": "mdi:pump", "unit": "m³/h"},
    "ADC4_value": {"name": "Analogsensor 4 (4-20mA)", "icon": "mdi:gauge", "unit": None},
    "ADC5_value": {"name": "Analogsensor 5 (0-10V)", "icon": "mdi:gauge", "unit": "V"},
    "IMP1_value": {"name": "Flow-Switch", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Pumpen-Durchfluss", "icon": "mdi:pump", "unit": "m³/h"},
}

# ⭐ System-Sensoren
SYSTEM_SENSORS = {
    "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:chip", "unit": "°C"},
    "CPU_TEMP_CARRIER": {"name": "Carrier Board", "icon": "mdi:expansion-card", "unit": "°C"},
    "CPU_UPTIME": {"name": "System Uptime", "icon": "mdi:clock", "unit": None},
}

# ⭐ Backwash-Sensoren
BACKWASH_SENSORS = {
    "BACKWASH_STATE": {"name": "Rückspül-Status", "icon": "mdi:valve"},
    "BACKWASH_STEP": {"name": "Rückspül-Schritt", "icon": "mdi:step-forward"},
    "BACKWASH_DELAY_RUNNING": {"name": "Rückspülung verzögert", "icon": "mdi:timer-sand"},
    "BACKWASH_OMNI_STATE": {"name": "Omni-Ventil Status", "icon": "mdi:valve-open"},
    "BACKWASH_OMNI_MOVING": {"name": "Omni-Ventil bewegt sich", "icon": "mdi:rotate-right"},
}

# ⭐ Erweiterte Dosierungs-Sensoren
DOSING_SENSORS = {
    # States
    "DOS_1_CL": "Chlor-Dosierung Status",
    "DOS_4_PHM": "pH-Minus Status",
    "DOS_5_PHP": "pH-Plus Status",
    "DOS_6_FLOC": "Flockmittel Status",
    
    # Tägliche Mengen
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": {"name": "Chlor Tagesmenge", "unit": "ml"},
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": {"name": "pH-Minus Tagesmenge", "unit": "ml"},
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": {"name": "pH-Plus Tagesmenge", "unit": "ml"},
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": {"name": "Flockmittel Tagesmenge", "unit": "ml"},
    
    # Can-Empty Kontakte
    "INPUT_CE1": {"name": "Kanister 1 leer", "icon": "mdi:cup-off-outline"},
    "INPUT_CE2": {"name": "Kanister 2 leer", "icon": "mdi:cup-off-outline"},
    "INPUT_CE3": {"name": "Kanister 3 leer", "icon": "mdi:cup-off-outline"},
    "INPUT_CE4": {"name": "Kanister 4 leer", "icon": "mdi:cup-off-outline"},
}

# ⭐ Overflow-Sensoren
OVERFLOW_SENSORS = {
    "OVERFLOW_DRYRUN_STATE": {"name": "Trockenlauf-Schutz", "icon": "mdi:water-alert"},
    "OVERFLOW_OVERFILL_STATE": {"name": "Überfüll-Schutz", "icon": "mdi:water-plus"},
    "OVERFLOW_REFILL_STATE": {"name": "Nachfüll-Status", "icon": "mdi:water"},
    "ADC2_value": {"name": "Überlaufbehälter Füllstand", "unit": "cm", "icon": "mdi:water-percent"},
}

# ⭐ Pumpen-Sensoren
PUMP_SENSORS = {
    "PUMP": {"name": "Filterpumpe Status", "supports_3_state": True},
    "PUMP_RPM_0": {"name": "Pumpe STOP", "icon": "mdi:stop"},
    "PUMP_RPM_1": {"name": "Pumpe Stufe 1 (Eco)", "icon": "mdi:speedometer-slow"},
    "PUMP_RPM_2": {"name": "Pumpe Stufe 2 (Normal)", "icon": "mdi:speedometer-medium"},
    "PUMP_RPM_3": {"name": "Pumpe Stufe 3 (Boost)", "icon": "mdi:speedometer"},
    "PUMP_RUNTIME": {"name": "Pumpe Laufzeit täglich", "unit": None},
    "PUMP_LAST_ON": {"name": "Pumpe letzte Einschaltung", "device_class": "timestamp"},
    "PUMP_LAST_OFF": {"name": "Pumpe letzte Ausschaltung", "device_class": "timestamp"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# BINARY SENSOREN MIT 3-STATE UNTERSTÜTZUNG
# ═══════════════════════════════════════════════════════════════════════════════

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
    {"name": "Cover Open Contact", "key": "OPEN_CONTACT", "icon": "mdi:window-open-variant", 
     "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
    {"name": "Cover Stop Contact", "key": "STOP_CONTACT", "icon": "mdi:stop-circle-outline", 
     "feature_id": "cover_control"},
    {"name": "Cover Close Contact", "key": "CLOSE_CONTACT", "icon": "mdi:window-closed-variant", 
     "feature_id": "cover_control", "device_class": BinarySensorDeviceClass.OPENING},
]

# Digital Inputs hinzufügen
for i in range(1, 13):
    BINARY_SENSORS.append({
        "name": f"Digital Input {i}", 
        "key": f"INPUT{i}", 
        "icon": "mdi:electric-switch",
        "feature_id": "digital_inputs", 
        "entity_category": EntityCategory.DIAGNOSTIC
    })

# Digital CE Inputs hinzufügen
for i in range(1, 5):
    BINARY_SENSORS.append({
        "name": f"Digital Input CE{i}", 
        "key": f"INPUT_CE{i}", 
        "icon": "mdi:electric-switch",
        "feature_id": "digital_inputs", 
        "entity_category": EntityCategory.DIAGNOSTIC
    })

# ═══════════════════════════════════════════════════════════════════════════════
# SWITCHES MIT 3-STATE UNTERSTÜTZUNG
# ═══════════════════════════════════════════════════════════════════════════════

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
    {"name": "Dosierung pH-", "key": "DOS_4_PHM", "icon": "mdi:flask-minus", 
     "feature_id": "ph_control", "supports_3_state": True, "supports_timer": True},
    {"name": "Chlor-Dosierung", "key": "DOS_1_CL", "icon": "mdi:flask", 
     "feature_id": "chlorine_control", "supports_3_state": True, "supports_timer": True},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask", 
     "feature_id": "chlorine_control", "supports_3_state": True, "supports_timer": True},
    {"name": "PV-Überschuss", "key": "PVSURPLUS", "icon": "mdi:solar-power-variant", 
     "feature_id": "pv_surplus", "supports_3_state": True, "supports_speed": True},
    {"name": "Rückspülung", "key": "BACKWASH", "icon": "mdi:valve", 
     "feature_id": "backwash", "supports_3_state": True},
    {"name": "Nachspülung", "key": "BACKWASHRINSE", "icon": "mdi:valve", 
     "feature_id": "backwash", "supports_3_state": True},
]

# Extension 1 Switches hinzufügen
for i in range(1, 9):
    SWITCHES.append({
        "name": f"Extension 1.{i}", 
        "key": f"EXT1_{i}", 
        "icon": "mdi:toggle-switch-outline",
        "feature_id": "extension_outputs", 
        "supports_3_state": True
    })

# Extension 2 Switches hinzufügen
for i in range(1, 9):
    SWITCHES.append({
        "name": f"Extension 2.{i}", 
        "key": f"EXT2_{i}", 
        "icon": "mdi:toggle-switch-outline",
        "feature_id": "extension_outputs", 
        "supports_3_state": True
    })

# Omni DC Switches hinzufügen
for i in range(6):
    SWITCHES.append({
        "name": f"Omni DC{i} Output", 
        "key": f"OMNI_DC{i}", 
        "icon": "mdi:electric-switch",
        "feature_id": "extension_outputs", 
        "supports_3_state": True
    })

# DMX Scenes hinzufügen
for scene_num in range(1, 13):
    SWITCHES.append({
        "name": f"DMX Szene {scene_num}", 
        "key": f"DMX_SCENE{scene_num}", 
        "icon": "mdi:lightbulb-multiple",
        "feature_id": "led_lighting", 
        "supports_3_state": True
    })

# Digital Rules hinzufügen
for rule_num in range(1, 8):
    SWITCHES.append({
        "name": f"Schaltregel {rule_num}", 
        "key": f"DIRULE_{rule_num}", 
        "icon": "mdi:script-text",
        "feature_id": "digital_inputs", 
        "supports_3_state": True
    })

# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME UND TIMESTAMP SENSOREN
# ═══════════════════════════════════════════════════════════════════════════════

RUNTIME_SENSORS = {
    "PUMP_RUNTIME": {"name": "Pumpe Laufzeit", "icon": "mdi:timer", "unit": None},
    "SOLAR_RUNTIME": {"name": "Solar Laufzeit", "icon": "mdi:timer", "unit": None},
    "HEATER_RUNTIME": {"name": "Heizung Laufzeit", "icon": "mdi:timer", "unit": None},
    "LIGHT_RUNTIME": {"name": "Beleuchtung Laufzeit", "icon": "mdi:timer", "unit": None},
    "BACKWASH_RUNTIME": {"name": "Rückspülung Laufzeit", "icon": "mdi:timer", "unit": None},
}

# Runtime für Dosierungen
for i in [1, 4, 5, 6]:
    if i == 1:
        RUNTIME_SENSORS[f"DOS_{i}_CL_RUNTIME"] = {"name": f"Chlor Laufzeit", "icon": "mdi:timer", "unit": None}
    elif i == 4:
        RUNTIME_SENSORS[f"DOS_{i}_PHM_RUNTIME"] = {"name": f"pH-Minus Laufzeit", "icon": "mdi:timer", "unit": None}
    elif i == 5:
        RUNTIME_SENSORS[f"DOS_{i}_PHP_RUNTIME"] = {"name": f"pH-Plus Laufzeit", "icon": "mdi:timer", "unit": None}
    elif i == 6:
        RUNTIME_SENSORS[f"DOS_{i}_FLOC_RUNTIME"] = {"name": f"Flockmittel Laufzeit", "icon": "mdi:timer", "unit": None}

# Runtime für Erweiterungen
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}_RUNTIME"
        RUNTIME_SENSORS[key] = {
            "name": f"Ext {ext_bank}.{relay_num} Laufzeit",
            "icon": "mdi:timer",
            "unit": None
        }

TIMESTAMP_SENSORS = {
    "PUMP_LAST_ON": {"name": "Pumpe letzte Einschaltung"},
    "PUMP_LAST_OFF": {"name": "Pumpe letzte Ausschaltung"},
    "BACKWASH_LAST_AUTO_RUN": {"name": "Letzte automatische Rückspülung"},
    "BACKWASH_LAST_MANUAL_RUN": {"name": "Letzte manuelle Rückspülung"},
    "DOS_1_CL_LAST_CAN_RESET": {"name": "Chlor-Kanister letzter Reset"},
    "DOS_4_PHM_LAST_CAN_RESET": {"name": "pH-Minus-Kanister letzter Reset"},
    "DOS_5_PHP_LAST_CAN_RESET": {"name": "pH-Plus-Kanister letzter Reset"},
    "DOS_6_FLOC_LAST_CAN_RESET": {"name": "Flockmittel-Kanister letzter Reset"},
}

# Timestamps für Erweiterungen
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        TIMESTAMP_SENSORS[f"EXT{ext_bank}_{relay_num}_LAST_ON"] = {
            "name": f"Ext {ext_bank}.{relay_num} letzte Einschaltung"
        }
        TIMESTAMP_SENSORS[f"EXT{ext_bank}_{relay_num}_LAST_OFF"] = {
            "name": f"Ext {ext_bank}.{relay_num} letzte Ausschaltung"
        }

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

UNIT_MAP = {
    # Temperature sensors
    "water_temp": "°C", 
    "air_temp": "°C", 
    "temp_value": "°C",
    "SYSTEM_cpu_temperature": "°C",
    "SYSTEM_carrier_cpu_temperature": "°C",
    "SYSTEM_DosageModule_cpu_temperature": "°C",
    "SYSTEM_dosagemodule_cpu_temperature": "°C",
    "CPU_TEMP": "°C",
    "CPU_TEMP_CARRIER": "°C",
    "CPU_TEMPERATURE": "°C",
    
    # Water chemistry (pH OHNE unit!)
    "orp_value": "mV", 
    "pot_value": "mg/l",
    # pH_value hat absichtlich KEINE unit!
    
    # Analog values
    "ADC1_value": "bar", 
    "ADC2_value": "cm",
    "ADC3_value": "m³/h",
    "ADC4_value": None,  # 4-20mA generic
    "ADC5_value": "V",   # 0-10V
    "IMP1_value": "cm/s", 
    "IMP2_value": "m³/h",
    
    # Dosing amounts
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "ml",
}

# OneWire Temperaturen hinzufügen
for i in range(1, 13):
    UNIT_MAP[f"onewire{i}_value"] = "°C"

# Pump RPMs hinzufügen
for i in range(4):
    UNIT_MAP[f"PUMP_RPM_{i}"] = "RPM"
    UNIT_MAP[f"PUMP_RPM_{i}_VALUE"] = "RPM"

# Sensoren ohne Einheiten
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
    "time", "TIME", "CURRENT_TIME", "CPU_UPTIME",
    "BACKWASH_STEP", "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_2",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_3",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_4",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_5",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_6",
    "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_7",
}

# DOS States hinzufügen
for i in range(1, 7):
    NO_UNIT_SENSORS.add(f"DOS_{i}_CL_STATE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_PHM_STATE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_PHP_STATE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_FLOC_STATE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_CL_REMAINING_RANGE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_PHM_REMAINING_RANGE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_PHP_REMAINING_RANGE")
    NO_UNIT_SENSORS.add(f"DOS_{i}_FLOC_REMAINING_RANGE")

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

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
    "ADC3_value": "filter_control",
    "ADC4_value": None,
    "ADC5_value": None,
    "IMP1_value": "filter_control",
    "IMP2_value": "filter_control",
    
    # Runtime sensors
    "PUMP_RUNTIME": "filter_control",
    "SOLAR_RUNTIME": "solar",
    "HEATER_RUNTIME": "heating",
    "LIGHT_RUNTIME": "led_lighting",
    "BACKWASH_RUNTIME": "backwash",
    
    # System sensors
    "CPU_TEMP": None,
    "CPU_TEMP_CARRIER": None,
    "CPU_UPTIME": None,
}

# Dosing feature mappings
for i in range(1, 7):
    SENSOR_FEATURE_MAP[f"DOS_{i}_CL_STATE"] = "chlorine_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_CL_RUNTIME"] = "chlorine_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_PHM_STATE"] = "ph_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_PHM_RUNTIME"] = "ph_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_PHP_STATE"] = "ph_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_PHP_RUNTIME"] = "ph_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_FLOC_STATE"] = "chlorine_control"
    SENSOR_FEATURE_MAP[f"DOS_{i}_FLOC_RUNTIME"] = "chlorine_control"

# Extension runtime mappings
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        SENSOR_FEATURE_MAP[f"EXT{ext_bank}_{relay_num}_RUNTIME"] = "extension_outputs"

# Omni runtime mappings
for i in range(6):
    SENSOR_FEATURE_MAP[f"OMNI_DC{i}_RUNTIME"] = "extension_outputs"

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
}

# Extensions
for i in range(1, 9):
    SWITCH_FEATURE_MAP[f"EXT1_{i}"] = "extension_outputs"
    SWITCH_FEATURE_MAP[f"EXT2_{i}"] = "extension_outputs"

# DMX Scenes
for i in range(1, 13):
    SWITCH_FEATURE_MAP[f"DMX_SCENE{i}"] = "led_lighting"

# Digital Rules
for i in range(1, 8):
    SWITCH_FEATURE_MAP[f"DIRULE_{i}"] = "digital_inputs"

# Omni DCs
for i in range(6):
    SWITCH_FEATURE_MAP[f"OMNI_DC{i}"] = "extension_outputs"

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
}

# Digital Inputs
for i in range(1, 13):
    BINARY_SENSOR_FEATURE_MAP[f"INPUT{i}"] = "digital_inputs"
for i in range(1, 5):
    BINARY_SENSOR_FEATURE_MAP[f"INPUT_CE{i}"] = "digital_inputs"

# ═══════════════════════════════════════════════════════════════════════════════
# API-AKTIONEN UND SERVICE-DEFINITIONEN
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

# API-Request-Templates
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
# ERWEITERTE SERVICE-DEFINITIONEN
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
    "mobile_emergency_stop": {
        "name": "🚨 NOTAUS (Mobile)",
        "description": "Sofortiger Stopp aller kritischen Systeme",
        "target": "device",
        "fields": {
            "stop_reason": {
                "selector": {"select": {"options": ["leak", "equipment_fault", "maintenance"]}},
                "required": True,
                "description": "Grund für Notaus"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_device_state_info(raw_state: str, device_key: str = None) -> dict:
    """Ermittle erweiterte Zustandsinformationen für ein Gerät."""
    if not raw_state:
        return {"mode": "auto", "active": False, "priority": 50, "desc": "Unknown"}
    
    upper_state = str(raw_state).upper().strip()
    
    if upper_state in DEVICE_STATE_MAPPING:
        return DEVICE_STATE_MAPPING[upper_state]
    
    return {"mode": "auto", "active": None, "priority": 10, "desc": f"Unknown state: {raw_state}"}

def legacy_is_on_state(raw_state: str) -> bool:
    """Legacy-Funktion für einfache On/Off-Prüfung."""
    if not raw_state:
        return False
    
    # Teste zuerst Integer-Werte direkt
    try:
        int_state = int(raw_state) if isinstance(raw_state, (int, float)) else int(str(raw_state))
        if int_state in STATE_MAP:
            return STATE_MAP[int_state]
    except (ValueError, TypeError):
        pass
    
    # Dann String-Werte
    upper_state = str(raw_state).upper().strip()
    if upper_state in STATE_MAP:
        return STATE_MAP[upper_state]
    
    # Fallback zu erweiterten Zustandsinformationen
    state_info = get_device_state_info(raw_state)
    if state_info.get("active") is not None:
        return state_info.get("active")
    
    return False

def get_device_mode_from_state(raw_state: str, device_key: str = None) -> str:
    """Ermittle den Gerätemodus aus dem rohen Zustandswert."""
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
    """Ermittle das passende Icon für ein Gerät basierend auf Modus."""
    if device_key in STATE_ICONS:
        return STATE_ICONS[device_key].get(mode, STATE_ICONS[device_key].get("auto_inactive", "mdi:help"))
    
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
    """Ermittle die Anzeigefarbe für einen Gerätemodus."""
    return STATE_COLORS.get(mode, "#9E9E9E")

def validate_device_parameter(device_key: str, parameter: str, value: any) -> tuple[bool, str]:
    """Validiere einen Geräteparameter."""
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
    """Erstelle API-Request-String basierend auf Geräteparametern."""
    if device_key not in DEVICE_PARAMETERS:
        duration = params.get("duration", 0)
        value = params.get("value", 0)
        return f"{device_key},{action},{duration},{value}"
    
    device_config = DEVICE_PARAMETERS[device_key]
    template = device_config.get("api_template", "{key},{action},0,0")
    
    template_params = {
        "key": device_key,
        "action": action,
        "duration": params.get("duration", 0),
        "speed": params.get("speed", device_config.get("default_on_speed", 0)),
        "value": params.get("value", 0)
    }
    
    return template.format(**template_params)

def is_device_activity_detected(device_key: str, coordinator_data: dict) -> bool:
    """Prüfe, ob ein Gerät tatsächlich aktiv ist (für AUTO-Modus)."""
    if device_key not in DEVICE_PARAMETERS:
        return False
    
    device_config = DEVICE_PARAMETERS[device_key]
    activity_sensors = device_config.get("activity_sensors", [])
    thresholds = device_config.get("activity_threshold", {})
    
    if device_key == "PUMP":
        rpm = coordinator_data.get("PUMP_RPM_1_VALUE", 0)
        try:
            return int(float(rpm)) > thresholds.get("PUMP_RPM_1_VALUE", 100)
        except (ValueError, TypeError):
            return False
            
    elif device_key in ["HEATER", "SOLAR"]:
        if device_key == "HEATER":
            device_temp = coordinator_data.get("onewire5_value")
        else:
            device_temp = coordinator_data.get("onewire3_value")
            
        water_temp = coordinator_data.get("onewire1_value")
        
        if device_temp is not None and water_temp is not None:
            try:
                temp_diff = float(device_temp) - float(water_temp)
                required_diff = thresholds.get("temp_diff", 2.0)
                return temp_diff > required_diff
            except (ValueError, TypeError):
                return False
                
    elif device_key.startswith("DOS_"):
        runtime = coordinator_data.get(f"{device_key}_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
        state = coordinator_data.get(f"{device_key}_STATE", "")
        return str(state).upper() in ["ON", "ACTIVE", "DOSING", "1"]
        
    elif device_key.startswith("EXT"):
        runtime = coordinator_data.get(f"{device_key}_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
    elif device_key == "LIGHT":
        runtime = coordinator_data.get("LIGHT_RUNTIME", "")
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
            
    elif device_key == "BACKWASH":
        state = coordinator_data.get("BACKWASHSTATE", "")
        runtime = coordinator_data.get("BACKWASH_RUNTIME", "")
        
        if str(state).upper() in ["ON", "ACTIVE", "RUNNING", "1"]:
            return True
        if isinstance(runtime, str) and ":" in runtime:
            return runtime != "00:00:00"
    
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
    """Erstelle erweiterte Attribute für einen 3-State-Switch."""
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
            
        if device_key in DEVICE_PARAMETERS:
            speeds = DEVICE_PARAMETERS[device_key].get("speeds", {})
            attributes["available_speeds"] = list(speeds.keys())
            attributes["speed_names"] = speeds
            
    elif device_key.startswith("DOS_"):
        runtime = coordinator_data.get(f"{device_key}_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        remaining = coordinator_data.get(f"{device_key}_REMAINING_RANGE")
        if remaining:
            attributes["remaining_range"] = remaining
            
        state = coordinator_data.get(f"{device_key}_STATE")
        if state:
            attributes["dosing_state"] = state
            
        if device_key in DEVICE_PARAMETERS:
            dosing_config = DEVICE_PARAMETERS[device_key]
            attributes["dosing_type"] = dosing_config.get("dosing_type", "")
            attributes["max_duration"] = dosing_config.get("max_dosing_duration", 300)
            attributes["safety_interval"] = dosing_config.get("safety_interval", 300)
            
    elif device_key in ["HEATER", "SOLAR"]:
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
        runtime = coordinator_data.get(f"{device_key}_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        if device_key in DEVICE_PARAMETERS:
            ext_config = DEVICE_PARAMETERS[device_key]
            attributes["default_duration"] = ext_config.get("default_on_duration", 3600)
            attributes["max_duration"] = ext_config.get("max_duration", 86400)
            
    elif device_key == "LIGHT":
        runtime = coordinator_data.get("LIGHT_RUNTIME")
        if runtime:
            attributes["runtime"] = runtime
            
        if device_key in DEVICE_PARAMETERS:
            light_config = DEVICE_PARAMETERS[device_key]
            attributes["supports_color_pulse"] = light_config.get("supports_color_pulse", False)
            attributes["color_pulse_duration"] = light_config.get("color_pulse_duration", 150)
            
    elif device_key == "PVSURPLUS":
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
                
        if device_key in DEVICE_PARAMETERS:
            speeds = DEVICE_PARAMETERS[device_key].get("speeds", {})
            attributes["available_speeds"] = list(speeds.keys())
            attributes["speed_names"] = speeds
    
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
# VALIDIERUNG UND MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

DEVICE_VALIDATION_RULES = {
    "PUMP": {
        "min_speed": 1, "max_speed": 3,
        "min_off_duration": 60, "max_off_duration": 3600,
        "rpm_thresholds": {"min_active": 100, "max_normal": 3000}
    },
    "HEATER": {
        "min_temp": 20.0, "max_temp": 40.0, "temp_step": 0.5,
        "max_temp_diff": 50.0
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

MONITORING_CONFIG = {
    "critical_devices": ["PUMP", "HEATER", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP"],
    "monitoring_intervals": {
        "critical": 10,
        "normal": 30,
        "background": 120
    },
    "alert_thresholds": {
        "pump_rpm_min": 100,
        "temp_diff_max": 50,
        "dosing_runtime_max": 300,
        "ph_deviation_max": 0.5,
        "orp_deviation_max": 100,
        "pressure_max": 2.5,
        "temp_sensor_timeout": 300
    },
    "error_recovery": {
        "max_retries": 3,
        "retry_delay": 5,
        "fallback_to_auto": True
    }
}

ERROR_CODES = {
    "OK": {"severity": "info", "message": "Operation successful", "action": "none"},
    "ERROR": {"severity": "error", "message": "General error occurred", "action": "retry"},
    "HTTP_401": {"severity": "error", "message": "Authentication required - check credentials", "action": "check_auth"},
    "HTTP_404": {"severity": "error", "message": "API endpoint not found", "action": "check_url"},
    "HTTP_500": {"severity": "error", "message": "Controller overloaded", "action": "wait_retry"},
    "HTTP_TIMEOUT": {"severity": "warning", "message": "Request timeout", "action": "retry"},
    "INVALID_SPEED": {"severity": "error", "message": "Pump speed must be 1-3", "action": "validate_input"},
    "INVALID_DURATION": {"severity": "error", "message": "Duration outside valid range", "action": "validate_input"},
    "DOSING_SAFETY": {"severity": "warning", "message": "Dosing safety interval not met", "action": "enforce_delay"},
    "DEVICE_LOCKED": {"severity": "warning", "message": "Device in maintenance mode", "action": "wait_maintenance"},
    "TEMP_SENSOR_FAULT": {"severity": "error", "message": "Temperature sensor malfunction", "action": "disable_temp_control"}
}

STATUS_PRIORITIES = {
    "error": 100,
    "maintenance": 90,
    "manual_on": 80,
    "manual_off": 70,
    "auto_active": 60,
    "auto_inactive": 50,
    "unknown": 10
}

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
    "movement_timeout": 120,
    "position_update_interval": 5
}

# ═══════════════════════════════════════════════════════════════════════════════
# PV-ÜBERSCHUSS KONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PV_SURPLUS_CONFIG = {
    "activation_modes": {
        "digital_input": 1,
        "http_request": 2
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
# VIOLET STATE CLASS
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
# VERSION INFO UND EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

VERSION_INFO = {
    "version": INTEGRATION_VERSION,
    "release_date": "2024-12-20",
    "major_features": [
        "Complete 3-State Switch Support with State 4 Fix",
        "PVSURPLUS Parameter Support",
        "Cover String-State Handling",
        "Extended Sensor Coverage (147 API Parameters)",
        "Enhanced DMX Scene Control (12 Scenes)",
        "Complete Extension Relay Support (EXT1/EXT2)",
        "Advanced Dosing Sensors with Daily Amounts",
        "System Temperature Monitoring",
        "Overflow Protection Sensors",
        "Complete Backwash State Tracking"
    ],
    "critical_fixes": [
        "STATE_MAP now includes State 4 (Manual Forced ON)",
        "PVSURPLUS added to SWITCH_FUNCTIONS",
        "COVER_STATE_MAP supports string states",
        "All 147 API parameters accessible"
    ]
}

# Hauptexporte
__all__ = [
    # Core
    "DOMAIN", "INTEGRATION_VERSION", "MANUFACTURER",
    
    # Configuration
    "CONF_API_URL", "CONF_USERNAME", "CONF_PASSWORD", "CONF_ACTIVE_FEATURES",
    "DEFAULT_POLLING_INTERVAL", "DEFAULT_TIMEOUT_DURATION",
    
    # API
    "API_READINGS", "API_SET_FUNCTION_MANUALLY", "ACTION_ON", "ACTION_OFF", "ACTION_AUTO",
    
    # State Support
    "DEVICE_STATE_MAPPING", "STATE_MAP", "COVER_STATE_MAP", "STATE_ICONS", "STATE_COLORS",
    "get_device_state_info", "get_device_mode_from_state", "is_device_activity_detected",
    "VioletState", "legacy_is_on_state",
    
    # Devices
    "DEVICE_PARAMETERS", "SWITCHES", "BINARY_SENSORS", "SWITCH_FUNCTIONS",
    "AVAILABLE_FEATURES", "ENHANCED_SERVICES",
    
    # Sensors
    "TEMP_SENSORS", "WATER_CHEM_SENSORS", "ANALOG_SENSORS", "SYSTEM_SENSORS",
    "BACKWASH_SENSORS", "DOSING_SENSORS", "OVERFLOW_SENSORS", "PUMP_SENSORS",
    "RUNTIME_SENSORS", "TIMESTAMP_SENSORS",
    
    # Utilities
    "validate_device_parameter", "build_api_request", "get_enhanced_switch_attributes",
    "UNIT_MAP", "NO_UNIT_SENSORS", "SENSOR_FEATURE_MAP", "SWITCH_FEATURE_MAP",
    
    # Version
    "VERSION_INFO"
]