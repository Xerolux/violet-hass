"""This module defines constants related to the Violet Pool Controller API.

It includes API endpoints, command actions, rate limiting settings, and
definitions for various controllable functions like switches, covers, and dosing pumps.
These constants provide a centralized and consistent way to interact with the
controller's HTTP API.
"""

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

# Settings for optimizing data refreshes by fetching specific groups.
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
SPECIFIC_FULL_REFRESH_INTERVAL = 10  # Number of updates before a full refresh

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

# Common Query and Target Parameters
QUERY_ALL = "ALL"
TARGET_PH = "pH"
TARGET_ORP = "ORP"
TARGET_MIN_CHLORINE = "MinChlorine"
KEY_MAINTENANCE = "MAINTENANCE"
KEY_PVSURPLUS = "PVSURPLUS"

# =============================================================================
# API RATE LIMITING
# =============================================================================

API_RATE_LIMIT_REQUESTS = 10  # Max requests per window
API_RATE_LIMIT_WINDOW = 1.0  # Window duration in seconds
API_RATE_LIMIT_BURST = 3  # Number of burst requests allowed
API_RATE_LIMIT_RETRY_AFTER = 0.1  # Wait time after exceeding the limit

# Priority levels for API requests
API_PRIORITY_CRITICAL = 1  # For state changes and critical operations
API_PRIORITY_HIGH = 2  # For target value updates
API_PRIORITY_NORMAL = 3  # For regular data fetches
API_PRIORITY_LOW = 4  # For history and statistics

# =============================================================================
# API FUNCTION AND KEY DEFINITIONS
# =============================================================================

# Base switchable functions
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

# Dynamically add extension relays
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        SWITCH_FUNCTIONS[f"EXT{ext_bank}_{relay_num}"] = (
            f"Erweiterung {ext_bank}.{relay_num}"
        )

# Dynamically add DMX scenes
for scene_num in range(1, 13):
    SWITCH_FUNCTIONS[f"DMX_SCENE{scene_num}"] = f"DMX Szene {scene_num}"

# Dynamically add digital input rules
for rule_num in range(1, 8):
    SWITCH_FUNCTIONS[f"DIRULE_{rule_num}"] = f"Schaltregel {rule_num}"

# Dynamically add Omni DC outputs
for dc_num in range(6):
    SWITCH_FUNCTIONS[f"OMNI_DC{dc_num}"] = f"Omni DC{dc_num}"

# Cover control functions
COVER_FUNCTIONS = {
    "OPEN": "COVER_OPEN",
    "CLOSE": "COVER_CLOSE",
    "STOP": "COVER_STOP",
}

# Dosing pump functions
DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO",
    "Flockmittel": "DOS_6_FLOC",
}
