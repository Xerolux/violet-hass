"""Konstanten für die Violet Pool Controller Integration - MODULAR VERSION.

Dieses Modul dient als zentrale Importstelle für alle Konstanten.
Die Konstanten sind jetzt in mehrere Dateien aufgeteilt für bessere Wartbarkeit:

- const_api.py: API Endpoints, Actions, Rate Limiting
- const_devices.py: Device Parameters, State Mappings, Validation
- const_sensors.py: Sensor Definitions, Units
- const_features.py: Features, Switches, Binary Sensors, Setpoints
"""

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
# POOL CONFIGURATION
# =============================================================================

POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# =============================================================================
# IMPORT FROM SUBMODULES
# =============================================================================

# Import API-related constants
from .const_api import (
    API_READINGS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES,
    API_GET_CONFIG,
    API_SET_CONFIG,
    API_GET_CALIB_RAW_VALUES,
    API_GET_CALIB_HISTORY,
    API_RESTORE_CALIBRATION,
    API_SET_OUTPUT_TESTMODE,
    API_GET_HISTORY,
    API_GET_WEATHER_DATA,
    API_GET_OVERALL_DOSING,
    API_GET_OUTPUT_STATES,
    SPECIFIC_READING_GROUPS,
    SPECIFIC_FULL_REFRESH_INTERVAL,
    ACTION_ON,
    ACTION_OFF,
    ACTION_AUTO,
    ACTION_PUSH,
    ACTION_MAN,
    ACTION_COLOR,
    ACTION_ALLON,
    ACTION_ALLOFF,
    ACTION_ALLAUTO,
    ACTION_LOCK,
    ACTION_UNLOCK,
    QUERY_ALL,
    TARGET_PH,
    TARGET_ORP,
    TARGET_MIN_CHLORINE,
    KEY_MAINTENANCE,
    KEY_PVSURPLUS,
    API_RATE_LIMIT_REQUESTS,
    API_RATE_LIMIT_WINDOW,
    API_RATE_LIMIT_BURST,
    API_RATE_LIMIT_RETRY_AFTER,
    API_PRIORITY_CRITICAL,
    API_PRIORITY_HIGH,
    API_PRIORITY_NORMAL,
    API_PRIORITY_LOW,
    SWITCH_FUNCTIONS,
    COVER_FUNCTIONS,
    DOSING_FUNCTIONS,
)

# Import device-related constants
from .const_devices import (
    DEVICE_PARAMETERS,
    DEVICE_STATE_MAPPING,
    STATE_MAP,
    COVER_STATE_MAP,
    STATE_ICONS,
    STATE_COLORS,
    STATE_TRANSLATIONS,
    DEVICE_VALIDATION_RULES,
    get_device_state_info,
    legacy_is_on_state,
    get_device_mode_from_state,
    get_device_icon,
    get_device_color,
    VioletState,
)

# Import sensor-related constants
from .const_sensors import (
    TEMP_SENSORS,
    WATER_CHEM_SENSORS,
    ANALOG_SENSORS,
    SYSTEM_SENSORS,
    RUNTIME_SENSORS,
    TIMESTAMP_SENSORS,
    UNIT_MAP,
    NO_UNIT_SENSORS,
    SENSOR_FEATURE_MAP,
)

