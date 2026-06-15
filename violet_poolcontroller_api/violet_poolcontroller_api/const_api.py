# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Module defining constants related to the Violet Pool Controller API.

Includes API endpoints, command actions, rate limiting settings, and
definitions for various controllable functions like switches, covers,
and dosing pumps. These constants provide a centralized and consistent
way to interact with the controller's HTTP API.
"""

from __future__ import annotations

# =============================================================================
# API ENDPOINTS
# =============================================================================

API_READINGS = "/getReadings"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"
API_GET_CONFIG = "/getConfig"
API_SET_CONFIG = "/setConfig"
API_GET_CALIB_RAW_VALUES = "/getCalibRawValues"
API_GET_CALIB_HISTORY = "/getCalibHistory"
API_RESTORE_CALIBRATION = "/restoreOldCalib"
API_SET_OUTPUT_TESTMODE = "/setOutputTestmode"
API_TRIGGER_MANUAL_DOSING = "/triggerManualDosing"
API_GET_HISTORY = "/getHistory"
API_GET_WEATHER_DATA = "/getWeatherdata"
API_GET_OVERALL_DOSING = "/getOverallDosing"
API_GET_OUTPUT_STATES = "/getOutputstates"
API_GET_OUTPUT_RUNTIMES = "/getOutputruntimes"
API_GET_LOG = "/getLog"
API_GET_NOTIFICATIONS = "/getNotifications"
API_INIT_UPDATE = "/initUpdate"
API_GET_UPDATE_STATE = "/getUpdateState"
API_GET_UPDATE_HISTORY = "/getUpdateHistory"

LOG_TYPE_ACTIONS = "actions"
LOG_TYPE_SWITCHING = "switching"
LOG_TYPE_ONEWIRE = "onewire"

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
TARGET_PH = "DOSAGE_phminus_setpoint"
TARGET_ORP = "DOSAGE_chlorine_setpoint_orp"
TARGET_MIN_CHLORINE = "DOSAGE_chlorine_lowerval_cl"
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
    "PUMP": "Filter Pump",
    "SOLAR": "Solar Absorber",
    "HEATER": "Heater",
    "LIGHT": "Lighting",
    "ECO": "Eco Mode",
    "BACKWASH": "Backwash",
    "BACKWASHRINSE": "Backwash Rinse",
    "REFILL": "Water Refill",
    "PVSURPLUS": "PV Surplus",
}

# Dynamically add extension relays
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        SWITCH_FUNCTIONS[f"EXT{ext_bank}_{relay_num}"] = f"Erweiterung {ext_bank}.{relay_num}"

DMX_SCENE_COUNT = 12  # Number of DMX scenes supported by the controller

# Dynamically add DMX scenes
for scene_num in range(1, DMX_SCENE_COUNT + 1):
    SWITCH_FUNCTIONS[f"DMX_SCENE{scene_num}"] = f"DMX Szene {scene_num}"

# Dynamically add digital input rules (controller exposes SWITCHINGRULE_1..8
# internally; we surface them as DIRULE_1..8 in line with the controller's
# DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1..8 keys – see setFunctionManually.js).
for rule_num in range(1, 9):
    SWITCH_FUNCTIONS[f"DIRULE_{rule_num}"] = f"Schaltregel {rule_num}"

# Dynamically add Omni DC outputs
for dc_num in range(6):
    SWITCH_FUNCTIONS[f"OMNI_DC{dc_num}"] = f"Omni DC{dc_num}"

# Dosing pump functions
DOSING_FUNCTIONS = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Elektrolyse": "DOS_2_ELO",
    "Flockmittel": "DOS_6_FLOC",
}

DOSING_OUTPUT_INDEX = {
    "DOS_1_CL": 0,
    "DOS_2_ELO": 1,
    "DOS_4_PHM": 3,
    "DOS_5_PHP": 4,
    "DOS_6_FLOC": 5,
}

DOSING_CONFIG_PREFIX = {
    "pH-": "DOSAGE_phminus",
    "pH+": "DOSAGE_phplus",
    "Chlor": "DOSAGE_chlorine",
    "Elektrolyse": "DOSAGE_electrolysis",
    "Flockmittel": "DOSAGE_floc",
    "H2O2": "DOSAGE_h2o2",
}

# =============================================================================
# CONTROLLER ERROR CODES (Manual Section 27.2 - Software 1.1.9)
# =============================================================================
# These codes are sent BY the controller TO external systems via outbound
# HTTP GET/POST requests.  Format: ERRORCODE=NNNN&SUBJECT=<text>
# They are NOT queryable via the API - the controller pushes them.

ERROR_SEVERITY_ALARM = "ALARM"
ERROR_SEVERITY_WARNING = "WARNING"
ERROR_SEVERITY_INFO = "INFO"
# REMINDER is a fourth category used by the controller for non-critical,
# user-actionable notifications (calibration due, update available, birthday
# greeting, daily status).  It is softer than INFO and should never trigger
# an alarm sensor in Home Assistant.
ERROR_SEVERITY_REMINDER = "REMINDER"

ERROR_CODES: dict[str, dict[str, str]] = {
    # -- System messages --
    "0000": {"severity": ERROR_SEVERITY_INFO, "message": "Testnachricht"},
    "0001": {"severity": ERROR_SEVERITY_INFO, "message": "Statusnachricht"},
    "0002": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Hardwareproblem (COM-Link zum Carrier fehlerhaft)",
    },
    # 0003: Friendly birthday greeting from the manufacturer (REMINDER).
    "0003": {
        "severity": ERROR_SEVERITY_REMINDER,
        "message": "Alles Gute zum Geburtstag!",
    },
    # 0005: Generic system status notification (REMINDER, not an error).
    # Source: notifications/codelist_*.csv row "0005".
    "0005": {
        "severity": ERROR_SEVERITY_REMINDER,
        "message": "Systemnachricht",
    },
    "0008": {"severity": ERROR_SEVERITY_WARNING, "message": "CPU-Temperatur hoch (> 83°C)"},
    "0009": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "CPU-Temperatur zu hoch (> 95°C)",
    },
    "0010": {
        "severity": ERROR_SEVERITY_REMINDER,
        "message": "Update steht zur Installation bereit. Keine Aktion erforderlich.",
    },
    "0011": {
        "severity": ERROR_SEVERITY_REMINDER,
        "message": "Update steht zur Installation bereit. Installation erforderlich.",
    },
    "0012": {
        "severity": ERROR_SEVERITY_REMINDER,
        "message": "Update steht zur Installation bereit. Installation erforderlich.",
    },
    # -- Filter / Circulation monitoring --
    "0020": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Filterdrucküberwachung (Druck zu niedrig)",
    },
    "0021": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Filterdrucküberwachung (Druck zu hoch)",
    },
    "0022": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Messwasserüberwachung (Anströmung fehlt)",
    },
    "0023": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Messwasserüberwachung (Anströmung zu hoch)",
    },
    "0024": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Zirkulationsüberwachung (Zirkulation fehlt)",
    },
    "0025": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Zirkulationsüberwachung (Zirkulation zu hoch)",
    },
    "0026": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Filterpumpen-Frostschutz nicht verfügbar - Sensorfehler",
    },
    "0027": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Absorber-Frostschutz nicht verfügbar - Sensorfehler",
    },
    # -- Heat exchanger --
    "0030": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Wärmetauscher Temperatur zu hoch",
    },
    "0031": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Wärmetauscher ÜberTemperatur-Schutz nicht verfügbar - Sensorfehler",
    },
    # -- Backwash / Water refill --
    "0040": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Rückspülung wurde ausgelassen",
    },
    "0041": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Nachspeisung fehlgeschlagen",
    },
    "0042": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Nachspeisung fehlgeschlagen",
    },
    # -- OmniTronic multi-port valve faults (BACKWASH_type == 1) --
    # Source: controlfunction_omni.js + notifications/codelist_*.csv 0045-0049.
    "0045": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "OmniTronic gibt keine Positionsrückmeldung (Rückspülen)",
    },
    "0046": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "OmniTronic gibt keine Positionsrückmeldung (Nachspülen)",
    },
    "0047": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Positionierung des Omni-Antriebs (Timeout)",
    },
    "0049": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "OmniTronic-Fehler: Rückmeldekontakt z1/z2 nicht geschlossen",
    },
    # -- Skimmer water level --
    "0050": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Wassernachspeisung / Schwimmerschalter",
    },
    "0051": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Wassernachspeisung / Schwimmerschalter",
    },
    "0052": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Wassernachspeisung / Schwimmerschalter",
    },
    "0053": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Wassernachspeisung / Magnetventil öffnet nicht",
    },
    "0054": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Fehler bei Wassernachspeisung / Magnetventil schließt nicht",
    },
    # -- Overflow tank --
    "0060": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Überlaufbehältersteuerung: Fehler bei Wassernachspeisung",
    },
    "0061": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Überlaufbehältersteuerung: Trockenlaufschutz ausgelöst",
    },
    "0062": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Überlaufbehälter: Pegelmessung fehlerhaft",
    },
    # -- Temperature control rules --
    "0071": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 1 ausgelöst",
    },
    "0072": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 2 ausgelöst",
    },
    "0073": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 3 ausgelöst",
    },
    "0074": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 4 ausgelöst",
    },
    "0075": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 5 ausgelöst",
    },
    "0076": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 6 ausgelöst",
    },
    "0077": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 7 ausgelöst",
    },
    "0078": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Temperatursteuerung, Schaltprogramm 8 ausgelöst",
    },
    # -- Analog rules --
    "0081": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 1 ausgelöst",
    },
    "0082": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 2 ausgelöst",
    },
    "0083": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 3 ausgelöst",
    },
    "0084": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 4 ausgelöst",
    },
    "0085": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 5 ausgelöst",
    },
    "0086": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 6 ausgelöst",
    },
    "0087": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 7 ausgelöst",
    },
    "0088": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Analogregeln, Schaltprogramm 8 ausgelöst",
    },
    # -- Switch input rules --
    "0091": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 1 ausgelöst",
    },
    "0092": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 2 ausgelöst",
    },
    "0093": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 3 ausgelöst",
    },
    "0094": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 4 ausgelöst",
    },
    "0095": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 5 ausgelöst",
    },
    "0096": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 6 ausgelöst",
    },
    "0097": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 7 ausgelöst",
    },
    "0098": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Schaltregeln: Schaltprogramm 8 ausgelöst",
    },
    # -- Temperature sensors --
    "0101": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 1: Fehler bei Messwerterfassung",
    },
    "0102": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 2: Fehler bei Messwerterfassung",
    },
    "0103": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 3: Fehler bei Messwerterfassung",
    },
    "0104": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 4: Fehler bei Messwerterfassung",
    },
    "0105": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 5: Fehler bei Messwerterfassung",
    },
    "0106": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 6: Fehler bei Messwerterfassung",
    },
    "0107": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 7: Fehler bei Messwerterfassung",
    },
    "0108": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 8: Fehler bei Messwerterfassung",
    },
    "0109": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 9: Fehler bei Messwerterfassung",
    },
    "0110": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 10: Fehler bei Messwerterfassung",
    },
    "0111": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 11: Fehler bei Messwerterfassung",
    },
    "0112": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Temperatursensor 12: Fehler bei Messwerterfassung",
    },
    # -- Chlor dosing --
    "0120": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Chlor-Dosierung: Redox Grenzwert erreicht",
    },
    "0121": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Chlor-Dosierung: Chlor Grenzwert erreicht",
    },
    "0122": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Chlor-Dosierung: max. Tagesdosierleistung erreicht",
    },
    "0123": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Chlor-Kanister Restinhalt niedrig",
    },
    "0124": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Chlor-Kanister leer",
    },
    "0125": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Leermeldekontakt: Chlor-Kanister",
    },
    # -- Electrolysis --
    "0130": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Elektrolyse: Redox Grenzwert erreicht",
    },
    "0131": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Elektrolyse: Chlor Grenzwert erreicht",
    },
    "0132": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Elektrolyse: maximale Tagesproduktion erreicht",
    },
    "0133": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Elektrolyse: Restlaufzeitwarnung für Zelle",
    },
    "0134": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Elektrolyse: maximale Gesamt-Betriebszeit erreicht",
    },
    # -- pH- dosing --
    "0150": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-minus Dosierung: pH Grenzwert erreicht",
    },
    "0152": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-minus Dosierung: max. Tagesdosierleistung erreicht",
    },
    "0153": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-minus Dosierung: Kanister Restinhalt niedrig",
    },
    "0154": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-minus Dosierung: Kanister leer",
    },
    "0155": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Leermeldekontakt: pH-minus Kanister",
    },
    # -- pH+ dosing --
    "0160": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-plus Dosierung: pH Grenzwert erreicht",
    },
    "0162": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-plus Dosierung: max. Tagesdosierleistung erreicht",
    },
    "0163": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-plus Dosierung: Kanister Restinhalt niedrig",
    },
    "0164": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "pH-plus Dosierung: Kanister leer",
    },
    "0165": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Leermeldekontakt: pH-plus Kanister",
    },
    # -- Flocculant --
    "0173": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Flockmittel: Kanister Restinhalt niedrig",
    },
    "0174": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Flockmittel: Kanister leer",
    },
    "0175": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Leermeldekontakt: Flockmittel Kanister",
    },
    # -- Calibration reminders --
    "0180": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Erinnerung: pH-Elektrode kalibrieren",
    },
    "0181": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Erinnerung: Redox-Elektrode kalibrieren",
    },
    "0182": {
        "severity": ERROR_SEVERITY_INFO,
        "message": "Erinnerung: Chlor-Elektrode kalibrieren",
    },
    # -- Hardware modules --
    "0200": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Dosiermodul: nicht mehr verbunden (abgesteckt)",
    },
    "0201": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Dosiermodul: Kommunikation verloren",
    },
    "0203": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Relais-Erweiterung 1: nicht mehr verbunden (abgesteckt)",
    },
    "0204": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Relais-Erweiterung 1: Kommunikation verloren",
    },
    "0206": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Relais-Erweiterung 2: nicht mehr verbunden (abgesteckt)",
    },
    "0207": {
        "severity": ERROR_SEVERITY_WARNING,
        "message": "Relais-Erweiterung 2: Kommunikation verloren",
    },
    "0208": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Zweites Dosiermodul erkannt. Wird ignoriert.",
    },
    "0209": {
        "severity": ERROR_SEVERITY_ALARM,
        "message": "Falsch codierte Relais Erweiterung erkannt.",
    },
}
