# Domain der Integration
DOMAIN = "violet_pool_controller"

# Konfigurationsschlüssel
CONF_API_URL = "host"  # Umbenannt zu 'host' – standardgemäß in Home Assistant
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"  # Added missing constant
CONF_RETRY_ATTEMPTS = "retry_attempts"      # Added missing constant
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"  # Device-Name hinzufügen

# Neue Konfigurationsschlüssel für erweiterte Features
CONF_POOL_SIZE = "pool_size"  # in m³
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"
CONF_ACTIVE_FEATURES = "active_features"

# Standardwerte
DEFAULT_POLLING_INTERVAL = 10  # Standard-Pollingintervall in Sekunden
DEFAULT_TIMEOUT_DURATION = 10  # Added default value
DEFAULT_RETRY_ATTEMPTS = 3     # Added default value
DEFAULT_USE_SSL = False  # Standard-SSL-Einstellung
DEFAULT_MQTT_ENABLED = False  # MQTT standardmäßig deaktiviert
DEFAULT_DEVICE_NAME = "Violet Pool Controller"  # Standard-Gerätename
DEFAULT_POOL_SIZE = 50  # m³
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

# Integrationsdetails
INTEGRATION_VERSION = "0.0.9.6"  # Erhöhte Version für die überarbeitete Integration

# Logger-Name
LOGGER_NAME = f"{DOMAIN}_logger"  # Einheitlich mit den anderen Dateien

# API-Endpunkte (Pfad-Erweiterungen)
API_READINGS = "/getReadings"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"
API_SET_DOSING_PARAMETERS = "/setDosingParameters"  # Neuer Endpunkt für Dosierungsparameter
API_SET_TARGET_VALUES = "/setTargetValues"  # Neuer Endpunkt für Sollwerte

# Herstellerinformationen
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# Verfügbare Switch-Funktionen
SWITCH_FUNCTIONS = {
    "PUMP": "Pumpe",
    "SOLAR": "Absorber",
    "HEATER": "Heizung",
    "LIGHT": "Licht",
    "ECO": "Eco-Modus",
    "BACKWASH": "Rückspülung",
    "BACKWASHRINSE": "Nachspülung",
    "EXT1_1": "Relais 1-1",
    "EXT1_2": "Relais 1-2",
    "EXT1_3": "Relais 1-3",
    "EXT1_4": "Relais 1-4",
    "EXT1_5": "Relais 1-5",
    "EXT1_6": "Relais 1-6",
    "EXT1_7": "Relais 1-7",
    "EXT1_8": "Relais 1-8",
    "EXT2_1": "Relais 2-1",
    "EXT2_2": "Relais 2-2",
    "EXT2_3": "Relais 2-3",
    "EXT2_4": "Relais 2-4",
    "EXT2_5": "Relais 2-5",
    "EXT2_6": "Relais 2-6",
    "EXT2_7": "Relais 2-7",
    "EXT2_8": "Relais 2-8",
    "DMX_SCENE1": "DMX Szene 1",
    "DMX_SCENE2": "DMX Szene 2",
    "DMX_SCENE3": "DMX Szene 3",
    "DMX_SCENE4": "DMX Szene 4",
    "DMX_SCENE5": "DMX Szene 5",
    "DMX_SCENE6": "DMX Szene 6",
    "DMX_SCENE7": "DMX Szene 7",
    "DMX_SCENE8": "DMX Szene 8",
    "DMX_SCENE9": "DMX Szene 9",
    "DMX_SCENE10": "DMX Szene 10",
    "DMX_SCENE11": "DMX Szene 11",
    "DMX_SCENE12": "DMX Szene 12",
    "REFILL": "Nachfüllen",
    "DIRULE_1": "Schaltregel 1",
    "DIRULE_2": "Schaltregel 2",
    "DIRULE_3": "Schaltregel 3",
    "DIRULE_4": "Schaltregel 4",
    "DIRULE_5": "Schaltregel 5",
    "DIRULE_6": "Schaltregel 6",
    "DIRULE_7": "Schaltregel 7",
    "PVSURPLUS": "PV-Überschuss",
}

# Verfügbare Cover-Funktionen
COVER_FUNCTIONS = {
    "OPEN": "COVER_OPEN",   # Diese Werte müssen gemäß der API angepasst werden
    "CLOSE": "COVER_CLOSE", # Falls das Cover über direkte Befehle gesteuert wird
    "STOP": "COVER_STOP",
}

# Verfügbare Dosierungsfunktionen
DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO",
    "Flockmittel": "DOS_6_FLOC",
}

# Abbildung von API-Status-Werten auf Home Assistant Zustände
STATE_MAP = {
    0: False,  # AUTO (not on)
    1: True,   # AUTO (on)
    2: False,  # OFF by control rule
    3: True,   # ON by emergency rule
    4: True,   # MANUAL ON
    5: False,  # OFF by emergency rule
    6: False,  # MANUAL OFF
}

# Temperatur- und andere Sensor-Mapping
TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Absorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
    # Weitere Temperatursensoren können nach Bedarf hinzugefügt werden
}

# Wasserchemiesensoren
WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": "pH"},
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}

# Weitere Sensortypen können nach Bedarf hinzugefügt werden
ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Füllstand", "icon": "mdi:water-percent", "unit": "cm"},
    "IMP1_value": {"name": "Messwasser-Durchfluss", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Förderleistung", "icon": "mdi:pump", "unit": "m³/h"},
}

# Liste der Sensoren, die als binary_sensor dargestellt werden sollen
BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:valve"},
    {"name": "Refill State", "key": "REFILL", "icon": "mdi:water"},
    {"name": "ECO Mode", "key": "ECO", "icon": "mdi:leaf"},
    # Weitere binäre Sensoren können nach Bedarf hinzugefügt werden
]

# Liste der Schalter die als Switch dargestellt werden
SWITCHES = [
    {"name": "Pumpe", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Absorber", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heizung", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Licht", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Dosierung Chlor", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "Dosierung pH-", "key": "DOS_4_PHM", "icon": "mdi:flask"},
    {"name": "Eco-Modus", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Rückspülung", "key": "BACKWASH", "icon": "mdi:valve"},
    {"name": "Nachspülung", "key": "BACKWASHRINSE", "icon": "mdi:water-sync"},
    {"name": "Dosierung pH+", "key": "DOS_5_PHP", "icon": "mdi:flask"},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask"},
    {"name": "PV-Überschuss", "key": "PVSURPLUS", "icon": "mdi:solar-power"},
    # Weitere Schalter können nach Bedarf hinzugefügt werden
]