# Import feature-related constants
from .const_features import (
    AVAILABLE_FEATURES,
    BINARY_SENSORS,
    SWITCHES,
    SETPOINT_DEFINITIONS,
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
        "Modular Constants Structure (const_api, const_devices, const_sensors, const_features)",
        "API Rate Limiting Support",
    ],
    "critical_fixes": [
        "STATE_MAP now includes State 4 (Manual Forced ON)",
        "PVSURPLUS added to SWITCH_FUNCTIONS",
        "COVER_STATE_MAP supports string states",
        "Migrated to clean Semantic Versioning",
        "Modular code structure for better maintainability",
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
    "CONF_POLLING_INTERVAL",
    "CONF_TIMEOUT_DURATION",
    "CONF_RETRY_ATTEMPTS",
    "CONF_USE_SSL",
    "CONF_DEVICE_ID",
    "CONF_DEVICE_NAME",
    "CONF_POOL_SIZE",
    "CONF_POOL_TYPE",
    "CONF_DISINFECTION_METHOD",
    "DEFAULT_POLLING_INTERVAL",
    "DEFAULT_TIMEOUT_DURATION",
    "DEFAULT_RETRY_ATTEMPTS",
    "DEFAULT_USE_SSL",
    "DEFAULT_DEVICE_NAME",
    "DEFAULT_POOL_SIZE",
    "DEFAULT_POOL_TYPE",
    "DEFAULT_DISINFECTION_METHOD",
    "POOL_TYPES",
    "DISINFECTION_METHODS",
    # API (from const_api)
    "API_READINGS",
    "API_SET_FUNCTION_MANUALLY",
    "API_SET_DOSING_PARAMETERS",
    "API_SET_TARGET_VALUES",
    "API_GET_CONFIG",
    "API_SET_CONFIG",
    "API_GET_CALIB_RAW_VALUES",
    "API_GET_CALIB_HISTORY",
    "API_RESTORE_CALIBRATION",
    "API_SET_OUTPUT_TESTMODE",
    "API_GET_HISTORY",
    "API_GET_WEATHER_DATA",
    "API_GET_OVERALL_DOSING",
    "API_GET_OUTPUT_STATES",
    "SPECIFIC_READING_GROUPS",
    "SPECIFIC_FULL_REFRESH_INTERVAL",
    "ACTION_ON",
    "ACTION_OFF",
    "ACTION_AUTO",
    "ACTION_PUSH",
    "ACTION_MAN",
    "ACTION_COLOR",
    "ACTION_ALLON",
    "ACTION_ALLOFF",
    "ACTION_ALLAUTO",
    "ACTION_LOCK",
    "ACTION_UNLOCK",
    "QUERY_ALL",
    "TARGET_PH",
    "TARGET_ORP",
    "TARGET_MIN_CHLORINE",
    "KEY_MAINTENANCE",
    "KEY_PVSURPLUS",
    "API_RATE_LIMIT_REQUESTS",
    "API_RATE_LIMIT_WINDOW",
    "API_RATE_LIMIT_BURST",
    "API_RATE_LIMIT_RETRY_AFTER",
    "API_PRIORITY_CRITICAL",
    "API_PRIORITY_HIGH",
    "API_PRIORITY_NORMAL",
    "API_PRIORITY_LOW",
    "SWITCH_FUNCTIONS",
    "COVER_FUNCTIONS",
    "DOSING_FUNCTIONS",
    # Devices (from const_devices)
    "DEVICE_PARAMETERS",
    "DEVICE_STATE_MAPPING",
    "STATE_MAP",
    "COVER_STATE_MAP",
    "STATE_ICONS",
    "STATE_COLORS",
    "STATE_TRANSLATIONS",
    "DEVICE_VALIDATION_RULES",
    "get_device_state_info",
    "legacy_is_on_state",
    "get_device_mode_from_state",
    "get_device_icon",
    "get_device_color",
    "VioletState",
    # Sensors (from const_sensors)
    "TEMP_SENSORS",
    "WATER_CHEM_SENSORS",
    "ANALOG_SENSORS",
    "SYSTEM_SENSORS",
    "RUNTIME_SENSORS",
    "TIMESTAMP_SENSORS",
    "UNIT_MAP",
    "NO_UNIT_SENSORS",
    "SENSOR_FEATURE_MAP",
    # Features (from const_features)
    "AVAILABLE_FEATURES",
    "BINARY_SENSORS",
    "SWITCHES",
    "SETPOINT_DEFINITIONS",
    # Version
    "VERSION_INFO",
]
