"""Konstanten für die Violet Pool Controller Integration in Home Assistant."""
from typing import Final, List, Dict, Any

# Domain der Integration
DOMAIN: Final[str] = "violet_pool_controller"

# Integrationsdetails
INTEGRATION_VERSION: Final[str] = "0.0.9.7"
MANUFACTURER: Final[str] = "PoolDigital GmbH & Co. KG"

# Logger-Name
LOGGER_NAME: Final[str] = f"{DOMAIN}_logger"

# Konfigurationsschlüssel (aus config_flow und bestehende)
CONF_API_URL: Final[str] = "host"
CONF_USERNAME: Final[str] = "username"
CONF_PASSWORD: Final[str] = "password"
CONF_POLLING_INTERVAL: Final[str] = "polling_interval"
CONF_TIMEOUT_DURATION: Final[str] = "timeout_duration"
CONF_RETRY_ATTEMPTS: Final[str] = "retry_attempts"
CONF_USE_SSL: Final[str] = "use_ssl"
CONF_DEVICE_ID: Final[str] = "device_id"
CONF_DEVICE_NAME: Final[str] = "device_name"
CONF_ACTIVE_FEATURES: Final[str] = "active_features"

# Neue Konfigurationsschlüssel (aus config_flow)
CONF_POOL_SIZE: Final[str] = "pool_size"    # in m³
CONF_POOL_TYPE: Final[str] = "pool_type"
CONF_DISINFECTION_METHOD: Final[str] = "disinfection_method"

# Standardwerte (aus config_flow und bestehende)
DEFAULT_POLLING_INTERVAL: Final[int] = 10  # Sekunden
DEFAULT_TIMEOUT_DURATION: Final[int] = 10  # Sekunden
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_USE_SSL: Final[bool] = False
DEFAULT_DEVICE_NAME: Final[str] = "Violet Pool Controller"
DEFAULT_POOL_SIZE: Final[int] = 50  # m³
DEFAULT_POOL_TYPE: Final[str] = "outdoor"
DEFAULT_DISINFECTION_METHOD: Final[str] = "chlorine"


# API-Endpunkte (Pfad-Erweiterungen)
API_READINGS: Final[str] = "/getReadings"
API_SET_FUNCTION_MANUALLY: Final[str] = "/setFunctionManually"
API_SET_DOSING_PARAMETERS: Final[str] = "/setDosingParameters"
API_SET_TARGET_VALUES: Final[str] = "/setTargetValues"
# API_SET_TEMPERATURE: Final[str] = "/set_temperature" # Already used in api.py, define if needed elsewhere


# Optionen für Pool-Typen und Desinfektionsmethoden (aus config_flow)
POOL_TYPES: Final[List[str]] = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS: Final[List[str]] = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# Verfügbare Features (aus config_flow)
AVAILABLE_FEATURES: Final[List[Dict[str, Any]]] = [
    {"id": "heating", "name": "Heizung", "default": True, "platforms": ["climate"]},
    {"id": "solar", "name": "Solarabsorber", "default": True, "platforms": ["climate"]},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True, "platforms": ["cover"]},
    {"id": "backwash", "name": "Rückspülung", "default": True, "platforms": ["switch"]},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True, "platforms": ["switch"]},
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]}, # Assuming switch for refill trigger
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch", "binary_sensor"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
    # New generic features for I/O if needed, or map existing features
    {"id": "digital_inputs", "name": "Digitale Eingänge", "default": False, "platforms": ["binary_sensor"]},
    {"id": "extension_outputs", "name": "Erweiterungsausgänge", "default": False, "platforms": ["switch"]},
]


# Verfügbare Switch-Funktionen (API Keys)
SWITCH_FUNCTIONS: Final[Dict[str, str]] = {
    "PUMP": "Pumpe", "SOLAR": "Absorber", "HEATER": "Heizung", "LIGHT": "Licht",
    "ECO": "Eco-Modus", "BACKWASH": "Rückspülung", "BACKWASHRINSE": "Nachspülung",
    "EXT1_1": "Relais 1-1", "EXT1_2": "Relais 1-2", "EXT1_3": "Relais 1-3", "EXT1_4": "Relais 1-4",
    "EXT1_5": "Relais 1-5", "EXT1_6": "Relais 1-6", "EXT1_7": "Relais 1-7", "EXT1_8": "Relais 1-8",
    "EXT2_1": "Relais 2-1", "EXT2_2": "Relais 2-2", "EXT2_3": "Relais 2-3", "EXT2_4": "Relais 2-4",
    "EXT2_5": "Relais 2-5", "EXT2_6": "Relais 2-6", "EXT2_7": "Relais 2-7", "EXT2_8": "Relais 2-8",
    "DMX_SCENE1": "DMX Szene 1", "DMX_SCENE2": "DMX Szene 2", "DMX_SCENE3": "DMX Szene 3",
    "DMX_SCENE4": "DMX Szene 4", "DMX_SCENE5": "DMX Szene 5", "DMX_SCENE6": "DMX Szene 6",
    "DMX_SCENE7": "DMX Szene 7", "DMX_SCENE8": "DMX Szene 8", "DMX_SCENE9": "DMX Szene 9",
    "DMX_SCENE10": "DMX Szene 10", "DMX_SCENE11": "DMX Szene 11", "DMX_SCENE12": "DMX Szene 12",
    "REFILL": "Nachfüllen",
    "DIRULE_1": "Schaltregel 1", "DIRULE_2": "Schaltregel 2", "DIRULE_3": "Schaltregel 3",
    "DIRULE_4": "Schaltregel 4", "DIRULE_5": "Schaltregel 5", "DIRULE_6": "Schaltregel 6",
    "DIRULE_7": "Schaltregel 7",
    "PVSURPLUS": "PV-Überschuss",
    # OMNI DC Outputs are also switches using setFunctionManually
    "OMNI_DC0": "Omni DC0", "OMNI_DC1": "Omni DC1", "OMNI_DC2": "Omni DC2",
    "OMNI_DC3": "Omni DC3", "OMNI_DC4": "Omni DC4", "OMNI_DC5": "Omni DC5",
}

