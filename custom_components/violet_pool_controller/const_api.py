"""API-bezogene Konstanten für die Violet Pool Controller Integration."""

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
# API RATE LIMITING (NEW)
# =============================================================================

# Rate limiting configuration
API_RATE_LIMIT_REQUESTS = 10  # Max requests per window
API_RATE_LIMIT_WINDOW = 1.0   # Window in seconds
API_RATE_LIMIT_BURST = 3      # Allow burst of N requests
API_RATE_LIMIT_RETRY_AFTER = 0.1  # Wait time after limit exceeded

# API request priority levels
API_PRIORITY_CRITICAL = 1  # State changes, critical operations
API_PRIORITY_HIGH = 2      # Target value updates
API_PRIORITY_NORMAL = 3    # Regular data fetches
API_PRIORITY_LOW = 4       # History, statistics

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
    "PVSURPLUS": "PV-Überschuss",
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

__all__ = [
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
]