# Verfügbare Cover-Funktionen (API Keys for setFunctionManually)
COVER_FUNCTIONS: Final[Dict[str, str]] = {
    "OPEN": "COVER_OPEN", "CLOSE": "COVER_CLOSE", "STOP": "COVER_STOP",
}

# Verfügbare Dosierungsfunktionen (API Keys for setFunctionManually with MAN action, or for setDosingParameters)
DOSING_FUNCTIONS: Final[Dict[str, str]] = {
    "pH-": "DOS_4_PHM", "pH+": "DOS_5_PHP", "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO", "Flockmittel": "DOS_6_FLOC",
}

# Abbildung von API-Status-Werten auf Home Assistant Zustände (für Switches/Binary Sensors)
STATE_MAP: Final[Dict[Any, bool]] = {
    0: False, 1: True, 2: False, 3: True, 4: True, 5: False, 6: False, # Integer states
    "0": False, "1": True, "2": False, "3": True, "4": True, "5": False, "6": False, # String states
    "ON": True, "OFF": False, "AUTO": False, # AUTO might be ON or OFF based on context, default to OFF if just "AUTO"
    "TRUE": True, "FALSE": False,
}

# Sensor-Mappings (für vordefinierte Sensoren)
TEMP_SENSORS: Final[Dict[str, Dict[str, str]]] = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Absorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
}
WATER_CHEM_SENSORS: Final[Dict[str, Dict[str, str]]] = {
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": "pH"},
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}
ANALOG_SENSORS: Final[Dict[str, Dict[str, str]]] = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Füllstand", "icon": "mdi:water-percent", "unit": "cm"},
    "IMP1_value": {"name": "Messwasser-Durchfluss", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Förderleistung", "icon": "mdi:pump", "unit": "m³/h"},
}

# Binary Sensor Definitions (Liste von Dictionaries)
BINARY_SENSORS: Final[List[Dict[str, str]]] = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump", "feature_id": "filter_control"}, # Existing
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power", "feature_id": "solar"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator", "feature_id": "heating"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb", "feature_id": "led_lighting"},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:valve", "feature_id": "backwash"},
    {"name": "Refill State", "key": "REFILL", "icon": "mdi:water", "feature_id": "water_refill"}, # Device class RUNNING handled in binary_sensor.py
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"}, # No specific feature_id, core function?

    # New Digital Inputs (feature_id: "digital_inputs")
    {"key": "INPUT1", "name": "Digital Input 1", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT2", "name": "Digital Input 2", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT3", "name": "Digital Input 3", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT4", "name": "Digital Input 4", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT5", "name": "Digital Input 5", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT6", "name": "Digital Input 6", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT7", "name": "Digital Input 7", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT8", "name": "Digital Input 8", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT9", "name": "Digital Input 9", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT10", "name": "Digital Input 10", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT11", "name": "Digital Input 11", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT12", "name": "Digital Input 12", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUTz1z2", "name": "Digital Input Z1Z2", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT_CE1", "name": "Digital Input CE1", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT_CE2", "name": "Digital Input CE2", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT_CE3", "name": "Digital Input CE3", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},
    {"key": "INPUT_CE4", "name": "Digital Input CE4", "icon": "mdi:electric-switch", "feature_id": "digital_inputs"},

    # New Cover Contacts (feature_id: "cover_control" or "cover_diagnostics")
    {"key": "OPEN_CONTACT", "name": "Cover Open Contact", "icon": "mdi:window-open-variant", "feature_id": "cover_control"},
    {"key": "STOP_CONTACT", "name": "Cover Stop Contact", "icon": "mdi:stop-circle-outline", "feature_id": "cover_control"},
    {"key": "CLOSE_CONTACT", "name": "Cover Close Contact", "icon": "mdi:window-closed-variant", "feature_id": "cover_control"},
]

# Switch Definitions (Liste von Dictionaries)
SWITCHES: Final[List[Dict[str, str]]] = [
    {"name": "Pumpe", "key": "PUMP", "icon": "mdi:water-pump", "feature_id": "filter_control"}, # Existing
    {"name": "Absorber", "key": "SOLAR", "icon": "mdi:solar-power", "feature_id": "solar"},
    {"name": "Heizung", "key": "HEATER", "icon": "mdi:radiator", "feature_id": "heating"},
    {"name": "Licht", "key": "LIGHT", "icon": "mdi:lightbulb", "feature_id": "led_lighting"},
    {"name": "Dosierung Chlor", "key": "DOS_1_CL", "icon": "mdi:flask", "feature_id": "chlorine_control"},
    {"name": "Dosierung pH-", "key": "DOS_4_PHM", "icon": "mdi:flask", "feature_id": "ph_control"},
    {"name": "Eco-Modus", "key": "ECO", "icon": "mdi:leaf"}, # No specific feature_id, core function?
    {"name": "Rückspülung", "key": "BACKWASH", "icon": "mdi:valve", "feature_id": "backwash"},
    {"name": "Nachspülung", "key": "BACKWASHRINSE", "icon": "mdi:water-sync", "feature_id": "backwash"},
    {"name": "Dosierung pH+", "key": "DOS_5_PHP", "icon": "mdi:flask", "feature_id": "ph_control"},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask", "feature_id": "chlorine_control"}, # Or a separate flocculant feature
    # PV-Überschuss is handled by a dedicated VioletPVSurplusSwitch class, not listed here for standard VioletSwitch

    # New Extension Outputs (feature_id: "extension_outputs")
    {"key": "EXT1_1", "name": "Extension 1.1", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_2", "name": "Extension 1.2", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_3", "name": "Extension 1.3", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_4", "name": "Extension 1.4", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_5", "name": "Extension 1.5", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_6", "name": "Extension 1.6", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_7", "name": "Extension 1.7", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT1_8", "name": "Extension 1.8", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_1", "name": "Extension 2.1", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_2", "name": "Extension 2.2", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_3", "name": "Extension 2.3", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_4", "name": "Extension 2.4", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_5", "name": "Extension 2.5", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_6", "name": "Extension 2.6", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_7", "name": "Extension 2.7", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},
    {"key": "EXT2_8", "name": "Extension 2.8", "icon": "mdi:toggle-switch-outline", "feature_id": "extension_outputs"},

    # New OMNI DC Outputs (feature_id: "extension_outputs" or specific omni feature)
    {"key": "OMNI_DC0", "name": "Omni DC0 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
    {"key": "OMNI_DC1", "name": "Omni DC1 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
    {"key": "OMNI_DC2", "name": "Omni DC2 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
    {"key": "OMNI_DC3", "name": "Omni DC3 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
    {"key": "OMNI_DC4", "name": "Omni DC4 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
    {"key": "OMNI_DC5", "name": "Omni DC5 Output", "icon": "mdi:electric-switch", "feature_id": "extension_outputs"},
]
# Note: PVSURPLUS switch is handled as a special class in switch.py so not listed in general SWITCHES.
# DMX_SCENEX and DIRULE_X are already in SWITCH_FUNCTIONS, if they need to be HA switches, they can be added to SWITCHES list.

# SETPOINT_DEFINITIONS for Number entities (from number.py)
# This would also be moved here if it's intended to be a central constant store.
# For now, assuming it stays in number.py as per its direct usage context there.
# If moved, ensure all necessary imports (NumberDeviceClass, EntityCategory) are here or handled.

# Example of moving SETPOINT_DEFINITIONS (partial, for pH only, to show structure)
# from homeassistant.components.number import NumberDeviceClass
# from homeassistant.helpers.entity import EntityCategory
# SETPOINT_DEFINITIONS: Final[List[Dict[str, Any]]] = [
#     {
#         "key": "ph_setpoint", # This is the HA entity key
#         "name": "pH Sollwert",
#         "min_value": 6.8, "max_value": 7.8, "step": 0.1,
#         "icon": "mdi:flask",
#         "api_key": "pH", # This is the 'target_type' for set_target_value
#         "feature_id": "ph_control",
#         "unit_of_measurement": "pH",
#         "api_endpoint": API_SET_TARGET_VALUES, # Use constant
#         "device_class": NumberDeviceClass.PH,
#         "entity_category": EntityCategory.CONFIG,
#         "setpoint_fields": ["pH_SETPOINT", "pH_TARGET", "TARGET_PH"], # Possible keys in API data for current setpoint
#         "indicator_fields": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"], # Related API keys to check for data presence
#         "default_value": 7.2,
#         # "dosing_type": None # Not needed for API_SET_TARGET_VALUES
#     },
#     # ... other number definitions would follow
# ]
